import streamlit as st
import asyncio
import edge_tts
import os

# Configuração da página
st.set_page_config(page_title="EXD SPEAK MINIMAL", page_icon="🎙️", layout="centered")

# CSS Minimalista (Preto, Cinza e Branco)
st.markdown("""
    <style>
    .stApp { background-color: #000000; }
    .main-card {
        background: #0a0a0a;
        border-radius: 8px;
        padding: 30px;
        border: 1px solid #1a1a1a;
        margin-top: 20px;
    }
    h1 { color: #FFFFFF !important; font-family: 'Inter', sans-serif; font-weight: 700; }
    label { color: #666666 !important; text-transform: uppercase; font-size: 0.8em; letter-spacing: 1px; }
    .stTextArea textarea {
        background-color: #050505 !important;
        color: #FFFFFF !important;
        border: 1px solid #222 !important;
        border-radius: 4px !important;
    }
    .stButton>button {
        width: 100%;
        background-color: #FFFFFF;
        color: #000000;
        border: none;
        padding: 12px;
        font-weight: bold;
        border-radius: 4px;
        transition: 0.2s;
    }
    .stButton>button:hover { background-color: #cccccc; }
    audio { filter: invert(100%); width: 100%; }
    /* Estilo para o seletor (Selectbox) */
    .stSelectbox div { background-color: #050505 !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# Função para buscar vozes atualizadas direto da Microsoft
async def get_voices():
    voices = await edge_tts.VoicesManager.create()
    # Filtra apenas vozes do Brasil (pt-BR) e remove duplicadas pelo nome curto
    br_voices = voices.find(Locale="pt-BR")
    return {v["FriendlyName"]: v["ShortName"] for v in br_voices}

# Título
st.markdown("<h1 style='text-align: center;'>EXD <span style='color: #333;'>SPEAK</span></h1>", unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    
    # Busca as vozes (usa cache para não ficar carregando toda hora)
    if 'lista_vozes' not in st.session_state:
        with st.spinner("Sincronizando com Microsoft..."):
            st.session_state.lista_vozes = asyncio.run(get_voices())
    
    texto = st.text_area("TEXTO", placeholder="Digite seu roteiro...", height=150)
    
    # Seletor dinâmico com vozes sempre atualizadas
    voz_selecionada_nome = st.selectbox("VOZES DISPONÍVEIS (AUTO-UPDATE)", list(st.session_state.lista_vozes.keys()))
    voz_id = st.session_state.lista_vozes[voz_selecionada_nome]

    if st.button("GERAR MP3"):
        if not texto.strip():
            st.error("Escreva o texto.")
        else:
            file_path = "output.mp3"
            
            async def run_tts():
                try:
                    communicate = edge_tts.Communicate(texto, voz_id)
                    await communicate.save(file_path)
                    return True
                except Exception as e:
                    st.error(f"Erro: {e}")
                    return False

            with st.spinner("GERANDO..."):
                ok = asyncio.run(run_tts())
            
            if ok and os.path.exists(file_path):
                st.audio(file_path)
                with open(file_path, "rb") as f:
                    st.download_button(
                        label="BAIXAR ARQUIVO",
                        data=f,
                        file_name="exd_audio.mp3",
                        mime="audio/mpeg"
                    )
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<p style='text-align: center; color: #1a1a1a; margin-top: 50px; font-size: 0.6em;'>SYNCED WITH MICROSOFT AZURE VOICES</p>", unsafe_allow_html=True)
