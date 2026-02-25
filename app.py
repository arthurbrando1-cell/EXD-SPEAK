import streamlit as st
import asyncio
import edge_tts
import os
import requests
import io
from PIL import Image
import random
import time

# Configuração da página
st.set_page_config(page_title="EXD STUDIO", page_icon="⚡", layout="wide")

# --- CSS MINIMALISTA DARK ---
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #050505 !important; border-right: 1px solid #111; }
    .main-card { background: #0a0a0a; padding: 40px; border-radius: 4px; border: 1px solid #151515; }
    
    /* Botão Metálico */
    .stButton>button {
        width: 100%; background: #ffffff; color: #000 !important;
        font-weight: 800; border: none; padding: 15px; border-radius: 2px;
        letter-spacing: 2px; transition: 0.3s;
    }
    .stButton>button:hover { background: #888; }
    
    /* Inputs Dark */
    .stTextArea textarea { background-color: #000 !important; color: #fff !important; border: 1px solid #222 !important; }
    
    h1 { font-weight: 900; letter-spacing: -2px; font-size: 4em; }
    audio { filter: invert(100%); width: 100%; }
    
    /* Sidebar Text */
    section[data-testid="stSidebar"] .st-emotion-cache-6qob1r { color: white !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÕES ---
async def get_voices():
    try:
        voices = await edge_tts.VoicesManager.create()
        return {v["FriendlyName"]: v["ShortName"] for v in voices.find(Locale="pt-BR")}
    except:
        return {"Antônio": "pt-BR-AntonioNeural"}

def generate_image(prompt):
    seed = random.randint(0, 9999999)
    # Refinamento de prompt automático para evitar erros de servidor
    p = prompt.replace(' ', '%20')
    url = f"https://pollinations.ai/p/{p}?width=1024&height=1024&seed={seed}&model=flux&nologo=true"
    
    headers = {"User-Agent": "Mozilla/5.0"}
    
    # Tentativas robustas com aumento de timeout
    for attempt in range(4): # Aumentado para 4 tentativas
        try:
            # Timeout estendido para 60 segundos
            response = requests.get(url, headers=headers, timeout=60)
            if response.status_code == 200 and len(response.content) > 10000:
                return response.content
            time.sleep(3) 
        except:
            time.sleep(3)
    return None

# --- SIDEBAR COM ÍCONES REAIS ---
st.sidebar.markdown("<h2 style='color:white; letter-spacing:2px;'>STUDIO</h2>", unsafe_allow_html=True)

# Mapeamento de ícones (Símbolos profissionais)
icon_mic = "🎙️ " # Microfone para áudio
icon_img = "🖼️ " # Moldura para imagem

aba = st.sidebar.radio(
    "SELECT TOOL", 
    ["SPEAK", "VISION"],
    format_func=lambda x: icon_mic + "SPEAK" if x == "SPEAK" else icon_img + "VISION"
)

# --- CONTEÚDO ---
if aba == "SPEAK":
    st.markdown("<h1>EXD <span style='color:#151515'>SPEAK</span></h1>", unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        if 'vozes' not in st.session_state:
            st.session_state.vozes = asyncio.run(get_voices())
        
        texto = st.text_area("SCRIPT", placeholder="Input text...", height=150)
        voz_nome = st.selectbox("VOICE", list(st.session_state.vozes.keys()))
        
        if st.button("GENERATE MP3"):
