import streamlit as st
import pandas as pd
from datetime import date, datetime, time
import os

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="FAB'S LAB.", page_icon="🔐", layout="wide", initial_sidebar_state="collapsed")
PASTA_DOCS = "meus_documentos"
if not os.path.exists(PASTA_DOCS): os.makedirs(PASTA_DOCS)

# --- 2. ESTILO ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Roboto+Mono:wght@300;700&display=swap');
    .stApp { background-color: #050505; color: #e0e0e0; }
    .header-title { font-family: 'Bebas Neue', sans-serif; font-size: 60px; background: -webkit-linear-gradient(#fff, #999); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; margin: 0; }
    .header-sub { font-family: 'Roboto Mono', monospace; color: #D32F2F; text-align: center; font-size: 12px; border-bottom: 1px solid #333; padding-bottom: 20px; margin-bottom: 30px; text-transform: uppercase; letter-spacing: 2px; font-weight: bold; }
    .escort-card { border-left: 4px solid #D32F2F; background-color: #111; padding: 15px; margin-bottom: 15px; border-radius: 0 10px 10px 0; }
    .stButton > button { border: 1px solid #444; color: #ccc; background: #0F0F0F; font-family: 'Bebas Neue', sans-serif; font-size: 20px; width: 100%; }
    .stButton > button:hover { border-color: #D32F2F; color: #D32F2F; }
    .stTextInput > div > div > input { background-color: #111; color: white; border: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SISTEMA DE SEGURANÇA ---
if 'authenticated' not in st.session_state: st.session_state.authenticated = False
def check_password():
    if st.session_state.password_input == "Iron6Maiden7":
        st.session_state.authenticated = True
        del st.session_state.password_input
    else: st.error("⛔ SENHA INCORRETA")
if not st.session_state.authenticated:
    st.markdown("<br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown('<div class="header-title">FAB\'S LAB.</div>', unsafe_allow_html=True)
        st.markdown('<div class="header-sub">RESTRICTED AREA • AUTHORIZED PERSONNEL ONLY</div>', unsafe_allow_html=True)
        st.text_input("SENHA DE ACESSO", type="password", key="password_input", on_change=check_password)
    st.stop()

# --- 4. DADOS ---
def init_db():
    if 'agenda' not in st.session_state: st.session_state.agenda = pd.DataFrame(columns=['Data', 'Hora', 'Evento', 'Status'])
    if 'saude' not in st.session_state: st.session_state.saude = {'agua_copos': 0, 'comida_ok': False, 'meds_tomados': False}
    if 'dados_kombi' not in st.session_state: st.session_state.dados_kombi = {'km_atual': 150000, 'km_oleo': 145000, 'consumo_medio': 9.0}
    if 'financas' not in st.session_state: st.session_state.financas = pd.DataFrame(columns=['Data', 'Descricao', 'Valor', 'Tipo'])
    if 'inventario' not in st.session_state: st.session_state.inventario = pd.DataFrame(columns=['Item', 'Local', 'Qtd', 'Setor'])
    
    cols_rota = ['Origem', 'Destino', 'Km', 'Custo_Est', 'Status']
    if 'roteiros' not in st.session_state:
        st.session_state.roteiros = pd.DataFrame(columns=cols_rota)
    else:
        if 'Origem' not in st.session_state.roteiros.columns:
            st.session_state.roteiros = pd.DataFrame(columns=cols_rota)

    if 'escort_chat' not in st.session_state: st.session_state.escort_chat = []
init_db()

# --- LISTA MESTRA DE CATEGORIAS ---
CATEGORIAS = [
    "GASTO: TECNOLOGIA/PESSOAL 💻",
    "GASTO: FERRAMENTA OURIVESARIA 💍", 
    "GASTO: FERRAMENTA MECÂNICA 🔧",
    "GASTO: PEÇA KOMBI 🚐", 
    "GASTO: SOLAR/CASA ⚡", 
    "GASTO: VIDA (ALIMENTAÇÃO/OUTROS) 🍔", 
    "GASTO: VIAGEM (GASOLINA/PEDÁGIO) ⛽",
    "RECEITA: VENDA/SERVIÇO 💰"
]

# --- 5. LÓGICA INTELIGENTE ---
def processar_dado(desc, valor, tipo, is_legacy):
    if not is_legacy:
        val_float = float(valor)
        novo_fin = pd.DataFrame({'Data': [date.today()], 'Descricao': [desc], 'Valor': [val_float], 'Tipo': [tipo]})
        st.session_state.financas = pd.concat([st.session_state.financas, novo_fin], ignore_index=True)
    
    # Roteador de Pastas (Define para onde vai)
    if "FERRAMENTA" in tipo or "PEÇA" in tipo or "TECNOLOGIA" in tipo or "SOLAR" in tipo:
        if "OURIVES" in tipo: setor = "JOALHERIA"
        elif "MECÂNICA" in tipo or "KOMBI" in tipo: setor = "MECÂNICA"
        elif "TECNOLOGIA" in tipo: setor = "PESSOAL"
        elif "SOLAR" in tipo: setor = "CASA/SOLAR"
        else: setor = "GERAL" 
        
        novo_inv = pd.DataFrame({'Item': [desc], 'Local': ['A Classificar'], 'Qtd': [1], 'Setor': [setor]})
        st.session_state.inventario = pd.concat([st.session_state.inventario, novo_inv], ignore_index=True)
        
        if is_legacy: return f"📦 {desc} guardado na pasta {setor}."
        return f"✅ {desc} comprado e enviado para {setor}!"
    return "✅ Registrado no Financeiro."

# --- 6. HEADER ---
st.markdown('<div class="header-title">FAB\'S LAB.</div>', unsafe_allow_html=True)
st.markdown('<div class="header-sub">VW KOMBI 1.4 • RAPID FIRE V29</div>', unsafe_allow_html=True)

# HUD
c1, c2, c3 = st.columns(3)
with c1: 
    hoje = date.today()
    if not st.session_state.agenda.empty:
        st.session_state.agenda['Data'] = pd.to_datetime(st.session_state.agenda['Data']).dt.date
        ag = st.session_state.agenda[(st.session_state.agenda['Data'] == hoje) & (st.session_state.agenda['Status'] == 'Pendente')]
        if not ag.empty: st.error(f"📅 {len(ag)} TAREFAS HOJE")
        else: st.success("LIVRE HOJE")
    else: st.success("LIVRE HOJE")
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
abas = st.tabs(["⚡ AÇÃO", "💰 COFRE", "⚒️ ARSENAL", "📅 AGENDA", "🚐 KOMBI", "🌎 ROTA", "🐴 ESCORT", "📁 DOCS"])

# --- ABA 1: AÇÃO (COM AUTO-LIMPEZA) ---
with abas[0]:
    st.markdown("### ⚡ LANÇAMENTO TÁTICO")
    st.caption("Escolha a categoria para enviar o item para a pasta correta.")
    
    # AQUI ESTÁ A MÁGICA: clear_on_submit=True
    with st.form("smart", clear_on_submit=True):
        c1, c2 = st.columns([2, 1])
        d = c1.text_input("Descrição do Item/Evento")
        v = c2.number_input("Valor (R$)", 0.0)
        
        t = st.selectbox("Onde devo guardar isso?", CATEGORIAS)
        
        is_legacy = st.checkbox("Já possuo este item (Apenas Inventário / Sem Gasto)")
        
        if st.form_submit_button("LANÇAR"):
            if "RECEITA" in t: pass 
            msg = processar_dado(d, v, t, is_legacy)
            st.success(msg)
            # O rerun não é estritamente necessário com clear_on_submit para limpar, 
            # mas ajuda a atualizar os contadores do HUD lá em cima.
            st.rerun()

# --- ABA 2: COFRE ---
with abas[1]:
    st.markdown("### 💰 FLUXO DE CAIXA")
    if not st.session_state.financas.empty:
        try:
            receitas = st.session_state.financas[st.session_state.financas['Tipo'].str.contains("RECEITA", na=False)]['Valor'].sum()
            despesas = st.session_state.financas[~st.session_state.financas['Tipo'].str.contains("RECEITA", na=False)]['Valor'].sum()
            saldo = receitas - despesas
            c_sal1, c_sal2, c_sal3 = st.columns(3)
            c_sal1.metric("Entradas", f"R$ {receitas:,.2f}")
            c_sal2.metric("Saídas", f"R$ {despesas:,.2f}")
            c_sal3.metric("Saldo Atual", f"R$ {saldo:,.2f}", delta=saldo)
            
            st.markdown("#### 📝 REGISTROS (Edite a Categoria direto aqui 👇)")










