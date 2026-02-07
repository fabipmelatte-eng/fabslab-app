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
    if 'roteiros' not in st.session_state: st.session_state.roteiros = pd.DataFrame(columns=['Destino', 'Pais', 'Status'])
    if 'escort_chat' not in st.session_state: st.session_state.escort_chat = []
init_db()

# --- 5. LÓGICA INTELIGENTE ---
def processar_dado(desc, valor, tipo, is_legacy):
    # Só lança no financeiro se NÃO for item antigo (legacy)
    if not is_legacy:
        # Garante que o valor é float para evitar erros de soma
        val_float = float(valor)
        novo_fin = pd.DataFrame({'Data': [date.today()], 'Descricao': [desc], 'Valor': [val_float], 'Tipo': [tipo]})
        st.session_state.financas = pd.concat([st.session_state.financas, novo_fin], ignore_index=True)
    
    # Lança no Inventário
    if "FERRAMENTA" in tipo or "PEÇA" in tipo or "TECNOLOGIA" in tipo:
        if "OURIVES" in tipo: setor = "JOALHERIA"
        elif "MECÂNICA" in tipo or "KOMBI" in tipo: setor = "MECÂNICA"
        elif "TECNOLOGIA" in tipo: setor = "PESSOAL"
        else: setor = "GERAL" 
        novo_inv = pd.DataFrame({'Item': [desc], 'Local': ['A Classificar'], 'Qtd': [1], 'Setor': [setor]})
        st.session_state.inventario = pd.concat([st.session_state.inventario, novo_inv], ignore_index=True)
        
        if is_legacy: return f"📦 {desc} cadastrado no Inventário (Sem custo)."
        return f"✅ {desc} comprado e estocado!"
        
    return "✅ Transação Financeira Registrada."

# --- 6. HEADER ---
st.markdown('<div class="header-title">FAB\'S LAB.</div>', unsafe_allow_html=True)
st.markdown('<div class="header-sub">VW KOMBI 1.4 • SYSTEM V23 (STABLE)</div>', unsafe_allow_html=True)

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
abas = st.tabs(["⚡ AÇÃO", "💰 COFRE", "⚒️ ARSENAL", "📅 AGENDA", "🐴 ESCORT", "🔋 ENERGIA", "📁 DOCS", "🌎 ROTA"])

# --- ABA 1: AÇÃO RÁPIDA ---
with abas[0]:
    st.markdown("### ⚡ LANÇAMENTO TÁTICO")
    with st.form("smart"):
        c1, c2 = st.columns([2, 1])
        d = c1.text_input("Descrição")
        v = c2.number_input("Valor (R$)", 0.0)
        t = st.selectbox("Categoria", [
            "GASTO: TECNOLOGIA/PESSOAL 💻",
            "GASTO: FERRAMENTA OURIVESARIA 💍", 
            "GASTO: FERRAMENTA MECÂNICA 🔧",
            "GASTO: PEÇA KOMBI 🚐", 
            "GASTO: SOLAR/CASA ⚡", 
            "GASTO: VIDA 🍔", 
            "GASTO: VIAGEM ⛽",
            "RECEITA: VENDA/SERVIÇO 💰"
        ])
        
        is_legacy = st.checkbox("Já possuo este item (Apenas Inventário / Sem Gasto)")
        
        if st.form_submit_button("EXECUTAR"):
            if "RECEITA" in t: pass 
            msg = processar_dado(d, v, t, is_legacy)
            st.success(msg)
            st.rerun()

# --- ABA 2: COFRE (CORRIGIDO) ---
with abas[1]:
    st.markdown("### 💰 FLUXO DE CAIXA")
    
    if not st.session_state.financas.empty:
        # CORREÇÃO DO ERRO: Adicionado 'na=False' para ignorar linhas vazias/sujas
        try:
            receitas = st.session_state.financas[st.session_state.financas['Tipo'].str.contains("RECEITA", na=False)]['Valor'].sum()
            despesas = st.session_state.financas[~st.session_state.financas['Tipo'].str.contains("RECEITA", na=False)]['Valor'].sum()
            saldo = receitas - despesas
            
            c_sal1, c_sal2, c_sal3 = st.columns(3)
            c_sal1.metric("Entradas", f"R$ {receitas:,.2f}")
            c_sal2.metric("Saídas", f"R$ {despesas:,.2f}")
            c_sal3.metric("Saldo Atual", f"R$ {saldo:,.2f}", delta=saldo)
            
            st.markdown("#### 📝 REGISTROS (Edite direto na tabela)")
            df_editado = st.data_editor(st.session_state.financas, num_rows="dynamic", use_container_width=True)
            
            if not df_editado.equals(st.session_state.financas):
                st.session_state.financas = df_editado
                st.rerun()
        except Exception as e:
            st.error(f"Erro ao calcular: {e}")
            st.warning("Dica: Tente apagar as linhas vazias na tabela abaixo.")
            st.data_editor(st.session_state.financas, key="fin_error_edit", num_rows="dynamic")
    else:
        st.info("Cofre vazio.")

# --- ABA 3: ARSENAL ---
with abas[2]:
    st.markdown("### ⚒️ ARSENAL MAKER")
    if not st.session_state.inventario.empty:
        df_inv_edit = st.data_editor(st.session_state.inventario, num_rows="dynamic", use_container_width=True)
        if not df_inv_edit.equals(st.session_state.inventario):
            st.session_state.inventario = df_inv_edit
            st.rerun()
    else:
        st.info("Inventário vazio.")

# --- ABA 4: AGENDA ---
with abas[3]:
    st.markdown("### 📅 CRONOGRAMA")
    with st.expander("➕ NOVA MISSÃO", expanded=False):
        with st.form("nova_missao"):
            c_data, c_hora = st.columns(2)
            data_task = c_data.date_input("Data", date.today())
            hora_task = c_hora.time_input("Hora", time(9, 0))
            task_desc = st.text_input("Missão")
            if st.form_submit_button("AGENDAR"):
                n = pd.DataFrame({'Data': [data_task], 'Hora': [hora_task.strftime('%H:%M')], 'Evento': [task_desc], 'Status': ['Pendente']})
                st.session_state.agenda = pd.concat([st.session_state.agenda, n], ignore_index=True)
                st.rerun()

    if not st.session_state.agenda.empty:
        df_agenda = st.session_state.agenda.sort_values(by=['Data', 'Hora'])
        for i, row in df_agenda.iterrows():
            if row['Status'] == 'Pendente':
                if st.checkbox(f"{row['Data']} | {row['Evento']}", key=f"t_{i}"):
                    st.session_state.agenda.at[i, 'Status'] = 'Concluído'
                    st.rerun()

# --- ABA 5: ESCORT ---
with abas[4]:
    c_esc1, c_esc2 = st.columns([2, 1])
    with c_esc1:
        if st.session_state.escort_chat:
            for msg in st.session_state.escort_chat:
                role = "FABI" if msg["role"] == "user" else "BIFÃO"
                cor = "#D32F2F" if role != "FABI" else "#555"
                st.markdown(f"""<div class="escort-card" style="border-color:{cor};"><small>{role}</small><br>{msg['content']}</div>""", unsafe_allow_html=True)
        user_input = st.chat_input("Comando...")
        if user_input:
            st.session_state.escort_chat.append({"role": "user", "content": user_input})
            st.session_state.escort_chat.append({"role": "assistant", "content": "Cópia."})
            st.rerun()
    with c_esc2:
        st.success("🟢 ONLINE")
        st.link_button("GEMINI CLOUD ☁️", "https://gemini.google.com/")

# --- ABA 6: ENERGIA & MECÂNICA ---
with abas[5]:
    col_carro, col_casa = st.columns(2)
    with col_carro:
        st.info("🔋 ARRANQUE: **JÚPITER 60Ah**")
        km = st.number_input("KM Painel", value=st.session_state.dados_kombi['km_atual'])
        if km != st.session_state.dados_kombi['km_atual']:
            st.session_state.dados_kombi['km_atual'] = km
            st.rerun()
        if st.button("ZERAR ÓLEO"):
            st.session_state.dados_kombi['km_oleo'] = km
            processar_dado("Troca Óleo", 250, "GASTO: PEÇA KOMBI", False)
            st.rerun()
    with col_casa:
        st.warning("🔋 ESTACIONÁRIA: **FREEDOM 115Ah**")

# --- ABA 7: DOCS ---
with abas[6]:
    up = st.file_uploader("Upload", type=['pdf', 'jpg'])
    if up:
        with open(os.path.join(PASTA_DOCS, up.name), "wb") as f: f.write(up.getbuffer())
        st.success("Salvo")
    if os.path.exists(PASTA_DOCS):
        for arq in os.listdir(PASTA_DOCS): st.markdown(f"📄 {arq}")

# --- ABA 8: ROTA ---
with abas[7]:
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




