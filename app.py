import streamlit as st
import asyncio
import edge_tts
import os
import requests
import io
import random

# Configuração
st.set_page_config(page_title="EXD STUDIO ULTRA", page_icon="⚡", layout="wide")

# CSS Minimalista Total Black
st.markdown("""
    <style>
    .stApp { background-color: #000000; }
    [data-testid="stSidebar"] { background-color: #050505 !important; border-right: 1px solid #1a1a1a; }
    .main-card { background: #080808; padding: 40px; border: 1px solid #111; border-radius: 2px; }
    h1 { color: #fff !important; font-weight: 900; letter-spacing: -2px; font-size: 4.5em !important; }
    .stButton>button {
        width: 100%; background: #fff; color: #000 !important;
        font-weight: 800; border: none; padding: 15px; border-radius: 0px;
        letter-spacing: 2px; text-transform: uppercase;
    }
    .stButton>button:hover { background: #666; }
    .stTextArea textarea { background-color: #000 !important; color: #fff !important; border: 1px solid #111 !important; }
    audio { filter: invert(100%); width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# --- ENGINE DE VOZ ---
async def get_voices():
    try:
        v = await edge_tts.VoicesManager.create()
        return {x["FriendlyName"]: x["ShortName"] for x in v.find(Locale="pt-BR")}
    except:
        return {"Padrao": "pt-BR-AntonioNeural"}

# --- ENGINE DE IMAGEM (ESTÁVEL) ---
def get_stable_image(keyword):
    """Usa Source Unsplash - Praticamente impossível dar Timeout"""
    seed = random.randint(0, 5000)
    # Tenta buscar uma imagem real baseada na palavra-chave
    url = f"https://source.unsplash.com/featured/1024x1024/?{keyword.replace(' ', ',')}&sig={seed}"
    try:
        response = requests.get(url, timeout=20)
        if response.status_code == 200:
            return response.content
    except:
        return None
    return None

# --- SIDEBAR ---
st.sidebar.title("EXD STUDIO")
aba = st.sidebar.radio("TOOLS", ["AUDIO", "VISION"], format_func=lambda x: f"▶ {x}")

if aba == "AUDIO":
    st.markdown("<h1>EXD <span style='color:#111'>AUDIO</span></h1>", unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        if 'v_list' not in st.session_state:
            st.session_state.v_list = asyncio.run(get_voices())
        
        txt = st.text_area("SCRIPT", placeholder="Digite o texto...")
        voz = st.selectbox("VOICE", list(st.session_state.v_list.keys()))
        
        if st.button("RENDER AUDIO"):
            if txt:
                path = "voice.mp3"
                asyncio.run(edge_tts.Communicate(txt, st.session_state.v_list[voz]).save(path))
                st.audio(path)
                st.download_button("SAVE MP3", open(path, "rb"), "exd.mp3")
        st.markdown('</div>', unsafe_allow_html=True)

elif aba == "VISION":
    st.markdown("<h1>EXD <span style='color:#111'>VISION</span></h1>", unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        key = st.text_input("KEYWORD (Busca imagens reais)", placeholder="Ex: dark city, neon, forest...")
        
        if st.button("SEARCH IMAGE"):
            if key:
                with st.spinner("FETCHING..."):
                    img = get_stable_image(key)
                    if img:
                        st.image(img, use_column_width=True)
                        st.download_button("SAVE PNG", img, "exd_img.png")
                    else:
                        st.error("Conexão falhou. Tente outra palavra.")
        st.markdown('</div>', unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.caption("V7.0 | ANTI-TIMEOUT")
