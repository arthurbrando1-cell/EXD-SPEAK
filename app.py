import streamlit as st
import asyncio
import edge_tts
import os

# Configuração da página
st.set_page_config(page_title="EXD SPEAK PRO", page_icon="🎙️", layout="centered")

# CSS para Interface Premium e Fundo Animado
st.markdown("""
    <style>
    /* Fundo Animado */
    .stApp {
        background: linear-gradient(-45deg, #0f172a, #1e293b, #0f172a, #1e1b4b);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
    }
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* Card Central com efeito de vidro */
    .main-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(15px);
        border-radius: 24px;
        padding: 40px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);
        margin-bottom: 20px;
    }

    /* Estilo dos inputs */
    .stTextArea textarea {
        background-color: rgba(15, 23, 42, 0.8) !important;
        color: white !important;
        border-radius: 12px !important;
        border: 1px solid #334155 !important;
    }

    /* Botão turbinado */
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #2563eb, #7c3aed);
        color: white;
        border: none;
        padding: 15px;
        font-weight: bold;
        border-radius: 12px;
        transition: 0.4s;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(37, 99, 235, 0.4);
        background: linear-gradient(90deg, #3b82f6, #8b5cf6);
    }
    </style>
    """, unsafe_allow_html=True)

# Cabeçalho com Ícone SVG
st.markdown("""
    <div style="text-align: center; margin-bottom: 30px;">
        <svg width="60" height="60" viewBox="0 0 24 24" fill="none" stroke="#60a5fa" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
            <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
            <line x1="12" y1="19" x2="12" y2="23"></line>
            <line x1="8" y1="23" x2="16" y2="23"></line>
        </svg>
        <h1 style="color: white; margin-top: 10px; font-size: 2.5em;">EXD SPEAK <span style="color:#60a5fa">PRO</span></h1>
        <p style="color: #94a3b8;">Gerador de Voz Neural para Criadores de Conteúdo</p>
    </div>
    """, unsafe_allow_html=True)

# Layout do Aplicativo
with st.container():
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    
    texto = st.text_area("O que a voz deve dizer?", placeholder="Escreva seu roteiro aqui...", height=150)

    c1, c2 = st.columns(2)
    
    with c1:
        genero = st.selectbox("Gênero da Voz", ["Masculino", "Feminino"])

    vozes_masc = {
        "Antônio (Padrão)": "pt-BR-AntonioNeural",
        "Donato (Grave)": "pt-BR-DonatoNeural",
        "Fábio (Formal)": "pt-BR-FabioNeural",
        "Nicolau (Animado)": "pt-BR-NicolauNeural"
    }
    vozes_fem = {
        "Francisca (Suave)": "pt-BR-FranciscaNeural",
        "Thalita (Rádio)": "pt-BR-ThalitaNeural",
        "Brenda (Jovem)": "pt-BR-BrendaNeural",
        "Elsa (Séria)": "pt-BR-ElsaNeural"
    }

    with c2:
        if genero == "Masculino":
            voz_nome = st.selectbox("Escolha o Locutor", list(vozes_masc.keys()))
            voz_id = vozes_masc[voz_nome]
        else:
            voz_nome = st.selectbox("Escolha a Locutora", list(vozes_fem.keys()))
            voz_id = vozes_fem[voz_nome]

    if st.button("GERAR MP3 AGORA"):
        if not texto.strip():
            st.warning("⚠️ Digite um texto antes de gerar.")
        else:
            file_path = "output.mp3"
            
            async def run_tts():
                try:
                    communicate = edge_tts.Communicate(texto, voz_id)
                    await communicate.save(file_path)
                    return True
                except Exception as e:
                    st.error(f"Erro na API: {e}")
                    return False

            with st.spinner("✨ Ajustando frequências neurais..."):
                ok = asyncio.run(run_tts())
            
            if ok and os.path.exists(file_path):
                st.success("✅ Áudio pronto para o CapCut!")
                st.audio(file_path)
                with open(file_path, "rb") as f:
                    st.download_button(
                        label="⬇️ BAIXAR MEU MP3",
                        data=f,
                        file_name="exd_audio_pro.mp3",
                        mime="audio/mpeg"
                    )
    st.markdown('</div>', unsafe_allow_html=True)

# Rodapé minimalista
st.markdown("<p style='text-align: center; color: #475569; font-size: 0.8em;'>© 2026 EXD SPEAK PRO - High Quality TTS</p>", unsafe_allow_html=True)
