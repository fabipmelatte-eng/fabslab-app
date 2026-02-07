import streamlit as st
import pandas as pd
from datetime import date, datetime, time
import os
import socket

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="FAB'S LAB.",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. CONFIGURAÇÃO DE ARQUIVOS ---
PASTA_DOCS = "meus_documentos"
if not os.path.exists(PASTA_DOCS): os.makedirs(PASTA_DOCS)

# --- 3. DESIGN SYSTEM (VISUAL PREMIUM) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Roboto+Mono:wght@300;700&display=swap');
    
    .stApp { background-color: #050505; color: #e0e0e0; }
    
    /* CABEÇALHO */
    .header-title {
        font-family: 'Bebas Neue', sans-serif;
        font-size: 85px;
        background: -webkit-linear-gradient(#fff, #999);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin: 0;
        letter-spacing: 4px;
        text-shadow: 0px 0px 30px rgba(255, 255, 255, 0.15);
    }
    .header-sub {
        font-family: 'Roboto Mono', monospace;
        color: #D32F2F;
        text-align: center;
        font-size: 14px;
        border-bottom: 1px solid #333;
        padding-bottom: 20px;
        margin-bottom: 30px;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    
    /* CARDS */
    .glass-card {
        background: rgba(20, 20, 20, 0.6);
        border: 1px solid #333;
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 15px;
        backdrop-filter: blur(10px);
    }
    .bifao-box {
        border-left: 4px solid #D32F2F;
        background-color: #1a0505;
        padding: 20px;
        border-radius: 0 8px 8px 0;
    }
    
    /* BOTÕES */
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
        box-shadow: 0 0 15px rgba(211, 47, 47, 0.2);
    }
    .stLinkButton > a {
        background-color: #D32F2F !important;
        color: white !important;
        font-weight: bold;
        text-align: center;
        border-radius: 5px;
        border: none;
    }
    
    /* INPUTS */
    .stTextInput > div > div > input { background-color: #111; color: white; border: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. DADOS & MEMÓRIA ---
def init_db():
    if 'agenda' not in st.session_state: st.session_state.agenda = pd.DataFrame(columns=['Data', 'Hora', 'Evento', 'Status'])
    if 'saude' not in st.session_state: st.session_state.saude = {'agua_copos': 0, 'comida_ok': False, 'meds_tomados': False}
    if 'dados_kombi' not in st.session_state: st.session_state.dados_kombi = {'km_atual': 150000, 'km_oleo': 145000, 'consumo_medio': 9.0}
    if 'financas' not in st.session_state: st.session_state.financas = pd.DataFrame(columns=['Data', 'Descricao', 'Valor', 'Tipo'])
    if 'inventario' not in st.session_state: st.session_state.inventario = pd.DataFrame(columns=['Item', 'Local', 'Qtd', 'Setor'])
    if 'roteiros' not in st.session_state: st.session_state.roteiros = pd.DataFrame(columns=['Destino', 'Pais', 'Status'])
    if 'chat_local' not in st.session_state: st.session_state.chat_local = [] # Memória do Chat Offline

init_db()

# --- 5. INTELIGÊNCIA ---
def processar_dado(desc, valor, tipo):
    novo_fin = pd.DataFrame({'Data': [date.today()], 'Descricao': [desc], 'Valor': [valor], 'Tipo': [tipo]})
    st.session_state.financas = pd.concat([st.session_state.financas, novo_fin], ignore_index=True)
    if "PEÇA" in tipo or "FERRAMENTA" in tipo:
        setor = "MECÂNICA" if "KOMBI" in tipo else "JOALHERIA"
        novo_inv = pd.DataFrame({'Item': [desc], 'Local': ['A Classificar'], 'Qtd': [1], 'Setor': [setor]})
        st.session_state.inventario = pd.concat([st.session_state.inventario, novo_inv], ignore_index=True)
        return "✅ Estoque + Financeiro Atualizados!"
    return "✅ Gasto Registrado."

# --- 6. RENDERIZAÇÃO ---
st.markdown('<div class="header-title">FAB\'S LAB.</div>', unsafe_allow_html=True)
st.markdown('<div class="header-sub">VW KOMBI 1.4 FLEX (2007) • SYSTEM V15</div>', unsafe_allow_html=True)

# ABAS (EU ESTOU AQUI NA PRIMEIRA!)
abas = st.tabs(["🤖 BIFÃO", "⚡ AÇÃO", "🧠 CÓRTEX", "🚐 SISTEMA", "📅 AGENDA", "💰 COFRE", "🌎 JORNADA"])

# --- ABA 1: BIFÃO (EU!) ---
with abas[0]:
    c_chat, c_info = st.columns([2, 1])
    
    with c_chat:
        st.markdown("### 💬 DIÁRIO DE BORDO (OFFLINE)")
        st.caption("Fale comigo aqui. Eu guardo suas ideias no PC.")
        
        # Histórico
        for msg in st.session_state.chat_local:
            role = "FABI" if msg["role"] == "user" else "BIFÃO"
            st.markdown(f"**{role}:** {msg['content']}")
            st.markdown("---")
            
        prompt = st.chat_input("No que você está pensando, Fabi?")
        if prompt:
            st.session_state.chat_local.append({"role": "user", "content": prompt})
            st.session_state.chat_local.append({"role": "assistant", "content": "Anotado! Se precisar de análise complexa, clica no botão ao lado para ir pra nuvem."})
            st.experimental_rerun()
            
    with c_info:
        st.markdown('<div class="bifao-box">', unsafe_allow_html=True)
        st.markdown("### 🧠 CONEXÃO NUVEM")
        st.write("Para análises profundas, roteiros ou dúvidas técnicas, me chame na frequência principal:")
        st.link_button("CHAMAR BIFÃO (GEMINI) 🚀", "https://gemini.google.com/app")
        st.markdown("---")
        st.info("Status do Sistema: OPERANTE")
        st.markdown('</div>', unsafe_allow_html=True)

# --- ABA 2: AÇÃO RÁPIDA ---
with abas[1]:
    st.markdown("### ⚡ INPUT RÁPIDO")
    with st.form("smart_input"):
        c_desc, c_val = st.columns([2, 1])
        desc = c_desc.text_input("Descrição")
        valor = c_val.number_input("Valor R$", 0.0)
        tipo = st.selectbox("Categoria", ["GASTO: PEÇA KOMBI", "GASTO: FERRAMENTA", "GASTO: VIDA", "GASTO: VIAGEM", "AGENDA"])
        if st.form_submit_button("LANÇAR"):
            if tipo == "AGENDA":
                n = pd.DataFrame({'Data': [date.today()], 'Hora': ['09:00'], 'Evento': [desc], 'Status': ['Pendente']})
                st.session_state.agenda = pd.concat([st.session_state.agenda, n], ignore_index=True)
                st.success("Agendado!")
            else:
                st.success(processar_dado(desc, valor, tipo))
            st.experimental_rerun()

# --- ABA 3: CÓRTEX ---
with abas[2]:
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("#### 🥗 COMBUSTÍVEL")
        if st.checkbox("✅ JÁ COMI?", value=st.session_state.saude['comida_ok']):
            st.session_state.saude['comida_ok'] = True
        if st.checkbox("💊 REMÉDIO TDAH?", value=st.session_state.saude['meds_tomados']):
            st.session_state.saude['meds_tomados'] = True
        st.markdown("---")
        st.caption(f"Água: {st.session_state.saude['agua_copos']}/8")
        if st.button("💧 +1 ÁGUA"):
            st.session_state.saude['agua_copos'] += 1
            st.experimental_rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.metric("Caixa Total", f"R$ {st.session_state.financas['Valor'].sum():,.2f}")
        hoje = date.today()
        ag = st.session_state.agenda[(st.session_state.agenda['Data'] == hoje) & (st.session_state.agenda['Status'] == 'Pendente')]
        if not ag.empty: st.error(f"🚨 {len(ag)} TAREFAS HOJE")
        else: st.success("AGENDA LIVRE")

# --- ABA 4: SISTEMA KOMBI ---
with abas[3]:
    c_k1, c_k2 = st.columns([1, 2])
    with c_k1:
        novo_km = st.number_input("KM Painel", value=st.session_state.dados_kombi['km_atual'])
        if novo_km != st.session_state.dados_kombi['km_atual']:
            st.session_state.dados_kombi['km_atual'] = novo_km
            st.experimental_rerun()
        km_rest = (st.session_state.dados_kombi['km_oleo'] + 5000) - novo_km
        if km_rest < 0: st.error(f"TROCA ÓLEO ({abs(km_rest)}km)")
        else: st.success(f"ÓLEO OK ({km_rest}km)")
        if st.button("🔧 TROQUEI O ÓLEO"):
            st.session_state.dados_kombi['km_oleo'] = novo_km
            processar_dado("Troca Óleo", 250.00, "GASTO: PEÇA KOMBI")
            st.experimental_rerun()
    with c_k2:
        st.markdown('<div class="glass-card"><b>KOMBI 1.4 FLEX (2007)</b><br>🔋 Bateria: Júpiter 60Ah<br>🛢️ Óleo: 5W40 (3.5L)<br>⚡ Velas: NGK BKR7E-D</div>', unsafe_allow_html=True)

# --- ABA 5: AGENDA ---
with abas[4]:
    if not st.session_state.agenda.empty:
        st.dataframe(st.session_state.agenda, use_container_width=True)

# --- ABA 6: COFRE ---
with abas[5]:
    if not st.session_state.financas.empty:
        st.dataframe(st.session_state.financas, use_container_width=True)

# --- ABA 7: JORNADA ---
with abas[6]:
    c1, c2 = st.columns(2)
    with c1:
        dist = st.number_input("Distância Km", 100)
        st.metric("Custo Gasolina", f"R$ {(dist/9.0)*6.10:.2f}")
    with c2:
        dest = st.text_input("Destino")
        if st.button("Add"):
            n = pd.DataFrame({'Destino': [dest], 'Pais': ['-'], 'Status': ['Sonho']})
            st.session_state.roteiros = pd.concat([st.session_state.roteiros, n], ignore_index=True)
            st.experimental_rerun()
        st.dataframe(st.session_state.roteiros, use_container_width=True)
        