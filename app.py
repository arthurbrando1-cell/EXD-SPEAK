import streamlit as st
import asyncio
import edge_tts
import os

# Configuração da página
st.set_page_config(page_title="EXD SPEAK MINIMAL", page_icon="🎙️", layout="centered")

# CSS para Visual Preto, Cinza e Branco (Estilo Dark Mode Pro)
st.markdown("""
    <style>
    /* Fundo Totalmente Escuro */
    .stApp {
        background-color: #000000;
    }

    /* Card Central Minimalista */
    .main-card {
        background: #111111;
        border-radius: 12px;
        padding: 40px;
        border: 1px solid #222222;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
        margin-top: 20px;
    }

    /* Títulos em Branco */
    h1 {
        color: #FFFFFF !important;
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        letter-spacing: -1px;
    }
    
    label { color: #888888 !important; }

    /* Inputs e Selects Cinzas */
    .stTextArea textarea {
        background-color: #050505 !important;
        color: #FFFFFF !important;
        border: 1px solid #333333 !important;
        border-radius: 8px !important;
    }

    /* Botão Branco com Texto Preto */
    .stButton>button {
        width: 100%;
        background-color: #FFFFFF;
        color: #000000;
        border: none;
        padding: 12px;
        font-weight: bold;
        border-radius: 6px;
        transition: 0.3s;
        text-transform: uppercase;
    }
    .stButton>button:hover {
        background-color: #CCCCCC;
        color: #000000;
        border: none;
    }
    
    /* Player de Áudio Dark */
    audio { filter: invert(100%); width: 100%; margin-top: 15px; }
    </style>
    """, unsafe_allow_html=True)

# Cabeçalho Minimalista
st.markdown("""
    <div style="text-align: center; margin-bottom: 20px;">
        <h1 style="font-size: 2em;">EXD <span style="color: #666;">SPEAK</span></h1>
        <p style="color: #444; font-size: 0.9em; letter-spacing: 2px;">MINIMALIST VOICE ENGINE</p>
    </div>
    """, unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    
    texto = st.text_area("TEXTO PARA CONVERSÃO", placeholder="Escreva aqui seu roteiro...", height=150)

    c1, c2 = st.columns(2)
    
    with c1:
        genero = st.selectbox("GÊNERO", ["Masculino", "Feminino"])

    # Vozes com nomes técnicos revisados para evitar o erro NoAudioReceived
    vozes_masc = {
        "Antônio (Padrão)": "pt-BR-AntonioNeural",
        "Donato (Grave)": "pt-BR-DonatoNeural",
        "Fábio (Formal)": "pt-BR-FabioNeural",
        "Nicolau (Animado)": "pt-BR-NicolauNeural"
    }
    vozes_fem = {
        "Francisca (Suave)": "pt-BR-FranciscaNeural",
        "Thalita (Clara)": "pt-BR-ThalitaNeural",
        "Brenda (Jovem)": "pt-BR-BrendaNeural",
        "Elsa (Séria)": "pt-BR-ElsaNeural"
    }

    with c2:
        if genero == "Masculino":
            voz_nome = st.selectbox("LOCUTOR", list(vozes_masc.keys()))
            voz_id = vozes_masc[voz_nome]
        else:
            voz_nome = st.selectbox("LOCUTORA", list(vozes_fem.keys()))
            voz_id = vozes_fem[voz_nome]

    if st.button("GERAR ÁUDIO"):
        if not texto.strip():
            st.error("Digite o texto.")
        else:
            file_path = "output.mp3"
            
            async def run_tts():
                try:
                    # Tenta gerar o áudio com a voz escolhida
                    communicate = edge_tts.Communicate(texto, voz_id)
                    await communicate.save(file_path)
                    return True
                except Exception:
                    # Se falhar (erro NoAudio), tenta com a voz padrão do sistema
                    try:
                        fallback_voz = "pt-BR-AntonioNeural" if genero == "Masculino" else "pt-BR-FranciscaNeural"
                        communicate = edge_tts.Communicate(texto, fallback_voz)
                        await communicate.save(file_path)
                        return True
                    except:
                        return False

            with st.spinner("PROCESSANDO..."):
                ok = asyncio.run(run_tts())
            
            if ok and os.path.exists(file_path):
                st.audio(file_path)
                with open(file_path, "rb") as f:
                    st.download_button(
                        label="BAIXAR MP3",
                        data=f,
                        file_name="exd_minimal.mp3",
                        mime="audio/mpeg"
                    )
            else:
                st.error("Erro na conexão. Tente frases menores ou troque a voz.")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<p style='text-align: center; color: #222; margin-top: 30px; font-size: 0.7em;'>EXD SYSTEM V2.0</p>", unsafe_allow_html=True)
