import streamlit as st
import asyncio
import edge_tts
import whisper
import os
import datetime

# --- CONFIGURAÇÃO VISUAL ---
st.set_page_config(page_title="EXD STUDIO PRO", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle at center, #111 0%, #000 100%); color: #fff; }
    [data-testid="stSidebar"] { background-color: #050505 !important; border-right: 1px solid #1a1a1a; }
    .main-card { background: rgba(10, 10, 10, 0.9); padding: 30px; border: 1px solid #1a1a1a; border-radius: 4px; }
    h1 { font-weight: 900; letter-spacing: -3px; font-size: 4em !important; }
    .stButton>button { width: 100%; background: #fff; color: #000 !important; font-weight: 800; padding: 15px; text-transform: uppercase; }
    .preview-box { padding: 20px; border: 2px dashed #333; text-align: center; margin-top: 10px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÕES DE SUPORTE ---
async def get_all_voices():
    """Busca lista expandida de vozes brasileiras"""
    try:
        v = await edge_tts.VoicesManager.create()
        return {x["FriendlyName"]: x["ShortName"] for x in v.find(Locale="pt-BR")}
    except:
        return {"Antônio": "pt-BR-AntonioNeural", "Francisca": "pt-BR-FranciscaNeural"}

def format_time(seconds: float):
    td = datetime.timedelta(seconds=seconds)
    return f"{int(td.total_seconds()//3600):02d}:{int(td.total_seconds()%3600//60):02d}:{int(td.total_seconds()%60):02d},{int(td.microseconds/1000):03d}"

# --- SIDEBAR ---
st.sidebar.markdown("## EXD STUDIO")
if 'voices' not in st.session_state:
    st.session_state.voices = asyncio.run(get_all_voices())

aba = st.sidebar.radio("FERRAMENTAS", ["🎤 SPEAK", "🎬 CAPTION"], format_func=lambda x: x)

# --- ABA SPEAK (GERADOR DE ÁUDIO) ---
if aba == "🎤 SPEAK":
    st.markdown("<h1>EXD <span style='color:#151515'>SPEAK</span></h1>", unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        col1, col2 = st.columns([2, 1])
        with col1:
            texto = st.text_area("ROTEIRO", height=200)
        with col2:
            voz_sel = st.selectbox("VOZES DISPONÍVEIS", list(st.session_state.voices.keys()))
            rate = st.slider("VELOCIDADE", -50, 50, 0, format="%d%%")
        
        if st.button("GERAR VOZ NEURAL"):
            if texto:
                rate_str = f"{rate:+d}%"
                path = "speech.mp3"
                asyncio.run(edge_tts.Communicate(texto, st.session_state.voices[voz_sel], rate=rate_str).save(path))
                st.audio(path)
        st.markdown('</div>', unsafe_allow_html=True)

# --- ABA CAPTION (GERADOR DE LEGENDAS VIA UPLOAD) ---
elif aba == "🎬 CAPTION":
    st.markdown("<h1>EXD <span style='color:#151515'>CAPTION</span></h1>", unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        
        # 1. Upload do Arquivo
        up = st.file_uploader("SUBIR ÁUDIO OU VÍDEO", type=["mp3", "wav", "mp4"])
        
        # 2. Editor de Estilo (Preview)
        st.markdown("### ESTILIZAÇÃO")
        c1, c2, c3 = st.columns(3)
        with c1:
            cor_txt = st.color_picker("COR DO TEXTO", "#FFFFFF")
        with c2:
            cor_glow = st.color_picker("COR DO BRILHO (GLOW)", "#9D00FF")
        with c3:
            tamanho = st.slider("TAMANHO", 20, 100, 60)
            
        # Preview em Tempo Real
        st.markdown(f"""
            <div class="preview-box">
                <p style="color:{cor_txt}; font-size:{tamanho}px; font-weight:bold; 
                text-shadow: 0px 0px 15px {cor_glow}; text-transform: uppercase; font-family: Arial;">
                    Exemplo de Legenda Viral
                </p>
            </div>
        """, unsafe_allow_html=True)

        if st.button("PROCESSAR E GERAR LEGENDA"):
            if up:
                with st.spinner("IA ESCANEANDO FREQUÊNCIAS..."):
                    with open("temp_file", "wb") as t: t.write(up.read())
                    model = whisper.load_model("tiny")
                    result = model.transcribe("temp_file", fp16=False)
                    
                    srt = ""
                    for i, seg in enumerate(result['segments']):
                        start = format_time(seg['start'])
                        end = format_time(seg['end'])
                        # Aplica o UPPER CASE automático para impacto
                        srt += f"{i+1}\n{start} --> {end}\n{seg['text'].strip().upper()}\n\n"
                    
                    st.success("Transcrição Completa!")
                    st.download_button("BAIXAR SRT CONFIGURADO", srt, "exd_viral.srt")
            else:
                st.error("Nenhum arquivo detectado.")
        st.markdown('</div>', unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.caption("v9.0 PRO | HIGH PERFORMANCE")
