import streamlit as st
import asyncio
import edge_tts
import os
import requests
import io
from PIL import Image
import random

# Configuração da página
st.set_page_config(page_title="EXD STUDIO PRO", page_icon="⚡", layout="wide")

# --- CSS PREMIUM ---
st.markdown("""
    <style>
    .stApp { background-color: #000000; background: radial-gradient(circle at center, #111 0%, #000 100%); }
    [data-testid="stSidebar"] { background-color: #050505 !important; border-right: 1px solid #1a1a1a; }
    .main-card { background: rgba(10, 10, 10, 0.9); padding: 45px; border-radius: 4px; border: 1px solid #1a1a1a; }
    h1 { color: #ffffff !important; font-weight: 900; letter-spacing: -3px; font-size: 5em !important; margin-bottom: 0px; }
    .sub-text { color: #444; letter-spacing: 5px; font-size: 0.7em; margin-bottom: 40px; }
    .stButton>button {
        width: 100%; background: #ffffff; color: #000000 !important;
        font-weight: 800; border: none; padding: 18px; border-radius: 2px;
        transition: 0.4s; letter-spacing: 3px; text-transform: uppercase;
    }
    .stButton>button:hover { background: #999; transform: translateY(-2px); }
    .stTextArea textarea { background-color: #000 !important; color: #fff !important; border: 1px solid #222 !important; }
    audio { filter: invert(100%) brightness(1.5); width: 100%; margin-top: 20px; }
    
    /* Custom Sidebar Icons Style */
    .sidebar-label { display: flex; align-items: center; gap: 10px; color: white; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÕES ---
async def get_voices():
    try:
        voices = await edge_tts.VoicesManager.create()
        return {v["FriendlyName"]: v["ShortName"] for v in voices.find(Locale="pt-BR")}
    except:
        return {"Antônio (Padrão)": "pt-BR-AntonioNeural"}

def generate_image_stable(prompt):
    """Nova API via Vyro.ai - Mais estável e rápida"""
    seed = random.randint(0, 10**6)
    # Adicionando parâmetros de qualidade automaticamente
    refined_prompt = f"{prompt}, professional photography, masterpiece, 8k resolution, highly detailed, cinematic lighting"
    
    # Usando o endpoint de renderização direta
    url = f"https://image.pollinations.ai/prompt/{refined_prompt.replace(' ', '%20')}?width=1024&height=1024&seed={seed}&nologo=true&enhance=true"
    
    try:
        response = requests.get(url, timeout=40)
        if response.status_code == 200:
            return response.content
        return None
    except:
        return None

# --- SIDEBAR COM ÍCONES TEXTUAIS ---
st.sidebar.markdown("<br><h2 style='color:white; letter-spacing:2px;'>STUDIO</h2>", unsafe_allow_html=True)

# Definindo ícones de microfone e imagem usando símbolos UNICODE de alta fidelidade
aba = st.sidebar.radio(
    "SELECT TOOL",
    ["SPEAK", "VISION"],
    format_func=lambda x: f"🎤 {x}" if x == "SPEAK" else f"🖼️ {x}"
)

# --- CONTEÚDO ---
if aba == "SPEAK":
    st.markdown("<h1>EXD <span style='color:#151515'>SPEAK</span></h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-text'>NEURAL VOICE SINTETHIZER</p>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        if 'vozes' not in st.session_state:
            st.session_state.vozes = asyncio.run(get_voices())
        
        texto = st.text_area("SCRIPT", placeholder="Digite seu roteiro...", height=180)
        voz_nome = st.selectbox("VOICE SELECTION", list(st.session_state.vozes.keys()))
        
        if st.button("GENERATE AUDIO"):
            if texto.strip():
                file_path = "exd_output.mp3"
                with st.spinner("SINTETIZANDO..."):
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
        prompt = st.text_area("PROMPT", placeholder="Describe the image in English for better results...", height=100)
        
        if st.button("RENDER IMAGE"):
            if prompt.strip():
                ph = st.empty()
                ph.info("ENGAGING NEURAL CORES...")
                
                img_data = generate_image_stable(prompt)
                
                if img_data:
                    try:
                        image = Image.open(io.BytesIO(img_data))
                        ph.empty()
                        st.image(image, use_column_width=True)
                        st.download_button("SAVE PNG", img_data, "exd_vision.png", "image/png")
                    except:
                        ph.error("API RETURNED INVALID DATA. PLEASE RETRY.")
                else:
                    ph.error("SERVER STILL BUSY. TRY A SHORTER PROMPT.")
            else:
                st.error("Empty prompt.")
        st.markdown('</div>', unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.caption("EXD STUDIO v6.0 | © 2026")
