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
    
    # Roteiros (Correção V26 mantida)
    cols_rota = ['Origem', 'Destino', 'Km', 'Custo_Est', 'Status']
    if 'roteiros' not in st.session_state: st.session_state.roteiros = pd.DataFrame(columns=cols_rota)
    else:
        if 'Origem' not in st.session_state.roteiros.columns: st.session_state.roteiros = pd.DataFrame(columns=cols_rota)

    if 'escort_chat' not in st.session_state: st.session_state.escort_chat = []
init_db()

# --- 5. LÓGICA INTELIGENTE ---
def processar_dado(desc, valor, tipo, is_legacy):
    if not is_legacy:
        val_float = float(valor)
        novo_fin = pd.DataFrame({'Data': [date.today()], 'Descricao': [desc], 'Valor': [val_float], 'Tipo': [tipo]})
        st.session_state.financas = pd.concat([st.session_state.financas, novo_fin], ignore_index=True)
    
    # Lógica de Setorização Aprimorada
    if "FERRAMENTA" in tipo or "PEÇA" in tipo or "TECNOLOGIA" in tipo or "SOLAR" in tipo:
        setor = "GERAL"
        if "OURIVES" in tipo: setor = "JOALHERIA"
        elif "MECÂNICA" in tipo or "KOMBI" in tipo: setor = "MECÂNICA"
        elif "TECNOLOGIA" in tipo or "PESSOAL" in tipo: setor = "PESSOAL"
        elif "SOLAR" in tipo or "CASA" in tipo: setor = "CASA"
            
        novo_inv = pd.DataFrame({'Item': [desc], 'Local': ['A Classificar'], 'Qtd': [1], 'Setor': [setor]})
        st.session_state.inventario = pd.concat([st.session_state.inventario, novo_inv], ignore_index=True)
        if is_legacy: return f"📦 {desc} cadastrado em {setor} (Sem custo)."
        return f"✅ {desc} comprado p/ {setor}!"
    return "✅ Registrado."

# --- 6. HEADER ---
st.markdown('<div class="header-title">FAB\'S LAB.</div>', unsafe_allow_html=True)
st.markdown('<div class="header-sub">VW KOMBI 1.4 • ARSENAL V27</div>', unsafe_allow_html=True)

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
abas = st.tabs(["⚡ AÇÃO", "⚒️ ARSENAL", "💰 COFRE", "📅 AGENDA", "🚐 KOMBI", "🌎 ROTA", "🐴 ESCORT", "📁 DOCS"])

# --- ABA 1: AÇÃO ---
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
        is_legacy = st.checkbox("Já possuo este item (Inventário / Sem Gasto)")
        if st.form_submit_button("EXECUTAR"):
            if "RECEITA" in t: pass 
            msg = processar_dado(d, v, t, is_legacy)
            st.success(msg)
            st.rerun()

# --- ABA 2: ARSENAL (CATEGORIZADO) ---
with abas[1]:
    st.markdown("### ⚒️ ARSENAL ESTRATÉGICO")
    
    if not st.session_state.inventario.empty:
        # Opções de Setor para edição
        setores_validos = ["JOALHERIA", "MECÂNICA", "PESSOAL", "CASA", "GERAL"]
        
        # Função helper para mostrar editor filtrado
        def mostrar_setor(nome_setor, emoji, filtro):
            st.markdown(f"#### {emoji} {nome_setor}")
            df_filt = st.session_state.inventario[st.session_state.inventario['Setor'] == filtro]
            
            # Mostra editor mesmo se vazio, para permitir adicionar linhas manuais se quiser no futuro
            if not df_filt.empty:
                st.dataframe(df_filt[['Item', 'Local', 'Qtd']], use_container_width=True, hide_index=True)
            else:
                st.caption("Nenhum item cadastrado neste setor.")

        # Exibição por Blocos (Expander para não poluir)
        with st.expander("💎 JOALHERIA (OURIVES)", expanded=True):
            mostrar_setor("ATELIÊ", "💍", "JOALHERIA")
            
        with st.expander("🔧 MECÂNICA (OFICINA)", expanded=False):
            mostrar_setor("GARAGEM", "🔧", "MECÂNICA")
            
        with st.expander("💻 PESSOAL & TECH", expanded=False):
            mostrar_setor("EQUIPAMENTOS", "💻", "PESSOAL")
            
        with st.expander("🏠 CASA & CAMPING", expanded=False):
            mostrar_setor("LOGÍSTICA", "⛺", "CASA")

        st.markdown("---")
        st.markdown("#### 📝 GERENCIADOR GERAL (Edite tudo aqui)")
        # Editor Mestre onde dá para trocar o setor
        df_inv_edit = st.data_editor(
            st.session_state.inventario, 
            num_rows="dynamic", 
            use_container_width=True,
            column_config={
                "Setor": st.column_config.SelectboxColumn(
                    "Setor (Categoria)",
                    help="Mude a categoria do item",
                    width="medium",
                    options=setores_validos,
                    required=True
                )
            }
        )
        if not df_inv_edit.equals(st.session_state.inventario):
            st.session_state.inventario = df_inv_edit
            st.rerun()

    else: st.info("Arsenal vazio. Adicione itens na aba AÇÃO.")

# --- ABA 3: COFRE ---
with abas[2]:
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
            st.markdown("#### 📝 REGISTROS")
            df_editado = st.data_editor(st.session_state.financas, num_rows="dynamic", use_container_width=True)
            if not df_editado.equals(st.session_state.financas):
                st.session_state.financas = df_editado
                st.rerun()
        except: st.error("Erro nos dados.")
    else: st.info("Cofre vazio.")

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

# --- ABA 5: KOMBI ---
with abas[4]:
    st.markdown("### 🚐 MÁQUINA DE GUERRA")
    col_mec, col_elet = st.columns(2)
    with col_mec:
        st.markdown("#### 🔧 MECÂNICA")
        st.info("🔋 PARTIDA: **JÚPITER 60Ah**")
        km = st.number_input("KM Painel", value=st.session_state.dados_kombi['km_atual'])
        if km != st.session_state.dados_kombi['km_atual']:
            st.session_state.dados_kombi['km_atual'] = km
            st.rerun()
        km_rest = (st.session_state.dados_kombi['km_oleo'] + 5000) - km
        if km_rest < 0: st.error(f"TROCA URGENTE ({abs(km_rest)}km)")
        else: st.success(f"Óleo: {km_rest}km restantes")
        if st.button("ZERAR ÓLEO"):
            st.session_state.dados_kombi['km_oleo'] = km
            processar_dado("Troca Óleo", 250, "GASTO: PEÇA KOMBI", False)
            st.rerun()
    with col_elet:
        st.markdown("#### ⚡ USINA (CASA)")
        st.warning("🔋 ESTACIONÁRIA: **FREEDOM 115Ah**")
        st.text_area("Log de Energia", height=150)

# --- ABA 6: ROTA ---
with abas[5]:
    st.markdown("### 🌎 LOGÍSTICA")
    with st.expander("➕ TRAÇAR NOVA ROTA", expanded=True):
        with st.form("nova_rota"):
            c1, c2 = st.columns(2)
            origem = c1.text_input("Origem")
            destino = c2.text_input("Destino")
            km_rota = st.number_input("Km", min_value=1)
            if origem and destino:
                st.link_button("🗺️ TESTAR NO MAPS", f"https://www.google.com/maps/dir/?api=1&origin={origem}&destination={destino}")
            custo_est = (km_rota / 9.0) * 6.10
            st.caption(f"Custo: R$ {custo_est:.2f}")
            status_rota = st.selectbox("Status", ["Planejado", "Em Rota", "Concluído"])
            if st.form_submit_button("REGISTRAR"):
                novo = pd.DataFrame([{'Origem': origem, 'Destino': destino, 'Km': km_rota, 'Custo_Est': custo_est, 'Status': status_rota}])
                st.session_state.roteiros = pd.concat([st.session_state.roteiros, novo], ignore_index=True)
                st.rerun()

    if not st.session_state.roteiros.empty:
        try:
            df_display = st.session_state.roteiros.copy()
            df_display["Navegar"] = df_display.apply(lambda x: f"https://www.google.com/maps/dir/?api=1&origin={x['Origem']}&destination={x['Destino']}", axis=1)
            st.data_editor(df_display, num_rows="dynamic", use_container_width=True, column_config={"Navegar": st.column_config.LinkColumn("Maps", display_text="🗺️ Ir")})
        except: st.write(st.session_state.roteiros)

# --- ABA 7: ESCORT ---
with abas[6]:
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

# --- ABA 8: DOCS ---
with abas[7]:
    up = st.file_uploader("Upload", type=['pdf', 'jpg'])
    if up:
        with open(os.path.join(PASTA_DOCS, up.name), "wb") as f: f.write(up.getbuffer())
        st.success("Salvo")
    if os.path.exists(PASTA_DOCS):
        for arq in os.listdir(PASTA_DOCS): st.markdown(f"📄 {arq}")







