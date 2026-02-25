import streamlit as st
import asyncio
import edge_tts
import whisper
import datetime
import io
from PIL import Image
from streamlit_option_menu import option_menu
import uuid # Para gerar IDs únicos para os post-its
import nest_asyncio

# Inicializa o loop para o Voice Engine não travar
nest_asyncio.apply()

# --- CONFIGURAÇÃO E ESTILO ---
st.set_page_config(page_title="EXD STUDIO PRO", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    /* INTRO EXD */
    .intro-screen { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background-color: #020202; z-index: 9999; display: flex; justify-content: center; align-items: center; animation: hide 3.5s forwards; }
    .intro-text { font-family: 'Arial Black'; font-size: 10vw; color: #fff; letter-spacing: 20px; animation: glow 3s forwards; }
    @keyframes glow { 0% { opacity:0; filter:blur(10px); } 50% { opacity:1; filter:blur(0px); text-shadow: 0 0 30px #9D00FF; } 100% { opacity:0; transform:scale(1.2); } }
    @keyframes hide { 0%, 90% { opacity:1; visibility:visible; } 100% { opacity:0; visibility:hidden; } }
    
    /* DESIGN SISTEMA */
    .stApp { background-color: #050505; color: #fff; }
    [data-testid="stSidebar"] { background-color: #000 !important; border-right: 1px solid #111; }
    .main-card { background: #0a0a0a; border: 1px solid #1a1a1a; padding: 25px; border-radius: 8px; margin-bottom: 20px; }
    .stButton>button { width: 100%; background: #ffffff; color: #000 !important; font-weight: 900; border-radius: 2px; padding: 12px; transition: 0.3s; }
    .stButton>button:hover { background: #9D00FF; color: #fff !important; box-shadow: 0px 0px 15px #9D00FF; }
    h1 { font-weight: 900; letter-spacing: -3px; font-size: 3.5em !important; }

    /* Estilo do Post-it */
    .post-it {
        background-color: #333333; /* Fundo mais escuro */
        border: 2px solid #555555; /* Borda visível */
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 3px 3px 8px rgba(0,0,0,0.4);
        position: relative;
        word-wrap: break-word; /* Garante que o texto se quebre */
    }
    .post-it-title {
        font-weight: bold;
        color: #9D00FF; /* Cor vibrante para o título */
        margin-bottom: 8px;
        font-size: 1.1em;
    }
    .post-it-content {
        color: #CCCCCC; /* Cor de texto mais clara */
        font-size: 0.9em;
    }
    .post-it-id {
        font-size: 0.7em;
        color: #888888;
        margin-top: 10px;
        text-align: right;
    }
    </style>
    <div class="intro-screen"><div class="intro-text">EXD</div></div>
    """, unsafe_allow_html=True)

# --- FUNÇÕES DE SUPORTE ---
def format_srt(seconds):
    td = datetime.timedelta(seconds=seconds)
    return f"{int(td.total_seconds()//3600):02d}:{int(td.total_seconds()%3600//60):02d}:{int(td.total_seconds()%60):02d},{int(td.microseconds/1000):03d}"

VOZES = {
    "Antônio (BR)": "pt-BR-AntonioNeural",
    "Francisca (BR)": "pt-BR-FranciscaNeural",
    "Guy (US)": "en-US-GuyNeural",
    "Jenny (US)": "en-US-JennyNeural"
}

# --- INICIALIZA O MURAL NO SESSION_STATE ---
if 'post_its' not in st.session_state:
    st.session_state.post_its = []

# --- SIDEBAR COM TUDO ---
with st.sidebar:
    st.markdown("<h2 style='text-align:center'>EXD STUDIO</h2>", unsafe_allow_html=True)
    menu = option_menu(None, ["Voice Engine", "Smart Caption", "Mural Infinito", "SEO & Ganchos"], 
        icons=["mic", "badge-cc", "window-grid", "lightning"], 
        menu_icon="cast", default_index=0,
        styles={"container": {"background-color": "#000"}, "nav-link": {"color": "#aaa", "font-size": "12px"}, "nav-link-selected": {"background-color": "#111", "border-left": "3px solid #9D00FF"}})

# --- LÓGICA DAS FERRAMENTAS ---

if menu == "Voice Engine":
    st.markdown("<h1>VOICE <span style='color:#222'>ENGINE</span></h1>", unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        txt_v = st.text_area("Roteiro", height=150)
        c1, c2 = st.columns(2)
        voz = c1.selectbox("Locutor", list(VOZES.keys()))
        vel = c2.slider("Velocidade", -50, 50, 0)
        if st.button("GERAR ÁUDIO"):
            asyncio.run(edge_tts.Communicate(txt_v, VOZES[voz], rate=f"{vel:+d}%").save("v.mp3"))
            st.audio("v.mp3")
        st.markdown('</div>', unsafe_allow_html=True)

elif menu == "Smart Caption":
    st.markdown("<h1>SMART <span style='color:#222'>CAPTION</span></h1>", unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        up_s = st.file_uploader("Upload Áudio/Vídeo", type=["mp3", "mp4"])
        if st.button("EXTRAIR SRT"):
            if up_s:
                with open("t", "wb") as f: f.write(up_s.read())
                res = whisper.load_model("tiny").transcribe("t")
                srt = "".join([f"{i+1}\n{format_srt(s['start'])} --> {format_srt(s['end'])}\n{s['text'].strip().upper()}\n\n" for i, s in enumerate(res['segments'])])
                st.download_button("BAIXAR SRT", srt, "exd.srt")
            else:
