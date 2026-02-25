import streamlit as st
import asyncio
import edge_tts
import os
import requests
import io
from PIL import Image
import random

# Configuração da página
st.set_page_config(page_title="EXD STUDIO", page_icon="⚡", layout="wide")

# CSS Minimalista Black & Metal
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #050505; border-right: 1px solid #111; }
    .main-card { background: #0a0a0a; padding: 40px; border-radius: 4px; border: 1px solid #151515; }
    .stButton>button {
        width: 100%; background: #FFFFFF; color: #000 !important;
        font-weight: 800; border: none; padding: 15px; border-radius: 2px;
        letter-spacing: 2px; transition: 0.3s;
    }
    .stButton>button:hover { background: #888; }
    .stTextArea textarea { background-color: #000 !important; color: #fff !important; border: 1px solid #222 !important; }
    h1 { font-weight: 900; letter-spacing: -2px; font-size: 4em; }
    audio { filter: invert(100%); width: 100%; }
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
    # Adicionando um seed aleatório para garantir que a imagem mude sempre
    seed = random.randint(0, 999999)
    # Refinando o prompt para a pegada que você quer (cinza/preto/branco/detalhado)
    full_prompt = f"{prompt}, cinematic, masterpiece, highly detailed, black and white aesthetic"
    url = f"https://pollinations.ai/p/{full_prompt.replace(' ', '%20')}?width=1024&height=1024&seed={seed}&model=flux"
    
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            return response.content
        return None
    except:
        return None

# --- INTERFACE ---
st.sidebar.markdown("<h2 style='color:white'>EXD STUDIO</h2>", unsafe_allow_html=True)
aba = st.sidebar.radio("TOOLS", ["SPEAK", "VISION"])

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
        prompt = st.text_area("PROMPT (INGLÊS)", placeholder="Ex: A lonely robot in a dark city...", height=100)
        
        if st.button("RENDERIZAR"):
            if prompt:
                with st.spinner("CONECTANDO ÀS NEURAIS..."):
                    img_data = generate_image(prompt)
                    if img_data:
                        try:
                            image = Image.open(io.BytesIO(img_data))
                            st.image(image, use_column_width=True)
                            st.download_button("BAIXAR PNG", img_data, "vision_exd.png", "image/png")
                        except:
                            st.error("Erro ao processar imagem. Tente clicar em Renderizar novamente.")
                    else:
                        st.error("Falha na conexão. Tente um prompt mais curto.")
        st.markdown('</div>', unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.caption("V5.1 | FIX ENGINE")
