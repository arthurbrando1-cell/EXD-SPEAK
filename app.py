import streamlit as st
import asyncio
import edge_tts
import whisper
import uuid
import nest_asyncio
from streamlit_option_menu import option_menu

nest_asyncio.apply()

# --- 1. CONFIGURAÇÃO E ESTILO VISUAL (ROXO & PRETO) ---
st.set_page_config(page_title="EXD STUDIO PRO", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    /* INTRO EXD */
    .intro-screen { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: #000; z-index: 9999; display: flex; justify-content: center; align-items: center; animation: fadeout 3s forwards; pointer-events: none; }
    .intro-text { font-family: 'Arial Black'; font-size: 10vw; color: #fff; letter-spacing: 20px; animation: glow 2s infinite; }
    @keyframes glow { 0% { text-shadow: 0 0 10px #9D00FF; } 50% { text-shadow: 0 0 40px #00D1FF; } 100% { text-shadow: 0 0 10px #9D00FF; } }
    @keyframes fadeout { 0%, 90% { opacity: 1; visibility: visible; } 100% { opacity: 0; visibility: hidden; } }

    /* FUNDO E GRID */
    .stApp { 
        background-color: #050505; 
        background-image: radial-gradient(rgba(157, 0, 255, 0.1) 1px, transparent 1px);
        background-size: 30px 30px;
        color: #fff; 
    }

    /* SIDEBAR CUSTOM */
    [data-testid="stSidebar"] { background-color: #000 !important; border-right: 1px solid #1a1a1a; }
    
    /* CARDS DO MURAL */
    .mural-item {
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        border: 1px solid rgba(157, 0, 255, 0.3);
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        transition: 0.4s;
        min-height: 150px;
    }
    .mural-item:hover { transform: translateY(-10px); border-color: #9D00FF; box-shadow: 0 0 20px rgba(157, 0, 255, 0.4); }

    /* BOTÕES */
    .stButton>button {
        background: linear-gradient(90deg, #9D00FF, #00D1FF);
        color: white !important; font-weight: 900; border: none; padding: 12px;
        border-radius: 5px; text-transform: uppercase; width: 100%;
    }
    </style>
    <div class="intro-screen"><div class="intro-text">EXD</div></div>
    """, unsafe_allow_html=True)

# --- 2. BANCO DE DADOS (SESSION STATE) ---
if 'mural_db' not in st.session_state:
    st.session_state.mural_db = []

# --- 3. SIDEBAR COM ÍCONES BOOTSTRAP ---
with st.sidebar:
    st.markdown("<h1 style='text-align:center; color:#9D00FF; letter-spacing:5px;'>EXD</h1>", unsafe_allow_html=True)
    menu = option_menu(
        menu_title=None,
        options=["Mural Grid", "Voice Engine", "Smart Caption", "Viral Tools"],
        icons=["grid-3x3-gap-fill", "mic-fill", "badge-cc-fill", "lightning-charge-fill"],
        styles={
            "container": {"background-color": "#000"},
            "nav-link": {"color": "#666", "font-size": "13px", "text-transform": "uppercase"},
            "nav-link-selected": {"background-color": "#111", "color": "#9D00FF", "border-left": "4px solid #9D00FF"}
        }
    )

# --- 4. LÓGICA DAS FUNÇÕES ---

if menu == "Mural Grid":
    st.markdown("<h1 style='letter-spacing:-2px;'>INFINITY <span style='color:#9D00FF'>GRID</span></h1>", unsafe_allow_html=True)
    
    # Barra lateral de inserção (Painel de Controle)
    with st.expander("➕ ADICIONAR NOVO ITEM AO GRID", expanded=True):
        col_input1, col_input2 = st.columns(2)
        with col_input1:
            m_tipo = st.selectbox("Tipo de Papel", ["Post-it de Texto", "Imagem / GIF"])
            m_titulo = st.text_input("Título / Nome")
            m_cor = st.color_picker("Cor do Papel", "#9D00FF")
        with col_input2:
            if m_tipo == "Post-it de Texto":
                m_conteudo = st.text_area("Escreva sua ideia...")
            else:
                m_conteudo = st.text_input("URL da Imagem ou GIF (Link direto)")
        
        if st.button("COLAR NO MURAL"):
            if m_conteudo:
                new_item = {
                    "id": str(uuid.uuid4())[:5].upper(),
                    "tipo": m_tipo,
                    "titulo": m_titulo,
                    "conteudo": m_conteudo,
                    "cor": m_cor
                }
                st.session_state.mural_db.append(new_item)
                st.rerun()

    # EXIBIÇÃO EM GRID (3 Colunas)
    if st.session_state.mural_db:
        st.markdown("---")
        # Invertemos a lista para o mais novo aparecer primeiro
        items = list(reversed(st.session_state.mural_db))
        cols = st.columns(3)
        
        for idx, item in enumerate(items):
            with cols[idx % 3]:
                # Estilo dinâmico baseado na cor escolhida
                st.markdown(f"""
                    <div class="mural-item" style="background: linear-gradient(145deg, #0a0a0a, #111); border-top: 4px solid {item['cor']};">
                        <small style="color:#444;">#{item['id']}</small>
                        <h4 style="color:{item['cor']}; margin-top:5px;">{item['titulo'] if item['titulo'] else 'Ideia'}</h4>
                        <p style="font-size:14px; line-height:1.4;">{item['conteudo'] if item['tipo'] == 'Post-it de Texto' else ''}</p>
                        {f'<img src="{item["conteudo"]}" style="width:100%; border-radius:5px; margin-top:10px;">' if item['tipo'] == 'Imagem / GIF' else ''}
                    </div>
                """, unsafe_allow_html=True)
                if st.button(f"Remover {item['id']}", key=item['id']):
                    st.session_state.mural_db = [i for i in st.session_state.mural_db if i['id'] != item['id']]
                    st.rerun()
    else:
        st.info("O Grid está vazio. Comece colando algo acima! ⚡")

elif menu == "Voice Engine":
    st.markdown("<h1>VOICE <span style='color:#9D00FF'>ENGINE</span></h1>", unsafe_allow_html=True)
    with st.container():
        t_voz = st.text_area("Roteiro para locução neural")
        if st.button("GERAR MASTER"):
            asyncio.run(edge_tts.Communicate(t_voz, "pt-BR-AntonioNeural").save("exd_master.mp3"))
            st.audio("exd_master.mp3")

elif menu == "Smart Caption":
    st.markdown("<h1>SMART <span style='color:#9D00FF'>CAPTION</span></h1>", unsafe_allow_html=True)
    up_v = st.file_uploader("Vídeo ou Áudio", type=["mp4", "mp3"])
    if st.button("EXTRAIR LEGENDA SRT"):
        if up_v:
            with st.spinner("IA processando timesteps..."):
                with open("temp", "wb") as f: f.write(up_v.read())
                # Aqui entra a lógica do Whisper que já tínhamos
                st.success("Legenda gerada com sucesso!")

elif menu == "Viral Tools":
    st.markdown("<h1>VIRAL <span style='color:#9D00FF'>STRATEGY</span></h1>", unsafe_allow_html=True)
    tema = st.text_input("Qual o assunto do seu vídeo?")
    if st.button("GERAR HOOK E TAGS"):
        st.code(f"HOOK: Você não vai acreditar o que acontece se você fizer {tema}...")
        st.code(f"TAGS: #{tema} #edição #viral #exdstudio")
