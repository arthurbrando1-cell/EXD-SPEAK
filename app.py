import streamlit as st
import asyncio
import edge_tts
import os

# Configuração da página
st.set_page_config(page_title="EXD STUDIO LEGENDAS", page_icon="🎬", layout="wide")

# CSS Minimalista EXD
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #050505 !important; border-right: 1px solid #1a1a1a; }
    .main-card { background: #080808; padding: 40px; border: 1px solid #111; border-radius: 4px; }
    h1 { color: #fff !important; font-weight: 900; letter-spacing: -3px; font-size: 5em !important; }
    .stButton>button {
        width: 100%; background: #ffffff; color: #000 !important;
        font-weight: 800; border: none; padding: 18px; border-radius: 2px;
        letter-spacing: 2px; text-transform: uppercase; transition: 0.3s;
    }
    .stButton>button:hover { background: #666; transform: scale(1.01); }
    .stTextArea textarea { background-color: #000 !important; color: #fff !important; border: 1px solid #222 !important; }
    audio { filter: invert(100%); width: 100%; margin-top: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÕES ---
async def get_voices():
    try:
        voices = await edge_tts.VoicesManager.create()
        return {v["FriendlyName"]: v["ShortName"] for v in voices.find(Locale="pt-BR")}
    except:
        return {"Antônio": "pt-BR-AntonioNeural"}

# --- INTERFACE ---
st.sidebar.markdown("<br><h2 style='color:white;'>EXD STUDIO</h2>", unsafe_allow_html=True)
aba = st.sidebar.radio("FERRAMENTAS", ["🎤 SPEAK (Voz)", "🎬 CAPTION (Legendas)"])

if aba == "🎤 SPEAK (Voz)":
    st.markdown("<h1>EXD <span style='color:#151515'>SPEAK</span></h1>", unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        
        if 'vozes' not in st.session_state:
            st.session_state.vozes = asyncio.run(get_voices())
        
        texto = st.text_area("ROTEIRO", placeholder="Digite seu roteiro para converter em áudio...", height=180)
        voz_nome = st.selectbox("LOCUTOR", list(st.session_state.vozes.keys()))
        
        if st.button("GERAR ÁUDIO"):
            if texto.strip():
                file_path = "voce_exd.mp3"
                with st.spinner("SINTETIZANDO..."):
                    asyncio.run(edge_tts.Communicate(texto, st.session_state.vozes[voz_nome]).save(file_path))
                st.audio(file_path)
                with open(file_path, "rb") as f:
                    st.download_button("BAIXAR MP3", f, "exd_audio.mp3")
            else:
                st.error("Roteiro vazio.")
        st.markdown('</div>', unsafe_allow_html=True)

elif aba == "🎬 CAPTION (Legendas)":
    st.markdown("<h1>EXD <span style='color:#151515'>CAPTION</span></h1>", unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        st.write("### Suba seu arquivo de áudio ou vídeo para legendar")
        
        uploaded_file = st.file_uploader("Upload Audio/Video", type=["mp3", "wav", "mp4"])
        
        cor_legenda = st.color_picker("COR DA LEGENDA ATIVA", "#FFFF00") # Amarelo por padrão
        
        if st.button("GERAR LEGENDAS DINÂMICAS"):
            if uploaded_file:
                st.info("Esta função requer processamento pesado. No Streamlit Cloud, pode levar alguns minutos.")
                # Aqui entra o processamento com Whisper + MoviePy
                # Por enquanto, vamos avisar que a engine está sendo montada
                st.warning("ENGINE EM FASE DE TESTES: O processador Whisper está sendo carregado no servidor.")
            else:
                st.error("Por favor, suba um arquivo primeiro.")
        st.markdown('</div>', unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.caption("v7.5 | PRO EDITION")
