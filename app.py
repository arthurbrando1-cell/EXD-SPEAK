import streamlit as st
import asyncio
import edge_tts
import os

# Configuração da página
st.set_page_config(page_title="EXD SPEAK PRO", page_icon="🎙️", layout="centered")

# CSS para Fundo Animado e Estilização de Ícones
st.markdown("""
    <style>
    /* Fundo Animado em Degradê */
    .stApp {
        background: linear-gradient(-45deg, #0f172a, #1e293b, #334155, #1e1b4b);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
    }

    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* Estilização do Card Central */
    .main-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 30px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.8);
    }

    /* Títulos e Textos */
    h1 {
        color: #60a5fa !important;
        font-family: 'Inter', sans-serif;
        font-weight: 800;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    /* Botão Customizado */
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        height: 3em;
        background: linear-gradient(90deg, #3b82f6, #2563eb);
        color: white;
        font-weight: bold;
        border: none;
        transition: transform 0.2s;
    }
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 0 15px rgba(59, 130, 246, 0.5);
    }
    </style>
    """, unsafe_allow_stdio=True)

# Título Principal com Ícone SVG (substituindo emoji)
st.markdown("""
    <div style="text-align: center;">
        <svg width="50" height="50" viewBox="0 0 24 24" fill="none" stroke="#60a5fa" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path><path d="M19 10v2a7 7 0 0 1-14 0v-2"></path><line x1="12" y1="19" x2="12" y2="23"></line><line x1="8" y1="23" x2="16" y2="23"></line></svg>
        <h1>EXD SPEAK PRO</h1>
        <p style="color: #94a3b8;">Sintetizador de Voz Neural de Alta Performance</p>
    </div>
    """, unsafe_allow_html=True)

# Container do Formulário
with st.container():
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    
    texto = st.text_area("Seu Roteiro:", placeholder="Digite aqui o que você quer que eu fale...", height=150)

    # Colunas para Vozes
    col1, col2 = st.columns(2)
    
    with col1:
        genero = st.selectbox("Gênero:", ["Masculino", "Feminino"])

    # Lista Expandida de Vozes
    vozes_masc = {
        "Antônio (Natural)": "pt-BR-AntonioNeural",
        "Donato (Grave)": "pt-BR-DonatoNeural",
        "Fábio (Formal)": "pt-BR-FabioNeural",
        "Nicolau (Expressivo)": "pt-BR-NicolauNeural"
    }
    vozes_fem = {
        "Francisca (Suave)": "pt-BR-FranciscaNeural",
        "Thalita (Clara)": "pt-BR-ThalitaNeural",
        "Brenda (Energética)": "pt-BR-BrendaNeural",
        "Elsa (Séria)": "pt-BR-ElsaNeural"
    }

    with col2:
        if genero == "Masculino":
            voz_nome = st.selectbox("Locutor:", list(vozes_masc.keys()))
            voz_id = vozes_masc[voz_nome]
        else:
            voz_nome = st.selectbox("Locutora:", list(vozes_fem.keys()))
            voz_id = vozes_fem[voz_nome]

    if st.button("GERAR ÁUDIO PROFISSIONAL"):
        if not texto.strip():
            st.warning("⚠️ Digite um texto para continuar.")
        else:
            file_path = "output.mp3"
            
            async def generate():
                try:
                    communicate = edge_tts.Communicate(texto, voz_id)
                    await communicate.save(file_path)
                    return True
                except Exception as e:
                    st.error(f"Falha na conexão com a Microsoft: {e}")
                    return False

            with st.spinner("🚀 Processando ondas sonoras..."):
                sucesso = asyncio.run(generate())
            
            if sucesso and os.path.exists(file_path):
                st.markdown("---")
                st.audio(file_path)
                with open(file_path, "rb") as f:
                    st.download_button(
                        label="⬇️ BAIXAR MP3 PARA O CAPCUT",
                        data=f,
                        file_name="exd_audio_pro.mp3",
                        mime="audio/mpeg"
                    )
    st.markdown('</div>', unsafe_allow_html=True)

# Rodapé
st.markdown("""
    <br><div style="text-align: center; color: #475569; font-size: 12px;">
    Powered by EXD Technology & Microsoft Neural Voices
    </div>
    """, unsafe_allow_html=True)
