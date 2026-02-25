import streamlit as st
import asyncio
import edge_tts
from moviepy.editor import TextClip, ColorClip, CompositeVideoClip
import os

st.set_page_config(page_title="EXD VIDEO GEN", layout="wide")

# CSS para o estilo Dark
st.markdown("<style>.stApp { background-color: #000; color: #fff; }</style>", unsafe_allow_html=True)

async def generate_voice_and_video(text, voice):
    audio_path = "temp_voice.mp3"
    video_path = "exd_overlay.mp4"
    
    # 1. Gera o Áudio
    await edge_tts.Communicate(text, voice).save(audio_path)
    
    # 2. Configura a Legenda (Estilo Viral)
    # Criamos um clip de texto que dura o tempo aproximado da fala
    # (Calculamos a duração baseada na quantidade de palavras: ~150 palavras por minuto)
    duration = max(len(text.split()) / 2.5, 2) 
    
    # Fundo Verde (Chroma Key)
    bg = ColorClip(size=(1080, 1920), color=[0, 255, 0]).set_duration(duration)
    
    # Texto Branco Centralizado (Maiúsculas)
    txt = TextClip(
        text.upper(),
        fontsize=100,
        color='white',
        font='Arial-Bold',
        method='caption',
        size=(900, None)
    ).set_duration(duration).set_position('center')
    
    # Montagem do Vídeo
    final_video = CompositeVideoClip([bg, txt])
    final_video.write_videofile(video_path, fps=24, codec="libx264")
    return video_path

st.title("EXD VIDEO CAPTION")

with st.container():
    texto = st.text_area("Digite o texto da legenda:")
    if st.button("GERAR VÍDEO OVERLAY"):
        if texto:
            with st.spinner("RENDERIZANDO VÍDEO..."):
                try:
                    video_out = asyncio.run(generate_voice_and_video(texto, "pt-BR-AntonioNeural"))
                    st.video(video_out)
                    with open(video_out, "rb") as f:
                        st.download_button("BAIXAR VÍDEO (GREEN SCREEN)", f, "overlay.mp4")
                except Exception as e:
                    st.error(f"Erro: {e}. Tente um texto menor.")
