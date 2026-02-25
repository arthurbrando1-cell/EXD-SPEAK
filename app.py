import streamlit as st
import asyncio
import edge_tts
import os
import requests
import io
from PIL import Image

# Configuração da página
st.set_page_config(page_title="EXD STUDIO", page_icon="⚡", layout="wide")

# --- CSS PREMIM MINIMALISTA ---
st.markdown("""
    <style>
    .stApp { background-color: #000000; }
    [data-testid="stSidebar"] { background-color: #050505; border-right: 1px solid #111; }
    
    /* Fundo Animado Sutil */
    .stApp {
        background: radial-gradient(circle at top right, #111, #000);
    }

    .main-card {
        background: #0a0a0a;
        padding: 40px;
        border-radius: 4px;
        border: 1px solid #151515;
    }

    /* Botão Metálico B&W */
    .stButton>button {
        width: 100%;
        background: #FFFFFF;
        color: #000000 !important;
        font-weight: 800;
        border: none;
        padding: 15px;
        border-radius: 2px;
        transition: 0.3s;
        letter-spacing: 2px;
    }
    .stButton>button:hover { background: #888; transform: translateY(-1px); }

    /* Inputs Dark */
    .stTextArea textarea { background-color: #000 !important; color: #fff !important; border: 1px solid #222 !important; }
    .stSelectbox div { background-color: #000 !important; color: #fff !important; }

    h1 { color: #fff !important; font-weight: 900; letter-spacing: -2px; font-size: 4em; }
    audio { filter: invert(100%); width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÕES ---
async def get_voices():
    voices = await edge_tts.VoicesManager.create()
    return {v["FriendlyName"]: v["ShortName"] for v in voices.find(Locale="pt-BR")}

def generate_image(prompt):
    # API da Pollinations - Rápida e sem necessidade de Token
    url = f"https://pollinations.ai/p/{prompt.replace(' ', '%20')}?width=1024&height=1024&seed=42&model=flux"
    response = requests.get(url)
    return response.content

# --- INTERFACE ---
# Ícones SVG Reais para o Menu
icon_mic = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2"><path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" x2="12" y1="19" y2="22"/></svg>'
icon_cam = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2"><rect width="18" height="18" x="3" y="3" rx="2"/><path d="m3 14 5-5 5 5 5-5 3 3v6H3Z"/><circle cx="9" cy="9" r="2"/></svg>'

st.sidebar.markdown(f"<div style='padding:20px 0'><h2 style='color:white'>EXD STUDIO</h2></div>", unsafe_allow_html=True)
aba = st.sidebar.radio("TOOLS", ["SPEAK", "VISION"], format_func=lambda x: f"{x}")

if aba == "SPEAK":
    st.markdown("<h1>EXD <span style='color:#222'>SPEAK</span></h1>", unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        if 'vozes' not in st.session_state:
            st.session_state.vozes = asyncio.run(get_voices())
        
        texto = st.text_area("ROTEIRO", placeholder="Input text...", height=150)
        voz_nome = st.selectbox("LOCUTOR", list(st.session_state.vozes.keys()))
        
        if st.button("GERAR ÁUDIO"):
            if texto:
                file_path = "output.mp3"
                asyncio.run(edge_tts.Communicate(texto, st.session_state.vozes[voz_nome]).save(file_path))
                st.audio(file_path)
                with open(file_path, "rb") as f:
                    st.download_button("BAIXAR MP3", f, "exd_audio.mp3")
        st.markdown('</div>', unsafe_allow_html=True)

elif aba == "VISION":
    st.markdown("<h1>EXD <span style='color:#222'>VISION</span></h1>", unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        prompt = st.text_area("PROMPT (INGLÊS)", placeholder="Ex: Cyberpunk city, cinematic, hyperrealistic, black and white...")
        
        if st.button("RENDERIZAR"):
            if prompt:
                with st.spinner("RENDERIZANDO..."):
                    img_data = generate_image(prompt)
                    image = Image.open(io.BytesIO(img_data))
                    st.image(image, use_column_width=True)
                    st.download_button("BAIXAR PNG", img_data, "vision_exd.png", "image/png")
        st.markdown('</div>', unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.caption("V5.0 | BY EXD")
