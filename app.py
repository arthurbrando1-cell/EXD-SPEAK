import streamlit as st
import asyncio
import edge_tts
import whisper
import datetime
import os

st.set_page_config(page_title="EXD STUDIO PRO", page_icon="⚡", layout="wide")

# CSS Minimalista
st.markdown("<style>.stApp { background-color: #000; } h1 { color: #fff; font-weight: 900; }</style>", unsafe_allow_html=True)

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
    st.markdown("<h1>EXD <span style='color:#151515'>SPEAK</span></h1>", unsafe_allow_html=True)
    texto = st.text_area("Roteiro")
    if st.button("GERAR"):
        if texto:
            asyncio.run(edge_tts.Communicate(texto, "pt-BR-AntonioNeural").save("v.mp3"))
            st.audio("v.mp3")

elif aba == "LEGENDA VIRAL":
    st.markdown("<h1>EXD <span style='color:#151515'>CAPTION</span></h1>", unsafe_allow_html=True)
    f = st.file_uploader("Suba o áudio/vídeo", type=["mp3", "mp4", "wav"])
    
    if st.button("EXTRAIR LEGENDA"):
        if f:
            with st.spinner("IA ANALISANDO ÁUDIO..."):
                # Salvando com extensão para o FFmpeg reconhecer
                ext = f.name.split(".")[-1]
                temp_file = f"temp_audio.{ext}"
                with open(temp_file, "wb") as tmp:
                    tmp.write(f.read())
                
                try:
                    model = whisper.load_model("tiny")
                    # O segredo: FP16=False evita erros em CPUs que não tem placa de vídeo (Streamlit Cloud)
                    result = model.transcribe(temp_file, fp16=False)
                    
                    srt = ""
                    for i, seg in enumerate(result['segments']):
                        start = format_srt_time(seg['start'])
                        end = format_srt_time(seg['end'])
                        text = seg['text'].strip().upper()
                        srt += f"{i+1}\n{start} --> {end}\n{text}\n\n"
                    
                    st.success("Legenda gerada com sucesso!")
                    st.download_button("BAIXAR SRT", srt, "legendas_exd.srt")
                except Exception as e:
                    st.error(f"Erro no processamento: Certifique-se de que o packages.txt com 'ffmpeg' foi criado.")
                finally:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
