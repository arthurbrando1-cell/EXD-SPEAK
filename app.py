import streamlit as st
import asyncio
import edge_tts
import os
import requests
import io
from PIL import Image

# Configuração da página
st.set_page_config(page_title="EXD STUDIO", page_icon="⚡", layout="wide")

# CSS Minimalista Premium
st.markdown("""
    <style>
    .stApp { background-color: #000000; }
    [data-testid="stSidebar"] { background-color: #050505; border-right: 1px solid #111; }
    .main-card {
        background: rgba(10, 10, 10, 0.9);
        padding: 30px;
        border-radius: 12px;
        border: 1px solid #1a1a1a;
    }
    h1, h2, h3 { color: #ffffff !important; font-family: 'Inter', sans-serif; }
    .stButton>button {
        width: 100%;
        background: #ffffff;
        color: #000;
        font-weight: bold;
        border-radius: 4px;
        border: none;
    }
    .stButton>button:hover { background: #cccccc; }
    audio { filter: invert(100%); }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÕES ---
async def get_voices():
    voices = await edge_tts.VoicesManager.create()
    br_voices = voices.find(Locale="pt-BR")
    return {v["FriendlyName"]: v["ShortName"] for v in br_voices}

def query_image(prompt):
    # Usando API gratuita do Hugging Face (Modelo estável)
    API_URL = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
    # Você pode criar um Token grátis no Hugging Face para não ter limite, 
    # mas por enquanto vamos tentar o acesso direto.
    headers = {"Authorization": "Bearer hf_XXX"} # Opcional: Coloque seu token aqui
    response = requests.post(API_URL, headers=headers, json={"inputs": prompt})
    return response.content

# --- SIDEBAR (NAVEGAÇÃO) ---
st.sidebar.title("EXD STUDIO")
aba = st.sidebar.radio("FERRAMENTAS", ["🎙️ EXD SPEAK (Voz)", "🖼️ EXD VISION (Imagem)"])

# --- ABA 1: GERADOR DE VOZ ---
if aba == "🎙️ EXD SPEAK (Voz)":
    st.markdown("<h1>VOICE <span style='color:#333'>ENGINE</span></h1>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        if 'vozes' not in st.session_state:
            st.session_state.vozes = asyncio.run(get_voices())
        
        texto = st.text_area("ROTEIRO", placeholder="Digite para narrar...", height=150)
        voz_nome = st.selectbox("LOCUTOR", list(st.session_state.vozes.keys()))
        
        if st.button("GERAR ÁUDIO"):
            if texto:
                file_path = "output.mp3"
                async def run_tts():
                    await edge_tts.Communicate(texto, st.session_state.vozes[voz_nome]).save(file_path)
                
                with st.spinner("Sintetizando..."):
                    asyncio.run(run_tts())
                st.audio(file_path)
                with open(file_path, "rb") as f:
                    st.download_button("BAIXAR MP3", f, file_name="exd_audio.mp3")
        st.markdown('</div>', unsafe_allow_html=True)

# --- ABA 2: GERADOR DE IMAGEM ---
elif aba == "🖼️ EXD VISION (Imagem)":
    st.markdown("<h1>VISION <span style='color:#333'>GEN</span></h1>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        prompt = st.text_area("PROMPT (EM INGLÊS)", placeholder="Ex: A futuristic city in dark aesthetic, 8k, cinematic...")
        st.info("Dica: Use o Google Tradutor para o prompt se precisar. O modelo entende melhor em Inglês.")
        
        if st.button("CRIAR IMAGEM"):
            if prompt:
                with st.spinner("Desenhando..."):
                    image_bytes = query_image(prompt)
                    try:
                        image = Image.open(io.BytesIO(image_bytes))
                        st.image(image, caption="Resultado EXD Vision", use_column_width=True)
                        
                        # Botão de download da imagem
                        buf = io.BytesIO()
                        image.save(buf, format="PNG")
                        st.download_button("BAIXAR PNG", buf.getvalue(), "imagem_exd.png", "image/png")
                    except:
                        st.error("O servidor de imagem está carregado. Tente novamente em alguns segundos.")
        st.markdown('</div>', unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.caption("EXD STUDIO v3.1")
