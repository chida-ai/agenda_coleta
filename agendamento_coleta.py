import streamlit as st
import requests
from datetime import datetime, date, timedelta
from supabase import create_client, Client

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
SUPABASE_URL = "https://hvnwgvacpbnzkvktdnmk.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh2bndndmFjcGJuemt2a3Rkbm1rIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzg4OTAxOTcsImV4cCI6MjA5NDQ2NjE5N30.N0RDowMhI8ckWxFGqn8IjI06JsbY_tN4LzjdMS1nIVE"

st.set_page_config(
    page_title="Agendamento de Coletas · Alpha Analytics",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    color: #1a2433;
}
#MainMenu, footer, header { visibility: hidden; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: #0f1923 !important;
    border-right: 1px solid #1e2d3d;
}
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
[data-testid="stSidebar"] .stRadio label {
    padding: 10px 14px;
    border-radius: 8px;
    transition: background .15s;
    cursor: pointer;
    display: block;
    font-size: 14px;
    font-weight: 500;
}
[data-testid="stSidebar"] .stRadio label:hover { background: #1e2d3d; }

/* Page header */
.page-header {
    background: linear-gradient(135deg, #1a56db 0%, #0e3fa8 100%);
    color: white;
    padding: 20px 28px;
    border-radius: 14px;
    margin-bottom: 24px;
    box-shadow: 0 8px 32px rgba(26,86,219,0.2);
}
.page-header h1 {
    margin: 0;
    font-family: 'Syne', sans-serif;
    font-size: 22px;
    font-weight: 800;
    letter-spacing: -0.5px;
}
.page-header p { margin: 4px 0 0; font-size: 13px; opacity: 0.75; }

/* Cards */
.metric-card {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 18px 20px;
    text-align: center;
    box-shadow: 0 2px 8px rgba(0,0,0,.04);
}
.metric-card .mc-val {
    font-family: 'Syne', sans-serif;
    font-size: 32px;
    font-weight: 700;
    line-height: 1;
    margin: 4px 0;
}
.metric-card .mc-label {
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: .8px;
    color: #64748b;
}
.mc-blue  .mc-val { color: #1a56db; }
.mc-orange .mc-val { color: #d97706; }
.mc-green .mc-val { color: #059669; }
.mc-red   .mc-val { color: #dc2626; }

/* Status badges */
.badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 600;
    white-space: nowrap;
}
.badge-pendente  { background: #fef3c7; color: #d97706; }
.badge-agendada  { background: #dbeafe; color: #1d4ed8; }
.badge-realizada { background: #d1fae5; color: #065f46; }
.badge-entregue  { background: #e0e7ff; color: #3730a3; }
.badge-rush      { background: #fee2e2; color: #dc2626; }
.badge-normal    { background: #f1f5f9; color: #475569; }

/* Ordem card */
.ordem-card {
    background: white;
    border: 1px solid #e2e8f0;
    border-left: 4px solid #1a56db;
    border-radius: 10px;
    padding: 16px 18px;
    margin-bottom: 10px;
    box-shadow: 0 1px 4px rgba(0,0,0,.04);
}
.ordem-card.rush { border-left-color: #dc2626; }
.ordem-card .oc-cliente { font-weight: 600; font-size: 15px; color: #1a2433; }
.ordem-card .oc-meta { font-size: 12px; color: #64748b; margin-top: 4px; }

/* Agenda card */
.agenda-slot {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 14px 16px;
    margin-bottom: 8px;
}
.agenda-slot .as-time {
    font-family: 'Syne', sans-serif;
    font-size: 13px;
    font-weight: 700;
    color: #1a56db;
}
.agenda-slot .as-cliente { font-weight: 600; font-size: 14px; }
.agenda-slot .as-meta { font-size: 11.5px; color: #64748b; margin-top: 3px; }

/* Coletor card */
.coletor-card {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 16px 18px;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 14px;
}
.coletor-avatar {
    width: 42px; height: 42px;
    background: linear-gradient(135deg, #1a56db, #0e3fa8);
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-family: 'Syne', sans-serif;
    font-weight: 700; font-size: 16px; color: white;
    flex-shrink: 0;
}
.coletor-nome { font-weight: 600; font-size: 14px; }
.coletor-meta { font-size: 12px; color: #64748b; margin-top: 2px; }

/* Section label */
.sec-label {
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: #94a3b8;
    margin: 20px 0 8px;
}

/* Table */
.data-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.data-table th {
    text-align: left;
    padding: 9px 12px;
    font-size: 10.5px;
    text-transform: uppercase;
    letter-spacing: .6px;
    color: #64748b;
    font-weight: 600;
    border-bottom: 2px solid #e2e8f0;
    background: #f8fafc;
}
.data-table td {
    padding: 10px 12px;
    border-bottom: 1px solid #f1f5f9;
    color: #1a2433;
    vertical-align: middle;
}
.data-table tr:hover td { background: #f8fafc; }

div[data-testid="stExpander"] {
    border: 1px solid #e2e8f0 !important;
    border-radius: 10px !important;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SUPABASE CLIENT
# ─────────────────────────────────────────────
@st.cache_resource
def get_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = get_supabase()

# ─────────────────────────────────────────────
# HELPERS — DB
# ─────────────────────────────────────────────
def get_coletores(apenas_ativos=True):
    q = supabase.table("coletores").select("*").order("nome")
    if apenas_ativos:
        q = q.eq("status", "ativo")
    return q.execute().data

def get_ordens(status=None):
    q = supabase.table("ordens_coleta").select("*").order("criado_em", desc=True)
    if status:
        q = q.eq("status", status)
    return q.execute().data

def get_agendamentos(data_inicio=None, data_fim=None, coletor_id=None):
    q = supabase.table("agendamentos").select(
        "*, ordens_coleta(*), coletores(*)"
    ).order("data_coleta").order("horario_saida")
    if data_inicio:
        q = q.gte("data_coleta", str(data_inicio))
    if data_fim:
        q = q.lte("data_coleta", str(data_fim))
    if coletor_id:
        q = q.eq("coletor_id", coletor_id)
    return q.execute().data

def criar_ordem(dados: dict):
    dados["atualizado_em"] = datetime.now().isoformat()
    return supabase.table("ordens_coleta").insert(dados).execute()

def atualizar_ordem_status(ordem_id: str, status: str):
    return supabase.table("ordens_coleta").update({
        "status": status,
        "atualizado_em": datetime.now().isoformat()
    }).eq("id", ordem_id).execute()

def criar_agendamento(dados: dict):
    res = supabase.table("agendamentos").insert(dados).execute()
    atualizar_ordem_status(dados["ordem_id"], "Agendada")
    return res

def criar_coletor(dados: dict):
    return supabase.table("coletores").insert(dados).execute()

def atualizar_coletor(coletor_id: str, dados: dict):
    return supabase.table("coletores").update(dados).eq("id", coletor_id).execute()

# ─────────────────────────────────────────────
# HELPERS — GOOGLE ROUTES
# ─────────────────────────────────────────────
def consultar_rota(origem: str, destino: str, api_key: str) -> dict:
    if not api_key or not destino:
        return {}
    url = "https://routes.googleapis.com/directions/v2:computeRoutes"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "routes.distanceMeters,routes.duration,routes.travelAdvisory.tollInfo",
    }
    body = {
        "origin": {"address": origem + ", Brasil"},
        "destination": {"address": destino + ", Brasil"},
        "travelMode": "DRIVE",
        "extraComputations": ["TOLLS"],
    }
    try:
        resp = requests.post(url, headers=headers, json=body, timeout=15)
        if resp.status_code != 200:
            return {"erro": resp.json().get("error", {}).get("message", "Erro na API")}
        route = resp.json()["routes"][0]
        km_ida = route["distanceMeters"] / 1000
        dur_s = int(route.get("duration", "0s").replace("s", ""))
        dur_str = f"{dur_s // 3600}h {(dur_s % 3600) // 60:02d}min"
        toll = route.get("travelAdvisory", {}).get("tollInfo", {})
        prices = toll.get("estimatedPrice", [])
        ped = 0.0
        for p in prices:
            if p.get("currencyCode") == "BRL":
                ped = float(p.get("units", 0)) + p.get("nanos", 0) / 1e9
                break
        return {"km_total": km_ida * 2, "km_ida": km_ida,
                "duracao": dur_str, "pedagio_total": ped * 2}
    except Exception as e:
        return {"erro": str(e)}

def fmt(v):
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def badge_status(status):
    cls = {
        "Pendente": "badge-pendente",
        "Agendada": "badge-agendada",
        "Realizada": "badge-realizada",
        "Entregue": "badge-entregue",
    }.get(status, "badge-normal")
    return f'<span class="badge {cls}">{status}</span>'

def badge_urgencia(urg):
    cls = "badge-rush" if urg == "Rush" else "badge-normal"
    return f'<span class="badge {cls}">{urg}</span>'

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding: 20px 8px 16px;">
        <div style="font-family:'Syne',sans-serif;font-size:20px;font-weight:800;color:#fff;">
            🧪 Alpha Analytics
        </div>
        <div style="font-size:12px;color:#64748b;margin-top:2px;">Agendamento de Coletas</div>
    </div>
    """, unsafe_allow_html=True)

    pagina = st.radio("", [
        "📊 Painel",
        "📥 Fila de Ordens",
        "➕ Nova Ordem",
        "📅 Agendamento",
        "🗓️ Agenda / Roteiro",
        "👷 Coletores",
    ], label_visibility="collapsed")

    st.markdown("---")
    st.markdown("""
    <div style="font-size:11px;color:#475569;padding:0 4px;">
        <b>Google API Key</b><br>
        Necessária para calcular rota e pedágio.
    </div>
    """, unsafe_allow_html=True)
    google_key = st.text_input("", type="password",
                                placeholder="Cole sua chave aqui",
                                key="google_key",
                                label_visibility="collapsed")
    if google_key:
        st.markdown('<span style="font-size:11px;color:#059669;">✓ Chave configurada</span>',
                    unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(f"""
    <div style="font-size:10px;color:#475569;padding:0 4px;">
        Desenvolvido por Alpha Analytics<br>
        v1.0 · {datetime.now().strftime("%d/%m/%Y")}
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════
# PÁGINA: PAINEL
# ═══════════════════════════════════════════════
if pagina == "📊 Painel":
    st.markdown("""
    <div class="page-header">
        <h1>📊 Painel de Operações</h1>
        <p>Visão geral das coletas e status da equipe</p>
    </div>
    """, unsafe_allow_html=True)

    ordens = get_ordens()
    agendamentos = get_agendamentos(
        data_inicio=date.today(),
        data_fim=date.today() + timedelta(days=7)
    )

    pendentes  = [o for o in ordens if o["status"] == "Pendente"]
    agendadas  = [o for o in ordens if o["status"] == "Agendada"]
    realizadas = [o for o in ordens if o["status"] == "Realizada"]
    rush       = [o for o in ordens if o["urgencia"] == "Rush" and o["status"] in ["Pendente","Agendada"]]

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class="metric-card mc-orange">
            <div class="mc-label">Pendentes</div>
            <div class="mc-val">{len(pendentes)}</div>
            <div style="font-size:11px;color:#64748b;">aguardando agendamento</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="metric-card mc-blue">
            <div class="mc-label">Agendadas</div>
            <div class="mc-val">{len(agendadas)}</div>
            <div style="font-size:11px;color:#64748b;">próximos 7 dias</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="metric-card mc-green">
            <div class="mc-label">Realizadas</div>
            <div class="mc-val">{len(realizadas)}</div>
            <div style="font-size:11px;color:#64748b;">total histórico</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class="metric-card mc-red">
            <div class="mc-label">Rush ativo</div>
            <div class="mc-val">{len(rush)}</div>
            <div style="font-size:11px;color:#64748b;">requerem atenção</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    col_a, col_b = st.columns([1, 1])

    with col_a:
        st.markdown('<div class="sec-label">⚡ Ordens Rush Pendentes</div>', unsafe_allow_html=True)
        if rush:
            for o in rush[:5]:
                st.markdown(f"""
                <div class="ordem-card rush">
                    <div class="oc-cliente">🔴 {o['cliente']}</div>
                    <div class="oc-meta">
                        {o.get('cidade','')}{' · ' + o.get('tipo_amostra','') if o.get('tipo_amostra') else ''}
                        · {o.get('vendedor','—')}
                    </div>
                </div>""", unsafe_allow_html=True)
        else:
            st.info("Nenhuma ordem Rush pendente.")

    with col_b:
        st.markdown('<div class="sec-label">📅 Próximas Coletas (7 dias)</div>', unsafe_allow_html=True)
        if agendamentos:
            for ag in agendamentos[:6]:
                o = ag.get("ordens_coleta") or {}
                c = ag.get("coletores") or {}
                hora = str(ag.get("horario_saida", ""))[:5] if ag.get("horario_saida") else "—"
                st.markdown(f"""
                <div class="agenda-slot">
                    <div style="display:flex;justify-content:space-between;align-items:center">
                        <div class="as-time">📅 {ag['data_coleta']} · {hora}</div>
                        <span style="font-size:11px;color:#64748b">{c.get('nome','—')}</span>
                    </div>
                    <div class="as-cliente">{o.get('cliente','—')}</div>
                    <div class="as-meta">{o.get('cidade','')} · {o.get('tipo_amostra','')}</div>
                </div>""", unsafe_allow_html=True)
        else:
            st.info("Nenhuma coleta agendada para os próximos 7 dias.")

# ═══════════════════════════════════════════════
# PÁGINA: FILA DE ORDENS
# ═══════════════════════════════════════════════
elif pagina == "📥 Fila de Ordens":
    st.markdown("""
    <div class="page-header">
        <h1>📥 Fila de Ordens de Coleta</h1>
        <p>Gerencie todas as ordens e acompanhe o status</p>
    </div>
    """, unsafe_allow_html=True)

    col_f1, col_f2 = st.columns([2, 1])
    with col_f1:
        filtro_status = st.selectbox("Filtrar por status",
            ["Todos", "Pendente", "Agendada", "Realizada", "Entregue"])
    with col_f2:
        filtro_urg = st.selectbox("Urgência", ["Todos", "Rush", "Normal"])

    ordens = get_ordens(None if filtro_status == "Todos" else filtro_status)
    if filtro_urg != "Todos":
        ordens = [o for o in ordens if o.get("urgencia") == filtro_urg]

    st.markdown(f'<div class="sec-label">{len(ordens)} ordem(ns) encontrada(s)</div>',
                unsafe_allow_html=True)

    if not ordens:
        st.info("Nenhuma ordem encontrada com os filtros selecionados.")
    else:
        for o in ordens:
            with st.expander(f"{'🔴 ' if o.get('urgencia')=='Rush' else ''}{o['cliente']} · {o.get('cidade','—')} · {o['status']}"):
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.markdown(f"**Cliente:** {o['cliente']}")
                    st.markdown(f"**Endereço:** {o.get('endereco','—')}")
                    st.markdown(f"**Cidade/UF:** {o.get('cidade','—')} / {o.get('estado','—')}")
                with c2:
                    st.markdown(f"**Tipo de Amostra:** {o.get('tipo_amostra','—')}")
                    st.markdown(f"**Vendedor:** {o.get('vendedor','—')}")
                    st.markdown(f"**Urgência:** {o.get('urgencia','Normal')}")
                with c3:
                    st.markdown(f"**Status:** {o['status']}")
                    st.markdown(f"**Criado em:** {str(o.get('criado_em',''))[:10]}")
                    if o.get("origem_proposta"):
                        st.markdown(f"**Proposta myLIMS:** {o['origem_proposta']}")

                if o.get("observacoes"):
                    st.markdown(f"**Obs:** {o['observacoes']}")

                st.markdown("---")
                cols_btn = st.columns(4)
                status_opts = ["Pendente", "Agendada", "Realizada", "Entregue"]
                for i, s in enumerate(status_opts):
                    with cols_btn[i]:
                        if s != o["status"]:
                            if st.button(f"→ {s}", key=f"st_{o['id']}_{s}",
                                        use_container_width=True):
                                atualizar_ordem_status(o["id"], s)
                                st.rerun()

# ═══════════════════════════════════════════════
# PÁGINA: NOVA ORDEM
# ═══════════════════════════════════════════════
elif pagina == "➕ Nova Ordem":
    st.markdown("""
    <div class="page-header">
        <h1>➕ Nova Ordem de Coleta</h1>
        <p>Cadastre uma nova demanda de amostragem</p>
    </div>
    """, unsafe_allow_html=True)

    with st.form("form_ordem"):
        st.markdown('<div class="sec-label">Dados do Cliente</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            cliente   = st.text_input("Cliente *", placeholder="Razão social")
            endereco  = st.text_input("Endereço", placeholder="Rua, número")
        with c2:
            cidade = st.text_input("Cidade *", placeholder="Ex: Cubatão")
            estado = st.selectbox("Estado", ["SP","RJ","MG","ES","PR","SC","RS","BA","GO","DF","Outro"])

        st.markdown('<div class="sec-label">Dados da Coleta</div>', unsafe_allow_html=True)
        c3, c4 = st.columns(2)
        with c3:
            tipo_amostra = st.selectbox("Tipo de Amostra", [
                "Água Subterrânea",
                "Efluente",
                "Água Superficial",
                "Solo",
                "Resíduo",
                "Misto",
                "Outro",
            ])
            vendedor = st.text_input("Vendedor responsável")
        with c4:
            urgencia = st.selectbox("Urgência", ["Normal", "Rush"])
            origem_proposta = st.text_input("ID Proposta myLIMS",
                                            placeholder="Opcional")

        observacoes = st.text_area("Observações", placeholder="Instruções especiais, restrições de acesso, etc.")

        submitted = st.form_submit_button("✅ Criar Ordem de Coleta",
                                          type="primary", use_container_width=True)

        if submitted:
            if not cliente or not cidade:
                st.error("Preencha Cliente e Cidade.")
            else:
                criar_ordem({
                    "cliente": cliente,
                    "endereco": endereco,
                    "cidade": cidade,
                    "estado": estado,
                    "tipo_amostra": tipo_amostra,
                    "vendedor": vendedor,
                    "urgencia": urgencia,
                    "status": "Pendente",
                    "observacoes": observacoes,
                    "origem_proposta": origem_proposta,
                })
                st.success(f"✅ Ordem criada para **{cliente}** — {cidade}/{estado}!")
                st.balloons()

# ═══════════════════════════════════════════════
# PÁGINA: AGENDAMENTO
# ═══════════════════════════════════════════════
elif pagina == "📅 Agendamento":
    st.markdown("""
    <div class="page-header">
        <h1>📅 Agendamento de Coleta</h1>
        <p>Atribua coletores, defina datas e calcule custos de deslocamento</p>
    </div>
    """, unsafe_allow_html=True)

    pendentes = get_ordens("Pendente")
    coletores = get_coletores()

    if not pendentes:
        st.info("✅ Não há ordens pendentes de agendamento.")
        st.stop()

    if not coletores:
        st.warning("Cadastre ao menos um coletor antes de agendar.")
        st.stop()

    # Seleção da ordem
    st.markdown('<div class="sec-label">1. Selecione a Ordem</div>', unsafe_allow_html=True)

    opcoes_ordens = {
        f"{'🔴 RUSH · ' if o['urgencia']=='Rush' else ''}{o['cliente']} — {o.get('cidade','—')}/{o.get('estado','—')}": o
        for o in pendentes
    }
    ordem_sel_label = st.selectbox("Ordem pendente", list(opcoes_ordens.keys()),
                                   label_visibility="collapsed")
    ordem_sel = opcoes_ordens[ordem_sel_label]

    # Detalhes da ordem
    with st.expander("📋 Detalhes da ordem selecionada"):
        cc1, cc2 = st.columns(2)
        with cc1:
            st.markdown(f"**Cliente:** {ordem_sel['cliente']}")
            st.markdown(f"**Endereço:** {ordem_sel.get('endereco','—')}")
            st.markdown(f"**Cidade/UF:** {ordem_sel.get('cidade','—')}/{ordem_sel.get('estado','—')}")
        with cc2:
            st.markdown(f"**Tipo:** {ordem_sel.get('tipo_amostra','—')}")
            st.markdown(f"**Vendedor:** {ordem_sel.get('vendedor','—')}")
            st.markdown(f"**Urgência:** {ordem_sel.get('urgencia','Normal')}")
        if ordem_sel.get("observacoes"):
            st.markdown(f"**Obs:** {ordem_sel['observacoes']}")

    st.markdown('<div class="sec-label">2. Selecione o Coletor</div>', unsafe_allow_html=True)

    # Sugestão por região
    estado_ordem = ordem_sel.get("estado", "")
    regiao_sugerida = "Grande SP" if estado_ordem == "SP" else \
                      "Rio de Janeiro" if estado_ordem == "RJ" else "Outros"

    opcoes_coletores = {}
    for c in coletores:
        sugerido = "⭐ " if c["regiao"] == regiao_sugerida else ""
        opcoes_coletores[f"{sugerido}{c['nome']} · {c['regiao']}"] = c

    coletor_label = st.selectbox("Coletor", list(opcoes_coletores.keys()),
                                 label_visibility="collapsed")
    coletor_sel = opcoes_coletores[coletor_label]

    st.info(f"💡 Região sugerida: **{regiao_sugerida}** · Coletores com ⭐ são os mais indicados para este destino.")

    st.markdown('<div class="sec-label">3. Data e Horário</div>', unsafe_allow_html=True)
    dc1, dc2 = st.columns(2)
    with dc1:
        data_coleta = st.date_input("Data da coleta", value=date.today() + timedelta(days=1),
                                     min_value=date.today())
    with dc2:
        horario_saida = st.time_input("Horário de saída", value=datetime.strptime("07:00", "%H:%M").time())

    # Rota
    st.markdown('<div class="sec-label">4. Calcular Rota (opcional)</div>', unsafe_allow_html=True)

    destino_rota = f"{ordem_sel.get('endereco','')}, {ordem_sel.get('cidade','')}, {ordem_sel.get('estado','')}"
    origem_rota = st.text_input("Origem (base)", value="São Paulo, SP")
    destino_input = st.text_input("Destino", value=destino_rota.strip(", "))

    rota_result = {}
    if st.button("🗺️ Calcular Rota", use_container_width=False):
        api_key = st.session_state.get("google_key", "")
        if not api_key:
            st.warning("Configure a Google API Key na sidebar para calcular rota.")
        else:
            with st.spinner("Consultando Google Maps..."):
                rota_result = consultar_rota(origem_rota, destino_input, api_key)
                if "erro" in rota_result:
                    st.error(f"Erro: {rota_result['erro']}")
                else:
                    st.session_state["_rota_ag"] = rota_result

    rota_ok = st.session_state.get("_rota_ag", {})
    if rota_ok:
        r1, r2, r3 = st.columns(3)
        with r1:
            st.metric("KM total (ida+volta)", f"{rota_ok.get('km_total',0):.0f} km")
        with r2:
            st.metric("Duração (ida)", rota_ok.get("duracao", "—"))
        with r3:
            st.metric("Pedágio total", fmt(rota_ok.get("pedagio_total", 0)))

    # Ajuste manual
    dc3, dc4 = st.columns(2)
    with dc3:
        km_manual = st.number_input("KM total (ida+volta)",
                                     value=float(rota_ok.get("km_total", 0)),
                                     min_value=0.0, step=10.0)
    with dc4:
        ped_manual = st.number_input("Pedágio total R$",
                                      value=float(rota_ok.get("pedagio_total", 0)),
                                      min_value=0.0, step=5.0)

    # Custo estimado simples
    custo_comb = (km_manual / 10) * 6.67
    custo_estimado = custo_comb + ped_manual

    if km_manual > 0:
        st.markdown(f"""
        <div style="background:#e0f2fe;border:1px solid #7dd3fc;border-radius:10px;
                    padding:14px 18px;margin:12px 0;">
            <b>💰 Custo estimado de deslocamento:</b>
            Combustível {fmt(custo_comb)} + Pedágio {fmt(ped_manual)} =
            <b style="color:#0369a1">{fmt(custo_estimado)}</b>
        </div>
        """, unsafe_allow_html=True)

    obs_ag = st.text_area("Observações do agendamento",
                           placeholder="Instruções para o coletor, restrições, contato no local...")

    st.markdown("---")
    if st.button("✅ Confirmar Agendamento", type="primary", use_container_width=True):
        criar_agendamento({
            "ordem_id": ordem_sel["id"],
            "coletor_id": coletor_sel["id"],
            "data_coleta": str(data_coleta),
            "horario_saida": str(horario_saida),
            "km_total": km_manual,
            "pedagio_total": ped_manual,
            "duracao_rota": rota_ok.get("duracao", ""),
            "custo_estimado": custo_estimado,
            "observacoes": obs_ag,
        })
        # Limpar rota da sessão
        if "_rota_ag" in st.session_state:
            del st.session_state["_rota_ag"]
        st.success(f"✅ Coleta agendada para **{coletor_sel['nome']}** em **{data_coleta.strftime('%d/%m/%Y')}**!")
        st.balloons()

# ═══════════════════════════════════════════════
# PÁGINA: AGENDA / ROTEIRO
# ═══════════════════════════════════════════════
elif pagina == "🗓️ Agenda / Roteiro":
    st.markdown("""
    <div class="page-header">
        <h1>🗓️ Agenda e Roteiro</h1>
        <p>Visualize as coletas por coletor e por data</p>
    </div>
    """, unsafe_allow_html=True)

    coletores = get_coletores()

    rf1, rf2, rf3 = st.columns(3)
    with rf1:
        data_ini = st.date_input("De", value=date.today())
    with rf2:
        data_fim_v = st.date_input("Até", value=date.today() + timedelta(days=6))
    with rf3:
        opcoes_col = {"Todos": None}
        for c in coletores:
            opcoes_col[c["nome"]] = c["id"]
        col_filtro = st.selectbox("Coletor", list(opcoes_col.keys()))
        coletor_id_filtro = opcoes_col[col_filtro]

    agendamentos = get_agendamentos(data_ini, data_fim_v, coletor_id_filtro)

    if not agendamentos:
        st.info("Nenhuma coleta agendada no período selecionado.")
    else:
        # Agrupar por data
        por_data = {}
        for ag in agendamentos:
            d = ag["data_coleta"]
            por_data.setdefault(d, []).append(ag)

        for data_str, ags in sorted(por_data.items()):
            data_fmt = datetime.strptime(data_str, "%Y-%m-%d").strftime("%A, %d/%m/%Y").capitalize()
            st.markdown(f"### 📅 {data_fmt} — {len(ags)} coleta(s)")

            for ag in ags:
                o = ag.get("ordens_coleta") or {}
                c = ag.get("coletores") or {}
                hora = str(ag.get("horario_saida", ""))[:5] if ag.get("horario_saida") else "—"
                km   = ag.get("km_total", 0) or 0
                custo = ag.get("custo_estimado", 0) or 0

                col_a, col_b = st.columns([3, 1])
                with col_a:
                    urgencia_icon = "🔴" if o.get("urgencia") == "Rush" else "🔵"
                    st.markdown(f"""
                    <div class="agenda-slot">
                        <div style="display:flex;justify-content:space-between;align-items:center">
                            <div class="as-time">🕐 Saída: {hora}</div>
                            <div style="font-size:12px;font-weight:600;color:#1a56db">{c.get('nome','—')}</div>
                        </div>
                        <div class="as-cliente">{urgencia_icon} {o.get('cliente','—')}</div>
                        <div class="as-meta">
                            📍 {o.get('endereco','—')}, {o.get('cidade','—')}/{o.get('estado','—')}
                            &nbsp;·&nbsp; 🧪 {o.get('tipo_amostra','—')}
                            &nbsp;·&nbsp; 🛣️ {km:.0f} km
                            &nbsp;·&nbsp; 💰 {fmt(custo)}
                        </div>
                        {f'<div class="as-meta" style="margin-top:4px;color:#475569">📝 {ag["observacoes"]}</div>' if ag.get("observacoes") else ''}
                    </div>
                    """, unsafe_allow_html=True)

                with col_b:
                    novo_status = st.selectbox("Status",
                        ["Agendada", "Realizada", "Entregue"],
                        key=f"ag_st_{ag['id']}",
                        index=["Agendada","Realizada","Entregue"].index(
                            o.get("status","Agendada")
                            if o.get("status","Agendada") in ["Agendada","Realizada","Entregue"]
                            else "Agendada"
                        )
                    )
                    if st.button("Atualizar", key=f"ag_upd_{ag['id']}",
                                 use_container_width=True):
                        atualizar_ordem_status(ag["ordem_id"], novo_status)
                        st.rerun()

# ═══════════════════════════════════════════════
# PÁGINA: COLETORES
# ═══════════════════════════════════════════════
elif pagina == "👷 Coletores":
    st.markdown("""
    <div class="page-header">
        <h1>👷 Gestão de Coletores</h1>
        <p>Cadastro da equipe de campo — permissões e regiões serão expandidas na Fase 2</p>
    </div>
    """, unsafe_allow_html=True)

    coletores = get_coletores(apenas_ativos=False)

    col_lista, col_form = st.columns([1.2, 1])

    with col_lista:
        st.markdown('<div class="sec-label">Equipe cadastrada</div>', unsafe_allow_html=True)
        if not coletores:
            st.info("Nenhum coletor cadastrado ainda.")
        for c in coletores:
            inicial = c["nome"][0].upper() if c["nome"] else "?"
            status_cor = "#059669" if c["status"] == "ativo" else "#dc2626"
            st.markdown(f"""
            <div class="coletor-card">
                <div class="coletor-avatar">{inicial}</div>
                <div style="flex:1">
                    <div class="coletor-nome">{c['nome']}</div>
                    <div class="coletor-meta">
                        📍 {c['regiao']}
                        &nbsp;·&nbsp;
                        <span style="color:{status_cor};font-weight:600">{c['status'].capitalize()}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Botão inline para ativar/desativar
            novo_status = "inativo" if c["status"] == "ativo" else "ativo"
            if st.button(f"→ Marcar como {novo_status}", key=f"col_st_{c['id']}"):
                atualizar_coletor(c["id"], {"status": novo_status})
                st.rerun()

    with col_form:
        st.markdown('<div class="sec-label">Adicionar novo coletor</div>', unsafe_allow_html=True)
        with st.form("form_coletor"):
            nome_col  = st.text_input("Nome *", placeholder="Ex: João Silva")
            regiao_col = st.selectbox("Região principal", [
                "Grande SP",
                "Interior SP",
                "Rio de Janeiro",
                "Minas Gerais",
                "Sul",
                "Nordeste",
                "Outros",
            ])
            sub_col = st.form_submit_button("➕ Adicionar Coletor",
                                             type="primary", use_container_width=True)
            if sub_col:
                if not nome_col:
                    st.error("Informe o nome do coletor.")
                else:
                    criar_coletor({"nome": nome_col, "regiao": regiao_col, "status": "ativo"})
                    st.success(f"✅ {nome_col} adicionado!")
                    st.rerun()

        st.markdown("""
        <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;
                    padding:14px 16px;margin-top:16px;font-size:12px;color:#64748b;">
            <b>🔒 Fase 2 — Em breve:</b><br>
            • Controle de habilitações (NR-33, NR-20...)<br>
            • Validade de documentos com alertas<br>
            • Restrições por tipo de cliente<br>
            • Certificados específicos por empresa
        </div>
        """, unsafe_allow_html=True)
