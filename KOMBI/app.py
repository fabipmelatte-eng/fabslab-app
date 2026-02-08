import streamlit as st
import pandas as pd
from datetime import date, datetime, time, timedelta
import os
import urllib.parse

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(page_title="FAB'S LAB.", page_icon="🧬", layout="wide", initial_sidebar_state="collapsed")
PASTA_DOCS = "meus_documentos"
if not os.path.exists(PASTA_DOCS): os.makedirs(PASTA_DOCS)

# --- FUNÇÃO DE TEMPO (BRASIL UTC-3) ---
def get_fabi_time():
    # Pega a hora universal (UTC) e tira 3 horas
    return datetime.utcnow() - timedelta(hours=3)

def get_fabi_date():
    return get_fabi_time().date()

# --- 2. ESTILO CYBERPUNK REFINADO (V33/34) ---
st.markdown("""
    <style>
    /* FONTES: Rajdhani (Técnica e Legível) e Orbitron (Títulos) */
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;900&family=Rajdhani:wght@400;600;700&display=swap');

    .stApp { 
        background-color: #050505; 
        color: #e0e0e0;
        font-family: 'Rajdhani', sans-serif;
        font-size: 18px;
    }

    /* TÍTULO COM PONTO PISCANTE */
    .header-title { 
        font-family: 'Orbitron', sans-serif; 
        font-size: 60px; 
        font-weight: 900;
        color: #fff;
        text-align: center; 
        margin: 0; 
        letter-spacing: 2px;
        text-shadow: 0 0 10px rgba(48, 105, 152, 0.5); /* Glow Azul Python */
    }
    
    @keyframes blink { 50% { opacity: 0; } }
    .blink { animation: blink 1s linear infinite; color: #FFD43B; } /* Ponto Amarelo Python */

    .header-sub { 
        font-family: 'Rajdhani', sans-serif; 
        font-weight: 600;
        color: #888; 
        text-align: center; 
        font-size: 16px; 
        border-bottom: 1px solid #333; 
        padding-bottom: 20px; 
        margin-bottom: 30px; 
        text-transform: uppercase; 
        letter-spacing: 4px; 
    }

    /* BOTÕES (VERDE NEON E AZUL PYTHON NO HOVER) */
    .stButton > button { 
        border: 1px solid #333; 
        color: #ccc; 
        background: #0F0F0F; 
        font-family: 'Orbitron', sans-serif; 
        font-size: 16px; 
        border-radius: 4px;
        transition: 0.3s;
    }
    .stButton > button:hover { 
        border-color: #00ff41; 
        color: #000; 
        background: #00ff41; /* Verde Matrix */
        box-shadow: 0 0 15px rgba(0, 255, 65, 0.4);
    }

    /* INPUTS (SEM VERMELHO) */
    .stTextInput > div > div > input { 
        background-color: #0a0a0a; 
        color: #FFD43B; /* Texto Amarelo */
        border: 1px solid #333; 
        font-family: 'Rajdhani', sans-serif;
        font-size: 18px;
    }
    .stTextInput > div > div > input:focus { 
        border-color: #306998 !important; /* Azul Python */
        box-shadow: 0 0 10px rgba(48, 105, 152, 0.4) !important;
    }
    
    /* ABAS */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { 
        height: 45px; 
        background-color: #111; 
        border-radius: 4px; 
        color: #aaa; 
        border: 1px solid #222; 
        font-family: 'Orbitron', sans-serif;
        font-size: 14px;
    }
    .stTabs [aria-selected="true"] { 
        background-color: #306998; /* Azul Python */
        color: #fff; 
        border: 1px solid #306998;
    }

    /* KPIs (HUD) */
    div[data-testid="stMetricValue"] {
        font-family: 'Orbitron', sans-serif;
        font-size: 24px;
        color: #00ff41;
    }
    div[data-testid="stMetricLabel"] {
        font-family: 'Rajdhani', sans-serif;
        font-size: 14px;
        color: #888;
    }
    </style> 
    """, unsafe_allow_html=True)

# --- 3. SEGURANÇA ---
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
        st.markdown('<div class="header-title">FAB\'S LAB<span class="blink">.</span></div>', unsafe_allow_html=True)
        st.markdown('<div class="header-sub">DATABASE LOCKED</div>', unsafe_allow_html=True)
        st.text_input("PASSWORD", type="password", key="password_input", on_change=check_password)
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
        # USA DATA CORRIGIDA
        novo_fin = pd.DataFrame({'Data': [get_fabi_date()], 'Descricao': [desc], 'Valor': [val_float], 'Tipo': [tipo]})
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
        if is_legacy: return f"📦 {desc} >> {setor}"
        return f"✅ {desc} >> {setor}"
    return "✅ FINANCEIRO ATUALIZADO"

# --- 6. HEADER (HUD INTELIGENTE) ---
st.markdown('<div class="header-title">FAB\'S LAB<span class="blink">.</span></div>', unsafe_allow_html=True)
st.markdown('<div class="header-sub">DATABASE ONLINE • V34 (BRT TIME)</div>', unsafe_allow_html=True)

# CÁLCULOS DO HUD
saldo_atual = 0.0
if not st.session_state.financas.empty:
    try:
        r = st.session_state.financas[st.session_state.financas['Tipo'].str.contains("RECEITA", na=False)]['Valor'].sum()
        d = st.session_state.financas[~st.session_state.financas['Tipo'].str.contains("RECEITA", na=False)]['Valor'].sum()
        saldo_atual = r - d
    except: pass

prox_missao = "SEM MISSÕES"
hoje_br = get_fabi_date() # DATA CORRIGIDA

if not st.session_state.agenda.empty:
    try:
        st.session_state.agenda['Data'] = pd.to_datetime(st.session_state.agenda['Data']).dt.date
        df_pendente = st.session_state.agenda[st.session_state.agenda['Status'] == 'Pendente'].sort_values(by=['Data', 'Hora'])
        if not df_pendente.empty:
            prox = df_pendente.iloc[0]
            prox_missao = f"{prox['Evento']} ({prox['Data'].strftime('%d/%m')})"
    except: pass

# MOSTRADORES DO HUD
c1, c2, c3 = st.columns(3)
with c1: st.metric("PRÓXIMA MISSÃO", prox_missao)
with c2: st.metric("SALDO ATUAL", f"R$ {saldo_atual:,.2f}")
# HORA CORRIGIDA NO HUD
with c3: st.metric("DATA/HORA (BR)", get_fabi_time().strftime("%d/%m %H:%M"))

st.markdown("---")

# ABAS
abas = st.tabs(["⚡ INPUT", "💰 CAIXA", "⚒️ ARSENAL", "📅 AGENDA", "🚐 KOMBI", "🌎 ROTA", "🐴 AI-LINK", "📁 DOCS"])

# --- ABA 1: AÇÃO ---
with abas[0]:
    st.markdown("### ⚡ INPUT RÁPIDO")
    with st.form("smart", clear_on_submit=True):
        c1, c2 = st.columns([2, 1])
        d = c1.text_input("DESCRIÇÃO")
        v = c2.number_input("VALOR (R$)", 0.0)
        t = st.selectbox("CATEGORIA", CATEGORIAS)
        is_legacy = st.checkbox("ITEM JÁ EXISTENTE (SEM CUSTO)")
        if st.form_submit_button("PROCESSAR"):
            if d:
                msg = processar_dado(d, v, t, is_legacy)
                st.toast(msg, icon="✅")
                st.rerun()

# --- ABA 2: COFRE ---
with abas[1]:
    st.markdown("### 💰 FLUXO FINANCEIRO")
    if not st.session_state.financas.empty:
        try:
            df_editado = st.data_editor(
                st.session_state.financas, num_rows="dynamic", use_container_width=True,
                column_config={
                    "Tipo": st.column_config.SelectboxColumn("Categoria", options=CATEGORIAS, required=True, width="medium"),
                    "Valor": st.column_config.NumberColumn("Valor", format="R$ %.2f")
                }
            )
            if not df_editado.equals(st.session_state.financas):
                st.session_state.financas = df_editado
                st.rerun()
        except: st.error("Erro nos dados.")
    else: st.info("CAIXA VAZIO.")

# --- ABA 3: ARSENAL ---
with abas[2]:
    st.markdown("### ⚒️ INVENTÁRIO TÉCNICO")
    sub_abas = st.tabs(["💍 JOIAS", "🔧 OFICINA", "🚐 KOMBI", "💻 TECH", "🎒 PESSOAL"])
    setores_map = ["OURIVESARIA", "OFICINA", "KOMBI", "TECNOLOGIA", "PESSOAL"]
    if not st.session_state.inventario.empty:
        for i, setor_alvo in enumerate(setores_map):
            with sub_abas[i]:
                df_setor = st.session_state.inventario[st.session_state.inventario['Setor'] == setor_alvo]
                if not df_setor.empty:
                    df_setor_edit = st.data_editor(
                        df_setor, key=f"editor_{setor_alvo}", num_rows="dynamic", use_container_width=True,
                        column_config={"Setor": st.column_config.SelectboxColumn("Mover para", options=setores_map, required=True)}
                    )
                    if not df_setor_edit.equals(df_setor):
                        st.session_state.inventario.update(df_setor_edit)
                        st.rerun()
                else: st.info(f"GAVETA {setor_alvo} VAZIA.")
    else: st.info("INVENTÁRIO VAZIO.")

# --- ABA 4: AGENDA ---
with abas[3]:
    st.markdown("### 📅 CRONOGRAMA")
    with st.expander("➕ NOVA MISSÃO", expanded=False):
        with st.form("nova_missao", clear_on_submit=True):
            c_data, c_hora = st.columns(2)
            # DATA CORRIGIDA NO INPUT PADRÃO
            data_task = c_data.date_input("DATA", get_fabi_date())
            hora_task = c_hora.time_input("HORA", time(9, 0))
            task_desc = st.text_input("MISSÃO")
            if st.form_submit_button("AGENDAR"):
                n = pd.DataFrame({'Data': [data_task], 'Hora': [hora_task.strftime('%H:%M')], 'Evento': [task_desc], 'Status': ['Pendente']})
                st.session_state.agenda = pd.concat([st.session_state.agenda, n], ignore_index=True)
                st.toast("MISSÃO AGENDADA", icon="📅")
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
    st.markdown("### 🚐 TELEMETRIA")
    col_mec, col_elet = st.columns(2)
    with col_mec:
        st.markdown("#### 🔧 MECÂNICA")
        st.info("🔋 ARRANQUE: **JÚPITER 60Ah**")
        km = st.number_input("ODÔMETRO", value=st.session_state.dados_kombi['km_atual'])
        if km != st.session_state.dados_kombi['km_atual']:
            st.session_state.dados_kombi['km_atual'] = km
            st.rerun()
        km_rest = (st.session_state.dados_kombi['km_oleo'] + 5000) - km
        if km_rest < 0: st.error(f"TROCA URGENTE ({abs(km_rest)}km)")
        else: st.success(f"ÓLEO: {km_rest}km RESTANTES")
        if st.button("ZERAR ÓLEO"):
            st.session_state.dados_kombi['km_oleo'] = km
            processar_dado("Troca Óleo", 250, "GASTO: PEÇA KOMBI", False)
            st.rerun()
    with col_elet:
        st.markdown("#### ⚡ ENERGIA (CASA)")
        st.warning("🔋 ESTACIONÁRIA: **FREEDOM 115Ah**")
        st.text_area("DIÁRIO DE BORDO ELÉTRICO", height=150)

# --- ABA 6: ROTA ---
with abas[5]:
    st.markdown("### 🌎 NAVEGAÇÃO")
    with st.expander("➕ NOVA ROTA", expanded=True):
        with st.form("nova_rota", clear_on_submit=True):
            c1, c2 = st.columns(2)
            origem = c1.text_input("ORIGEM")
            destino = c2.text_input("DESTINO")
            km_rota = st.number_input("DISTÂNCIA (KM)", min_value=1)
            
            if st.form_submit_button("TRAÇAR ROTA"):
                custo_est = (km_rota / 9.0) * 6.10
                novo_roteiro = pd.DataFrame([{
                    'Origem': origem, 'Destino': destino, 'Km': km_rota,
                    'Custo_Est': custo_est, 'Status': "Planejado"
                }])
                st.session_state.roteiros = pd.concat([st.session_state.roteiros, novo_roteiro], ignore_index=True)
                st.toast("ROTA TRAÇADA", icon="🛰️")
                st.rerun()

    if not st.session_state.roteiros.empty:
        st.markdown("#### 🗺️ MAPA TÁTICO")
        df_display = st.session_state.roteiros.copy()
        try:
            df_display["Navegar"] = df_display.apply(lambda x: f"https://www.google.com/maps/dir/?api=1&origin={urllib.parse.quote(x['Origem'])}&destination={urllib.parse.quote(x['Destino'])}", axis=1)
            st.data_editor(
                df_display, num_rows="dynamic", use_container_width=True,
                column_config={
                    "Navegar": st.column_config.LinkColumn("Link", display_text="🗺️ IR"),
                    "Custo_Est": st.column_config.NumberColumn("Custo Est.", format="R$ %.2f"),
                    "Status": st.column_config.SelectboxColumn("Status", options=["Planejado", "Em Rota", "Concluído"])
                }
            )
        except: st.error("Erro no link.")
    else: st.info("SEM ROTAS ATIVAS.")

# --- ABA 7: ESCORT ---
with abas[6]:
    c_esc1, c_esc2 = st.columns([2, 1])
    with c_esc1:
        if st.session_state.escort_chat:
            for msg in st.session_state.escort_chat:
                role = "FABI" if msg["role"] == "user" else "BIFÃO"
                st.markdown(f"""<div style="background:#111; padding:10px; border-radius:4px; margin-bottom:5px; border-left: 3px solid #306998;"><small style="color:#888">{role}</small><br>{msg['content']}</div>""", unsafe_allow_html=True)
        user_input = st.chat_input("COMANDO...")
        if user_input:
            st.session_state.escort_chat.append({"role": "user", "content": user_input})
            st.session_state.escort_chat.append({"role": "assistant", "content": "COPIADO."})
            st.rerun()
    with c_esc2:
        st.success("🟢 ONLINE")
        st.link_button("GEMINI AI ☁️", "https://gemini.google.com/")

# --- ABA 8: DOCS ---
with abas[7]:
    up = st.file_uploader("UPLOAD ARQUIVO", type=['pdf', 'jpg'])
    if up:
        with open(os.path.join(PASTA_DOCS, up.name), "wb") as f: f.write(up.getbuffer())
        st.success("SALVO")
    if os.path.exists(PASTA_DOCS):
        for arq in os.listdir(PASTA_DOCS): st.markdown(f"📄 {arq}")
