import streamlit as st
import asyncio
import edge_tts
import uuid
import nest_asyncio
from streamlit_option_menu import option_menu

nest_asyncio.apply()

# --- 1. SETTINGS & FULLSCREEN UI ---
st.set_page_config(page_title="EXD GRID MULTIPLAYER", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    /* FUNDO GRID INFINITO */
    .stApp {
        background-color: #050505;
        background-image: 
            linear-gradient(rgba(255, 255, 255, 0.05) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255, 255, 255, 0.05) 1px, transparent 1px);
        background-size: 50px 50px;
    }
    
    /* POST-IT & GIF CARDS */
    .grid-item {
        background: rgba(15, 15, 15, 0.9);
        border: 1px solid #333;
        border-radius: 8px;
        padding: 15px;
        box-shadow: 10px 10px 20px rgba(0,0,0,0.5);
        transition: 0.3s ease;
    }
    .grid-item:hover {
        border-color: #9D00FF;
        transform: scale(1.02) rotate(1deg);
    }
    
    /* SIDEBAR DE EDIÇÃO (CUSTOM) */
    [data-testid="stSidebar"] {
        background-color: rgba(0, 0, 0, 0.95) !important;
        border-right: 2px solid #9D00FF !important;
        backdrop-filter: blur(10px);
    }
    
    /* BOTÃO FLUTUANTE */
    .stButton>button {
        border-radius: 50px;
        font-weight: 900;
        text-transform: uppercase;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. MULTIPLAYER SIMULATION (SESSION STATE) ---
# Nota: Em produção, aqui você conectaria com Firebase.
if 'global_mural' not in st.session_state:
    st.session_state.global_mural = []

# --- 3. SIDEBAR DE CONTROLE (O "EDITOR") ---
with st.sidebar:
    st.markdown("<h1 style='color:#9D00FF;'>EDITOR EXD</h1>", unsafe_allow_html=True)
    
    tab_editor = option_menu(None, ["Canvas", "Voz", "Roteiro"], 
        icons=["grid-fill", "mic-fill", "pencil-square"], default_index=0)
    
    st.divider()
    
    if tab_editor == "Canvas":
        st.subheader("🚀 Colar no Mural")
        m_tipo = st.selectbox("Formato", ["📝 Papelzinho", "🖼️ Imagem / GIF"])
        m_texto = st.text_area("Texto ou Link do GIF", placeholder="Cole o link .gif aqui...")
        m_cor = st.color_picker("Cor do Papel", "#9D00FF")
        
        if st.button("LANÇAR NO GRID"):
            if m_texto:
                new_node = {
                    "id": str(uuid.uuid4())[:4].upper(),
                    "tipo": m_tipo,
                    "conteudo": m_texto,
                    "cor": m_cor
                }
                st.session_state.global_mural.append(new_node)
                st.toast("Postado com sucesso!")
                st.rerun()

# --- 4. ÁREA DO GRID (TELA CHEIA) ---

if tab_editor == "Canvas":
    st.markdown("<h2 style='text-align:center; color:white; letter-spacing:10px;'>MURAL <span style='color:#9D00FF'>MULTIPLAYER</span></h2>", unsafe_allow_html=True)
    
    # Criamos o Grid Dinâmico
    if not st.session_state.global_mural:
        st.info("O Grid está limpo. Use a barra lateral para colar o primeiro GIF ou Papelzinho!")
    else:
        # Organiza os itens em colunas para simular o grid livre
        cols = st.columns(4)
        for i, item in enumerate(reversed(st.session_state.global_mural)):
            with cols[i % 4]:
                if "Papelzinho" in item["tipo"]:
                    st.markdown(f"""
                        <div class="grid-item" style="border-left: 5px solid {item['cor']};">
                            <small style="color:#555;">#{item['id']}</small>
                            <p style="color:white; font-weight:bold; margin-top:10px;">{item['conteudo']}</p>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    # Lógica para Imagem/GIF
                    st.markdown(f"""
                        <div class="grid-item" style="border-top: 5px solid {item['cor']};">
                            <small style="color:#555;">#{item['id']}</small>
                            <img src="{item['conteudo']}" style="width:100%; border-radius:5px; margin-top:5px;">
                        </div>
                    """, unsafe_allow_html=True)
                
                # Botão para deletar individualmente
                if st.button(f"🗑️ #{item['id']}", key=f"del_{item['id']}"):
                    st.session_state.global_mural = [x for x in st.session_state.global_mural if x['id'] != item['id']]
                    st.rerun()

# --- 5. OUTRAS FUNÇÕES (REINTEGRADAS) ---
elif tab_editor == "Voz":
    st.title("🎤 Voice Engine")
    v_text = st.text_area("Roteiro")
    v_actor = st.selectbox("Voz", ["pt-BR-AntonioNeural", "pt-BR-FranciscaNeural"])
    if st.button("Gerar Áudio"):
        asyncio.run(edge_tts.Communicate(v_text, v_actor).save("s.mp3"))
        st.audio("s.mp3")

elif tab_editor == "Roteiro":
    st.title("📝 Script Gen")
    tema = st.text_input("Tema")
    if st.button("Criar Roteiro"):
        st.code(f"GANCHO: Você já viu {tema}?\nRETENÇÃO: O segredo é...\nCTA: Siga para mais!")
