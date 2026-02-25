import streamlit as st
import asyncio
import edge_tts
import os

# Configuração da Página
st.set_page_config(page_title="EXD SPEAK - Gerador Profissional", page_icon="🎙️")

st.title("🎙️ EXD SPEAK - Texto para Voz")
st.markdown("Gere áudios em MP3 com vozes reais da Microsoft. Totalmente grátis.")

# Área de Texto
texto = st.text_area("Digite seu roteiro aqui:", "Olá! Este áudio foi gerado pelo meu próprio site.", height=150)

# Opções de Vozes
col1, col2 = st.columns(2)
with col1:
    tipo_voz = st.radio("Gênero da Voz:", ["Masculina", "Feminina"])

# Mapeamento de vozes
vozes_masc = {
    "Antônio (Natural)": "pt-BR-AntonioNeural",
    "Donato (Robusto)": "pt-BR-DonatoNeural"
}
vozes_fem = {
    "Francisca (Suave)": "pt-BR-FranciscaNeural",
    "Thalita (Clara)": "pt-BR-ThalitaNeural"
}

with col2:
    if tipo_voz == "Masculina":
        voz_nome = st.selectbox("Escolha o locutor:", list(vozes_masc.keys()))
        voz_final = vozes_masc[voz_nome]
    else:
        voz_nome = st.selectbox("Escolha a locutora:", list(vozes_fem.keys()))
        voz_final = vozes_fem[voz_nome]

# Botão de Ação
if st.button("🚀 GERAR MP3 PARA DOWNLOAD"):
    if texto.strip() == "":
        st.error("Por favor, digite algum texto.")
    else:
        # Nome do arquivo temporário
        file_path = "output_audio.mp3"
        
        async def make_audio():
            communicate = edge_tts.Communicate(texto, voz_final)
            await communicate.save(file_path)

        with st.spinner("Sintetizando voz..."):
            asyncio.run(make_audio())
        
        if os.path.exists(file_path):
            st.audio(file_path)
            with open(file_path, "rb") as f:
                st.download_button(
                    label="⬇️ BAIXAR AGORA (MP3 REAL)",
                    data=f,
                    file_name="meu_audio_exd.mp3",
                    mime="audio/mpeg"
                )
            # O arquivo fica no servidor até a sessão fechar, 
            # cumprindo o que você falou: gera, baixa e depois some.