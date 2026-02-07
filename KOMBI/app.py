import streamlit as st
import pandas as pd
from datetime import date, datetime, time
import os
import urllib.parse

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="FAB'S LAB.", page_icon="☣️", layout="wide", initial_sidebar_state="collapsed")
PASTA_DOCS = "meus_documentos"
if not os.path.exists(PASTA_DOCS): os.makedirs(PASTA_DOCS)

# --- 2. ESTÉTICA CYBERPUNK MAKER (CSS V32) ---
st.markdown("""
    <style>
    /* IMPORTANDO FONTES FUTURISTAS */
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Share+Tech+Mono&display=swap');

    /* FUNDO GERAL - PRETO ABSOLUTO */
    .stApp { 
        background-color: #000000; 
        color: #e0e0e0;
        font-family: 'Share Tech Mono', monospace; /* Fonte padrão terminal */
    }

    /* TÍTULO PRINCIPAL COM GLOW */
    .header-title { 
        font-family: 'Orbitron', sans-serif; 
        font-size: 55px; 
        font-weight: 900;
        color: #fff;
        text-align: center; 
        margin: 0; 
        letter-spacing: 4px;
        text-shadow: 0 0 10px #00ff41, 0 0 20px #00ff41; /* NEON VERDE */
    }

    /* SUBTÍTULO TÉCNICO */
    .header-sub { 
        font-family: 'Share Tech Mono', monospace; 
        color: #ff0055; /* ROSA CYBER */
        text-align: center; 
        font-size: 14px; 
        border-bottom: 2px solid #333; 
        padding-bottom: 20px; 
        margin-bottom: 30px; 
        text-transform: uppercase; 
        letter-spacing: 3px; 
    }

    /* CARD DE CHAT (ESCORT) */
    .escort-card { 
        border: 1px solid #333;
        border-left: 5px solid #ff0055; 
        background-color: #0a0a0a; 
        padding: 15px; 
        margin-bottom: 15px; 
        font-family: 'Share Tech Mono', monospace;
    }

    /* BOTÕES (ESTILO INDUSTRIAL) */
    .stButton > button { 
        border: 2px solid #00ff41; /* Borda Verde */
        color: #00ff41; 
        background: transparent; 
        font-family: 'Orbitron', sans-serif; 
        font-size: 18px; 
        text-transform: uppercase;
        width: 100%; 
        transition: 0.3s; 
        border-radius: 0px; /* Cantos quadrados */
    }
    .stButton > button:hover { 
        background: #00ff41; 
        color: #000; 
        box-shadow: 0 0 15px #00ff41; /* Glow no hover */
        border-color: #00ff41;
    }

    /* INPUTS DE TEXTO (ESTILO TERMINAL) */
    .stTextInput > div > div > input { 
        background-color: #050505; 
        color: #00ff41; /* Texto verde terminal */
        border: 1px solid #333; 
        border-radius: 0px;
        font-family: 'Share Tech Mono', monospace;
    }
    .stTextInput > div > div > input:focus { 
        border-color: #ff0055 !important; /* Foco Rosa */
        box-shadow: 0 0 10px #ff0055 !important;
    }
    
    /* NUMBER INPUT & SELECTBOX */
    .stNumberInput > div > div > input { background-color: #050505; color: #00ff41; border: 1px solid #333; border-radius: 0px; font-family: 'Share Tech Mono', monospace; }
    .stSelectbox > div > div { background-color: #050505; color: #fff; border: 1px solid #333; border-radius: 0px; font-family: 'Share Tech Mono', monospace; }

    /* ABAS (TABS) */
    .stTabs [data-baseweb="tab-list"] { gap: 5px; }
    .stTabs [data-baseweb="tab"] { 
        height: 45px; 
        background-color: #111; 
        border-radius: 0px; 
        color: #666; 
        border: 1px solid #222; 
        font-family: 'Orbitron', sans-serif;
        font-size: 14px;
    }
    .stTabs [aria-selected="true"] { 
        background-color: #ff0055; 
        color: #000; 
        border: 1px solid #ff0055;
        font-weight: bold;
        box-shadow: 0 0 10px #ff0055;
    }

    /* TOAST (MENSAGENS) */
    div[data-baseweb="toast"] {
        background-color: #000 !important;
        border: 1px solid #00ff41 !important;
        color: #00ff41 !important;
        font-family: 'Share Tech Mono', monospace;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SEGURANÇA BLINDADA ---
if 'authenticated' not in st.session_state: st.session_state.authenticated = False
def check_password():
    if st.session_state.password_input == "Iron6Maiden7":
        st.session_state.authenticated = True
        del st.session_state.password_input
    else: st.error("⛔ ACCESS DENIED")
if not st.session_state.authenticated:
    st.markdown("<br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown('<div class="header-title">FAB\'S LAB.</div>', unsafe_allow_html=True)
        st.markdown('<div class="header-sub">SYSTEM LOCKED • ENTER PASSPHRASE</div>', unsafe_allow_html=True)
        st.text_input("TERMINAL ACCESS", type="password", key="password_input", on_change=check_password)
    st.stop()

# --- 4. DADOS ---
def init_db():
    if 'agenda' not in st.session_state: st.session_state.agenda = pd.DataFrame(columns=['Data', 'Hora', 'Evento', 'Status'])
    if 'saude' not in st.session_state: st.session_state.saude = {'agua_copos': 0, 'comida_ok': False, 'meds_tomados': False}
    if 'dados_kombi' not in st.session_state: st.session_state.dados_kombi = {'km_atual': 150000, 'km_oleo': 145000, 'consumo_medio': 9.0}
    if 'financas' not in st.session_state: st.session_state.financas = pd.DataFrame(columns=['Data', 'Descricao', 'Valor', 'Tipo'])
    if 'inventario' not in st.session_state: st.session_state.inventario = pd.DataFrame(columns=['Item', 'Local', 'Qtd', 'Setor'])
    
    cols_rota = ['Origem', 'Destino', 'Km', 'Custo_Est', 'Status']
    if 'roteiros' not in st.session_state: st.session_state.roteiros = pd.DataFrame(columns=cols_rota)
    else:
        if 'Origem' not in st.session_state.roteiros.columns:
            st.session_state.roteiros = pd.DataFrame(columns=cols_rota)

    if 'escort_chat' not in st.session_state: st.session_state.escort_chat = []
init_db()

CATEGORIAS = [
    "GASTO: TECNOLOGIA (Drone/PC/Câmera) 💻",
    "GASTO: OURIVESARIA (Ferramentas/Metais) 💍", 
    "GASTO: OFICINA (Ferramenta Mecânica) 🔧",
    "GASTO: PEÇA KOMBI/SOLAR (Peças/Baterias) 🚐", 
    "GASTO: PESSOAL (Roupas/Cuidados) 🎒",
    "GASTO: VIDA (Alimentação/Mercado) 🍔", 
    "GASTO: VIAGEM (Gasolina/Pedágio) ⛽",
    "RECEITA: VENDA/SERVIÇO 💰"
]

# --- 5. LÓGICA ---
def processar_dado(desc, valor, tipo, is_legacy):
    if not is_legacy:
        val_float = float(valor)
        novo_fin = pd.DataFrame({'Data': [date.today()], 'Descricao': [desc], 'Valor': [val_float], 'Tipo': [tipo]})
        st.session_state.financas = pd.concat([st.session_state.financas, novo_fin], ignore_index=True)
    
    setor = None
    if "OURIVESARIA" in tipo: setor = "OURIVESARIA"
    elif "OFICINA" in tipo: setor = "OFICINA"
    elif "KOMBI" in tipo or "SOLAR" in tipo: setor = "KOMBI"
    elif "TECNOLOGIA" in tipo: setor = "TECNOLOGIA"
    elif "PESSOAL" in tipo: setor = "PESSOAL"
    
    if setor:
        novo_inv = pd.DataFrame({'Item': [desc], 'Local': ['A Classificar'], 'Qtd': [1], 'Setor': [setor]})
        st.session_state.inventario = pd.concat([st.session_state.inventario, novo_inv], ignore_index=True)
        if is_legacy: return f"📦 {desc} >> {setor} (STORED)"
        return f"✅ {desc} >> {setor} (ACQUIRED)"
    return "✅ FINANCE LOG UPDATED"

# --- 6. HEADER ---
st.markdown('<div class="header-title">FAB\'S LAB.</div>', unsafe_allow_html=True)
st.markdown('<div class="header-sub">CYBER-OFFICE V32 • ONLINE</div>', unsafe_allow_html=True)

# HUD
c1, c2, c3 = st.columns(3)
with c1: 
    hoje = date.today()
    if not st.session_state.agenda.empty:
        try: st.session_state.agenda['Data'] = pd.to_datetime(st.session_state.agenda['Data']).dt.date
        except: pass
        ag = st.session_state.agenda[(st.session_state.agenda['Data'] == hoje) & (st.session_state.agenda['Status'] == 'Pendente')]
        if not ag.empty: st.error(f"⚠️ {len(ag)} MISSIONS PENDING")
        else: st.success("🟢 SYSTEM CLEAR")
    else: st.success("🟢 SYSTEM CLEAR")
with c2:
    km_rest = (st.session_state.dados_kombi['km_oleo'] + 5000) - st.session_state.dados_kombi['km_atual']
    if km_rest < 0: st.error(f"🔧 OIL CRITICAL")
    else: st.info(f"ENGINE OK ({km_rest}km)")
with c3:
    if not st.session_state.saude['comida_ok']: st.warning("🍎 LOW ENERGY")
    elif not st.session_state.saude['meds_tomados']: st.warning("💊 MEDS REQUIRED")
    else: st.success("🟢 BIO-SIGNS NORMAL")

st.markdown("---")

# ABAS
abas = st.tabs(["⚡ INPUT", "💰 CREDIT", "⚒️ ARSENAL", "📅 OPS", "🚐 MECH", "🌎 NAV", "🐴 AI-LINK", "📁 DATA"])

# --- ABA 1: AÇÃO ---
with abas[0]:
    st.markdown("### ⚡ QUICK INPUT")
    with st.form("smart", clear_on_submit=True):
        c1, c2 = st.columns([2, 1])
        d = c1.text_input("DATA DESCRIPTION")
        v = c2.number_input("VALUE (R$)", 0.0)
        t = st.selectbox("TARGET SECTOR", CATEGORIAS)
        is_legacy = st.checkbox("INVENTORY ONLY (NO COST)")
        if st.form_submit_button("EXECUTE"):
            if d:
                if "RECEITA" in t: pass 
                msg = processar_dado(d, v, t, is_legacy)
                st.toast(msg, icon="💾")
                st.rerun()

# --- ABA 2: COFRE ---
with abas[1]:
    st.markdown("### 💰 CREDITS FLOW")
    if not st.session_state.financas.empty:
        try:
            receitas = st.session_state.financas[st.session_state.financas['Tipo'].str.contains("RECEITA", na=False)]['Valor'].sum()
            despesas = st.session_state.financas[~st.session_state.financas['Tipo'].str.contains("RECEITA", na=False)]['Valor'].sum()
            saldo = receitas - despesas
            
            c_sal1, c_sal2, c_sal3 = st.columns(3)
            c_sal1.metric("INFLOW", f"R$ {receitas:,.2f}")
            c_sal2.metric("OUTFLOW", f"R$ {despesas:,.2f}")
            c_sal3.metric("NET BALANCE", f"R$ {saldo:,.2f}", delta=saldo)
            
            st.markdown("#### 📝 TRANSACTION LOG")
            df_editado = st.data_editor(
                st.session_state.financas, num_rows="dynamic", use_container_width=True,
                column_config={
                    "Tipo": st.column_config.SelectboxColumn("Category", options=CATEGORIAS, required=True, width="medium"),
                    "Valor": st.column_config.NumberColumn("Value", format="R$ %.2f")
                }
            )
            if not df_editado.equals(st.session_state.financas):
                st.session_state.financas = df_editado
                st.rerun()
        except: st.error("DATA CORRUPTION DETECTED.")
    else: st.info("NO FINANCIAL DATA.")

# --- ABA 3: ARSENAL ---
with abas[2]:
    st.markdown("### ⚒️ INVENTORY MATRIX")
    sub_abas = st.tabs(["💍 JEWELRY", "🔧 WORKSHOP", "🚐 KOMBI/SOLAR", "💻 TECH", "🎒 PERSONAL"])
    setores_map = ["OURIVESARIA", "OFICINA", "KOMBI", "TECNOLOGIA", "PESSOAL"]
    if not st.session_state.inventario.empty:
        for i, setor_alvo in enumerate(setores_map):
            with sub_abas[i]:
                df_setor = st.session_state.inventario[st.session_state.inventario['Setor'] == setor_alvo]
                if not df_setor.empty:
                    df_setor_edit = st.data_editor(
                        df_setor, key=f"editor_{setor_alvo}", num_rows="dynamic", use_container_width=True,
                        column_config={"Setor": st.column_config.SelectboxColumn("Relocate", options=setores_map, required=True)}
                    )
                    if not df_setor_edit.equals(df_setor):
                        st.session_state.inventario.update(df_setor_edit)
                        st.rerun()
                else: st.info(f"SECTOR {setor_alvo} EMPTY.")
    else: st.info("INVENTORY EMPTY.")

# --- ABA 4: AGENDA ---
with abas[3]:
    st.markdown("### 📅 OPERATIONS")
    with st.expander("➕ NEW MISSION", expanded=False):
        with st.form("nova_missao", clear_on_submit=True):
            c_data, c_hora = st.columns(2)
            data_task = c_data.date_input("Date", date.today())
            hora_task = c_hora.time_input("Time", time(9, 0))
            task_desc = st.text_input("Mission Objective")
            if st.form_submit_button("CONFIRM"):
                n = pd.DataFrame({'Data': [data_task], 'Hora': [hora_task.strftime('%H:%M')], 'Evento': [task_desc], 'Status': ['Pendente']})
                st.session_state.agenda = pd.concat([st.session_state.agenda, n], ignore_index=True)
                st.toast("MISSION ADDED", icon="📅")
                st.rerun()
    if not st.session_state.agenda.empty:
        df_agenda = st.session_state.agenda.sort_values(by=['Data', 'Hora'])
        for i, row in df_agenda.iterrows():
            if row['Status'] == 'Pendente':
                if st.checkbox(f"{row['Data']} | {row['Evento']}", key=f"t_{i}"):
                    st.session_state.agenda.at[i, 'Status'] = 'Concluído'
                    st.rerun()

# --- ABA 5: KOMBI ---
with abas[4]:
    st.markdown("### 🚐 UNIT TELEMETRY")
    col_mec, col_elet = st.columns(2)
    with col_mec:
        st.markdown("#### 🔧 MECHANICAL")
        st.info("🔋 STARTER: **JÚPITER 60Ah**")
        km = st.number_input("ODOMETER", value=st.session_state.dados_kombi['km_atual'])
        if km != st.session_state.dados_kombi['km_atual']:
            st.session_state.dados_kombi['km_atual'] = km
            st.rerun()
        km_rest = (st.session_state.dados_kombi['km_oleo'] + 5000) - km
        if km_rest < 0: st.error(f"OIL CRITICAL ({abs(km_rest)}km)")
        else: st.success(f"OIL LIFE: {km_rest}km")
        if st.button("RESET OIL TIMER"):
            st.session_state.dados_kombi['km_oleo'] = km
            processar_dado("Troca Óleo", 250, "GASTO: PEÇA KOMBI", False)
            st.rerun()
    with col_elet:
        st.markdown("#### ⚡ POWER GRID")
        st.warning("🔋 DEEP CYCLE: **FREEDOM 115Ah**")
        st.text_area("POWER LOG", height=150)

# --- ABA 6: ROTA ---
with abas[5]:
    st.markdown("### 🌎 NAVIGATION")
    with st.expander("➕ PLOT COURSE", expanded=True):
        with st.form("nova_rota", clear_on_submit=True):
            c1, c2 = st.columns(2)
            origem = c1.text_input("Origin")
            destino = c2.text_input("Destination")
            km_rota = st.number_input("Distance (Km)", min_value=1)
            
            if st.form_submit_button("ENGAGE"):
                custo_est = (km_rota / 9.0) * 6.10
                novo_roteiro = pd.DataFrame([{
                    'Origem': origem, 'Destino': destino, 'Km': km_rota,
                    'Custo_Est': custo_est, 'Status': "Planejado"
                }])
                st.session_state.roteiros = pd.concat([st.session_state.roteiros, novo_roteiro], ignore_index=True)
                st.toast("COURSE PLOTTED", icon="🛰️")
                st.rerun()

    if not st.session_state.roteiros.empty:
        st.markdown("#### 🗺️ TACTICAL MAP")
        df_display = st.session_state.roteiros.copy()
        try:
            df_display["Navegar"] = df_display.apply(lambda x: f"https://www.google.com/maps/dir/?api=1&origin={urllib.parse.quote(x['Origem'])}&destination={urllib.parse.quote(x['Destino'])}", axis=1)
            st.data_editor(
                df_display, num_rows="dynamic", use_container_width=True,
                column_config={
                    "Navegar": st.column_config.LinkColumn("Uplink", display_text="🗺️ GO"),
                    "Custo_Est": st.column_config.NumberColumn("Est. Cost", format="R$ %.2f"),
                    "Status": st.column_config.SelectboxColumn("Status", options=["Planejado", "Em Rota", "Concluído"])
                }
            )
        except: st.error("LINK ERROR.")
    else: st.info("NO ACTIVE ROUTES.")

# --- ABA 7: ESCORT ---
with abas[6]:
    c_esc1, c_esc2 = st.columns([2, 1])
    with c_esc1:
        if st.session_state.escort_chat:
            for msg in st.session_state.escort_chat:
                role = "FABI" if msg["role"] == "user" else "BIFÃO"
                cor = "#D32F2F" if role != "FABI" else "#00ff41"
                st.markdown(f"""<div class="escort-card" style="border-left-color:{cor}; color: {cor};"><small>{role}</small><br>{msg['content']}</div>""", unsafe_allow_html=True)
        user_input = st.chat_input("CMD...")
        if user_input:
            st.session_state.escort_chat.append({"role": "user", "content": user_input})
            st.session_state.escort_chat.append({"role": "assistant", "content": "COPY."})
            st.rerun()
    with c_esc2:
        st.success("🟢 LINK ESTABLISHED")
        st.link_button("GEMINI MAIN ☁️", "https://gemini.google.com/")

# --- ABA 8: DOCS ---
with abas[7]:
    up = st.file_uploader("UPLOAD DATA", type=['pdf', 'jpg'])
    if up:
        with open(os.path.join(PASTA_DOCS, up.name), "wb") as f: f.write(up.getbuffer())
        st.success("FILE SECURED")
    if os.path.exists(PASTA_DOCS):
        for arq in os.listdir(PASTA_DOCS): st.markdown(f"📄 {arq}")
