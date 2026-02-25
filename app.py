import streamlit as st
import asyncio
import edge_tts
import whisper
import os
from moviepy.editor import TextClip, ColorClip, CompositeVideoClip, AudioFileClip

# --- CONFIGURAÇÃO DE INTERFACE ---
st.set_page_config(page_title="EXD STUDIO VIDEO", page_icon="🎬", layout="wide")

st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle at center, #111 0%, #000 100%); color: #fff; }
    [data-testid="stSidebar"] { background-color: #050505 !important; border-right: 1px solid #1a1a1a; }
    .main-card { background: rgba(10, 10, 10, 0.9); padding: 30px; border: 1px solid #1a1a1a; border-radius: 4px; }
    h1 { font-weight: 900; letter-spacing: -3px; font-size: 4em !important; }
    .stButton>button { width: 100%; background: #fff; color: #000 !important; font-weight: 800; padding: 15px; text-transform: uppercase; }
    </style>
    """, unsafe_allow_html=True)

# --- ENGINE DE VÍDEO ---
def generate_mp4_overlay(audio_path, segments, color_txt, color_glow, font_size):
    clips = []
    audio = AudioFileClip(audio_path)
    
    # Fundo Verde para Chroma Key
    bg = ColorClip(size=(1080, 1920), color=[0, 255, 0]).set_duration(audio.duration)
    
    for seg in segments:
        duration = seg['end'] - seg['start']
        if duration <= 0: continue
        
        txt = TextClip(
            seg['text'].strip().upper(),
            fontsize=font_size,
            color=color_txt,
            font='Arial-Bold',
            method='caption',
            size=(900, None),
            stroke_color=color_glow,
            stroke_width=2
        ).set_start(seg['start']).set_duration(duration).set_position('center')
        
        clips.append(txt)
    
    final_video = CompositeVideoClip([bg] + clips).set_audio(audio)
    output_path = "exd_viral_video.mp4"
    final_video.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")
    return output_path

# --- SIDEBAR ---
st.sidebar.title("EXD STUDIO")
aba = st.sidebar.radio("TOOLS", ["🎤 SPEAK", "🎬 VIDEO CAPTION"])

# --- ABA SPEAK ---
if aba == "🎤 SPEAK":
    st.markdown("<h1>EXD <span style='color:#151515'>SPEAK</span></h1>", unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        text_input = st.text_area("ROTEIRO")
        if st.button("GERAR MP3"):
            if text_input:
                asyncio.run(edge_tts.Communicate(text_input, "pt-BR-AntonioNeural").save("out.mp3"))
                st.audio("out.mp3")
        st.markdown('</div>', unsafe_allow_html=True)

# --- ABA VIDEO CAPTION ---
elif aba == "🎬 VIDEO CAPTION":
    st.markdown("<h1>EXD <span style='color:#151515'>VIDEO</span></h1>", unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        up_file = st.file_uploader("UPLOAD (Áudio/Vídeo)", type=["mp3", "mp4", "wav"])
        
        st.markdown("### CUSTOMIZAÇÃO")
        col1, col2, col3 = st.columns(3)
        with col1: color_main = st.color_picker("COR TEXTO", "#FFFFFF")
        with col2: color_edge = st.color_picker("COR BORDA/GLOW", "#9D00FF")
        with col3: f_size = st.slider("TAMANHO", 50, 150, 90)

        if st.button("RENDERIZAR MP4"):
            if up_file:
                with st.spinner("PROCESSANDO VÍDEO..."):
                    with open("temp_in", "wb") as f: f.write(up_file.read())
                    
                    # Transcrição
                    model = whisper.load_model("tiny")
                    result = model.transcribe("temp_in")
                    
                    # Geração do MP4
                    video_out = generate_mp4_overlay("temp_in", result['segments'], color_main, color_edge, f_size)
                    
                    st.video(video_out)
                    with open(video_out, "rb") as file:
                        st.download_button("BAIXAR MP4 OVERLAY", file, "exd_video.mp4")
            else:
                st.error("Suba um arquivo primeiro!")
        st.markdown('</div>', unsafe_allow_html=True)
