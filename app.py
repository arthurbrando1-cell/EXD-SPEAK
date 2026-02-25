import streamlit as st
import asyncio
import edge_tts
import os
import requests
import io
from PIL import Image

# Configuração da página
st.set_page_config(page_title="EXD STUDIO PRO", page_icon="⚡", layout="wide")

# CSS Minimalista Premium: Preto, Cinza e Branco com Animações
st.markdown("""
    <style>
    .stApp { background-color: #000000; }
    
    /* Sidebar Minimalista */
    [data-testid="stSidebar"] { background-color: #050505; border-right: 1px solid #111; }
    
    /* Fundo Animado Sutil */
    .stApp {
        background: linear-gradient(-45deg, #000000, #0a0a0a, #000000, #111111);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
    }
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* Cards e Inputs */
    .main-card {
        background: rgba(10, 10, 10, 0.95);
        padding: 30px;
        border-radius: 8px;
        border: 1px solid #1a1a1a;
        box-shadow: 0 15px 40px rgba(0,0,0,0.8);
    }
    .stTextArea textarea {
        background-color: #020202 !important;
        color: #fff !important;
        border: 1px solid #222 !important;
    }

    /* Botão com Gradiente Branco/Cinza */
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #ffffff, #888888);
        color: #000 !important;
        font-weight: 900;
        border: none;
        padding: 12px;
        border-radius: 4px;
        transition: 0.4s;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 0 20px rgba(255,255,255,0.2);
    }

    /* Títulos Metálicos */
    .premium-title {
        background: linear-gradient(to right, #ffffff, #333333);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 900;
        font-size: 3.5em;
        letter-spacing: -2px;
    }
    
    audio { filter: invert(100%); width: 100%; margin-top: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÕES ---
async def get_voices():
    try:
        manager = await edge_tts.VoicesManager.create()
        voices = manager.find(Locale="pt-BR")
        return {v["FriendlyName"]: v["ShortName"] for v in voices}
    except:
        return {"Antônio (Padrão)": "pt-BR-AntonioNeural"}

def query_image(prompt):
    # Trocando para um modelo alternativo para evitar erro de carga
    API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1"
    headers = {"Authorization": "Bearer hf_XXX"} # Coloque seu token aqui para evitar erros
    response = requests.post(API_URL, headers=headers, json={"inputs": prompt})
    return response.content

# --- INTERFACE ---
# Ícones SVG Reais
icon_voice = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-mic"><path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" x2="12" y1="19" y2="22"/></svg>'
icon_image = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-image"><rect width="18" height="18" x="3" y="3" rx="2" ry="2"/><circle cx="9" cy="9" r="2"/><path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21"/></svg>'

st.sidebar.markdown(f"<h2 style='color:white'>EXD STUDIO</h2>", unsafe_allow_html=True)
aba = st.sidebar.radio("FERRAMENTAS", ["SPEAK", "VISION"], format_func=lambda x: f"● {x}")

if aba == "SPEAK":
    st.markdown('<div style="text-align: center;"><div class="premium-title">EXD SPEAK</div></div>', unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        if 'vozes' not in st.session_state:
            st.session_state.vozes = asyncio.run(get_voices())
        
        texto = st.text_area("ROTEIRO", placeholder="Digite para narrar...", height=150)
        voz_nome = st.selectbox("LOCUTORES ATUALIZADOS", list(st.session_state.vozes.keys()))
        
        if st.button("SINTETIZAR ÁUDIO"):
            if texto:
                file_path = "output.mp3"
                async def run_tts():
                    await edge_tts.Communicate(texto, st.session_state.vozes[voz_nome]).save(file_path)
                with st.spinner("Gerando ondas neurais..."):
                    asyncio.run(run_tts())
                st.audio(file_path)
                with open(file_path, "rb") as f:
                    st.download_button("BAIXAR MP3", f, "audio_exd.mp3")
        st.markdown('</div>', unsafe_allow_html=True)

elif aba == "VISION":
    st.markdown('<div style="text-align: center;"><div class="premium-title">EXD VISION</div></div>', unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        prompt = st.text_area("PROMPT (INGLÊS)", placeholder="Ex: Black and white cinematic photography, detailed, 8k...")
        
        if st.button("RENDERIZAR IMAGEM"):
            if prompt:
                with st.spinner("Processando IA..."):
                    image_bytes = query_image(prompt)
                    try:
                        image = Image.open(io.BytesIO(image_bytes))
                        st.image(image, use_column_width=True)
                        buf = io.BytesIO()
                        image.save(buf, format="PNG")
                        st.download_button("BAIXAR PNG", buf.getvalue(), "vision_exd.png")
                    except:
                        st.error("O servidor está ocupado. Use um prompt curto ou tente de novo.")
        st.markdown('</div>', unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.caption("EXD STUDIO V4.0 | DARK MINIMAL")
