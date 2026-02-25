import streamlit as st
import asyncio
import edge_tts
import whisper
import datetime
import os

# --- SETUP E ESTILO VISUAL ---
st.set_page_config(page_title="EXD STUDIO ULTIMATE", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    /* Gradiente Animado no Fundo */
    .stApp {
        background: linear-gradient(135deg, #000000 0%, #0a0a0a 50%, #1a0033 100%);
        color: #fff;
    }
    
    /* Animação entre seções */
    .element-container { animation: fadeIn 0.8s ease-in-out; }
    @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

    /* Sidebar Ultra Dark */
    [data-testid="stSidebar"] { background-color: #000 !important; border-right: 1px solid #222; }
    
    /* Cards de Edição */
    .edit-card {
        background: rgba(20, 20, 20, 0.6);
        padding: 25px;
        border-radius: 15px;
        border: 1px solid #333;
        backdrop-filter: blur(10px);
        margin-bottom: 20px;
    }

    /* Botões Neon */
    .stButton>button {
        width: 100%; background: linear-gradient(90deg, #9D00FF, #00D1FF);
        color: white !important; font-weight: 800; border: none; padding: 15px;
        border-radius: 8px; text-transform: uppercase; transition: 0.3s;
    }
    .stButton>button:hover { transform: scale(1.02); box-shadow: 0px 0px 20px rgba(157, 0, 255, 0.5); }
    
    h1 { font-weight: 900; letter-spacing: -4px; background: -webkit-linear-gradient(#fff, #444); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 5em !important; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÕES ---
async def get_voices():
    v = await edge_tts.VoicesManager.create()
    return {x["FriendlyName"]: x["ShortName"] for x in v.find(Locale="pt-BR")}

def format_srt(seconds):
    td = datetime.timedelta(seconds=seconds)
    return f"{int(td.total_seconds()//3600):02d}:{int(td.total_seconds()%3600//60):02d}:{int(td.total_seconds()%60):02d},{int(td.microseconds/1000):03d}"

# --- INTRO E TÍTULO ---
st.markdown("<h1>EXD STUDIO <span style='font-size: 0.2em; vertical-align: middle; color: #555;'>V12 PRO</span></h1>", unsafe_allow_html=True)

# --- SISTEMA DE ABAS ANIMADAS ---
tab1, tab2, tab3, tab4 = st.tabs(["🎤 VOICE ENGINE", "🎬 CAPTION SRT", "🧠 SCRIPT AI", "📺 PROMPTER"])

with tab1:
    st.markdown('<div class="edit-card">', unsafe_allow_html=True)
    st.subheader("Sintetizador Neural")
    col1, col2 = st.columns([3, 1])
    with col1:
        script = st.text_area("Script do Vídeo", height=150)
    with col2:
        if 'v_list' not in st.session_state: st.session_state.v_list = asyncio.run(get_voices())
        voz = st.selectbox("Locutor", list(st.session_state.v_list.keys()))
        speed = st.slider("Velocidade", -50, 50, 0)
    
    if st.button("GERAR MASTER ÁUDIO"):
        if script:
            path = "voice.mp3"
            asyncio.run(edge_tts.Communicate(script, st.session_state.v_list[voz], rate=f"{speed:+d}%").save(path))
            st.audio(path)
    st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="edit-card">', unsafe_allow_html=True)
    st.subheader("Gerador de Legendas (SRT)")
    up = st.file_uploader("Upload do Áudio para Legendar", type=["mp3", "wav", "m4a"])
    if st.button("EXTRAIR TIMECODES"):
        if up:
            with st.spinner("Analisando frequências..."):
                with open("temp", "wb") as f: f.write(up.read())
                model = whisper.load_model("tiny")
                res = model.transcribe("temp")
                srt_out = ""
                for i, s in enumerate(res['segments']):
                    srt_out += f"{i+1}\n{format_srt(s['start'])} --> {format_srt(s['end'])}\n{s['text'].strip().upper()}\n\n"
                st.download_button("BAIXAR SRT (CAPCUT READY)", srt_out, "legenda.srt")
    st.markdown('</div>', unsafe_allow_html=True)

with tab3:
    st.markdown('<div class="edit-card">', unsafe_allow_html=True)
    st.subheader("Editor de Ganchos (Hook AI)")
    ideia = st.text_input("Qual o assunto do vídeo?")
    if st.button("CRIAR GANCHOS VIRAIS"):
        st.info("1. 'E se eu te dissesse que você foi enganado sobre...'")
        st.info("2. 'Parem de fazer isso se você quer ter resultado em...'")
        st.info("3. 'O segredo que os grandes editores não te contam...'")
    st.markdown('</div>', unsafe_allow_html=True)

with tab4:
    st.markdown('<div class="edit-card">', unsafe_allow_html=True)
    st.subheader("Teleprompter de Estúdio")
    txt_p = st.text_area("Cole seu texto aqui para ler enquanto grava", height=100)
    vel_p = st.slider("Velocidade de Leitura", 1, 10, 5)
    if st.button("INICIAR LEITURA"):
        st.markdown(f"""
            <div style="height: 300px; overflow: hidden; border: 1px solid #333; padding: 20px; font-size: 30px; line-height: 1.6; text-align: center;">
                <marquee direction="up" scrollamount="{vel_p}" style="height: 100%;">
                    {txt_p}
                </marquee>
            </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.sidebar.markdown("### STATUS DO SISTEMA")
st.sidebar.success("Servidores Online")
st.sidebar.info("GPU Acceleration: OFF")
st.sidebar.markdown("---")
st.sidebar.caption("EXD STUDIO | © 2026")
