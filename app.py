import streamlit as st
import asyncio
import edge_tts
import whisper
import uuid
import nest_asyncio
from streamlit_option_menu import option_menu

nest_asyncio.apply()

# --- 1. INTERFACE & DESIGN SYSTEM ---
st.set_page_config(page_title="EXD STUDIO PRO", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    /* INTRO EXD CINEMATOGRÁFICA */
    .intro-screen { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: #000; z-index: 9999; display: flex; justify-content: center; align-items: center; animation: fadeout 3s forwards; pointer-events: none; }
    .intro-text { font-family: 'Arial Black'; font-size: 12vw; color: #fff; letter-spacing: 25px; animation: glow 2.5s ease-in-out forwards; }
    @keyframes glow { 0% { opacity:0; filter:blur(20px); text-shadow: 0 0 0px #9D00FF; } 50% { opacity:1; filter:blur(0px); text-shadow: 0 0 50px #9D00FF; } 100% { opacity:0; transform:scale(1.3); } }
    @keyframes fadeout { 0%, 90% { opacity: 1; visibility: visible; } 100% { opacity: 0; visibility: hidden; } }

    /* DARK MODE & NEON GRID */
    .stApp { background-color: #050505; background-image: radial-gradient(rgba(157, 0, 255, 0.1) 1px, transparent 1px); background-size: 30px 30px; color: #fff; }
    [data-testid="stSidebar"] { background-color: #000 !important; border-right: 1px solid #1a1a1a; }
    
    /* CARDS DO MURAL */
    .mural-card { background: rgba(10,10,10,0.8); border: 1px solid #1a1a1a; border-radius: 12px; padding: 20px; transition: 0.3s; }
    .mural-card:hover { border-color: #9D00FF; box-shadow: 0 0 20px rgba(157, 0, 255, 0.2); }
    
    /* BOTÕES EXD */
    .stButton>button { background: linear-gradient(90deg, #9D00FF, #00D1FF); color: white !important; font-weight: 900; border: none; padding: 12px; border-radius: 4px; text-transform: uppercase; width: 100%; letter-spacing: 1px; }
    .stButton>button:hover { box-shadow: 0 0 15px #9D00FF; transform: scale(1.02); }
    </style>
    <div class="intro-screen"><div class="intro-text">EXD</div></div>
    """, unsafe_allow_html=True)

# --- 2. STORAGE (SESSION STATE) ---
if 'mural_db' not in st.session_state: st.session_state.mural_db = []

# --- 3. SIDEBAR PROFISSIONAL ---
with st.sidebar:
    st.markdown("<h1 style='text-align:center; color:#9D00FF; font-weight:900;'>EXD STUDIO</h1>", unsafe_allow_html=True)
    menu = option_menu(
        menu_title=None,
        options=["Mural Grid", "Voice Engine", "Smart Script", "Smart Caption", "Viral SEO"],
        icons=["grid-3x3-gap-fill", "mic-fill", "file-earmark-medical-fill", "badge-cc-fill", "lightning-charge-fill"],
        styles={
            "container": {"background-color": "#000"},
            "nav-link": {"color": "#888", "font-size": "13px", "text-transform": "uppercase", "font-weight": "bold"},
            "nav-link-selected": {"background-color": "#111", "color": "#9D00FF", "border-left": "4px solid #9D00FF"}
        }
    )

# --- 4. VOZES DISPONÍVEIS ---
VOZES_BANCO = {
    "Antônio (BR - Grave)": "pt-BR-AntonioNeural",
    "Francisca (BR - Suave)": "pt-BR-FranciscaNeural",
    "Thalita (BR - Jovem)": "pt-BR-ThalitaNeural",
    "Guy (US - Narrador)": "en-US-GuyNeural",
    "Jenny (US - Doce)": "en-US-JennyNeural"
}

# --- 5. LÓGICA DAS FUNÇÕES ---

if menu == "Mural Grid":
    st.markdown("<h1>INFINITY <span style='color:#9D00FF'>GRID</span></h1>", unsafe_allow_html=True)
    with st.expander("➕ ADICIONAR AO GRID", expanded=False):
        c1, c2 = st.columns(2)
        tipo = c1.radio("Conteúdo", ["Texto", "Imagem/GIF"])
        tit = c1.text_input("Título")
        cor_p = c1.color_picker("Cor de Destaque", "#9D00FF")
        cont = c2.text_area("Conteúdo ou URL")
        if st.button("COLAR NO GRID"):
            st.session_state.mural_db.append({"id": str(uuid.uuid4())[:4], "tipo": tipo, "titulo": tit, "cor": cor_p, "cont": cont})
            st.rerun()

    cols = st.columns(3)
    for i, item in enumerate(reversed(st.session_state.mural_db)):
        with cols[i % 3]:
            st.markdown(f"""<div class="mural-card" style="border-top: 5px solid {item['cor']};">
                <small style="color:#444;">#{item['id']}</small>
                <h4 style="color:{item['cor']};">{item['titulo']}</h4>
                <p>{item['cont'] if item['tipo'] == 'Texto' else ''}</p>
                {f'<img src="{item["cont"]}" style="width:100%; border-radius:8px;">' if item['tipo'] == 'Imagem/GIF' else ''}
            </div>""", unsafe_allow_html=True)

elif menu == "Voice Engine":
    st.markdown("<h1>VOICE <span style='color:#9D00FF'>ENGINE</span></h1>", unsafe_allow_html=True)
    c1, c2 = st.columns([2,1])
    txt_f = c1.text_area("Cole seu roteiro aqui", height=250)
    voz_f = c2.selectbox("Escolha a Voz", list(VOZES_BANCO.keys()))
    vel_f = c2.slider("Velocidade", -50, 50, 0)
    if st.button("RENDERIZAR ÁUDIO"):
        with st.spinner("Sintetizando..."):
            path = "exd_audio.mp3"
            asyncio.run(edge_tts.Communicate(txt_f, VOZES_BANCO[voz_f], rate=f"{vel_f:+d}%").save(path))
            st.audio(path)

elif menu == "Smart Script":
    st.markdown("<h1>SCRIPT <span style='color:#9D00FF'>GEN</span></h1>", unsafe_allow_html=True)
    tema = st.text_input("Qual o tema do vídeo?")
    estilo = st.selectbox("Estilo", ["Storytelling", "Educativo", "Venda Agressiva", "Curiosidades"])
    if st.button("GERAR ROTEIRO COMPLETO"):
        st.markdown(f"### Roteiro: {tema}")
        st.write(f"**[00:00 - GANCHO]** Você sabia que {tema} pode mudar tudo?")
        st.write(f"**[00:15 - DESENVOLVIMENTO]** No estilo {estilo}, explicamos que o segredo de {tema} está nos detalhes...")
        st.info("💡 Copie e cole no Voice Engine ao lado!")

elif menu == "Smart Caption":
    st.markdown("<h1>SMART <span style='color:#9D00FF'>CAPTION</span></h1>", unsafe_allow_html=True)
    up = st.file_uploader("Upload MP3/MP4", type=["mp3", "mp4"])
    if st.button("GERAR LEGENDA"):
        st.warning("IA Transcrevendo... (Aguarde)")

elif menu == "Viral SEO":
    st.markdown("<h1>VIRAL <span style='color:#9D00FF'>STRATEGY</span></h1>", unsafe_allow_html=True)
    assunto = st.text_input("Assunto para Ganchos")
    if st.button("GERAR GANCHOS EXPLOSIVOS"):
        st.success(f"1. O que ninguém te conta sobre {assunto}...")
        st.success(f"2. Pare de fazer isso se você quer dominar {assunto}!")
        st.success(f"3. O segredo obscuro do {assunto} revelado.")
