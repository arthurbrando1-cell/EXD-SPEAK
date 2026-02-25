import streamlit as st
import asyncio
import edge_tts
import whisper
import uuid
import nest_asyncio
from streamlit_option_menu import option_menu

nest_asyncio.apply()

# --- SETUP DA PÁGINA ---
st.set_page_config(page_title="EXD STUDIO", layout="wide", initial_sidebar_state="collapsed")

# --- CSS ULTRA CUSTOM: GRID, ANIMAÇÕES E INTERFACE ---
st.markdown("""
    <style>
    /* INTRO EXD */
    .intro-screen { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: #000; z-index: 9999; display: flex; justify-content: center; align-items: center; animation: fadeout 3s forwards; }
    .intro-text { font-family: 'Arial Black'; font-size: 10vw; color: #fff; animation: glow 2s infinite; }
    @keyframes glow { 0% { text-shadow: 0 0 10px #9D00FF; } 50% { text-shadow: 0 0 40px #00D1FF; } 100% { text-shadow: 0 0 10px #9D00FF; } }
    @keyframes fadeout { 0%, 80% { opacity: 1; visibility: visible; } 100% { opacity: 0; visibility: hidden; } }

    /* FUNDO PRETO ANIMADO COM GRID BRANCO */
    .canvas-container {
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        background-color: #050505;
        background-image: radial-gradient(rgba(255, 255, 255, 0.1) 1px, transparent 1px);
        background-size: 40px 40px;
        z-index: 1;
        overflow: auto;
    }
    
    /* BOTÃO FLUTUANTE VOLTAR */
    .btn-back {
        position: fixed; top: 20px; left: 20px; z-index: 100;
        background: #fff; color: #000; border: none; padding: 10px 20px;
        font-weight: 900; border-radius: 5px; cursor: pointer;
    }

    /* BARRA LATERAL DE EDIÇÃO (OVERLAY) */
    .edit-sidebar {
        position: fixed; right: 20px; top: 20px; bottom: 20px; width: 300px;
        background: rgba(10, 10, 10, 0.95); backdrop-filter: blur(10px);
        border: 1px solid #222; z-index: 101; border-radius: 15px; padding: 20px;
        color: white;
    }

    /* ESTILO DOS PAPELZINHOS (POST-ITS) */
    .post-it {
        display: inline-block; padding: 15px; border-radius: 5px;
        color: #000; font-weight: bold; min-width: 150px; min-height: 150px;
        box-shadow: 5px 5px 15px rgba(0,0,0,0.3); margin: 10px;
        cursor: grab;
    }
    </style>
    <div class="intro-screen"><div class="intro-text">EXD</div></div>
    """, unsafe_allow_html=True)

# --- DATABASE NO SESSION STATE ---
if 'mural_items' not in st.session_state:
    st.session_state.mural_items = []
if 'view' not in st.session_state:
    st.session_state.view = "menu"

# --- ROTEAMENTO DE TELAS ---

# 1. TELA DE MENU/TOOLS
if st.session_state.view == "menu":
    with st.sidebar:
        menu = option_menu("EXD TOOLS", ["Voice", "Caption", "Canvas Grid"], 
            icons=["mic", "badge-cc", "grid-fill"], default_index=0)
    
    if menu == "Canvas Grid":
        st.session_state.view = "canvas"
        st.rerun()
    
    # Renderizar Voice e Caption normalmente...
    if menu == "Voice":
        st.title("VOICE ENGINE")
        txt = st.text_area("Roteiro")
        if st.button("GERAR"):
            asyncio.run(edge_tts.Communicate(txt, "pt-BR-AntonioNeural").save("v.mp3"))
            st.audio("v.mp3")

# 2. TELA DO MURAL INFINITO (MODO TELA CHEIA)
elif st.session_state.view == "canvas":
    # Botão de Voltar
    if st.button("← VOLTAR", key="back_btn"):
        st.session_state.view = "menu"
        st.rerun()

    # Barra Lateral de Edição (Injetada via Streamlit)
    with st.sidebar:
        st.markdown("### 🛠️ FERRAMENTAS")
        tipo = st.radio("O que quer colar?", ["Texto/Papelzinho", "Imagem/GIF"])
        
        with st.form("new_item"):
            if tipo == "Texto/Papelzinho":
                content = st.text_area("Escreva aqui...")
                cor = st.color_picker("Cor do Papel", "#FFFF00")
            else:
                content = st.text_input("URL da Imagem/GIF")
                cor = "#FFFFFF"
            
            if st.form_submit_button("COLAR NO GRID"):
                st.session_state.mural_items.append({
                    "id": str(uuid.uuid4())[:4],
                    "tipo": tipo,
                    "content": content,
                    "cor": cor
                })
        
        if st.button("LIMPAR TUDO"):
            st.session_state.mural_items = []
            st.rerun()

    # ÁREA DO CANVAS (Onde os itens aparecem)
    st.markdown('<div class="canvas-container">', unsafe_allow_html=True)
    
    # Criar um layout de "mural" dinâmico usando colunas para os itens
    if st.session_state.mural_items:
        cols = st.columns(4) # Simula a disposição no grid
        for i, item in enumerate(st.session_state.mural_items):
            with cols[i % 4]:
                if item["tipo"] == "Texto/Papelzinho":
                    st.markdown(f"""
                        <div class="post-it" style="background-color: {item['cor']};">
                            {item['content']}
                            <br><small style="opacity:0.5; font-size:10px;">#{item['id']}</small>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.image(item["content"], use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
