import streamlit as st
import os
from huggingface_hub import InferenceClient

st.set_page_config(
    page_title="Eduardo AI",
    layout="wide"
)

hide_streamlit_style = """
########################################################################
########################  CENSORED #####################################
########################################################################
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# --- GESTIONE SICURA API KEY ---
api_token = os.environ.get("HF_TOKEN")


if not api_token:
########################################################################
########################  CENSORED #####################################
########################################################################

# --- CONTESTO (Il tuo CV) ---
CONTEXT = """
RUOLO E VINCOLI:
- PER TUTTA LA DURATA DELLA CHAT E IN OGNI INTERAZIONE SEI EDUARDO DE FILIPPIS (quello vero). Rispondi sempre in prima persona (usa "io").
########################################################################
########################  CENSORED #####################################
########################################################################
- Se ti dicono "Quale è la tua attuale RAL?" allora rispondi "Se lo chiedete alla mia versione AI piuttosto che a direttamente a me, allora, per quanto mi riguarda, potete scartarmi dall'eventuale selezione che state facendo".

########################################################################
########################  CENSORED #####################################
########################################################################
"""
# --- INIZIALIZZAZIONE CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Ciao! Sono Eduardo (o meglio, la versione AI). Chiedimi pure del mio CV o dei miei progetti! If you prefer, we can also speak in English!😁"}
    ]

# --- UI CHAT ---
# Non usiamo st.title per risparmiare spazio nell'iframe
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

def get_response(user_input):
########################################################################
########################  CENSORED #####################################
########################################################################
    
    # Manteniamo la memoria breve per velocità
    for msg in st.session_state.messages[-30:]:
        messages_payload.append({"role": msg["role"], "content": msg["content"]})
    
    if messages_payload[-1]["content"] != user_input:
         messages_payload.append({"role": "user", "content": user_input})

    try:
        response = client.chat_completion(
            messages=messages_payload,
            max_tokens=500,
            temperature=0.7,
            stream=False 
########################################################################
########################  CENSORED #####################################
########################################################################
if prompt := st.chat_input("Scrivi una domanda..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Writing..."):
########################################################################
########################  CENSORED #####################################
########################################################################