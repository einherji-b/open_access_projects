"""
ReadMe

MuseumLangAPI — API REST per il Riconoscimento della Lingua di Testi Museali

Questo script non richiede alcuna installazione manuale né file aggiuntivi. 
All'avvio provvede autonomamente a: installare le dipendenze python necessarie (se non già presenti), scaricare 
il modello ML dalla repository (se non già presente), avviare il server API REST

Il modello è una sklearn pipeline (countvectorizer + multinomialNB) in grado
di riconoscere tre lingue (italiano, inglese, tedesco)

>>>>> STRUTTURA
- Autoinstallazione delle dipendenze
- Importazioni
- Configurazione del logging
- Download automatico del modello ML
- Caricamento del modello ML in memoria
- Definizione dei modelli pydantic (schema dati input/output)
- Inizializzazione dell'app FastAPI con metadati
- Middleware per il logging automatico di ogni richiesta HTTP
- Endpoint principale POST/identify-language
- Endpoint di health-check  GET/health
- Avvio del server (uvicorn)

>>>>> COME ESEGUIRE
- Posizionarsi nella cartella ed eseguire da terminale 
    python museum_lang_api.py
- Al primo avvio le dipendenze vengono installate e il modello scaricato (ai successivi avvii parte immediatamente)

>>>>> ESEMPIO DI CHIAMATA (da terminale, mentre il server è in esecuzione)
    curl -X POST http://localhost:8000/identify-language -H "Content-Type: application/json" -d '{"text": "Questo è un testo di esempio in italiano."}'
"""




# >>>>> AUTOINSTALLAZIONE DELLE DIPENDENZE
# Questo blocco viene eseguito prima di qualsiasi import di librerie esterne usando solo moduli della libreria 
# standard (sys, subprocess) che sono sempre disponibili senza installazione.
# L'obiettivo di questo blocco è rendere lo script zero-setup (basta avere python).
# Viene usato subprocess.check_call() con sys.executable (non il comando python generico) per garantire che 
# pip installi nell'interprete corretto (anche in presenza di virtualenv multipli o ambienti conda)

import sys
import subprocess

# Lista delle dipendenze nel formato "nome_pacchetto==versione" (per garantirela riproducibilità)
# scikit-learn è fissato alla 1.6.0 perché il file .pkl è stato serializzato con quella versione
REQUIRED_PACKAGES = [
    "fastapi==0.115.12",
    "uvicorn==0.34.0",
    "scikit-learn==1.6.0",
    "pydantic==2.11.3",
]

# Mappa tra nome pacchetto pip e nome modulo python da importare.
IMPORT_NAME_MAP = {
    "fastapi": "fastapi",
    "uvicorn": "uvicorn",
    "scikit-learn": "sklearn",
    "pydantic":"pydantic",
}


def install_dependencies(packages: list) -> None:
    """
    Installa le dipendenze Python elencate usando pip
    Per ogni pacchetto verifica prima se è già importabile: se sì, salta
    l'installazione (evita reinstallazioni inutili ad ogni avvio). Se non è presente, lo installa

    Parametri
    packages : list ----- Lista di pacchetti nel formato "nome==versione"
    """
    for package in packages:
        package_name = package.split("==")[0].lower()
        import_name = IMPORT_NAME_MAP.get(package_name, package_name)

        try:
            __import__(import_name)  #se riesce, il pacchetto è già installato
        except ImportError:
            print(f"[SETUP] Installazione di '{package}'...")
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", package, "--quiet"],
                stdout=subprocess.DEVNULL,  #nasconde l'output verboso di pip
                stderr=subprocess.STDOUT,
            )
            print(f"[SETUP] '{package}' installato correttamente.")


#esegue l'installazione automatica prima di qualsiasi import esterno
install_dependencies(REQUIRED_PACKAGES)


# >>>>> IMPORTAZIONI
# Le dipendenze sono garantite quindi vengono importate in sicurezza.

import logging  #gestione dei log applicativi
import os #operazioni sul filesystem e variabili d'ambiente
import pickle  #deserializzazione del modello ML da file .pkl
import time   #misurazione del tempo di elaborazione per ogni richiesta
import urllib.request #download del modello via HTTP
import warnings  #soppressione avvisi non critici
from datetime import datetime  #timestamp leggibili nei messaggi di log
from fastapi import FastAPI, Request #per API REST con supporto nativo a pydantic per la validazione dei dati e generazione automatica della documentazione OpenAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator
import uvicorn #server ASGI (Asynchronous Server Gateway Interface) per eseguire applicazioni FastAPI in produzione


# >>>>> CONFIGURAZIONE DEL LOGGING
# permette di tracciare ogni richiesta,ogni risposta e ogni errore per scopi di monitoraggio
# sono configurati due handler:
#   - StreamHandler, che stampa sulla console (visibile durante l'esecuzione)
#   - FileHandler, che scrive su file .log
#il formato include: timestamp, livello di log,  messaggio

LOG_FILE = "museum_lang_api.log"   #file di log creato nella cartella corrente

logging.basicConfig(
    level=logging.INFO, #registra INFO, WARNING, ERROR, CRITICAL
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(), #output su console
        logging.FileHandler(LOG_FILE, encoding="utf-8"), #output su file
    ],
)

#Logger specifico per questa applicazione. Usare un logger nominato (non il root logger) è buona 
# prassi poichè evita conflitti con i logger di uvicorn/fastapi.
logger = logging.getLogger("MuseumLangAPI")


# >>>>> DOWNLOAD AUTOMATICO DEL MODELLO ML
# Il modello viene scaricato automaticamente dalla repository github solo se non è già presente nella cartella corrente.

MODEL_URL = (
    "https://github.com/Profession-AI/progetti-python/raw/refs/heads/main/Messa%20in%20produzione%20di%20un%20sistema%20per%20il%20riconoscimento%20della%20lingua%20di%20testi%20per%20un%20museo/language_detection_pipeline.pkl"
)

# Percorso locale dove salvare il modello. La variabile d'ambiente MODEL_PATH permette di scegliere il percorso
# senza modificare il codice
MODEL_PATH = os.environ.get(
    "MODEL_PATH",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "language_detection_pipeline.pkl"),
)


def download_model(url: str, destination: str) -> None:
    """
    Scarica il file del modello ML dalla URL indicata e lo salva localmente. Se il file esiste già allora la funzione 
    non fa nulla (così evitando download ripetuti).

    Parametri
    url : str ----- URL pubblica da cui scaricare il file .pkl del modello
    destination : str ----- Percorso completo del file locale in cui salvare il modello
    """

    if os.path.exists(destination):
        logger.info(f"Modello già presente in: {destination} ----- download saltato.")
        return

    logger.info(f"Download del modello da: {url}")

    try:
        # urllib.request.urlretrieve scarica il file e lo salva direttamente su disco
        urllib.request.urlretrieve(url, destination)
        file_size_kb = os.path.getsize(destination) / 1024
        logger.info(
            f"Modello scaricato correttamente "
            f"({file_size_kb:.1f} KB) >>>>> {destination}"
        )
    except Exception as e:
        logger.critical(f"Impossibile scaricare il modello: {e}")
        logger.critical("Verificare la connessione a internet e che l'url sia raggiungibil")
        raise SystemExit(1)  #arresta l'applicazione: senza modello non ha senso continuare


#avvia il download o verifica che il file esista già
download_model(MODEL_URL, MODEL_PATH)


# CARICAMENTO DEL MODELLO ML IN MEMORIA
#il modello viene caricato una sola volta all'avvio dell'API (non ad ogni richiesta).
#deserializzare un file pickle ad ogni chiamata HTTP introdurrebbe latenze in un ipotetico sistema multi-utente
#Il modello rimane in memoria per tutta la durata del processo server

warnings.filterwarnings("ignore", category=UserWarning, module="sklearn") #sopprimo gli avvisi di versione sklearn

try:
    logger.info(f"Caricamento del modello da: {MODEL_PATH}")
    with open(MODEL_PATH, "rb") as f:
        pipeline = pickle.load(f)
    logger.info(
        f"Modello caricato con successo. "
        f"Lingue supportate: {list(pipeline.classes_)}"
    )
except FileNotFoundError:
    logger.critical(f"File del modello non trovato: '{MODEL_PATH}'.")
    raise SystemExit(1)
except Exception as e:
    logger.critical(f"Errore durante il caricamento del modello: {e}")
    raise SystemExit(1)


# >>>>> MODELLI PYDANTIC (SCHEMA DATI INPUT/OUTPUT)
#pydantic definisce la struttura attesa dei dati in ingresso e in uscita garantendo:
#- Validazione automatica (campo obbligatorio, tipo corretto)
# - Messaggi di errore chiari in caso di input malformati
# - Documentazione openAPI generata automaticamente da FastAPI

class LanguageRequest(BaseModel):
    """
    Schema della richiesta in ingresso all'endpoint /identify-language

    Attributi
    text : str ----- Testo di cui identificare la lingua. Non può essere vuoto o solo spazi.
    """
    text: str

    @field_validator("text")
    @classmethod
    def text_must_not_be_empty(cls, value: str) -> str:
        """
        Validatore eseguito automaticamente da pydantic prima dell'endpoint.
        Rifiuta testi vuoti o composti da soli spazi bianchi restituendo un errore HTTP 422 con messaggio
        """
        if not value.strip():
            raise ValueError(
                "Il campo text non può essere vuoto o composto da soli spazi"
            )
        return value.strip()  #restituisce il testo ripulito dagli spazi iniziali e finali

    model_config = {
        "json_schema_extra": {
            "example": {"text": "testo di esempio in italiano."}
        }
    }


class LanguageResponse(BaseModel):
    """
    Schema della risposta di successo dell'endpoint /identify-language

    Attributi
    language_code : str ----- Codice ISO della lingua identificata (IT, EN, DE).
    confidence : float ----- Probabilità della previsione (tra 0.0 e 1.0)
    """
    language_code: str
    confidence: float

    model_config = {
        "json_schema_extra": {
            "example": {"language_code": "IT", "confidence": 0.98}
        }
    }



# >>>>> INIZIALIZZAZIONE DELL'APP FASTAPI
# I metadati (titolo, descrizione, versione) vengono mostrati nella documentazione interattiva disponibile agli indirizzi:
#Swagger UI ----- http://localhost:8000/docs
#ReDoc ----- http://localhost:8000/redoc

app = FastAPI(
    title="MuseumLangAPI",
    description=(
        "API REST per il riconoscimento automatico della lingua di testi museali"
        "Supporta Italiano (IT), Inglese (EN) e Tedesco (DE)"
    ),
    version="1.0.0",
)



# >>>>>MIDDLEWARE PER IL LOGGING DI OGNI RICHIESTA HTTP
# Il middleware intercetta tutte le richieste prima che raggiungano l'endpoint e tutte le risposte prima che siano inviate al client.
# Vengono registrati: ip client, metodo http, path, status code, tempo di elaborazione

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Middleware che registra nel log ogni richiesta ricevuta e risposta inviata

    Parametri
    request : Request ----- Oggetto richiesta FastAPI (metodo, URL, headers, IP, ecc.)
    call_next : Callable ----- Funzione che passa la richiesta all'endpoint appropriato.
    """
    client_ip = request.client.host if request.client else "unknown"

    logger.info(
        f"RICHIESTA | {request.method} {request.url.path} | Client: {client_ip}"
    )

    start_time = time.perf_counter()
    response   = await call_next(request)
    elapsed_ms = (time.perf_counter() - start_time) * 1000

    logger.info(
        f"RISPOSTA | {request.method} {request.url.path} | "
        f"Status: {response.status_code} | Tempo: {elapsed_ms:.1f}ms"
    )

    return response



# >>>>> ENDPOINT: POST/identify-language

@app.post(
    "/identify-language",
    response_model=LanguageResponse,
    responses={
        200: {"description": "Lingua identificata con successo"},
        422: {"description": "Input non valido (es. testo vuoto)"},
        500: {"description": "Errore interno durante la previsione"},
    },
    summary="Identifica la lingua di un testo",
    description=(
        "Riceve un testo in formato json e restituisce il codice della lingua riconosciuta (IT, EN o DE)"
        "con la relativa confidenza della previsione."
    ),
    tags=["Riconoscimento Lingua"],
)
async def identify_language(request_body: LanguageRequest):
    """
    Endpoint principale dell'API

    Flusso di elaborazione:
    - Pydantic valida il corpo della richiesta automaticamente. Se il testo è vuoto allora errore 422
    - Il testo viene passato al modello sklearn per la previsione della lingua
    - predict_proba() fornisce le probabilità per ciascuna lingua supportata
    - viene restituita la lingua con probabilità più alta e la relativa confidenza
    - n caso di errore imprevisto allora risposta 500 con messaggio (i dettagli tecnici vengono registrati nel log non esposti al client)

    Parametri
    request_body : LanguageRequest ------ Oggetto validato da Pydantic contenente il campo text

    Ritorna
    LanguageResponse ------ JSON con language_code e confidence
    """
    text = request_body.text  #testo già validato e ripulito da pydantic

    #log del testo ricevuto troncato a 100 caratteri per evitare log enormi
    logger.info(
        f"PREVISIONE | Testo: '{text[:100]}{'...' if len(text) > 100 else ''}'"
    )

    try:
        #previsione della lingua
        #predict() richiede una lista di stringhe e restituisce un array numpy con i codici lingua
        predicted_classes = pipeline.predict([text])
        language_code = predicted_classes[0]  #risultato per il nostro unico testo

        #calcolo della confidenza
        # predict_proba() restituisce una matrice (n_testi × n_lingue)
        #ogni colonna corrisponde a una lingua in pipeline.classes_
        # viene recuperata la probabilità corrispondente alla lingua predetta
        probabilities = pipeline.predict_proba([text])[0]
        class_index = list(pipeline.classes_).index(language_code)
        confidence = round(float(probabilities[class_index]), 4)

        logger.info(
            f"RISULTATO | Lingua: {language_code} | Confidenza: {confidence:.4f}"
        )

        return LanguageResponse(language_code=language_code, confidence=confidence)

    except Exception as e:
        #loggo il traceback completo per il debug interno
        logger.error(f"ERRORE | Previsione fallita: {e}", exc_info=True)
        #ma viene esposto solo un messaggio generico al client per sicurezza
        return JSONResponse(
            status_code=500,
            content={"error": "Errore interno del server durante l'analisi del testo."},
        )


# ENDPOINT: GET /health

@app.get(
    "/health",
    summary="Health check dell'API",
    description=(
        "Verifica che il servizio sia attivo e che il modello sia caricato. "
        "Usato da sistemi di monitoraggio (Kubernetes, load balancer, Uptime Robot)."
    ),
    tags=["Sistema"],
)
async def health_check():
    """
    Endpoint di health check per sistemi di monitoraggio

    Ritorna
    dict ----- JSON con stato del servizio, timestamp e informazioni sul modello
    """
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "model": {
            "loaded": pipeline is not None,
            "supported_languages": list(pipeline.classes_),
        },
    }


# AVVIO DEL SERVER
#questo blocco viene eseguito solo quando lo script viene lanciato direttamente con python museum_lang_api.py, non quando 
# viene importato come modulo

if __name__ == "__main__":
    logger.info("\n Avvio MuseumLangAPI v1.0.0")
    logger.info("Endpoint: POST http://localhost:8000/identify-language")
    logger.info("Swagger: http://localhost:8000/docs")
    logger.info("Health: http://localhost:8000/health")
    logger.info(f"Log file: {os.path.abspath(LOG_FILE)}")

    uvicorn.run(
        "museum_lang_api:app",  #riferimento al modulo e alla variabile app
        host="0.0.0.0", # accetta connessioni da qualsiasi interfaccia di rete
        port=8000,  # porta http standard
        reload=False, #disabilitato in produzione (abilitare solo in sviluppo)
        log_level="warning", #uvicorn usa il proprio logger; warning evita duplicati
    )