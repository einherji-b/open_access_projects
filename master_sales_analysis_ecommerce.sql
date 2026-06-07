-- PROGETTO: Analisi dei dati di vendita di un ecommerce


-- PREPARAZIONE DEI DATI

-- Creazione delle tabelle

CREATE TABLE prodotto (
    id INT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    prezzo DECIMAL(10, 2) NOT NULL
);

CREATE TABLE cliente (
    id INT PRIMARY KEY,
    email VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE ordini (
    id_prodotto INT,
    id_cliente INT,
    data DATE,
    FOREIGN KEY (id_prodotto) REFERENCES prodotto(id),
    FOREIGN KEY (id_cliente) REFERENCES cliente(id)
);

-- inserimento dati nella tabella prodotto
INSERT INTO prodotto (id, nome, prezzo) VALUES
(1,  'Smartphone',           699.99),
(2,  'Laptop',              1099.99),
(3,  'Auricolari Bluetooth',  49.99),
(4,  'Monitor 4K',           299.99),
(5,  'Mouse Wireless',        19.99),
(6,  'Tastiera Meccanica',    89.99),
(7,  'Tablet',               499.99),
(8,  'Smartwatch',           199.99),
(9,  'Fotocamera DSLR',      799.99),
(10, 'Stampante',            129.99);

-- inserimento dati nella tabella cliente
INSERT INTO cliente (id, email) VALUES
(1, 'mario.rossi@example.com'),
(2, 'luigi.verdi@example.com'),
(3, 'anna.bianchi@example.com'),
(4, 'carla.neri@example.com'),
(5, 'giulia.ferri@example.com');

-- inserimento dati nella tabella ordini
INSERT INTO ordini (id_prodotto, id_cliente, data) VALUES
(1,  1, '2025-01-01'),
(2,  1, '2025-01-02'),
(3,  2, '2025-01-03'),
(4,  3, '2025-01-04'),
(5,  4, '2025-01-05'),
(6,  5, '2025-01-06'),
(7,  1, '2025-01-07'),
(8,  2, '2025-01-08'),
(9,  3, '2025-01-09'),
(10, 4, '2025-01-10'),
(1,  5, '2025-01-11'),
(2,  1, '2025-01-12'),
(3,  2, '2025-01-13'),
(4,  3, '2025-01-14'),
(5,  4, '2025-01-15'),
(6,  5, '2025-01-16'),
(7,  1, '2025-01-17'),
(8,  2, '2025-01-18'),
(9,  3, '2025-01-19'),
(10, 4, '2025-01-20');


-- Dataset integrato
-- Unione ordini, clienti e prodotti in un'unica vista

CREATE VIEW vista_ordini_completa AS
SELECT
    o.id_cliente,
    c.email	AS email_cliente,
    o.id_prodotto,
    p.nome	AS nome_prodotto,
    p.prezzo,
    o.data	AS data_ordine
FROM ordini o
JOIN cliente c ON o.id_cliente  = c.id
JOIN prodotto p ON o.id_prodotto = p.id;


-- ANALISI DEI CLIENTI

-- Spesa totale per cliente, ordinata dalla più alta

SELECT
    id_cliente,
    email_cliente,
    SUM(prezzo)	AS spesa_totale
FROM vista_ordini_completa
GROUP BY id_cliente, email_cliente
ORDER BY spesa_totale DESC;

/*
  L'obiettivo di questa prima parte è stato quello di identificare i clienti che hanno speso di più.
  La query somma i prezzi di tutti i prodotti acquistati da ciascun cliente e li ordina in 
  modo decrescente, mettendo in evidenza i top spender
*/

-- ////////////////////////////////////////////////

-- ANALISI DEI PRODOTTI

-- Fatturato totale per prodotto, ordinato dal più alto

SELECT
    id_prodotto,
    nome_prodotto,
    SUM(prezzo)	AS fatturato_totale,
    COUNT(*)	AS numero_vendite
FROM vista_ordini_completa
GROUP BY id_prodotto, nome_prodotto
ORDER BY fatturato_totale DESC;

/*
  L'obiettivo di questa seconda parte è stato quello di determinare i prodotti con il maggiore fatturato.
  La query calcola il fatturato cumulato (prezzo * quantità venduta) per ogni prodotto e lo ordina in modo 
  decrescente per individuare i best-seller.
*/


-- ////////////////////////////////////////////////

-- ANALISI TEMPORALE

-- Fatturato medio per giorno della settimana

SELECT
    -- DAYOFWEEK: 1=domenica … 7=sabato (standard MySQL/MariaDB)
    DAYOFWEEK(data_ordine)	AS numero_giorno,
    CASE DAYOFWEEK(data_ordine)
        WHEN 1 THEN 'Domenica'
        WHEN 2 THEN 'Lunedì'
        WHEN 3 THEN 'Martedì'
        WHEN 4 THEN 'Mercoledì'
        WHEN 5 THEN 'Giovedì'
        WHEN 6 THEN 'Venerdì'
        WHEN 7 THEN 'Sabato'
    END	AS giorno_settimana,
    ROUND(AVG(fatturato_giornaliero), 2) AS fatturato_medio
FROM (
    -- Sotto-query: fatturato aggregato per singola data
    SELECT
        data_ordine,
        SUM(prezzo)	AS fatturato_giornaliero
    FROM vista_ordini_completa
    GROUP BY data_ordine
) AS fatturati_giornalieri
GROUP BY numero_giorno, giorno_settimana
ORDER BY fatturato_medio DESC;

/*
  L'obiettivo di questa terza parte è stato quello di analizzare i giorni della settimana con il
  fatturato medio più alto.
  Prima si calcola il fatturato di ogni singola giornata, poi si fa la media per giorno della settimana, 
  così da individuare quali giorni tendono a generare più entrate
*/


-- ////////////////////////////////////////////////


-- ANALISI DEGLI ORDINI

-- Numero medio di prodotti per ordine

-- 5a >> Numero di prodotti per ciascun ordine
-- Viene usato ROW_NUMBER() per assegnare un ID surrogato a ogni ordine distinto (id_cliente + data), 
-- così da rendere esplicita l'identità di ciascun ordine

WITH ordini_con_id AS (
    SELECT
        id_cliente,
        data	AS data_ordine,
        COUNT(id_prodotto)	AS num_prodotti_ordine,
        ROW_NUMBER() OVER (
            ORDER BY id_cliente, data
        )	AS id_ordine_surrogato
    FROM ordini
    GROUP BY id_cliente, data
)
SELECT
    id_ordine_surrogato,
    id_cliente,
    data_ordine,
    num_prodotti_ordine
FROM ordini_con_id
ORDER BY id_ordine_surrogato;


-- 5b >> Media e distribuzione del numero di prodotti per ordine

WITH ordini_aggregati AS (
    SELECT
        id_cliente,
        data,
        COUNT(id_prodotto)	AS num_prodotti_ordine
    FROM ordini
    GROUP BY id_cliente, data
)
SELECT
    num_prodotti_ordine,
    COUNT(*)	AS numero_ordini,
    ROUND(AVG(num_prodotti_ordine) OVER (), 2) AS media_prodotti_per_ordine
FROM ordini_aggregati
GROUP BY num_prodotti_ordine
ORDER BY num_prodotti_ordine;

/*
  L'obiettivo di questa ultima parte è stato quello di calcolare il numero medio di prodotti per ordine
  e analizzarne la distribuzione.
  Poiché la tabella ordini non ha un ID ordine esplicito, viene usato ROW_NUMBER() OVER 
  (ORDER BY id_cliente, data) per assegnare un identificatore surrogato a ogni ordine distinto.
  Con la query 5b viene unificata in un solo blocco distribuzione e media calcolando quest'ultima con 
  AVG() OVER () come window function sull'intero risultato, eliminando la CTE duplicata.
*/
