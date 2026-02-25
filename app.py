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
st.set_page_config(page_title="EXD STUDIO PRO", page_icon="⚡", layout="wide")

# --- CSS PREMIM MINIMALISTA (BLACK, GREY, WHITE) ---
st.markdown("""
    <style>
    /* Reset e Fundo */
    .stApp { 
        background-color: #000000; 
        background: radial-gradient(circle at center, #111 0%, #000 100%);
    }
    
    /* Sidebar Dark */
    [data-testid="stSidebar"] { 
        background-color: #050505 !important; 
        border-right: 1px solid #1a1a1a; 
    }
    
    /* Card Principal */
    .main-card {
        background: rgba(10, 10, 10, 0.9);
        padding: 45px;
        border-radius: 4px;
        border: 1px solid #1a1a1a;
        box-shadow: 0 20px 60px rgba(0,0,0,1);
    }

    /* Títulos e Tipografia */
    h1 { 
        color: #ffffff !important; 
        font-weight: 900; 
        letter-spacing: -3px; 
        font-size: 5em !important;
        margin-bottom: 0px;
    }
    .sub-text { color: #444; letter-spacing: 5px; font-size: 0.7em; margin-bottom: 40px; }

    /* Botão Metálico */
    .stButton>button {
        width: 100%;
        background: #ffffff;
        color: #000000 !important;
        font-weight: 800;
        border: none;
        padding: 18px;
        border-radius: 2px;
        transition: 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
        letter-spacing: 3px;
        text-transform: uppercase;
    }
    .stButton>button:hover { 
        background: #999; 
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(255,255,255,0.1);
    }

    /* Inputs Estilizados */
    .stTextArea textarea { 
        background-color: #000 !important; 
        color: #fff !important; 
        border: 1px solid #222 !important;
        font-family: 'Inter', sans-serif;
    }
    
    /* Audio Player Dark */
    audio { filter: invert(100%) brightness(1.5); width: 100%; margin-top: 20px; }
    
    /* Sidebar Labels */
    .st-emotion-cache-6qob1r { color: #fff !important; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÕES DE NÚCLEO ---

async def get_voices():
    """Busca vozes oficiais da Microsoft Azure."""
    try:
        voices = await edge_tts.VoicesManager.create()
        return {v["FriendlyName"]: v["ShortName"] for v in voices.find(Locale="pt-BR")}
    except:
        return {"Antônio (Padrão)": "pt-BR-AntonioNeural"}

def generate_image(prompt):
    """Gera imagem com sistema de retentativa e headers de navegador."""
    seed = random.randint(0, 10**6)
    # Adicionando tempero visual ao prompt
    enhanced_prompt = f"{prompt}, dark aesthetic, high contrast, monochrome photography, hyper-detailed, 8k"
    url = f"https://pollinations.ai/p/{enhanced_prompt.replace(' ', '%20')}?width=1024&height=1024&seed={seed}&model=flux"
    
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    for attempt in range(3):
        try:
            response = requests.get(url, headers=headers, timeout=35)
            if response.status_code == 200 and len(response.content) > 10000:
                return response.content
            time.sleep(2)
        except:
            time.sleep(2)
    return None

# --- SIDEBAR E NAVEGAÇÃO ---

st.sidebar.markdown("<br><h2 style='color:white; letter-spacing:2px;'>STUDIO</h2>", unsafe_allow_html=True)

# Ícones via símbolos de texto (Mais elegantes que emojis)
OPCOES = {
    "SPEAK": "⊚ SPEAK",
    "VISION": "□ VISION"
}

aba = st.sidebar.radio(
    "SELECT TOOL", 
    list(OPCOES.keys()), 
    format_func=lambda x: OPCOES[x]
)

# --- CONTEÚDO ---

if aba == "SPEAK":
    st.markdown("<h1>EXD <span style='color:#151515'>SPEAK</span></h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-text'>NEURAL VOICE SINTETHIZER</p>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        
        if 'vozes' not in st.session_state:
            with st.spinner("SYNCING VOICES..."):
                st.session_state.vozes = asyncio.run(get_voices())
        
        texto = st.text_area("SCRIPT", placeholder="Digite seu roteiro...", height=180)
        
        col_v1, col_v2 = st.columns([2, 1])
        with col_v1:
            voz_nome = st.selectbox("VOICE SELECTION", list(st.session_state.vozes.keys()))
        
        if st.button("GENERATE AUDIO"):
            if texto.strip():
                file_path = "exd_output.mp3"
                with st.spinner("PROCESSING..."):
                    asyncio.run(edge_tts.Communicate(texto, st.session_state.vozes[voz_nome]).save(file_path))
                
                st.audio(file_path)
                with open(file_path, "rb") as f:
                    st.download_button("DOWNLOAD MP3", f, "exd_voice.mp3")
            else:
                st.error("Empty script.")
        st.markdown('</div>', unsafe_allow_html=True)

elif aba == "VISION":
    st.markdown("<h1>EXD <span style='color:#151515'>VISION</span></h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-text'>AI IMAGE GENERATION</p>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        prompt = st.text_area("PROMPT", placeholder="Describe the visual content...", height=100)
        
        if st.button("RENDER IMAGE"):
            if prompt.strip():
                placeholder = st.empty()
                placeholder.info("CONNECTING TO NEURAL NETWORK...")
                
                img_data = generate_image(prompt)
                
                if img_data:
                    try:
                        image = Image.open(io.BytesIO(img_data))
                        placeholder.empty()
                        st.image(image, use_column_width=True)
                        st.download_button("SAVE PNG", img_data, "exd_vision.png", "image/png")
                    except:
                        placeholder.error("DECODE ERROR: Server sent invalid data. Retry.")
                else:
                    placeholder.error("TIMEOUT: Image server busy. Try again.")
            else:
                st.error("Empty prompt.")
        st.markdown('</div>', unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.caption("EXD STUDIO v5.2")
st.sidebar.caption("© 2026 PREMIUM EDITION")
