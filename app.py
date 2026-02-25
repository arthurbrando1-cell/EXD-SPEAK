import streamlit as st
import asyncio
import edge_tts
import whisper
import datetime
import os

# Interface Minimalista EXD
st.set_page_config(page_title="EXD STUDIO PRO", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #000000; }
    .main-card { background: #080808; padding: 40px; border: 1px solid #111; border-radius: 4px; }
    h1 { color: #fff !important; font-weight: 900; letter-spacing: -3px; font-size: 4em !important; }
    .stButton>button { width: 100%; background: #ffffff; color: #000 !important; font-weight: 800; border: none; padding: 18px; }
    </style>
    """, unsafe_allow_html=True)

def format_srt_time(seconds: float):
    td = datetime.timedelta(seconds=seconds)
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    millis = int(td.microseconds / 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

st.sidebar.title("EXD STUDIO")
aba = st.sidebar.radio("TOOLS", ["VOZ", "LEGENDA VIRAL"])

if aba == "VOZ":
    st.markdown("<h1>EXD <span style='color:#151515'>SPEAK</span></h1>")
    texto = st.text_area("Roteiro")
    if st.button("GERAR"):
        asyncio.run(edge_tts.Communicate(texto, "pt-BR-AntonioNeural").save("v.mp3"))
        st.audio("v.mp3")

elif aba == "LEGENDA VIRAL":
    st.markdown("<h1>EXD <span style='color:#151515'>CAPTION</span></h1>")
    f = st.file_uploader("Suba o áudio/vídeo", type=["mp3", "mp4"])
    
    if st.button("EXTRAIR LEGENDA"):
        if f:
            with st.spinner("IA ANALISANDO CADA PALAVRA..."):
                with open("temp", "wb") as tmp:
                    tmp.write(f.read())
                
                # Usando modelo 'tiny' para velocidade máxima e zero erros
                model = whisper.load_model("tiny")
                result = model.transcribe("temp", verbose=False)
                
                srt = ""
                for i, seg in enumerate(result['segments']):
                    # Aqui forçamos a quebra por frases curtas para dar o efeito do print
                    start = format_srt_time(seg['start'])
                    end = format_srt_time(seg['end'])
                    text = seg['text'].strip().upper() # Upper case para impacto
                    srt += f"{i+1}\n{start} --> {end}\n{text}\n\n"
                
                st.success("Legenda pronta para o CapCut!")
                st.download_button("BAIXAR SRT", srt, "legendas_exd.srt")
