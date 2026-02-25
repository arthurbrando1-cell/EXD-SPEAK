import streamlit as st
import asyncio
import edge_tts
import whisper
import datetime
import io
from PIL import Image
from streamlit_option_menu import option_menu
from streamlit_drawable_canvas import st_canvas
import nest_asyncio

# Inicializa o loop para o Voice Engine não travar
nest_asyncio.apply()

# --- CONFIGURAÇÃO E ESTILO ---
st.set_page_config(page_title="EXD STUDIO PRO", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    /* INTRO EXD */
    .intro-screen { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background-color: #020202; z-index: 9999; display: flex; justify-content: center; align-items: center; animation: hide 3.5s forwards; }
    .intro-text { font-family: 'Arial Black'; font-size: 10vw; color: #fff; letter-spacing: 20px; animation: glow 3s forwards; }
    @keyframes glow { 0% { opacity:0; filter:blur(10px); } 50% { opacity:1; filter:blur(0px); text-shadow: 0 0 30px #9D00FF; } 100% { opacity:0; transform:scale(1.2); } }
    @keyframes hide { 0%, 90% { opacity:1; visibility:visible; } 100% { opacity:0; visibility:hidden; } }
    
    /* DESIGN SISTEMA */
    .stApp { background-color: #050505; color: #fff; }
    [data-testid="stSidebar"] { background-color: #000 !important; border-right: 1px solid #111; }
    .main-card { background: #0a0a0a; border: 1px solid #1a1a1a; padding: 25px; border-radius: 8px; margin-bottom: 20px; }
    .stButton>button { width: 100%; background: #ffffff; color: #000 !important; font-weight: 900; border-radius: 2px; padding: 12px; transition: 0.3s; }
    .stButton>button:hover { background: #9D00FF; color: #fff !important; box-shadow: 0px 0px 15px #9D00FF; }
    h1 { font-weight: 900; letter-spacing: -3px; font-size: 3.5em !important; }
    </style>
    <div class="intro-screen"><div class="intro-text">EXD</div></div>
    """, unsafe_allow_html=True)

# --- FUNÇÕES DE SUPORTE ---
def format_srt(seconds):
    td = datetime.timedelta(seconds=seconds)
    return f"{int(td.total_seconds()//3600):02d}:{int(td.total_seconds()%3600//60):02d}:{int(td.total_seconds()%60):02d},{int(td.microseconds/1000):03d}"

def image_to_custom_ascii(img, chars, new_width=100):
    width, height = img.size
    new_height = int(new_width * (height / width) * 0.5)
    img = img.resize((new_width, new_height)).convert("L")
    pixels = img.getdata()
    # Mapeamento dinâmico em 4 estágios de luz
    new_pixels = [chars[min(pixel // 64, 3)] for pixel in pixels]
    ascii_str = "".join(new_pixels)
    return "\n".join([ascii_str[i:i + new_width] for i in range(0, len(ascii_str), new_width)])

VOZES = {
    "Antônio (BR)": "pt-BR-AntonioNeural",
    "Francisca (BR)": "pt-BR-FranciscaNeural",
    "Guy (US)": "en-US-GuyNeural",
    "Jenny (US)": "en-US-JennyNeural"
}

# --- SIDEBAR COM TUDO ---
with st.sidebar:
    st.markdown("<h2 style='text-align:center'>EXD STUDIO</h2>", unsafe_allow_html=True)
    menu = option_menu(None, ["Voice Engine", "Smart Caption", "Image Editor", "ASCII Mapper", "SEO & Ganchos"], 
        icons=["mic", "badge-cc", "brush", "grid-3x3", "lightning"], 
        menu_icon="cast", default_index=0,
        styles={"container": {"background-color": "#000"}, "nav-link": {"color": "#aaa", "font-size": "12px"}, "nav-link-selected": {"background-color": "#111", "border-left": "3px solid #9D00FF"}})

# --- LÓGICA DAS FERRAMENTAS ---

if menu == "Voice Engine":
    st.markdown("<h1>VOICE <span style='color:#222'>ENGINE</span></h1>", unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        txt_v = st.text_area("Roteiro", height=150)
        c1, c2 = st.columns(2)
        voz = c1.selectbox("Locutor", list(VOZES.keys()))
        vel = c2.slider("Velocidade", -50, 50, 0)
        if st.button("GERAR ÁUDIO"):
            asyncio.run(edge_tts.Communicate(txt_v, VOZES[voz], rate=f"{vel:+d}%").save("v.mp3"))
            st.audio("v.mp3")
        st.markdown('</div>', unsafe_allow_html=True)

elif menu == "Smart Caption":
    st.markdown("<h1>SMART <span style='color:#222'>CAPTION</span></h1>", unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        up_s = st.file_uploader("Upload Áudio/Vídeo", type=["mp3", "mp4"])
        if st.button("EXTRAIR SRT"):
            with open("t", "wb") as f: f.write(up_s.read())
            res = whisper.load_model("tiny").transcribe("t")
            srt = "".join([f"{i+1}\n{format_srt(s['start'])} --> {format_srt(s['end'])}\n{s['text'].strip().upper()}\n\n" for i, s in enumerate(res['segments'])])
            st.download_button("BAIXAR SRT", srt, "exd.srt")
        st.markdown('</div>', unsafe_allow_html=True)

elif menu == "Image Editor":
    st.markdown("<h1>IMAGE <span style='color:#222'>EDITOR</span></h1>", unsafe_allow_html=True)
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    bg_file = st.file_uploader("Foto de Fundo", type=["png", "jpg"])
    c1, c2 = st.columns([1, 4])
    with c1:
        tool = st.selectbox("Ferramenta", ["freedraw", "line", "rect", "circle", "transform"])
        color = st.color_picker("Cor", "#9D00FF")
        stroke = st.slider("Pincel", 1, 30, 5)
    with c2:
        bg_img = Image.open(bg_file) if bg_file else None
        st_canvas(fill_color="rgba(255,255,255,0.2)", stroke_width=stroke, stroke_color=color, 
                  background_image=bg_img, drawing_mode=tool, key="canvas_main", height=500, width=700)
    st.markdown('</div>', unsafe_allow_html=True)

elif menu == "ASCII Mapper":
    st.markdown("<h1>ASCII <span style='color:#222'>MAPPER</span></h1>", unsafe_allow_html=True)
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    up_a = st.file_uploader("Imagem Base", type=["jpg", "png"])
    st.write("### Mapeamento de Caracteres")
    c1, c2, c3, c4 = st.columns(4)
    ch1 = c1.text_input("Sombra", "@", maxlength=1)
    ch2 = c2.text_input("Meio-Sombra", "#", maxlength=1)
    ch3 = c3.text_input("Meio-Luz", "*", maxlength=1)
    ch4 = c4.text_input("Luz", ".", maxlength=1)
    res_a = st.slider("Resolução", 50, 200, 100)
    if st.button("GERAR ASCII"):
        if up_a:
            img_a = Image.open(up_a)
            arte = image_to_custom_ascii(img_a, [ch1, ch2, ch3, ch4], res_a)
            st.code(arte)
    st.markdown('</div>', unsafe_allow_html=True)

elif menu == "SEO & Ganchos":
    st.markdown("<h1>VIRAL <span style='color:#222'>TOOLS</span></h1>", unsafe_allow_html=True)
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    tema = st.text_input("Tema do Vídeo")
    if st.button("GERAR ESTRATÉGIA"):
        st.info(f"GANCHO: Por que você nunca deve ignorar {tema}...")
        st.success(f"TAGS: {tema}, edição, viral, tutorial, dicas")
    st.markdown('</div>', unsafe_allow_html=True)
