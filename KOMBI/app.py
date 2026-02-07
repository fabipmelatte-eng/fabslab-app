import streamlit as st
import pandas as pd
from datetime import date, datetime, time
import os

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="FAB'S LAB.",
    page_icon="🐴",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. CONFIGURAÇÃO DE ARQUIVOS ---
# Ajuste para funcionar bem na nuvem (cria a pasta se não existir)
PASTA_DOCS = "meus_documentos"
if not os.path.exists(PASTA_DOCS): 
    os.makedirs(PASTA_DOCS)

# --- 3. DESIGN SYSTEM ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Roboto+Mono:wght@300;700&display=swap');
    
    .stApp { background-color: #050505; color: #e0e0e0; }
    
    .header-title {
        font-family: 'Bebas Neue', sans-serif;
        font-size: 60px; /* Ajustei um pouco para mobile */
        background: -webkit-linear-gradient(#fff, #777);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin: 0;
        letter-spacing: 3px;
    }
    .header-sub {
        font-family: 'Roboto Mono', monospace;
        color: #D32F2F;
        text-align: center;
        font-size: 12px;
        border-bottom: 1px solid #333;
        padding-bottom: 20px;
        margin-bottom: 30px;
        text-transform: uppercase;
        letter-spacing: 2px;
        font-weight: bold;
    }
    
    .escort-card {
        border-left: 4px solid #D32F2F;
        background-color: #111;
        padding: 15px;
        margin-bottom: 15px;
        border-radius: 0 10px 10px 0;
    }
    
    .stButton > button {
        border: 1px solid #444;
        color: #ccc;
        background: #0F0F0F;
        font-family: 'Bebas Neue', sans-serif;
        font-size: 20px;
        width: 100%;
        transition: 0.3s;
        border-radius: 4px;
    }
    .stButton > button:hover {
        border-color: #D32F2F;
        color: #D32F2F;
        background: #1a1a1a;
    }
    
    .stTextInput > div > div > input { background-color: #111; color: white; border: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. DADOS ---
def init_db():
    if 'agenda' not in st.session_state: st.session_state.agenda = pd.DataFrame(columns=['Data', 'Hora', 'Evento', 'Status'])
    if 'saude' not in st.session_state: st.session_state.saude = {'agua_copos': 0, 'comida_ok': False, 'meds_tomados': False}
    if 'dados_kombi' not in st.session_state: st.session_state.dados_kombi = {'km_atual': 150000, 'km_oleo': 145000, 'consumo_medio': 9.0}
    if 'financas' not in st.session_state: st.session_state.financas = pd.DataFrame(columns=['Data', 'Descricao', 'Valor', 'Tipo'])
    if 'inventario' not in st.session_state: st.session_state.inventario = pd.DataFrame(columns=['Item', 'Local', 'Qtd', 'Setor'])
    if 'roteiros' not in st.session_state: st.session_state.roteiros = pd.DataFrame(columns=['Destino', 'Pais', 'Status'])
    if 'escort_chat' not in st.session_state: st.session_state.escort_chat = []

init_db()

# --- 5. LÓGICA ---
def processar_dado(desc, valor, tipo):
    novo_fin = pd.DataFrame({'Data': [date.today()], 'Descricao': [desc], 'Valor': [valor], 'Tipo': [tipo]})
    st.session_state.financas = pd.concat([st.session_state.financas, novo_fin], ignore_index=True)
    if "PEÇA" in tipo or "FERRAMENTA" in tipo:
        setor = "MECÂNICA" if "KOMBI" in tipo else "JOALHERIA"
        novo_inv = pd.DataFrame({'Item': [desc], 'Local': ['A Classificar'], 'Qtd': [1], 'Setor': [setor]})
        st.session_state.inventario = pd.concat([st.session_state.inventario, novo_inv], ignore_index=True)
        return "✅ Escolta confirma: Item estocado e pago."
    return "✅ Escolta confirma: Gasto registrado."

# --- 6. HEADER ---
st.markdown('<div class="header-title">FAB\'S LAB.</div>', unsafe_allow_html=True)
st.markdown('<div class="header-sub">VW KOMBI STANDARD 1.4 (2007) • CLOUD SYSTEM</div>', unsafe_allow_html=True)

# HUD
c1, c2, c3 = st.columns(3)
with c1: 
    hoje = date.today()
    ag = st.session_state.agenda[(st.session_state.agenda['Data'] == hoje) & (st.session_state.agenda['Status'] == 'Pendente')]
    if not ag.empty: st.error(f"📅 {len(ag)} MISSÕES")
    else: st.success("LIVRE")
with c2:
    km_rest = (st.session_state.dados_kombi['km_oleo'] + 5000) - st.session_state.dados_kombi['km_atual']
    if km_rest < 0: st.error(f"🔧 ÓLEO VENCIDO")
    else: st.info(f"MOTOR OK ({km_rest}km)")
with c3:
    if not st.session_state.saude['comida_ok']: st.warning("🍎 COMER")
    elif not st.session_state.saude['meds_tomados']: st.warning("💊 REMÉDIO")
    else: st.success("BIO OK")

st.markdown("---")

# ABAS
abas = st.tabs(["🐴 ESCORT", "⚡ AÇÃO", "🧠 CÓRTEX", "🚐 KOMBI", "📅 AGENDA", "💰 COFRE", "📁 DOCS", "🌎 ROTA"])

# --- ABA 1: ESCORT ---
with abas[0]:
    c_esc1, c_esc2 = st.columns([2, 1])
    with c_esc1:
        st.markdown("### 📡 COMUNICAÇÃO")
        if st.session_state.escort_chat:
            for msg in st.session_state.escort_chat:
                role = "FABI" if msg["role"] == "user" else "BIFÃO"
                cor = "#D32F2F" if role != "FABI" else "#555"
                st.markdown(f"""<div class="escort-card" style="border-color:{cor};"><small>{role}</small><br>{msg['content']}</div>""", unsafe_allow_html=True)
        
        user_input = st.chat_input("Comando...")
        if user_input:
            st.session_state.escort_chat.append({"role": "user", "content": user_input})
            resp = "Cópia. Mensagem registrada. Verifique sistemas vitais."
            st.session_state.escort_chat.append({"role": "assistant", "content": resp})
            st.rerun() # <--- AQUI ESTÁ A CORREÇÃO (Era experimental_rerun)

    with c_esc2:
        st.markdown("### 🛡️ STATUS")
        st.success("🟢 ONLINE")
        st.link_button("GEMINI CLOUD ☁️", "https://gemini.google.com/")

# --- ABA 2: AÇÃO ---
with abas[1]:
    st.markdown("### ⚡ LANÇAMENTO")
    with st.form("smart"):
        c1, c2 = st.columns([2, 1])
        d = c1.text_input("Descrição")
        v = c2.number_input("Valor", 0.0)
        t = st.selectbox("Tipo", ["GASTO: PEÇA KOMBI", "GASTO: FERRAMENTA", "GASTO: VIDA", "GASTO: VIAGEM", "AGENDA: EVENTO"])
        if st.form_submit_button("EXECUTAR"):
            if "AGENDA" in t:
                n = pd.DataFrame({'Data': [date.today()], 'Hora': ['09:00'], 'Evento': [d], 'Status': ['Pendente']})
                st.session_state.agenda = pd.concat([st.session_state.agenda, n], ignore_index=True)
                st.success("Agendado")
            else:
                msg = processar_dado(d, v, t)
                st.success(msg)
            st.rerun() # <--- CORREÇÃO AQUI TAMBÉM

# --- ABA 3: CÓRTEX ---
with abas[2]:
    st.markdown("### 🧠 BIO-FEEDBACK")
    c1, c2 = st.columns(2)
    with c1:
        comida = st.checkbox("✅ REFEIÇÃO SÓLIDA?", value=st.session_state.saude['comida_ok'])
        if comida != st.session_state.saude['comida_ok']:
            st.session_state.saude['comida_ok'] = comida
            if comida: st.balloons()
            st.rerun() # <--- CORREÇÃO
        if st.button("💧 +1 ÁGUA"):
            st.session_state.saude['agua_copos'] += 1
            st.rerun() # <--- CORREÇÃO
    with c2:
        meds = st.checkbox("MEDICAÇÃO TDAH", value=st.session_state.saude['meds_tomados'])
        if meds != st.session_state.saude['meds_tomados']:
            st.session_state.saude['meds_tomados'] = meds
            st.rerun() # <--- CORREÇÃO

# --- ABA 4: KOMBI ---
with abas[3]:
    st.markdown("### 🚐 TELEMETRIA")
    c1, c2 = st.columns([1, 2])
    with c1:
        km = st.number_input("KM Painel", value=st.session_state.dados_kombi['km_atual'])
        if km != st.session_state.dados_kombi['km_atual']:
            st.session_state.dados_kombi['km_atual'] = km
            st.rerun() # <--- CORREÇÃO
        if st.button("ZERAR ÓLEO"):
            st.session_state.dados_kombi['km_oleo'] = km
            processar_dado("Troca Óleo", 250, "GASTO: PEÇA KOMBI")
            st.rerun() # <--- CORREÇÃO
    with c2:
        st.info("🔋 BATERIA: Júpiter 60Ah / Freedom 115Ah")
        st.info("🛢️ ÓLEO: 5W40 Sintético (3.5L)")

# --- ABA 5: AGENDA ---
with abas[4]:
    st.markdown("### 📅 MISSÕES")
    if not st.session_state.agenda.empty:
        for i, row in st.session_state.agenda.iterrows():
            st.checkbox(f"{row['Evento']}", value=(row['Status']=='Concluído'), key=i)

# --- ABA 6: COFRE ---
with abas[5]:
    st.markdown("### 💰 CAIXA")
    if not st.session_state.financas.empty: st.dataframe(st.session_state.financas, use_container_width=True)

# --- ABA 7: DOCS ---
with abas[6]:
    st.markdown("### 📁 ARQUIVO")
    up = st.file_uploader("Upload", type=['pdf', 'jpg'])
    if up:
        with open(os.path.join(PASTA_DOCS, up.name), "wb") as f: f.write(up.getbuffer())
        st.success("Salvo")
    
    if os.path.exists(PASTA_DOCS):
        arquivos = os.listdir(PASTA_DOCS)
        if arquivos:
            for arq in arquivos: st.markdown(f"📄 {arq}")

# --- ABA 8: ROTA ---
with abas[7]:
    st.markdown("### 🌎 ROTEIROS")
    c1, c2 = st.columns(2)
    with c1:
        dist = st.number_input("Km", 100)
        st.metric("Gasolina Est.", f"R$ {(dist/9)*6.10:.2f}")
    with c2:
        dest = st.text_input("Novo Destino")
        if st.button("Add"):
            n = pd.DataFrame({'Destino': [dest], 'Pais': ['-'], 'Status': ['Sonho']})
            st.session_state.roteiros = pd.concat([st.session_state.roteiros, n], ignore_index=True)
            st.rerun() # <--- CORREÇÃO
        st.dataframe(st.session_state.roteiros, use_container_width=True)
        
