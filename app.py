import streamlit as st
import asyncio
import edge_tts
import whisper
import os
from moviepy.editor import TextClip, ColorClip, CompositeVideoClip, AudioFileClip
from moviepy.config import change_settings

# --- FIX PARA O STREAMLIT CLOUD ENCONTRAR O IMAGEMAGICK ---
# Isso aponta para o caminho padrão do Linux no Streamlit
change_settings({"IMAGEMAGICK_BINARY": "/usr/bin/convert"})

st.set_page_config(page_title="EXD STUDIO PRO", page_icon="⚡", layout="wide")

# CSS Premium Original
st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle at center, #111 0%, #000 100%); color: #fff; }
    [data-testid="stSidebar"] { background-color: #050505 !important; border-right: 1px solid #1a1a1a; }
    .main-card { background: rgba(10, 10, 10, 0.9); padding: 30px; border: 1px solid #1a1a1a; border-radius: 4px; }
    h1 { font-weight: 900; letter-spacing: -3px; font-size: 4em !important; }
    .stButton>button { width: 100%; background: #fff; color: #000 !important; font-weight: 800; padding: 15px; text-transform: uppercase; }
    </style>
    """, unsafe_allow_html=True)

def generate_mp4_overlay(audio_path, segments, color_txt, color_edge, f_size, pos_y):
    audio = AudioFileClip(audio_path)
    # Fundo Verde Puro
    bg = ColorClip(size=(1080, 1920), color=[0, 255, 0]).set_duration(audio.duration)
    
    clips = [bg]
    for seg in segments:
        duration = seg['end'] - seg['start']
        if duration <= 0: continue
        
        # Criando o clip de texto com borda para simular o Glow
        txt = TextClip(
            seg['text'].strip().upper(),
            fontsize=f_size,
            color=color_txt,
            font='Arial-Bold',
            method='caption',
            size=(900, None),
            stroke_color=color_edge,
            stroke_width=3
        ).set_start(seg['start']).set_duration(duration).set_position(('center', pos_y))
        
        clips.append(txt)
    
    final_video = CompositeVideoClip(clips).set_audio(audio)
    output_path = "exd_output.mp4"
    final_video.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac", temp_audiofile='temp-audio.m4a', remove_temp=True)
    return output_path

# --- INTERFACE ---
st.sidebar.title("EXD STUDIO")
aba = st.sidebar.radio("TOOLS", ["🎤 SPEAK", "🎬 VIDEO CAPTION"])

if aba == "🎤 SPEAK":
    st.markdown("<h1>EXD <span style='color:#151515'>SPEAK</span></h1>", unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        txt_input = st.text_area("ROTEIRO")
        if st.button("GERAR MP3"):
            if txt_input:
                asyncio.run(edge_tts.Communicate(txt_input, "pt-BR-AntonioNeural").save("out.mp3"))
                st.audio("out.mp3")
        st.markdown('</div>', unsafe_allow_html=True)

elif aba == "🎬 VIDEO CAPTION":
    st.markdown("<h1>EXD <span style='color:#151515'>VIDEO</span></h1>", unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        up_file = st.file_uploader("UPLOAD (Áudio/Vídeo)", type=["mp3", "mp4", "wav"])
        
        st.markdown("### CUSTOMIZAÇÃO")
        c1, c2, c3 = st.columns(3)
        with c1: color_main = st.color_picker("COR TEXTO", "#FFFFFF")
        with c2: color_edge = st.color_picker("COR BORDA", "#9D00FF")
        with c3: f_size = st.slider("TAMANHO", 50, 150, 90)
        
        pos_y = st.selectbox("POSIÇÃO VERTICAL", options=[400, "center", 1400], format_func=lambda x: "Topo" if x==400 else ("Centro" if x=="center" else "Baixo"))

        if st.button("RENDERIZAR MP4"):
            if up_file:
                with st.spinner("RENDERIZANDO VÍDEO..."):
                    with open("temp_in", "wb") as f: f.write(up_file.read())
                    model = whisper.load_model("tiny")
                    result = model.transcribe("temp_in")
                    video_out = generate_mp4_overlay("temp_in", result['segments'], color_main, color_edge, f_size, pos_y)
                    st.video(video_out)
                    st.download_button("BAIXAR MP4 OVERLAY", open(video_out, "rb"), "exd_video.mp4")
        st.markdown('</div>', unsafe_allow_html=True)
