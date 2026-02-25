import streamlit as st
import asyncio
import edge_tts
import os

# Configuração da página
st.set_page_config(page_title="EXD SPEAK ULTIMATE", page_icon="🎙️", layout="centered")

# CSS Avançado: Fundo Animado, Gradientes e Ícones
st.markdown("""
    <style>
    /* Fundo Animado Dark Minimal */
    .stApp {
        background: linear-gradient(-45deg, #000000, #111111, #050505, #1a1a1a);
        background-size: 400% 400%;
        animation: gradient 12s ease infinite;
    }
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* Card com Efeito de Vidro Fumê */
    .main-card {
        background: rgba(10, 10, 10, 0.8);
        backdrop-filter: blur(20px);
        border-radius: 16px;
        padding: 40px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        box-shadow: 0 25px 50px rgba(0, 0, 0, 0.9);
    }

    /* Título com Gradiente Branco/Cinza */
    .glitch-title {
        background: linear-gradient(to right, #ffffff, #666666);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 900;
        font-size: 3em;
        text-align: center;
        margin-bottom: 10px;
    }

    /* Botão com Gradiente Metálico */
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #333333, #ffffff, #333333);
        background-size: 200% auto;
        color: #000 !important;
        border: none;
        padding: 14px;
        font-weight: 800;
        border-radius: 8px;
        transition: 0.5s;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    .stButton>button:hover {
        background-position: right center;
        transform: scale(1.01);
    }

    /* Área de texto e Inputs */
    .stTextArea textarea {
        background-color: rgba(0,0,0,0.9) !important;
        color: white !important;
        border: 1px solid #222 !important;
    }
    
    /* Player de Áudio Invertido (Dark) */
    audio { filter: invert(100%) hue-rotate(180deg); width: 100%; margin-top: 20px; }
    
    /* Esconder elementos desnecessários do Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# Função para buscar vozes atualizadas direto da Microsoft
async def get_voices():
    try:
        voices = await edge_tts.VoicesManager.create()
        br_voices = voices.find(Locale="pt-BR")
        # Cria um dicionário com nome amigável e ID técnico
        return {v["FriendlyName"]: v["ShortName"] for v in br_voices}
    except:
        # Fallback caso a API falhe
        return {"Antônio (Padrão)": "pt-BR-AntonioNeural", "Francisca (Padrão)": "pt-BR-FranciscaNeural"}

# Cabeçalho com Ícone SVG Minimalista
st.markdown("""
    <div style="text-align: center; margin-bottom: 30px;">
        <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="1" stroke-linecap="round" stroke-linejoin="round">
            <rect x="4" y="2" width="16" height="20" rx="2" ry="2"></rect>
            <circle cx="12" cy="14" r="4"></circle>
            <line x1="12" y1="6" x2="12.01" y2="6"></line>
        </svg>
        <div class="glitch-title">EXD SPEAK</div>
        <p style="color: #444; letter-spacing: 3px; font-size: 0.7em;">PREMIUM VOICE INTERFACE</p>
    </div>
    """, unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    
    # Busca vozes se não estiverem no cache
    if 'vozes' not in st.session_state:
        st.session_state.vozes = asyncio.run(get_voices())
    
    texto = st.text_area("ROTEIRO", placeholder="O que deseja converter para áudio?", height=150)

    # Seletor de vozes completo e atualizado
    voz_nome = st.selectbox("LOCUTOR (AUTO-SYNC)", list(st.session_state.vozes.keys()))
    voz_id = st.session_state.vozes[voz_nome]

    if st.button("GERAR ONDAS SONORAS"):
        if not texto.strip():
            st.error("TEXTO VAZIO")
        else:
            file_path = "exd_output.mp3"
            
            async def run_tts():
                try:
                    communicate = edge_tts.Communicate(texto, voz_id)
                    await communicate.save(file_path)
                    return True
                except Exception as e:
                    st.error(f"ERRO: {e}")
                    return False

            with st.spinner("SINTETIZANDO..."):
                ok = asyncio.run(run_tts())
            
            if ok and os.path.exists(file_path):
                st.audio(file_path)
                with open(file_path, "rb") as f:
                    st.download_button(
                        label="BAIXAR MP3",
                        data=f,
                        file_name="exd_pro_audio.mp3",
                        mime="audio/mpeg"
                    )
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<p style='text-align: center; color: #111; margin-top: 40px; font-size: 0.6em;'>VERSION 3.0 | NO LOGS | ENCRYPTED CONNECTION</p>", unsafe_allow_html=True)
