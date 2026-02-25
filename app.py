import streamlit as st
import asyncio
import edge_tts
import whisper
import datetime
from PIL import Image
from streamlit_option_menu import option_menu
from streamlit_drawable_canvas import st_canvas

# --- CONFIGURAÇÃO E INTRO EXD ---
st.set_page_config(page_title="EXD STUDIO V14", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .intro-screen { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background-color: #020202; z-index: 999999; display: flex; justify-content: center; align-items: center; animation: hideIntro 3.5s forwards; pointer-events: none; }
    .intro-text { font-family: 'Arial Black', sans-serif; font-size: 12vw; font-weight: 900; color: #fff; letter-spacing: 25px; animation: cinematicGlow 3s ease-in-out forwards; }
    @keyframes cinematicGlow { 0% { opacity: 0; transform: scale(0.8); filter: blur(20px); text-shadow: 0 0 0px #9D00FF; } 40% { opacity: 1; filter: blur(0px); text-shadow: 0 0 60px #9D00FF; } 80% { opacity: 1; transform: scale(1.05); text-shadow: 0 0 100px #00D1FF; } 100% { opacity: 0; transform: scale(1.5); filter: blur(15px); } }
    @keyframes hideIntro { 0% { opacity: 1; } 90% { opacity: 1; } 100% { opacity: 0; visibility: hidden; } }
    .stApp { background-color: #050505; color: #fff; }
    [data-testid="stSidebar"] { background-color: #000 !important; border-right: 1px solid #111; }
    .main-card { background: #0a0a0a; border: 1px solid #151515; padding: 30px; border-radius: 6px; box-shadow: 0 4px 20px rgba(0,0,0,0.5); margin-bottom: 20px; }
    .stButton>button { width: 100%; background: #ffffff; color: #000 !important; font-weight: 900; border: none; padding: 15px; border-radius: 2px; text-transform: uppercase; transition: 0.3s; letter-spacing: 2px; }
    .stButton>button:hover { background: #9D00FF; color: #fff !important; box-shadow: 0px 0px 20px rgba(157, 0, 255, 0.6); transform: translateY(-2px); }
    </style>
    <div class="intro-screen"><div class="intro-text">EXD</div></div>
    """, unsafe_allow_html=True)

# --- BANCO DE VOZES FIXO (Fim dos Bugs) ---
VOZES_PREMIUM = {
    "🇧🇷 Antônio (Masculino, Forte)": "pt-BR-AntonioNeural",
    "🇧🇷 Francisca (Feminino, Clara)": "pt-BR-FranciscaNeural",
    "🇧🇷 Thalita (Feminino, Dinâmica)": "pt-BR-ThalitaNeural",
    "🇺🇸 Guy (Inglês, Masculino)": "en-US-GuyNeural",
    "🇺🇸 Jenny (Inglês, Feminino)": "en-US-JennyNeural"
}

def format_srt(seconds):
    td = datetime.timedelta(seconds=seconds)
    return f"{int(td.total_seconds()//3600):02d}:{int(td.total_seconds()%3600//60):02d}:{int(td.total_seconds()%60):02d},{int(td.microseconds/1000):03d}"

def image_to_ascii(img, new_width=100):
    chars = ["@", "#", "S", "%", "?", "*", "+", ";", ":", ",", "."]
    width, height = img.size
    aspect_ratio = height / width
    new_height = int(new_width * aspect_ratio * 0.55)
    img = img.resize((new_width, new_height)).convert("L")
    pixels = img.getdata()
    new_pixels = [chars[pixel // 25] for pixel in pixels]
    ascii_str = "".join(new_pixels)
    return "\n".join([ascii_str[index:index + new_width] for index in range(0, len(ascii_str), new_width)])

# --- SIDEBAR (THE OS MENU) ---
with st.sidebar:
    st.markdown("<h2 style='text-align: center; letter-spacing: 8px; font-weight: 900;'>EXD</h2>", unsafe_allow_html=True)
    
    menu = option_menu(
        menu_title=None,
        options=["Voice Engine", "Smart Caption", "Image Editor", "ASCII Art", "Hook Machine", "Color Grading"],
        icons=["mic-fill", "badge-cc-fill", "palette-fill", "file-earmark-font-fill", "lightning-charge-fill", "droplet-fill"],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"background-color": "#000"},
            "icon": {"color": "#9D00FF"},
            "nav-link": {"color": "#aaa", "font-size": "13px", "font-weight": "bold", "text-transform": "uppercase"},
            "nav-link-selected": {"background-color": "#111", "color": "#fff", "border-left": "4px solid #00D1FF"},
        }
    )

# --- 1. VOICE ENGINE (CORRIGIDO) ---
if menu == "Voice Engine":
    st.markdown("<h1>VOICE <span style='color:#333'>ENGINE</span></h1>", unsafe_allow_html=True)
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    c1, c2 = st.columns([2, 1])
    with c1: text_input = st.text_area("Roteiro", height=150)
    with c2:
        voz_sel = st.selectbox("Locutor", list(VOZES_PREMIUM.keys()))
        vel = st.slider("Velocidade", -50, 50, 0, format="%d%%")
        
    if st.button("RENDERIZAR ÁUDIO"):
        if text_input:
            path = "audio_exd.mp3"
            v_str = f"{vel:+d}%"
            asyncio.run(edge_tts.Communicate(text_input, VOZES_PREMIUM[voz_sel], rate=v_str).save(path))
            st.audio(path)
            st.download_button("BAIXAR MP3", open(path, "rb"), "exd_voice.mp3")
    st.markdown('</div>', unsafe_allow_html=True)

# --- 2. SMART CAPTION ---
elif menu == "Smart Caption":
    st.markdown("<h1>SMART <span style='color:#333'>CAPTION</span></h1>", unsafe_allow_html=True)
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    up = st.file_uploader("Upload Áudio/Vídeo", type=["mp3", "mp4", "wav"])
    if st.button("GERAR SRT"):
        if up:
            with st.spinner("Analisando..."):
                with open("temp", "wb") as f: f.write(up.read())
                res = whisper.load_model("tiny").transcribe("temp")
                srt = "".join([f"{i+1}\n{format_srt(s['start'])} --> {format_srt(s['end'])}\n{s['text'].strip().upper()}\n\n" for i, s in enumerate(res['segments'])])
                st.download_button("BAIXAR SRT", srt, "exd.srt")
    st.markdown('</div>', unsafe_allow_html=True)

# --- 3. IMAGE EDITOR (NOVO!) ---
elif menu == "Image Editor":
    st.markdown("<h1>IMAGE <span style='color:#333'>EDITOR</span></h1>", unsafe_allow_html=True)
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.info("🎨 Ferramenta de edição estilo Paint/Photoshop. Suba uma imagem de fundo para começar!")
    
    bg_image = st.file_uploader("Upload de Imagem Base", type=["png", "jpg", "jpeg"])
    
    col1, col2 = st.columns([1, 4])
    with col1:
        st.markdown("### Ferramentas")
        tool = st.selectbox("Ação", ("freedraw", "line", "rect", "circle", "transform"))
        stroke_width = st.slider("Tamanho do Pincel", 1, 25, 3)
        stroke_color = st.color_picker("Cor da Linha", "#00D1FF")
        bg_color = st.color_picker("Cor de Fundo", "#000000")
    
    with col2:
        img_data = Image.open(bg_image) if bg_image else None
        canvas_result = st_canvas(
            fill_color="rgba(255, 165, 0, 0.3)",
            stroke_width=stroke_width,
            stroke_color=stroke_color,
            background_color=bg_color,
            background_image=img_data,
            update_streamlit=True,
            height=500,
            width=800,
            drawing_mode=tool,
            key="canvas",
        )
    st.markdown('</div>', unsafe_allow_html=True)

# --- 4. ASCII ART (NOVO!) ---
elif menu == "ASCII Art":
    st.markdown("<h1>ASCII <span style='color:#333'>ART</span></h1>", unsafe_allow_html=True)
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    img_up = st.file_uploader("Suba uma imagem para virar texto (Estilo Matrix)", type=["jpg", "png"])
    col1, col2 = st.columns(2)
    with col1: width_ascii = st.slider("Largura dos Caracteres", 50, 150, 100)
    
    if st.button("TRANSFORMAR EM CÓDIGO"):
        if img_up:
            img = Image.open(img_up)
            arte = image_to_ascii(img, width_ascii)
            st.code(arte, language="text")
            st.download_button("BAIXAR TEXTO", arte, "exd_ascii.txt")
    st.markdown('</div>', unsafe_allow_html=True)

# --- 5 & 6. HOOK MACHINE & COLOR GRADING ---
elif menu == "Hook Machine":
    st.markdown("<h1>HOOK <span style='color:#333'>MACHINE</span></h1>", unsafe_allow_html=True)
    nicho = st.text_input("Qual seu Nicho?")
    if st.button("GERAR GANCHOS"):
        st.success(f"O MAIOR erro que quem trabalha com {nicho} comete todos os dias.")
        st.success(f"Você foi enganado sobre {nicho} a sua vida inteira. Veja por quê.")

elif menu == "Color Grading":
    st.markdown("<h1>COLOR <span style='color:#333'>PALETTE</span></h1>", unsafe_allow_html=True)
    st.code("Cyberpunk: #9D00FF (Roxo) | #00D1FF (Ciano)")
