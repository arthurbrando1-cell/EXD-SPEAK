import streamlit as st
import asyncio
import edge_tts
import whisper
import datetime
import time
from streamlit_option_menu import option_menu

# --- 1. CONFIGURAÇÃO BASE ---
st.set_page_config(page_title="EXD STUDIO", layout="wide", initial_sidebar_state="expanded")

# --- 2. INTRO CINEMATOGRÁFICA E CSS PREMIUM ---
st.markdown("""
    <style>
    /* ANIMAÇÃO DE INTRODUÇÃO 'EXD' */
    .intro-screen {
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        background-color: #020202; z-index: 999999;
        display: flex; justify-content: center; align-items: center;
        animation: hideIntro 3.5s forwards; pointer-events: none;
    }
    .intro-text {
        font-family: 'Arial Black', sans-serif; font-size: 12vw; font-weight: 900; 
        color: #fff; letter-spacing: 25px; text-transform: uppercase;
        animation: cinematicGlow 3s ease-in-out forwards;
    }
    @keyframes cinematicGlow {
        0% { opacity: 0; transform: scale(0.8); filter: blur(20px); text-shadow: 0 0 0px #9D00FF; }
        40% { opacity: 1; filter: blur(0px); text-shadow: 0 0 60px #9D00FF; }
        80% { opacity: 1; transform: scale(1.05); text-shadow: 0 0 100px #00D1FF; }
        100% { opacity: 0; transform: scale(1.5); filter: blur(15px); }
    }
    @keyframes hideIntro { 0% { opacity: 1; } 90% { opacity: 1; } 100% { opacity: 0; visibility: hidden; } }

    /* ESTILO GERAL DO APP */
    .stApp { background-color: #050505; color: #fff; }
    [data-testid="stSidebar"] { background-color: #000 !important; border-right: 1px solid #111; }
    .main-card { background: #0a0a0a; border: 1px solid #151515; padding: 35px; border-radius: 6px; box-shadow: 0 4px 20px rgba(0,0,0,0.5); margin-bottom: 20px; }
    h1, h2, h3, p { color: #fff !important; }
    
    /* BOTÕES METÁLICOS & NEON */
    .stButton>button { width: 100%; background: #ffffff; color: #000 !important; font-weight: 900; border: none; padding: 15px; border-radius: 2px; text-transform: uppercase; transition: 0.3s; letter-spacing: 2px; }
    .stButton>button:hover { background: #9D00FF; color: #fff !important; box-shadow: 0px 0px 20px rgba(157, 0, 255, 0.6); transform: translateY(-2px); }
    
    /* INPUTS */
    .stTextArea textarea, .stTextInput input { background-color: #0a0a0a !important; color: #fff !important; border: 1px solid #222 !important; border-radius: 2px; }
    </style>
    
    <div class="intro-screen"><div class="intro-text">EXD</div></div>
    """, unsafe_allow_html=True)

# --- 3. FUNÇÕES DO SISTEMA ---
@st.cache_data
def get_all_voices():
    """Busca centenas de vozes do Edge TTS (PT-BR e EN-US)"""
    import nest_asyncio
    nest_asyncio.apply()
    async def fetch():
        v = await edge_tts.VoicesManager.create()
        br = {f"🇧🇷 {x['FriendlyName']}": x["ShortName"] for x in v.find(Locale="pt-BR")}
        us = {f"🇺🇸 {x['FriendlyName']}": x["ShortName"] for x in v.find(Locale="en-US")}
        return {**br, **us} # Junta as listas
    return asyncio.run(fetch())

def format_srt(seconds):
    td = datetime.timedelta(seconds=seconds)
    return f"{int(td.total_seconds()//3600):02d}:{int(td.total_seconds()%3600//60):02d}:{int(td.total_seconds()%60):02d},{int(td.microseconds/1000):03d}"

# --- 4. SIDEBAR COM ÍCONES PROFISSIONAIS ---
with st.sidebar:
    st.markdown("<h2 style='text-align: center; letter-spacing: 8px; font-weight: 900; font-size: 2.5em;'>EXD</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #555; font-size: 0.8em; letter-spacing: 2px; margin-top:-15px;'>STUDIO OS</p><br>", unsafe_allow_html=True)
    
    # Menu com Ícones Reais do Bootstrap (SEM EMOJIS)
    menu = option_menu(
        menu_title=None,
        options=["Sintetizador Neural", "Caption SRT", "Teleprompter", "YouTube SEO", "Color Grading", "Gerador de Ganchos"],
        icons=["mic-fill", "badge-cc-fill", "display", "youtube", "palette-fill", "lightning-charge-fill"],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "#000"},
            "icon": {"color": "#9D00FF", "font-size": "18px"},
            "nav-link": {"color": "#aaaaaa", "font-size": "13px", "font-weight": "bold", "text-transform": "uppercase", "letter-spacing": "1px", "margin": "8px 0", "transition": "0.3s"},
            "nav-link-selected": {"background-color": "#0a0a0a", "color": "#fff", "border-left": "4px solid #00D1FF"},
        }
    )

# --- 5. ROTEAMENTO DAS PÁGINAS (Tudo Limpo e Dividido) ---

if menu == "Sintetizador Neural":
    st.markdown("<h1>VOICE <span style='color:#333'>ENGINE</span></h1>", unsafe_allow_html=True)
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    vozes = get_all_voices()
    
    col1, col2 = st.columns([2, 1])
    with col1:
        texto_voz = st.text_area("Roteiro de Locução", height=200, placeholder="Cole seu texto aqui...")
    with col2:
        voz_selecionada = st.selectbox("Banco de Vozes (BR e US)", list(vozes.keys()))
        velocidade = st.slider("Ajuste de Velocidade", -50, 50, 0, format="%d%%")
        tom = st.slider("Ajuste de Tom (Pitch)", -50, 50, 0, format="%dHz")
        
    if st.button("RENDERIZAR ÁUDIO FINAL"):
        if texto_voz:
            with st.spinner("Sintetizando..."):
                import nest_asyncio
                nest_asyncio.apply()
                v_str = f"{velocidade:+d}%"
                p_str = f"{tom:+d}Hz"
                path = "master_exd.mp3"
                asyncio.run(edge_tts.Communicate(texto_voz, vozes[voz_selecionada], rate=v_str, pitch=p_str).save(path))
                st.audio(path)
                st.download_button("BAIXAR MP3", open(path, "rb"), "exd_audio.mp3")
    st.markdown('</div>', unsafe_allow_html=True)

elif menu == "Caption SRT":
    st.markdown("<h1>SMART <span style='color:#333'>CAPTION</span></h1>", unsafe_allow_html=True)
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    arquivo = st.file_uploader("Arquivo de Áudio/Vídeo para Legendar", type=["mp3", "wav", "mp4"])
    
    if st.button("GERAR LEGENDA SINCRONIZADA"):
        if arquivo:
            with st.spinner("IA Transcrevendo Frame por Frame..."):
                with open("temp_audio", "wb") as f: f.write(arquivo.read())
                model = whisper.load_model("tiny")
                result = model.transcribe("temp_audio")
                
                srt_final = ""
                for i, seg in enumerate(result['segments']):
                    srt_final += f"{i+1}\n{format_srt(seg['start'])} --> {format_srt(seg['end'])}\n{seg['text'].strip().upper()}\n\n"
                
                st.success("Legenda Concluída!")
                st.download_button("BAIXAR .SRT (USAR NO CAPCUT/PREMIERE)", srt_final, "legenda_exd.srt")
    st.markdown('</div>', unsafe_allow_html=True)

elif menu == "Teleprompter":
    st.markdown("<h1>LIVE <span style='color:#333'>PROMPTER</span></h1>", unsafe_allow_html=True)
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    texto_prompter = st.text_area("Texto de Leitura", height=150)
    vel = st.slider("Velocidade do Rolo", 1, 20, 5)
    
    if st.button("MODO TELA CHEIA (INICIAR)"):
        st.markdown(f"""
            <div style="height: 50vh; background: #000; border: 2px solid #333; padding: 40px; border-radius: 10px; overflow: hidden;">
                <marquee direction="up" scrollamount="{vel}" style="height: 100%; font-size: 45px; font-weight: bold; line-height: 1.5; color: white; text-align: center;">
                    {texto_prompter}
                </marquee>
            </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

elif menu == "YouTube SEO":
    st.markdown("<h1>VIDEO <span style='color:#333'>METADATA</span></h1>", unsafe_allow_html=True)
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.write("Gerador de Títulos Virais e Tags")
    tema = st.text_input("Qual o tema do seu vídeo?")
    if st.button("GERAR SEO MÁXIMO"):
        st.write("### 🔥 Títulos de Alta Conversão")
        st.info(f"O SEGREDO OBSCURO SOBRE {tema.upper()} (Não Assista à Noite)")
        st.info(f"POR QUE VOCÊ ESTÁ FAZENDO {tema.upper()} ERRADO.")
        st.info(f"A VERDADE QUE TENTARAM ESCONDER SOBRE {tema.upper()}")
        st.write("### 🏷️ Tags para Copiar")
        st.code(f"{tema.lower()}, {tema.lower()} dicas, como fazer {tema.lower()}, segredos {tema.lower()}, dark video, edição viral")
    st.markdown('</div>', unsafe_allow_html=True)

elif menu == "Color Grading":
    st.markdown("<h1>COLOR <span style='color:#333'>PALETTE</span></h1>", unsafe_allow_html=True)
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.write("Escolha o clima do seu vídeo para pegar os códigos Hexadecimais para usar na correção de cor do Premiere/CapCut.")
    estilo = st.selectbox("Mood do Vídeo", ["Cyberpunk / Neon Dark", "True Crime / Suspense", "Minimalista / Luxury"])
    
    if estilo == "Cyberpunk / Neon Dark":
        st.code("Roxo: #9D00FF | Ciano: #00D1FF | Preto Profundo: #050505 | Rosa: #FF007F")
    elif estilo == "True Crime / Suspense":
        st.code("Sangue Frio: #8A0303 | Sombra: #1A1A1A | Amarelo Fita: #FFCC00 | Verde Pálido: #2C3E35")
    else:
        st.code("Ouro: #D4AF37 | Branco Gelo: #F5F5F5 | Cinza Carvão: #36454F | Preto Absoluto: #000000")
    st.markdown('</div>', unsafe_allow_html=True)

elif menu == "Gerador de Ganchos":
    st.markdown("<h1>HOOK <span style='color:#333'>MACHINE</span></h1>", unsafe_allow_html=True)
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    nicho = st.text_input("Qual o seu nicho? (Ex: Finanças, Terror, Curiosidades)")
    if st.button("GERAR HOOK (3 SEGUNDOS INICIAIS)"):
        st.success(f"99% das pessoas do nicho de {nicho} estão perdendo tempo. Aqui está o porquê.")
        st.success(f"Se você parar de rolar a tela agora, eu vou te provar que o que te contaram sobre {nicho} é mentira.")
        st.success(f"Guarde este vídeo. Ele é o único tutorial sobre {nicho} que você vai precisar neste ano.")
    st.markdown('</div>', unsafe_allow_html=True)
