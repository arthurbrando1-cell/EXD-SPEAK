import streamlit as st
import asyncio
import edge_tts
from moviepy.editor import TextClip, ColorClip, CompositeVideoClip
import os

# 1. CONFIGURAÇÃO E CSS (O RETORNO DO VISUAL)
st.set_page_config(page_title="EXD STUDIO PRO", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    /* Fundo Animado/Degradê */
    .stApp { 
        background: radial-gradient(circle at center, #111 0%, #000 100%);
        color: #ffffff;
    }
    
    /* Sidebar com Estilo */
    [data-testid="stSidebar"] { 
        background-color: #050505 !important; 
        border-right: 1px solid #1a1a1a; 
    }
    
    /* Cards e Títulos */
    .main-card { 
        background: rgba(10, 10, 10, 0.9); 
        padding: 40px; 
        border: 1px solid #1a1a1a; 
        border-radius: 4px; 
    }
    h1 { font-weight: 900; letter-spacing: -3px; font-size: 5em !important; }
    
    /* Botões Metálicos EXD */
    .stButton>button {
        width: 100%; background: #ffffff; color: #000 !important;
        font-weight: 800; border: none; padding: 18px; border-radius: 2px;
        letter-spacing: 2px; text-transform: uppercase; transition: 0.4s;
    }
    .stButton>button:hover { background: #999; transform: translateY(-2px); }
    
    /* Inputs */
    .stTextArea textarea { background-color: #000 !important; color: #fff !important; border: 1px solid #222 !important; }
    
    /* Audio Player Dark */
    audio { filter: invert(100%) brightness(1.5); width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# 2. LÓGICA DE GERAÇÃO (VOZ + OVERLAY VÍDEO)
async def process_all(text, voice_name):
    audio_path = "temp_voice.mp3"
    video_path = "exd_overlay.mp4"
    
    # Gera Áudio
    communicate = edge_tts.Communicate(text, voice_name)
    await communicate.save(audio_path)
    
    # Configura Vídeo Green Screen (Estilo Viral)
    duration = max(len(text.split()) / 2.5, 3) # Duração dinâmica
    bg = ColorClip(size=(1080, 1920), color=[0, 255, 0]).set_duration(duration)
    
    txt = TextClip(
        text.upper(),
        fontsize=110,
        color='white',
        font='Arial-Bold',
        method='caption',
        size=(900, None)
    ).set_duration(duration).set_position('center')
    
    final_video = CompositeVideoClip([bg, txt])
    final_video.write_videofile(video_path, fps=24, codec="libx264", audio=audio_path)
    return video_path, audio_path

# 3. SIDEBAR COM ÍCONES
st.sidebar.markdown("<br><h2 style='color:white; letter-spacing:2px;'>EXD STUDIO</h2>", unsafe_allow_html=True)
aba = st.sidebar.radio(
    "SELECT TOOL",
    ["SPEAK", "CAPTION"],
    format_func=lambda x: f"🎤 {x}" if x == "SPEAK" else f"🎬 {x}"
)

# 4. CONTEÚDO DAS ABAS
if aba == "SPEAK":
    st.markdown("<h1>EXD <span style='color:#151515'>SPEAK</span></h1>", unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        texto_voz = st.text_area("ROTEIRO", placeholder="Sua voz começa aqui...", height=150)
        if st.button("SINTETIZAR ÁUDIO"):
            if texto_voz:
                with st.spinner("GERANDO FREQUÊNCIAS..."):
                    path = "v.mp3"
                    asyncio.run(edge_tts.Communicate(texto_voz, "pt-BR-AntonioNeural").save(path))
                    st.audio(path)
                    st.download_button("DOWNLOAD MP3", open(path, "rb"), "exd.mp3")
        st.markdown('</div>', unsafe_allow_html=True)

elif aba == "CAPTION":
    st.markdown("<h1>EXD <span style='color:#151515'>VIDEO</span></h1>", unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        st.info("O vídeo será gerado com fundo verde para aplicação de Chroma Key no CapCut.")
        texto_cap = st.text_area("TEXTO DA LEGENDA", placeholder="O que deve aparecer no vídeo?", height=100)
        
        if st.button("RENDERIZAR OVERLAY"):
            if texto_cap:
                with st.spinner("PROCESSANDO RENDER..."):
                    try:
                        v_file, a_file = asyncio.run(process_all(texto_cap, "pt-BR-AntonioNeural"))
                        st.video(v_file)
                        st.download_button("BAIXAR VÍDEO (GREEN SCREEN)", open(v_file, "rb"), "overlay_exd.mp4")
                    except Exception as e:
                        st.error("Erro na renderização. Verifique se o ImageMagick está disponível no servidor.")
        st.markdown('</div>', unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.caption("EXD STUDIO v8.0 | DARK MINIMAL")
