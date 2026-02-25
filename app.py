import streamlit as st
import asyncio
import edge_tts
import whisper
import datetime
import io
import base64
from PIL import Image
from streamlit_option_menu import option_menu
from streamlit_drawable_canvas import st_canvas

# --- CONFIG E INTRO ---
st.set_page_config(page_title="EXD STUDIO PRO", layout="wide")

st.markdown("""
    <style>
    .intro-screen { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background-color: #020202; z-index: 9999; display: flex; justify-content: center; align-items: center; animation: hide 3.5s forwards; }
    .intro-text { font-family: 'Arial Black'; font-size: 10vw; color: #fff; letter-spacing: 20px; animation: glow 3s forwards; }
    @keyframes glow { 0% { opacity:0; filter:blur(10px); } 50% { opacity:1; filter:blur(0px); text-shadow: 0 0 30px #9D00FF; } 100% { opacity:0; transform:scale(1.2); } }
    @keyframes hide { 0%, 90% { opacity:1; visibility:visible; } 100% { opacity:0; visibility:hidden; } }
    .stApp { background-color: #050505; color: #fff; }
    .main-card { background: #0a0a0a; border: 1px solid #1a1a1a; padding: 25px; border-radius: 8px; }
    </style>
    <div class="intro-screen"><div class="intro-text">EXD</div></div>
    """, unsafe_allow_html=True)

# --- ENGINE ASCII CUSTOMIZADA ---
def image_to_custom_ascii(img, chars, new_width=100):
    # chars é uma lista de 4 caracteres: [Sombra, Meio-Sombra, Meio-Luz, Luz]
    width, height = img.size
    new_height = int(new_width * (height / width) * 0.5)
    img = img.resize((new_width, new_height)).convert("L")
    pixels = img.getdata()
    
    # Mapeia 255 tons para 4 caracteres escolhidos pelo usuário
    new_pixels = [chars[pixel // 65] if pixel < 255 else chars[3] for pixel in pixels]
    ascii_str = "".join(new_pixels)
    return "\n".join([ascii_str[i:i + new_width] for i in range(0, len(ascii_str), new_width)])

# --- SIDEBAR ---
with st.sidebar:
    st.title("EXD STUDIO")
    menu = option_menu(None, ["Voice", "Caption", "Editor", "ASCII"], 
        icons=["mic", "cc", "brush", "sort-alpha-down"], menu_icon="cast", default_index=0,
        styles={"container": {"background-color": "#000"}, "nav-link-selected": {"background-color": "#9D00FF"}})

# --- PÁGINAS ---
if menu == "Voice":
    st.markdown("<h1>VOICE <span style='color:#222'>ENGINE</span></h1>", unsafe_allow_html=True)
    txt = st.text_area("Texto")
    if st.button("GERAR"):
        path = "v.mp3"
        asyncio.run(edge_tts.Communicate(txt, "pt-BR-AntonioNeural").save(path))
        st.audio(path)

elif menu == "Editor":
    st.markdown("<h1>IMAGE <span style='color:#222'>EDITOR</span></h1>", unsafe_allow_html=True)
    st.info("🎨 Corrigido: Desenhe ou edite sobre fotos.")
    
    up_bg = st.file_uploader("Subir foto de fundo", type=["png", "jpg"])
    col1, col2 = st.columns([1, 3])
    
    with col1:
        mode = st.selectbox("Ferramenta", ["freedraw", "line", "rect", "circle", "transform"])
        color = st.color_picker("Cor", "#00D1FF")
        size = st.slider("Grosso", 1, 50, 5)
        
    with col2:
        # Se houver imagem, carregamos ela de forma que o Canvas não dê erro
        bg_img = Image.open(up_bg) if up_bg else None
        
        canvas_result = st_canvas(
            fill_color="rgba(255, 255, 255, 0.3)",
            stroke_width=size,
            stroke_color=color,
            background_image=bg_img,
            drawing_mode=mode,
            key="canvas_v15",
            update_streamlit=True,
            height=600,
            width=800 if not bg_img else (800 * bg_img.width // bg_img.height)
        )

elif menu == "ASCII":
    st.markdown("<h1>ASCII <span style='color:#222'>MAPPER</span></h1>", unsafe_allow_html=True)
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    
    up_ascii = st.file_uploader("Imagem para ASCII", type=["jpg", "png"])
    
    st.markdown("### Configurar Mapeamento de Luz")
    c1, c2, c3, c4 = st.columns(4)
    with c1: char1 = st.text_input("Sombra (Escuro)", "@", maxlength=1)
    with c2: char2 = st.text_input("Meio-Tom 1", "#", maxlength=1)
    with c3: char3 = st.text_input("Meio-Tom 2", "*", maxlength=1)
    with c4: char4 = st.text_input("Luz (Claro)", ".", maxlength=1)
    
    largura = st.slider("Resolução (Largura)", 50, 200, 100)
    
    if st.button("GERAR ARTE ASCII"):
        if up_ascii:
            chars_list = [char1, char2, char3, char4]
            img = Image.open(up_ascii)
            res = image_to_custom_ascii(img, chars_list, largura)
            st.code(res, language="text")
    st.markdown('</div>', unsafe_allow_html=True)

elif menu == "Caption":
    st.write("Sistema de SRT Ativo.")
