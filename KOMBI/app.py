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
    
    /* LOGIN SCREEN */
    .login-box { border: 1px solid #D32F2F; padding: 40px; border-radius: 10px; text-align: center; margin-top: 50px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SISTEMA DE SEGURANÇA (O PORTEIRO) ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

def check_password():
    # --- SUA SENHA AQUI ---
    if st.session_state.password_input == "Iron6Maiden7":
        st.session_state.authenticated = True
        del st.session_state.password_input
    else:
        st.error("⛔ ACESSO NEGADO: Senha Incorreta")

if not st.session_state.authenticated:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown('<div class="header-title">FAB\'S LAB.</div>', unsafe_allow_html=True)
        st.markdown('<div class="header-sub">RESTRICTED AREA • AUTHORIZED PERSONNEL ONLY</div>', unsafe_allow_html=True)
        st.text_input("SENHA DE ACESSO", type="password", key="password_input", on_change=check_password)
        st.caption("Dica: fabslab2026")
    st.stop() # PÁRA TUDO AQUI SE NÃO TIVER SENHA

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

# --- 5. LÓGICA INTELIGENTE ---
def processar_dado(desc, valor, tipo):
    # Lança Gasto
    novo_fin = pd.DataFrame({'Data': [date.today()], 'Descricao': [desc], 'Valor': [valor], 'Tipo': [tipo]})
    st.session_state.financas = pd.concat([st.session_state.financas, novo_fin], ignore_index=True)
    
    # Lança Item no Inventário (Incluindo Pessoal/Tech)
    if "FERRAMENTA" in tipo or "PEÇA" in tipo or "TECNOLOGIA" in tipo:
        if "OURIVES" in tipo: setor = "JOALHERIA"
        elif "MECÂNICA" in tipo or "KOMBI" in tipo: setor = "MECÂNICA"
        elif "TECNOLOGIA" in tipo: setor = "PESSOAL" # NOVA CATEGORIA
        else: setor = "GERAL"
            
        novo_inv = pd.DataFrame({'Item': [desc], 'Local': ['A Classificar'], 'Qtd': [1], 'Setor': [setor]})
        st.session_state.inventario = pd.concat([st.session_state.inventario, novo_inv], ignore_index=True)
        return f"✅ {desc} adicionado ao Arsenal ({setor})!"
        
    return "✅ Gasto Registrado."

# --- 6. HEADER (SÓ APARECE SE TIVER SENHA) ---
st.markdown('<div class="header-title">FAB\'S LAB.</div>', unsafe_allow_html=True)
st.markdown('<div class="header-sub">VW KOMBI 1.4 • SECURE SYSTEM V20</div>', unsafe_allow_html=True)

# HUD
c1, c2, c3 = st.columns(3)
with c1: 
    hoje = date.today()
    ag = st.session_state.agenda[(st.session_state.agenda['Data'] == hoje) & (st.session_state.agenda['Status'] == 'Pendente')]
    if not ag.empty: st.error(f"📅 {len(ag)} TAREFAS")
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
abas = st.tabs(["⚡ AÇÃO", "⚒️ ARSENAL", "🐴 ESCORT", "🔋 ENERGIA", "📅 AGENDA", "💰 COFRE", "📁 DOCS", "🌎 ROTA"])

# --- ABA 1: AÇÃO RÁPIDA ---
with abas[0]:
    st.markdown("### ⚡ LANÇAMENTO TÁTICO")
    with st.form("smart"):
        c1, c2 = st.columns([2, 1])
        d = c1.text_input("Descrição (Ex: MacBook, Drone, Alicate)")
        v = c2.number_input("Valor (R$)", 0.0)
        
        # CATEGORIAS ATUALIZADAS
        t = st.selectbox("Categoria", [
            "GASTO: TECNOLOGIA/PESSOAL 💻", # NOVO!
            "GASTO: FERRAMENTA OURIVESARIA 💍", 
            "GASTO: FERRAMENTA MECÂNICA 🔧",
            "GASTO: PEÇA KOMBI 🚐", 
            "GASTO: SOLAR/CASA ⚡", 
            "GASTO: VIDA 🍔", 
            "GASTO: VIAGEM ⛽", 
            "AGENDA: EVENTO 📅"
        ])
        
        if st.form_submit_button("EXECUTAR"):
            if "AGENDA" in t:
                n = pd.DataFrame({'Data': [date.today()], 'Hora': ['09:00'], 'Evento': [d], 'Status': ['Pendente']})
                st.session_state.agenda = pd.concat([st.session_state.agenda, n], ignore_index=True)
                st.success("Agendado")
            else:
                msg = processar_dado(d, v, t)
                st.success(msg)
            st.rerun()

# --- ABA 2: ARSENAL (3 COLUNAS AGORA) ---
with abas[1]:
    st.markdown("### ⚒️ ARSENAL MAKER & PESSOAL")
    
    col_pes, col_joia, col_mec = st.columns(3)
    
    with col_pes:
        st.markdown("#### 💻 PESSOAL/TECH")
        if not st.session_state.inventario.empty:
            df_pes = st.session_state.inventario[st.session_state.inventario['Setor'] == 'PESSOAL']
            if not df_pes.empty:
                st.dataframe(df_pes[['Item', 'Local']], use_container_width=True, hide_index=True)
            else: st.info("Vazio.")
        else: st.info("Vazio.")

    with col_joia:
        st.markdown("#### 💎 ATELIÊ")
        if not st.session_state.inventario.empty:
            df_joia = st.session_state.inventario[st.session_state.inventario['Setor'] == 'JOALHERIA']
            if not df_joia.empty:
                st.dataframe(df_joia[['Item', 'Local']], use_container_width=True, hide_index=True)
            else: st.info("Vazio.")
        else: st.info("Vazio.")

    with col_mec:
        st.markdown("#### 🔧 OFICINA")
        if not st.session_state.inventario.empty:
            df_mec = st.session_state.inventario[st.session_state.inventario['Setor'] == 'MECÂNICA']
            if not df_mec.empty:
                st.dataframe(df_mec[['Item', 'Local']], use_container_width=True, hide_index=True)
            else: st.info("Vazio.")
        else: st.info("Vazio.")

# --- ABA 3: ESCORT ---
with abas[2]:
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
            st.session_state.escort_chat.append({"role": "assistant", "content": "Cópia. Registrado."})
            st.rerun()
    with c_esc2:
        st.markdown("### 🛡️ STATUS")
        st.success("🟢 ONLINE")
        st.info("🔒 PROTEGIDO")
        st.link_button("GEMINI CLOUD ☁️", "https://gemini.google.com/")

# --- ABA 4: ENERGIA & MECÂNICA ---
with abas[3]:
    col_carro, col_casa = st.columns(2)
    with col_carro:
        st.markdown("### 🚐 MOTOR")
        st.info("🔋 ARRANQUE: **JÚPITER 60Ah**")
        km = st.number_input("KM Painel", value=st.session_state.dados_kombi['km_atual'])
        if km != st.session_state.dados_kombi['km_atual']:
            st.session_state.dados_kombi['km_atual'] = km
            st.rerun()
        km_rest = (st.session_state.dados_kombi['km_oleo'] + 5000) - km
        if km_rest < 0: st.error(f"TROCA URGENTE ({abs(km_rest)}km)")
        else: st.success(f"Óleo: {km_rest}km restantes")
        if st.button("ZERAR ÓLEO"):
            st.session_state.dados_kombi['km_oleo'] = km
            processar_dado("Troca Óleo", 250, "GASTO: PEÇA KOMBI")
            st.rerun()
    with col_casa:
        st.markdown("### ⚡ CASA")
        st.warning("🔋 ESTACIONÁRIA: **FREEDOM 115Ah**")
        st.text_area("Log Elétrica", height=100)

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
        for arq in os.listdir(PASTA_DOCS): st.markdown(f"📄 {arq}")

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
            st.rerun()
        st.dataframe(st.session_state.roteiros, use_container_width=True)
        

