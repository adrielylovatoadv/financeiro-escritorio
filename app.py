import streamlit as st
import json
import os
from datetime import date
import streamlit.components.v1 as _components

st.set_page_config(
    page_title="Financeiro – Escritório",
    page_icon="💼",
    layout="wide",
)

# ── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.main { background: #0a0f1e; color: #e8eaf6; }
section[data-testid="stSidebar"] { background: #0d1427; }

.stApp { background: #0a0f1e; }

.bloco {
    background: linear-gradient(135deg, #0d1b3e 0%, #1a2a5e 100%);
    border: 1px solid #2a3f7e;
    border-radius: 12px;
    padding: 20px;
    margin: 8px 0;
}

.card-titulo {
    font-size: 11px;
    font-weight: 600;
    color: #7986cb;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 4px;
}
.card-valor {
    font-size: 28px;
    font-weight: 700;
    color: #e8eaf6;
}
.card-valor.verde { color: #4caf50; }
.card-valor.vermelho { color: #ef5350; }
.card-valor.azul { color: #42a5f5; }
.card-valor.laranja { color: #ffa726; }

.stTabs [data-baseweb="tab-list"] {
    background: #0d1427;
    border-radius: 10px;
    padding: 4px;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    color: #7986cb;
    border-radius: 8px;
    font-weight: 500;
    font-size: 14px;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #1a2a6c, #3949ab) !important;
    color: white !important;
}

.stButton > button {
    background: linear-gradient(135deg, #1a2a6c, #3949ab);
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    padding: 8px 20px;
    transition: all 0.2s;
}
.stButton > button:hover { opacity: 0.85; transform: translateY(-1px); }

.stTextInput > div > div > input,
.stSelectbox > div > div > div {
    background: #1a2a5e !important;
    border: 1px solid #2a3f7e !important;
    color: #e8eaf6 !important;
    border-radius: 8px !important;
}

h1,h2,h3 { color: #e8eaf6; }

.linha-tabela {
    display: grid;
    align-items: center;
    gap: 8px;
    padding: 6px 0;
    border-bottom: 1px solid #1a2a5e;
}
.linha-tabela:last-child { border-bottom: none; }

.badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 600;
}
.badge-adriely { background: #1a237e; color: #9fa8da; }
.badge-eduarda { background: #1b5e20; color: #a5d6a7; }
.badge-dividido { background: #4a148c; color: #ce93d8; }
.badge-recebido { background: #1b5e20; color: #a5d6a7; }
.badge-pendente { background: #b71c1c; color: #ef9a9a; }

.mes-header {
    background: linear-gradient(90deg, #1a2a6c, #2a3f7e);
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: 600;
    color: #7986cb;
    font-size: 13px;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin: 12px 0 6px 0;
}

.divider { border: none; border-top: 1px solid #2a3f7e; margin: 16px 0; }

[data-testid="stMetricValue"] { color: #e8eaf6 !important; }
</style>
""", unsafe_allow_html=True)

# ── JS masks ─────────────────────────────────────────────────────────────────
_components.html("""
<script>
(function(){
  var setter=Object.getOwnPropertyDescriptor(window.parent.HTMLInputElement.prototype,'value').set;
  function fire(el,val){setter.call(el,val);el.dispatchEvent(new Event('input',{bubbles:true}));}
  function currencyMask(input){
    if(input._cm)return; input._cm=true;
    input.addEventListener('input',function(){
      if(input._busy)return; input._busy=true;
      var digits=input.value.replace(/\D/g,'');
      if(!digits){fire(input,'');input._busy=false;return;}
      var num=parseInt(digits,10);
      var cents=(num%100).toString().padStart(2,'0');
      var integer=Math.floor(num/100).toString();
      integer=integer.replace(/\B(?=(\d{3})+(?!\d))/g,'.');
      fire(input,integer+','+cents);
      input._busy=false;
    });
  }
  function apply(){
    var doc=window.parent.document;
    doc.querySelectorAll('input[placeholder="0,00"]').forEach(currencyMask);
  }
  apply();
  new MutationObserver(apply).observe(window.parent.document.body,{childList:true,subtree:true});
})();
</script>
""", height=0)

# ── Persistência ─────────────────────────────────────────────────────────────
DATA_FILE = os.path.join(os.path.dirname(__file__), "financeiro_data.json")

MESES_ORDEM = ["Out/2024","Nov/2024","Dez/2024","Jan/2025","Fev/2025",
               "Mar/2025","Abr/2025","Mai/2025","Jun/2025","Jul/2025",
               "Ago/2025","Set/2025","Out/2025","Nov/2025","Dez/2025"]

MESES_FIXAS_COLS = ["Out","Nov","Dez","Jan","Fev","Mar","Abr","Mai",
                    "Jun","Jul","Ago","Set","Out2","Nov2","Dez2"]

def _v(s):
    """Converte string 'R$ 1.234,56' ou '1.234,56' para float."""
    if not s: return 0.0
    s = str(s)
    # remove tudo exceto dígitos, vírgula e ponto
    import re
    nums = re.sub(r'[^\d,.]','', s)
    if not nums: return 0.0
    # formato brasileiro: último separador é vírgula
    if ',' in nums:
        nums = nums.replace('.','').replace(',','.')
    try:
        return float(nums)
    except:
        return 0.0

def _fmt(v):
    try:
        return f"R$ {float(v):,.2f}".replace(",","X").replace(".",",").replace("X",".")
    except:
        return "R$ 0,00"

def _vs(v):
    """Formata float como string de input '1.234,56'."""
    try:
        return f"{float(v):,.2f}".replace(",","X").replace(".",",").replace("X",".")
    except:
        return "0,00"

# ── Dados iniciais (do FINANCEIRO.xlsm) ───────────────────────────────────
def dados_iniciais():
    # Receitas
    receitas = [
        {"mes":"Out/2024","cliente":"BERNADETE","reu":"SANTANDER","processo":"5001026-20.2025.8.13.0329","recibo":5000.00,"honorarios":2075.00,"status":"recebido"},
        {"mes":"Jan/2025","cliente":"ANA MARIA","reu":"ITAU","processo":"5001218-50.2025.8.13.0329","recibo":4638.00,"honorarios":1924.00,"status":"recebido"},
        {"mes":"Jan/2025","cliente":"MARTA","reu":"ITAU","processo":"5001241-93.2025.8.13.0329","recibo":4155.00,"honorarios":1725.00,"status":"recebido"},
        {"mes":"Jan/2025","cliente":"MARTA","reu":"ITAU","processo":"5001131-94.2025.8.13.0329","recibo":4000.00,"honorarios":1660.00,"status":"recebido"},
        {"mes":"Jan/2025","cliente":"JOSE CARLOS","reu":"ITAU","processo":"5001339-78.2025.8.13.0329","recibo":4770.00,"honorarios":1975.00,"status":"recebido"},
        {"mes":"Jan/2025","cliente":"LENITA","reu":"ITAU","processo":"5001329-34.2025.8.13.0329","recibo":2900.00,"honorarios":1203.50,"status":"recebido"},
        {"mes":"Fev/2025","cliente":"MARTA","reu":"ITAU","processo":"5001194-22.2025.8.13.0329","recibo":4000.00,"honorarios":1660.00,"status":"recebido"},
        {"mes":"Fev/2025","cliente":"MARTA","reu":"ITAU","processo":"5001130-12.2025.8.13.0329","recibo":3900.00,"honorarios":1618.50,"status":"recebido"},
        {"mes":"Fev/2025","cliente":"ANA MARIA","reu":"ITAU","processo":"5001143-11.2025.8.13.0329","recibo":3300.00,"honorarios":1369.50,"status":"recebido"},
        {"mes":"Mar/2025","cliente":"BERNADETE","reu":"ITAU","processo":"5001232-34.2025.8.13.0329","recibo":3000.00,"honorarios":1245.00,"status":"pendente"},
        {"mes":"Mar/2025","cliente":"ROSARIA","reu":"ITAU","processo":"5000000-50.2026.8.13.0329","recibo":5000.00,"honorarios":2075.00,"status":"recebido"},
        {"mes":"Mar/2025","cliente":"MARTA","reu":"ITAU","processo":"5001331-04.2025.8.13.0329","recibo":5000.00,"honorarios":2075.00,"status":"recebido"},
        {"mes":"Mar/2025","cliente":"JOSE","reu":"CARLOS","processo":"5000452-42.2026.8.13.0432","recibo":2500.00,"honorarios":2500.00,"status":"recebido"},
        {"mes":"Mar/2025","cliente":"TEREZINHA","reu":"ITAU","processo":"5000013-49.2026.8.13.0329","recibo":4000.00,"honorarios":1660.00,"status":"recebido"},
        {"mes":"Mar/2025","cliente":"LENITA","reu":"ITAU","processo":"5001328-49.2025.8.13.0329","recibo":3760.00,"honorarios":1560.40,"status":"recebido"},
        {"mes":"Mar/2025","cliente":"CLEIDE","reu":"ITAU","processo":"5001141-41.2025.8.13.0329","recibo":4500.00,"honorarios":2075.00,"status":"pendente"},
        {"mes":"Mar/2025","cliente":"LENITA","reu":"ITAU","processo":"5001327-64.2025.8.13.0329","recibo":5000.00,"honorarios":2075.00,"status":"recebido"},
        {"mes":"Mar/2025","cliente":"MARTA","reu":"ITAU","processo":"5000001-35.2026.8.13.0329","recibo":5000.00,"honorarios":2075.00,"status":"recebido"},
        {"mes":"Mar/2025","cliente":"MARTA","reu":"ITAU","processo":"5001333-71.2025.8.13.0329","recibo":5600.00,"honorarios":2324.00,"status":"recebido"},
        {"mes":"Abr/2025","cliente":"ELISABETE","reu":"ITAU","processo":"5001363-09.2025.8.13.0329","recibo":8237.44,"honorarios":2883.10,"status":"recebido"},
        {"mes":"Abr/2025","cliente":"JOÃO VAZ","reu":"ITAU","processo":"5001243-63.2025.8.13.0329","recibo":6442.64,"honorarios":2673.70,"status":"recebido"},
        {"mes":"Abr/2025","cliente":"CLEIDE","reu":"ITAU","processo":"5001149-18.2025.8.13.0329","recibo":5500.00,"honorarios":2282.50,"status":"recebido"},
        {"mes":"Abr/2025","cliente":"HELIO","reu":"ITAU","processo":"5008533-48.2025.8.13.0647","recibo":11000.00,"honorarios":4565.00,"status":"recebido"},
        {"mes":"Abr/2025","cliente":"MARTA","reu":"ITAU","processo":"5001193-37.2025.8.13.0329","recibo":4270.00,"honorarios":1772.00,"status":"recebido"},
        {"mes":"Mai/2025","cliente":"LENITA","reu":"ITAU","processo":"5000206-64.2026.8.13.0329","recibo":4320.68,"honorarios":1793.00,"status":"pendente"},
        {"mes":"Mai/2025","cliente":"JOÃO VAZ","reu":"ITAU","processo":"5001242-78.2025.8.13.0329","recibo":3000.00,"honorarios":1245.00,"status":"pendente"},
        {"mes":"Mai/2025","cliente":"CRISTINA/MILLENE","reu":"PROTESTO INDEVIDO","processo":"4010523-32.2026.8.26.0506","recibo":3000.00,"honorarios":3000.00,"status":"pendente"},
    ]

    # Despesas fixas: {categoria: {mes: valor}}
    fixas_dados = {
        "Aluguel":      {"Out":600,"Nov":280.80,"Dez":600,"Jan":600,"Fev":600,"Mar":600,"Abr":600,"Mai":600},
        "Água":         {"Nov":27.18,"Jan":27.28,"Fev":24.78,"Mar":28.46,"Abr":25.77},
        "Força":        {"Dez":103.22,"Jan":98.75,"Mar":94.05},
        "Internet":     {"Out":110.83,"Nov":79.90,"Dez":79.90,"Jan":79.90,"Fev":79.90,"Mar":79.90,"Abr":79.90,"Mai":79.90},
        "Funcionário 1":{},
        "Funcionário 2":{},
    }

    # Despesas variáveis
    variaveis = [
        {"descricao":"Poltronas","valor":750.00,"parcelas":"10x","quem":"Eduarda","onde":"Shopee","meses":{"Out":75,"Nov":75,"Dez":75,"Jan":75,"Fev":75,"Mar":75,"Abr":75,"Mai":75,"Jun":75,"Jul":75}},
        {"descricao":"Cortina 1,7x1,7","valor":320.00,"parcelas":"8x","quem":"Eduarda","onde":"Mercado Livre","meses":{"Nov":40,"Dez":40,"Jan":40,"Fev":40,"Mar":40,"Abr":40,"Mai":40,"Jun":40}},
        {"descricao":"Banner","valor":151.44,"parcelas":"7x","quem":"Eduarda","onde":"Mercado Livre","meses":{"Nov":21.63,"Dez":21.63,"Jan":21.63,"Fev":21.63,"Mar":21.63,"Abr":21.63,"Mai":21.63}},
        {"descricao":"Impressora","valor":1677.00,"parcelas":"10x","quem":"Eduarda","onde":"Mercado Livre","meses":{"Mar":167.70,"Abr":167.70,"Mai":167.70,"Jun":167.70,"Jul":167.70,"Ago":167.70,"Set":167.70,"Out":167.70,"Nov":167.70,"Dez":167.70}},
        {"descricao":"OAB/MG","valor":950.40,"parcelas":"12x","quem":"Adriely","onde":"OAB","meses":{"Fev":79.20,"Mar":79.21,"Abr":79.21,"Mai":79.21,"Jun":79.21,"Jul":79.21,"Ago":79.21,"Set":79.21,"Out2":79.21,"Nov2":79.21,"Dez2":79.21}},
        {"descricao":"Envelope/cápsula/porta treco","valor":227.95,"parcelas":"3x","quem":"Adriely","onde":"Shopee","meses":{"Mar":75.98,"Abr":75.98,"Mai":75.98}},
        {"descricao":"Mangueira","valor":35.30,"parcelas":"1x","quem":"Adriely","onde":"Mercado Livre","meses":{"Mai":35.30}},
        {"descricao":"Cápsulas Itallé","valor":89.29,"parcelas":"1x","quem":"Adriely","onde":"Mercado Livre","meses":{"Mai":89.29}},
        {"descricao":"Filtro de água","valor":552.80,"parcelas":"10x","quem":"Eduarda","onde":"Mercado Livre","meses":{"Mai":55.28,"Jun":55.28,"Jul":55.28,"Ago":55.28,"Set":55.28,"Out":55.28,"Nov":55.28,"Dez":55.28}},
        {"descricao":"Mercado ABC","valor":75.87,"parcelas":"1x","quem":"Adriely","onde":"ABC","meses":{"Abr":75.87}},
        {"descricao":"Terra e pedras","valor":53.00,"parcelas":"1x","quem":"Adriely","onde":"Floricultura","meses":{"Abr":53.00}},
        {"descricao":"Fitas","valor":76.66,"parcelas":"1x","quem":"Eduarda","onde":"Mercado Livre","meses":{"Abr":76.66}},
        {"descricao":"Compras limpeza (rodo/pá/cheirinho)","valor":46.87,"parcelas":"1x","quem":"Adriely","onde":"ABC","meses":{"Abr":46.87}},
        {"descricao":"Tampa do vaso","valor":73.69,"parcelas":"1x","quem":"Adriely","onde":"Mercado Livre","meses":{"Out":73.69}},
        {"descricao":"Mercado 30/08","valor":68.08,"parcelas":"1x","quem":"Eduarda","onde":"Mercado","meses":{"Out":68.08}},
        {"descricao":"Chaveiro","valor":80.00,"parcelas":"1x","quem":"Adriely","onde":"Chaveiro","meses":{"Out":80.00}},
        {"descricao":"João Gabriel (faxina)","valor":150.00,"parcelas":"1x","quem":"Eduarda","onde":"Faxina","meses":{"Out":150.00}},
        {"descricao":"Bianca (iniciais)","valor":250.00,"parcelas":"1x","quem":"Adriely","onde":"Iniciais","meses":{"Out":250.00}},
        {"descricao":"Felipe (eletricista)","valor":319.20,"parcelas":"1x","quem":"Adriely","onde":"Eletricista","meses":{"Nov":319.20}},
        {"descricao":"Varão Cortina","valor":40.00,"parcelas":"1x","quem":"Eduarda","onde":"Zé Natal","meses":{"Dez":40.00}},
        {"descricao":"Cortina Sala","valor":157.50,"parcelas":"2x","quem":"Eduarda","onde":"Shopee","meses":{"Nov":78.75,"Dez":78.75}},
        {"descricao":"Pasta e impressões","valor":51.85,"parcelas":"1x","quem":"Adriely","onde":"Uno & Due","meses":{"Dez":51.85}},
        {"descricao":"Mercado 29/11/25","valor":66.46,"parcelas":"1x","quem":"Adriely","onde":"ABC","meses":{"Dez":66.46}},
        {"descricao":"Pasta 03/12/25","valor":26.90,"parcelas":"1x","quem":"Adriely","onde":"Uno & Due","meses":{"Dez":26.90}},
        {"descricao":"Espelho, nicho e placa","valor":233.91,"parcelas":"3x","quem":"Eduarda","onde":"Shopee","meses":{"Nov":77.97,"Dez":77.97,"Jan":77.97}},
        {"descricao":"Mesa","valor":750.92,"parcelas":"4x","quem":"Eduarda","onde":"Mercado Livre","meses":{"Out":187.70,"Nov":187.70,"Dez":187.70,"Jan":187.70}},
        {"descricao":"Felipe (instalação e campainha)","valor":160.00,"parcelas":"1x","quem":"dividido","onde":"","meses":{"Mar":160.00}},
        {"descricao":"Cadeiras","valor":381.18,"parcelas":"6x","quem":"Adriely","onde":"Shopee","meses":{"Out":63.53,"Nov":63.53,"Dez":63.53,"Jan":63.53,"Fev":63.53,"Mar":63.53}},
        {"descricao":"Placa, fita e tapete","valor":224.59,"parcelas":"3x","quem":"Eduarda","onde":"Shopee","meses":{"Dez":74.86,"Jan":74.86,"Fev":74.86}},
        {"descricao":"Impressão","valor":30.00,"parcelas":"1x","quem":"Adriely","onde":"Tecmania","meses":{"Fev":30.00}},
        {"descricao":"Cartão de visita","valor":69.00,"parcelas":"1x","quem":"Adriely","onde":"Canva","meses":{"Fev":69.00}},
        {"descricao":"Bianca (café)","valor":17.00,"parcelas":"1x","quem":"Adriely","onde":"Via Caffè","meses":{"Fev":17.00}},
        {"descricao":"Impressão","valor":9.60,"parcelas":"1x","quem":"Eduarda","onde":"Uno & Due","meses":{"Fev":9.60}},
        {"descricao":"Vaso de planta","valor":55.44,"parcelas":"1x","quem":"Adriely","onde":"Shopee","meses":{"Abr":55.44}},
        {"descricao":"Mão francesa suporte","valor":40.84,"parcelas":"1x","quem":"Adriely","onde":"Mercado Livre","meses":{"Abr":40.84}},
        {"descricao":"Copos","valor":6.50,"parcelas":"1x","quem":"Adriely","onde":"MegaShopping","meses":{"Abr":6.50}},
        {"descricao":"Cápsula, pendente e porta pasta","valor":134.39,"parcelas":"1x","quem":"Adriely","onde":"Shopee","meses":{"Abr":134.39}},
    ]

    return {
        "receitas": receitas,
        "fixas": fixas_dados,
        "variaveis": variaveis,
    }

def carregar_dados():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return dados_iniciais()

def salvar_dados(d):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)

# ── Session state ─────────────────────────────────────────────────────────
if "dados" not in st.session_state:
    st.session_state.dados = carregar_dados()

dados = st.session_state.dados

# ── Cabeçalho ─────────────────────────────────────────────────────────────
st.markdown("""
<div style='text-align:center; padding: 24px 0 8px 0'>
  <h1 style='font-size:28px; font-weight:700; margin:0; color:#e8eaf6;
      background: linear-gradient(90deg,#5c6bc0,#42a5f5);
      -webkit-background-clip:text; -webkit-text-fill-color:transparent;'>
    💼 CONTROLE FINANCEIRO – ESCRITÓRIO
  </h1>
  <p style='color:#5c6bc0; font-size:13px; margin-top:4px;'>
    Sócias: Adriely &amp; Eduarda
  </p>
</div>
""", unsafe_allow_html=True)

# ── Abas ──────────────────────────────────────────────────────────────────
tab_dash, tab_rec, tab_fix, tab_var, tab_bal = st.tabs([
    "📊 Dashboard", "💰 Receitas", "🏢 Desp. Fixas", "🛒 Desp. Variáveis", "⚖️ Balanço das Sócias"
])

# ──────────────────────────────────────────────────────────────────────────
# Helpers de cálculo
# ──────────────────────────────────────────────────────────────────────────
def totais_por_mes():
    """Retorna dict mes → {recibo, honorarios, fixas, variaveis}"""
    res = {m: {"recibo":0,"honorarios":0,"fixas":0,"variaveis":0} for m in MESES_ORDEM}

    for r in dados["receitas"]:
        m = r.get("mes","")
        if m in res:
            res[m]["recibo"]     += float(r.get("recibo",0) or 0)
            res[m]["honorarios"] += float(r.get("honorarios",0) or 0)

    # fixas: mapear col → mes completo
    col_to_mes = {
        "Out":"Out/2024","Nov":"Nov/2024","Dez":"Dez/2024",
        "Jan":"Jan/2025","Fev":"Fev/2025","Mar":"Mar/2025","Abr":"Abr/2025",
        "Mai":"Mai/2025","Jun":"Jun/2025","Jul":"Jul/2025",
        "Ago":"Ago/2025","Set":"Set/2025","Out2":"Out/2025","Nov2":"Nov/2025","Dez2":"Dez/2025",
    }
    for cat, meses in dados["fixas"].items():
        for col, val in meses.items():
            m = col_to_mes.get(col,"")
            if m in res:
                res[m]["fixas"] += float(val or 0)

    for item in dados["variaveis"]:
        for col, val in item.get("meses",{}).items():
            m = col_to_mes.get(col,"")
            if m in res:
                res[m]["variaveis"] += float(val or 0)

    return res

# ──────────────────────────────────────────────────────────────────────────
# DASHBOARD
# ──────────────────────────────────────────────────────────────────────────
with tab_dash:
    totais = totais_por_mes()

    # cards de totais gerais (somente meses com dados)
    total_recibo   = sum(v["recibo"]     for v in totais.values())
    total_honor    = sum(v["honorarios"] for v in totais.values())
    total_fixas    = sum(v["fixas"]      for v in totais.values())
    total_variaveis= sum(v["variaveis"]  for v in totais.values())
    total_despesas = total_fixas + total_variaveis
    saldo_geral    = total_honor - total_despesas

    c1,c2,c3,c4,c5 = st.columns(5)
    with c1:
        st.markdown(f"""<div class="bloco">
            <div class="card-titulo">Recibo Bruto Total</div>
            <div class="card-valor azul">{_fmt(total_recibo)}</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="bloco">
            <div class="card-titulo">Honorários Total</div>
            <div class="card-valor verde">{_fmt(total_honor)}</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="bloco">
            <div class="card-titulo">Desp. Fixas Total</div>
            <div class="card-valor laranja">{_fmt(total_fixas)}</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""<div class="bloco">
            <div class="card-titulo">Desp. Variáveis Total</div>
            <div class="card-valor laranja">{_fmt(total_variaveis)}</div>
        </div>""", unsafe_allow_html=True)
    with c5:
        cor = "verde" if saldo_geral >= 0 else "vermelho"
        st.markdown(f"""<div class="bloco">
            <div class="card-titulo">Saldo Líquido</div>
            <div class="card-valor {cor}">{_fmt(saldo_geral)}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # tabela por mês
    meses_com_dados = [m for m in MESES_ORDEM if
        totais[m]["recibo"] + totais[m]["honorarios"] +
        totais[m]["fixas"] + totais[m]["variaveis"] > 0]

    if meses_com_dados:
        st.markdown("### Resumo por Mês")
        header = "| Mês | Recibo Bruto | Honorários | Desp. Fixas | Desp. Variáveis | Saldo |"
        sep    = "|---|---|---|---|---|---|"
        rows   = []
        for m in meses_com_dados:
            t = totais[m]
            saldo = t["honorarios"] - t["fixas"] - t["variaveis"]
            s = "🟢" if saldo >= 0 else "🔴"
            rows.append(f"| {m} | {_fmt(t['recibo'])} | {_fmt(t['honorarios'])} | {_fmt(t['fixas'])} | {_fmt(t['variaveis'])} | {s} {_fmt(saldo)} |")
        st.markdown(header + "\n" + sep + "\n" + "\n".join(rows))

    # clientes pendentes
    pendentes = [r for r in dados["receitas"] if r.get("status") == "pendente"]
    if pendentes:
        st.markdown("### ⚠️ Receitas Pendentes")
        for p in pendentes:
            st.markdown(f"""<div class="bloco" style="border-color:#b71c1c;">
                <span style="color:#ef5350;font-weight:600;">{p.get('cliente','')}</span>
                &nbsp;|&nbsp; {p.get('mes','')}
                &nbsp;|&nbsp; Honorários: <strong>{_fmt(p.get('honorarios',0))}</strong>
                &nbsp;|&nbsp; <span style="font-size:11px;color:#7986cb;">{p.get('processo','')}</span>
            </div>""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────
# RECEITAS
# ──────────────────────────────────────────────────────────────────────────
with tab_rec:
    st.markdown("### Receitas por Cliente")

    col_add, col_save = st.columns([6,1])
    with col_add:
        if st.button("➕ Nova Receita"):
            dados["receitas"].append({
                "mes": MESES_ORDEM[0],
                "cliente":"","reu":"","processo":"",
                "recibo":0.0,"honorarios":0.0,"status":"pendente"
            })
            salvar_dados(dados)
            st.rerun()
    with col_save:
        if st.button("💾 Salvar"):
            salvar_dados(dados)
            st.success("Salvo!")

    # cabeçalho da tabela
    hdr = st.columns([1.5, 2, 1.5, 3, 1.5, 1.5, 1.2, 0.5])
    labels = ["Mês","Cliente","Réu","Processo","Recibo Bruto","Honorários","Status",""]
    for col, lbl in zip(hdr, labels):
        col.markdown(f"<span style='font-size:11px;color:#7986cb;font-weight:600;'>{lbl}</span>", unsafe_allow_html=True)

    to_del = None
    for i, r in enumerate(dados["receitas"]):
        cols = st.columns([1.5, 2, 1.5, 3, 1.5, 1.5, 1.2, 0.5])

        novo_mes = cols[0].selectbox("", MESES_ORDEM,
            index=MESES_ORDEM.index(r["mes"]) if r.get("mes") in MESES_ORDEM else 0,
            key=f"r_mes_{i}", label_visibility="collapsed")

        novo_cli = cols[1].text_input("", value=r.get("cliente",""), key=f"r_cli_{i}", label_visibility="collapsed")
        novo_reu = cols[2].text_input("", value=r.get("reu",""), key=f"r_reu_{i}", label_visibility="collapsed")
        novo_proc = cols[3].text_input("", value=r.get("processo",""), key=f"r_proc_{i}", label_visibility="collapsed")

        # campos de valor
        _rb_str = st.session_state.get(f"r_rb_{i}", _vs(r.get("recibo",0)))
        novo_rb_str = cols[4].text_input("", value=_rb_str, placeholder="0,00", key=f"r_rb_{i}", label_visibility="collapsed")
        try:
            novo_rb = float(novo_rb_str.replace(".","").replace(",",".")) if novo_rb_str else 0.0
        except: novo_rb = 0.0

        _rh_str = st.session_state.get(f"r_rh_{i}", _vs(r.get("honorarios",0)))
        novo_rh_str = cols[5].text_input("", value=_rh_str, placeholder="0,00", key=f"r_rh_{i}", label_visibility="collapsed")
        try:
            novo_rh = float(novo_rh_str.replace(".","").replace(",",".")) if novo_rh_str else 0.0
        except: novo_rh = 0.0

        novo_st = cols[6].selectbox("", ["recebido","pendente"],
            index=0 if r.get("status","") == "recebido" else 1,
            key=f"r_st_{i}", label_visibility="collapsed")

        if cols[7].button("🗑️", key=f"r_del_{i}"):
            to_del = i

        dados["receitas"][i].update({
            "mes": novo_mes, "cliente": novo_cli, "reu": novo_reu,
            "processo": novo_proc, "recibo": novo_rb,
            "honorarios": novo_rh, "status": novo_st,
        })

    if to_del is not None:
        dados["receitas"].pop(to_del)
        salvar_dados(dados)
        st.rerun()

    # totais da aba
    total_r = sum(float(r.get("recibo",0) or 0) for r in dados["receitas"])
    total_h = sum(float(r.get("honorarios",0) or 0) for r in dados["receitas"])
    rec = sum(1 for r in dados["receitas"] if r.get("status") == "recebido")
    pend = len(dados["receitas"]) - rec
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    tc1,tc2,tc3,tc4 = st.columns(4)
    tc1.metric("Total Recibo Bruto", _fmt(total_r))
    tc2.metric("Total Honorários", _fmt(total_h))
    tc3.metric("Recebidos", rec)
    tc4.metric("Pendentes", pend)

# ──────────────────────────────────────────────────────────────────────────
# DESPESAS FIXAS
# ──────────────────────────────────────────────────────────────────────────
with tab_fix:
    st.markdown("### Despesas Fixas Mensais")

    # mapear MESES_FIXAS_COLS → rótulos legíveis
    col_labels = {
        "Out":"Out/24","Nov":"Nov/24","Dez":"Dez/24",
        "Jan":"Jan/25","Fev":"Fev/25","Mar":"Mar/25","Abr":"Abr/25",
        "Mai":"Mai/25","Jun":"Jun/25","Jul":"Jul/25",
        "Ago":"Ago/25","Set":"Set/25","Out2":"Out/25","Nov2":"Nov/25","Dez2":"Dez/25",
    }

    # botão adicionar categoria
    col_nova, col_sv = st.columns([5,1])
    with col_nova:
        nova_cat = st.text_input("Nova categoria:", key="nova_fix_cat", placeholder="Ex: Contador")
    if st.button("➕ Adicionar Categoria") and nova_cat.strip():
        if nova_cat.strip() not in dados["fixas"]:
            dados["fixas"][nova_cat.strip()] = {}
            salvar_dados(dados)
            st.rerun()
    with col_sv:
        if st.button("💾 Salvar ", key="sv_fix"):
            salvar_dados(dados)
            st.success("Salvo!")

    # mostrar os últimos 8 meses para não ficar muito largo
    COLS_VIS = ["Out","Nov","Dez","Jan","Fev","Mar","Abr","Mai"]

    # cabeçalho
    hdr_cols = st.columns([2] + [1]*len(COLS_VIS) + [1, 0.5])
    hdr_cols[0].markdown("<span style='font-size:11px;color:#7986cb;font-weight:600;'>CATEGORIA</span>", unsafe_allow_html=True)
    for idx, c in enumerate(COLS_VIS):
        hdr_cols[idx+1].markdown(f"<span style='font-size:11px;color:#7986cb;font-weight:600;'>{col_labels[c]}</span>", unsafe_allow_html=True)
    hdr_cols[-2].markdown("<span style='font-size:11px;color:#7986cb;font-weight:600;'>TOTAL</span>", unsafe_allow_html=True)
    hdr_cols[-1].markdown("")

    cats_del = None
    totais_col = {c: 0.0 for c in COLS_VIS}

    for cat in list(dados["fixas"].keys()):
        row_cols = st.columns([2] + [1]*len(COLS_VIS) + [1, 0.5])
        row_cols[0].markdown(f"<div style='padding-top:8px;font-size:13px;'>{cat}</div>", unsafe_allow_html=True)
        total_cat = 0.0
        for idx, col in enumerate(COLS_VIS):
            cur = dados["fixas"][cat].get(col, 0)
            cur_str = st.session_state.get(f"fx_{cat}_{col}", _vs(cur))
            val_str = row_cols[idx+1].text_input("", value=cur_str, placeholder="0,00",
                key=f"fx_{cat}_{col}", label_visibility="collapsed")
            try:
                val = float(val_str.replace(".","").replace(",",".")) if val_str else 0.0
            except: val = 0.0
            dados["fixas"][cat][col] = val
            total_cat += val
            totais_col[col] += val
        row_cols[-2].markdown(f"<div style='padding-top:8px;font-size:13px;font-weight:600;color:#ffa726;'>{_fmt(total_cat)}</div>", unsafe_allow_html=True)
        if row_cols[-1].button("🗑️", key=f"fx_del_{cat}"):
            cats_del = cat

    # linha de totais
    tot_row = st.columns([2] + [1]*len(COLS_VIS) + [1, 0.5])
    tot_row[0].markdown("<strong style='color:#7986cb;'>TOTAL</strong>", unsafe_allow_html=True)
    for idx, col in enumerate(COLS_VIS):
        tot_row[idx+1].markdown(f"<strong style='color:#ffa726;font-size:12px;'>{_fmt(totais_col[col])}</strong>", unsafe_allow_html=True)

    if cats_del:
        del dados["fixas"][cats_del]
        salvar_dados(dados)
        st.rerun()

# ──────────────────────────────────────────────────────────────────────────
# DESPESAS VARIÁVEIS
# ──────────────────────────────────────────────────────────────────────────
with tab_var:
    st.markdown("### Despesas Variáveis")

    cva, cvs = st.columns([6,1])
    with cva:
        if st.button("➕ Nova Despesa Variável"):
            dados["variaveis"].append({
                "descricao":"","valor":0.0,"parcelas":"1x",
                "quem":"Adriely","onde":"","meses":{}
            })
            salvar_dados(dados)
            st.rerun()
    with cvs:
        if st.button("💾 Salvar  ", key="sv_var"):
            salvar_dados(dados)
            st.success("Salvo!")

    # filtro por sócia
    filtro_quem = st.selectbox("Filtrar por:", ["Todas","Adriely","Eduarda","dividido"], key="filtro_var")

    COLS_VIS_V = ["Out","Nov","Dez","Jan","Fev","Mar","Abr","Mai"]
    col_labels_v = {
        "Out":"Out/24","Nov":"Nov/24","Dez":"Dez/24",
        "Jan":"Jan/25","Fev":"Fev/25","Mar":"Mar/25","Abr":"Abr/25",
        "Mai":"Mai/25",
    }

    # cabeçalho
    hcols = st.columns([3, 1.2, 1, 1.2, 1.2] + [0.9]*len(COLS_VIS_V) + [1, 0.4])
    for lbl, col in zip(["Descrição","Valor Total","Parcelas","Quem Pagou","Onde Comprou"]+
                         [col_labels_v[c] for c in COLS_VIS_V]+["Total",""], hcols):
        col.markdown(f"<span style='font-size:10px;color:#7986cb;font-weight:600;'>{lbl}</span>", unsafe_allow_html=True)

    to_del_v = None
    totais_v_col = {c: 0.0 for c in COLS_VIS_V}
    totais_adriely = {c: 0.0 for c in COLS_VIS_V}
    totais_eduarda = {c: 0.0 for c in COLS_VIS_V}

    for i, item in enumerate(dados["variaveis"]):
        quem = item.get("quem","Adriely")
        if filtro_quem != "Todas" and quem != filtro_quem:
            continue

        vcols = st.columns([3, 1.2, 1, 1.2, 1.2] + [0.9]*len(COLS_VIS_V) + [1, 0.4])

        desc = vcols[0].text_input("", value=item.get("descricao",""), key=f"vd_{i}", label_visibility="collapsed")
        vstr = st.session_state.get(f"vv_{i}", _vs(item.get("valor",0)))
        vstr_new = vcols[1].text_input("", value=vstr, placeholder="0,00", key=f"vv_{i}", label_visibility="collapsed")
        try:
            vval = float(vstr_new.replace(".","").replace(",",".")) if vstr_new else 0.0
        except: vval = 0.0
        parc = vcols[2].text_input("", value=item.get("parcelas","1x"), key=f"vp_{i}", label_visibility="collapsed")
        quem_new = vcols[3].selectbox("", ["Adriely","Eduarda","dividido"],
            index=["Adriely","Eduarda","dividido"].index(quem) if quem in ["Adriely","Eduarda","dividido"] else 0,
            key=f"vq_{i}", label_visibility="collapsed")
        onde = vcols[4].text_input("", value=item.get("onde",""), key=f"vo_{i}", label_visibility="collapsed")

        total_item = 0.0
        for idx, col in enumerate(COLS_VIS_V):
            cur = item.get("meses",{}).get(col, 0)
            cstr = st.session_state.get(f"vm_{i}_{col}", _vs(cur))
            cstr_new = vcols[5+idx].text_input("", value=cstr, placeholder="0,00",
                key=f"vm_{i}_{col}", label_visibility="collapsed")
            try:
                cval = float(cstr_new.replace(".","").replace(",",".")) if cstr_new else 0.0
            except: cval = 0.0
            if "meses" not in dados["variaveis"][i]:
                dados["variaveis"][i]["meses"] = {}
            dados["variaveis"][i]["meses"][col] = cval
            total_item += cval
            totais_v_col[col] += cval
            if quem_new == "Adriely":
                totais_adriely[col] += cval
            elif quem_new == "Eduarda":
                totais_eduarda[col] += cval

        vcols[-2].markdown(f"<div style='padding-top:8px;font-size:12px;font-weight:600;color:#ffa726;'>{_fmt(total_item)}</div>", unsafe_allow_html=True)
        if vcols[-1].button("🗑️", key=f"vdel_{i}"):
            to_del_v = i

        dados["variaveis"][i].update({
            "descricao": desc, "valor": vval,
            "parcelas": parc, "quem": quem_new, "onde": onde,
        })

    # totais
    tot_vrow = st.columns([3, 1.2, 1, 1.2, 1.2] + [0.9]*len(COLS_VIS_V) + [1, 0.4])
    tot_vrow[0].markdown("<strong style='color:#7986cb;'>TOTAL</strong>", unsafe_allow_html=True)
    for idx, col in enumerate(COLS_VIS_V):
        tot_vrow[5+idx].markdown(f"<strong style='color:#ffa726;font-size:11px;'>{_fmt(totais_v_col[col])}</strong>", unsafe_allow_html=True)

    if to_del_v is not None:
        dados["variaveis"].pop(to_del_v)
        salvar_dados(dados)
        st.rerun()

# ──────────────────────────────────────────────────────────────────────────
# BALANÇO DAS SÓCIAS
# ──────────────────────────────────────────────────────────────────────────
with tab_bal:
    st.markdown("### Balanço por Sócia")

    COLS_VIS_B = ["Out","Nov","Dez","Jan","Fev","Mar","Abr","Mai"]
    col_to_mes = {
        "Out":"Out/2024","Nov":"Nov/2024","Dez":"Dez/2024",
        "Jan":"Jan/2025","Fev":"Fev/2025","Mar":"Mar/2025","Abr":"Abr/2025",
        "Mai":"Mai/2025",
    }

    # honorários por mês
    honorarios_mes = {c: 0.0 for c in COLS_VIS_B}
    for r in dados["receitas"]:
        m_full = r.get("mes","")
        for c, mf in col_to_mes.items():
            if mf == m_full:
                honorarios_mes[c] += float(r.get("honorarios",0) or 0)

    # gastos por sócia por mês
    adriely_gasto = {c: 0.0 for c in COLS_VIS_B}
    eduarda_gasto = {c: 0.0 for c in COLS_VIS_B}

    for item in dados["variaveis"]:
        quem = item.get("quem","")
        for c in COLS_VIS_B:
            val = float(item.get("meses",{}).get(c, 0) or 0)
            if quem == "Adriely":
                adriely_gasto[c] += val
            elif quem == "Eduarda":
                eduarda_gasto[c] += val
            elif quem == "dividido":
                adriely_gasto[c] += val / 2
                eduarda_gasto[c] += val / 2

    # fixas: dividido meio a meio
    for cat, meses in dados["fixas"].items():
        for c in COLS_VIS_B:
            val = float(meses.get(c, 0) or 0)
            adriely_gasto[c] += val / 2
            eduarda_gasto[c] += val / 2

    # exibir
    col_labels_b = {"Out":"Out/24","Nov":"Nov/24","Dez":"Dez/24",
                    "Jan":"Jan/25","Fev":"Fev/25","Mar":"Mar/25","Abr":"Abr/25","Mai":"Mai/25"}

    meses_btn = st.columns(len(COLS_VIS_B))
    mes_sel = st.radio("Mês:", COLS_VIS_B, horizontal=True,
        format_func=lambda x: col_labels_b[x], key="bal_mes_sel")

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    honor = honorarios_mes[mes_sel]
    a_gasto = adriely_gasto[mes_sel]
    e_gasto = eduarda_gasto[mes_sel]
    total_gasto = a_gasto + e_gasto
    honor_cada = honor / 2

    c1,c2,c3 = st.columns(3)
    with c1:
        st.markdown(f"""<div class="bloco">
            <div class="card-titulo">Honorários do Mês</div>
            <div class="card-valor azul">{_fmt(honor)}</div>
            <div style="color:#5c6bc0;font-size:12px;margin-top:4px;">
                Cada sócia: {_fmt(honor_cada)}
            </div>
        </div>""", unsafe_allow_html=True)
    with c2:
        saldo_a = honor_cada - a_gasto
        cor_a = "verde" if saldo_a >= 0 else "vermelho"
        st.markdown(f"""<div class="bloco">
            <div class="card-titulo">Adriely</div>
            <div style="font-size:13px;color:#9fa8da;">Gastos: {_fmt(a_gasto)}</div>
            <div style="font-size:13px;color:#9fa8da;">Recebe: {_fmt(honor_cada)}</div>
            <div class="card-valor {cor_a}" style="font-size:22px;">{_fmt(saldo_a)}</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        saldo_e = honor_cada - e_gasto
        cor_e = "verde" if saldo_e >= 0 else "vermelho"
        st.markdown(f"""<div class="bloco">
            <div class="card-titulo">Eduarda</div>
            <div style="font-size:13px;color:#9fa8da;">Gastos: {_fmt(e_gasto)}</div>
            <div style="font-size:13px;color:#9fa8da;">Recebe: {_fmt(honor_cada)}</div>
            <div class="card-valor {cor_e}" style="font-size:22px;">{_fmt(saldo_e)}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### Acumulado Geral")

    total_honor_all = sum(honorarios_mes.values())
    total_a = sum(adriely_gasto.values())
    total_e = sum(eduarda_gasto.values())
    honor_cada_total = total_honor_all / 2

    bc1,bc2,bc3 = st.columns(3)
    with bc1:
        st.markdown(f"""<div class="bloco">
            <div class="card-titulo">Total Honorários</div>
            <div class="card-valor azul">{_fmt(total_honor_all)}</div>
            <div style="color:#5c6bc0;font-size:12px;margin-top:4px;">
                Cada sócia: {_fmt(honor_cada_total)}
            </div>
        </div>""", unsafe_allow_html=True)
    with bc2:
        saldo_at = honor_cada_total - total_a
        cor_at = "verde" if saldo_at >= 0 else "vermelho"
        st.markdown(f"""<div class="bloco">
            <div class="card-titulo">Adriely – Acumulado</div>
            <div style="font-size:13px;color:#9fa8da;">Total gasto: {_fmt(total_a)}</div>
            <div class="card-valor {cor_at}" style="font-size:22px;">{_fmt(saldo_at)}</div>
        </div>""", unsafe_allow_html=True)
    with bc3:
        saldo_et = honor_cada_total - total_e
        cor_et = "verde" if saldo_et >= 0 else "vermelho"
        st.markdown(f"""<div class="bloco">
            <div class="card-titulo">Eduarda – Acumulado</div>
            <div style="font-size:13px;color:#9fa8da;">Total gasto: {_fmt(total_e)}</div>
            <div class="card-valor {cor_et}" style="font-size:22px;">{_fmt(saldo_et)}</div>
        </div>""", unsafe_allow_html=True)

    # detalhe de quem pagou mais
    if abs(total_a - total_e) > 0.01:
        diff = abs(total_a - total_e)
        quem_mais = "Adriely" if total_a > total_e else "Eduarda"
        st.markdown(f"""<div class="bloco" style="border-color:#ffa726;margin-top:12px;">
            <span style="color:#ffa726;font-weight:600;">⚠️ Diferença de gastos:</span>
            <strong>{quem_mais}</strong> pagou <strong>{_fmt(diff)}</strong> a mais que a outra sócia no período.
            Para equalizar, <strong>{'Eduarda' if quem_mais=='Adriely' else 'Adriely'}</strong>
            deve <strong>{_fmt(diff/2)}</strong> para <strong>{quem_mais}</strong>.
        </div>""", unsafe_allow_html=True)

    # botão exportar resumo
    if st.button("📋 Copiar Resumo"):
        linhas = ["BALANÇO DAS SÓCIAS – ESCRITÓRIO\n"]
        linhas.append(f"Total Honorários: {_fmt(total_honor_all)}")
        linhas.append(f"Adriely gastou: {_fmt(total_a)} | Saldo: {_fmt(honor_cada_total - total_a)}")
        linhas.append(f"Eduarda gastou: {_fmt(total_e)} | Saldo: {_fmt(honor_cada_total - total_e)}")
        if abs(total_a - total_e) > 0.01:
            diff = abs(total_a - total_e)
            quem_mais = "Adriely" if total_a > total_e else "Eduarda"
            linhas.append(f"\n{quem_mais} pagou R$ {diff:.2f} a mais.")
        st.code("\n".join(linhas))
