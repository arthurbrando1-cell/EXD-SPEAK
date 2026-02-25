import streamlit as st
import whisper
import os
from moviepy.editor import TextClip, ColorClip, CompositeVideoClip
import datetime

# Função para criar o vídeo da legenda
def create_caption_video(segments, output_filename):
    clips = []
    # Criamos um fundo verde de 1080x1920 (Vertical/TikTok)
    bg = ColorClip(size=(1080, 1920), color=[0, 255, 0], duration=segments[-1]['end'])
    
    for seg in segments:
        duration = seg['end'] - seg['start']
        if duration <= 0: continue
        
        # Criando o texto estilo "Viral"
        txt = TextClip(
            seg['text'].strip().upper(),
            fontsize=90,
            color='white',
            font='Arial-Bold', # Ou outra que tenha no servidor
            method='caption',
            size=(900, None)
        ).set_start(seg['start']).set_duration(duration).set_position('center')
        
        clips.append(txt)
    
    result = CompositeVideoClip([bg] + clips)
    result.write_videofile(output_filename, fps=24, codec="libx264")

# Na aba de CAPTION do seu código:
# ... (lógica do Whisper que já temos)
# result = model.transcribe(temp_file)
# create_caption_video(result['segments'], "overlay_exd.mp4")
# st.video("overlay_exd.mp4")
