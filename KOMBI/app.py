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
    
    /* ABAS CUSTOMIZADAS */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; background-color: #111; border-radius: 5px; color: #888; }
    .stTabs [aria-selected="true"] { background-color: #D32F2F; color: white; }
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

# --- LISTA MESTRA DE CATEGORIAS (INPUT) ---
# Mapeamento claro para garantir que caia na pasta certa
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

# --- 5. LÓGICA INTELIGENTE (O ORGANIZADOR) ---
def processar_dado(desc, valor, tipo, is_legacy):
    # Lança no Financeiro (se não for item antigo)
    if not is_legacy:
        val_float = float(valor)
        novo_fin = pd.DataFrame({'Data': [date.today()], 'Descricao': [desc], 'Valor': [val_float], 'Tipo': [tipo]})
        st.session_state.financas = pd.concat([st.session_state.financas, novo_fin], ignore_index=True)
    
    # Roteador de Inventário (5 GAVETAS REAIS)
    setor = None
    if "OURIVESARIA" in tipo: setor = "OURIVESARIA"
    elif "OFICINA" in tipo: setor = "OFICINA"
    elif "KOMBI" in tipo or "SOLAR" in tipo: setor = "KOMBI"
    elif "TECNOLOGIA" in tipo: setor = "TECNOLOGIA"
    elif "PESSOAL" in tipo: setor = "PESSOAL"
    
    # Se encontrou um setor válido, salva no inventário
    if setor:
        novo_inv = pd.DataFrame({'Item': [desc], 'Local': ['A Classificar'], 'Qtd': [1], 'Setor': [setor]})
        st.session_state.inventario = pd.concat([st.session_state.inventario, novo_inv], ignore_index=True)
        if is_legacy: return f"📦 {desc} arquivado na pasta {setor}."
        return f"✅ {desc} comprado e enviado para {setor}!"
        
    return "✅ Registrado no Financeiro."

# --- 6. HEADER ---
st.markdown('<div class="header-title">FAB\'S LAB.</div>', unsafe_allow_html=True)
st.markdown('<div class="header-sub">VW KOMBI 1.4 • ORGANIZER V29 (5 FOLDERS)</div>', unsafe_allow_html=True)

# HUD
c1, c2, c3 = st.columns(3)
with c1: 
    hoje = date.today()
    if not st.session_state.agenda.empty:
        try: st.session_state.agenda['Data'] = pd.to_datetime(st.session_state.agenda['Data']).dt.date
        except: pass
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

# --- ABA 1: AÇÃO ---
with abas[0]:
    st.markdown("### ⚡ LANÇAMENTO TÁTICO")
    st.caption("Escolha a categoria para o arquivamento automático.")
    with st.form("smart"):
        c1, c2 = st.columns([2, 1])
        d = c1.text_input("Descrição (Ex: Drone DJI, Lima Suiça)")
        v = c2.number_input("Valor (R$)", 0.0)
        t = st.selectbox("Destino", CATEGORIAS)
        
        is_legacy = st.checkbox("Já tenho (Apenas Inventário / Sem Gasto)")
        if st.form_submit_button("LANÇAR"):
            if "RECEITA" in t: pass 
            msg = processar_dado(d, v, t, is_legacy)
            st.success(msg)
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
            
            st.markdown("#### 📝 REGISTROS")
            df_editado = st.data_editor(
                st.session_state.financas, 
                num_rows="dynamic", 
                use_container_width=True,
                column_config={
                    "Tipo": st.column_config.SelectboxColumn("Categoria", options=CATEGORIAS, required=True, width="medium"),
                    "Valor": st.column_config.NumberColumn("Valor (R$)", format="R$ %.2f")
                }
            )
            if not df_editado.equals(st.session_state.financas):
                st.session_state.financas = df_editado
                st.rerun()
        except: st.error("Erro nos dados.")
    else: st.info("Cofre vazio.")

# --- ABA 3: ARSENAL (5 GAVETAS REAIS) ---
with abas[2]:
    st.markdown("### ⚒️ ARSENAL MAKER")
    
    # Criando as 5 Sub-Abas EXATAS que você pediu
    sub_abas = st.tabs(["💍 OURIVESARIA", "🔧 OFICINA", "🚐 KOMBI", "💻 TECNOLOGIA", "🎒 PESSOAL"])
    
    # Lista de setores para filtrar
    setores_map = ["OURIVESARIA", "OFICINA", "KOMBI", "TECNOLOGIA", "PESSOAL"]
    
    if not st.session_state.inventario.empty:
        # Loop para criar cada aba automaticamente
        for i, setor_alvo in enumerate(setores_map):
            with sub_abas[i]:
                # Filtra apenas o que é daquela gaveta
                df_setor = st.session_state.inventario[st.session_state.inventario['Setor'] == setor_alvo]
                
                if not df_setor.empty:
                    # Mostra tabela editável
                    df_setor_edit = st.data_editor(
                        df_setor,
                        key=f"editor_{setor_alvo}", # Chave única para não dar erro
                        num_rows="dynamic",
                        use_container_width=True,
                        column_config={
                            "Setor": st.column_config.SelectboxColumn(
                                "Mover para",
                                options=setores_map,
                                required=True
                            )
                        }
                    )
                    
                    # Se houve edição, precisamos atualizar o DataFrame principal (lógica ninja aqui)
                    if not df_setor_edit.equals(df_setor):
                        # Atualiza as linhas modificadas no DataFrame principal
                        st.session_state.inventario.update(df_setor_edit)
                        st.rerun()
                else:
                    st.info(f"Gaveta {setor_alvo} vazia.")
    else:
        st.info("Arsenal vazio.")

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
    st.markdown("### 🌎 LOGÍSTICA DE COMBATE")
    with st.expander("➕ TRAÇAR NOVA ROTA", expanded=True):
        with st.form("nova_rota"):
            c1, c2 = st.columns(2)
            origem = c1.text_input("Origem (Ex: Curitiba, PR)")
            destino = c2.text_input("Destino (Ex: Florianópolis, SC)")
            km_rota = st.number_input("Distância (Km)", min_value=1)
            
            if origem and destino:
                link_test = f"https://www.google.com/maps/dir/?api=1&origin={origem}&destination={destino}"
                st.link_button("🗺️ TESTAR NO MAPS", link_test)
            
            custo_est = (km_rota / 9.0) * 6.10
            st.caption(f"Custo Estimado: R$ {custo_est:.2f}")
            status_rota = st.selectbox("Status", ["Planejado", "Em Rota", "Concluído"])
            
            if st.form_submit_button("REGISTRAR ROTA"):
                novo_roteiro = pd.DataFrame([{
                    'Origem': origem, 'Destino': destino, 'Km': km_rota,
                    'Custo_Est': custo_est, 'Status': status_rota
                }])
                st.session_state.roteiros = pd.concat([st.session_state.roteiros, novo_roteiro], ignore_index=True)
                st.rerun()

    if not st.session_state.roteiros.empty:
        st.markdown("#### 🗺️ MAPA DE OPERAÇÕES")
        df_display = st.session_state.roteiros.copy()
        try:
            df_display["Navegar"] = df_display.apply(
                lambda x: f"https://www.google.com/maps/dir/?api=1&origin={x['Origem']}&destination={x['Destino']}", axis=1
            )
            st.data_editor(
                df_display, 
                num_rows="dynamic", 
                use_container_width=True,
                column_config={
                    "Navegar": st.column_config.LinkColumn("Link Maps", display_text="🗺️ Ir"),
                    "Custo_Est": st.column_config.NumberColumn("Custo (R$)", format="R$ %.2f"),
                    "Km": st.column_config.NumberColumn("Distância", format="%d km"),
                    "Status": st.column_config.SelectboxColumn("Status", options=["Planejado", "Em Rota", "Concluído"])
                }
            )
        except: st.error("Erro ao gerar links.")
    else: st.info("Nenhuma rota traçada.")

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
