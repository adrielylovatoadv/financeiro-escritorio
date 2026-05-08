import streamlit as st
import json
import os
import streamlit.components.v1 as _components

st.set_page_config(page_title="Financeiro – Escritório", page_icon="💼", layout="wide")

# ── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif;}
.main,.stApp{background:#0a0f1e;color:#e8eaf6;}
section[data-testid="stSidebar"]{background:#0d1427;}
.bloco{background:linear-gradient(135deg,#0d1b3e 0%,#1a2a5e 100%);
       border:1px solid #2a3f7e;border-radius:12px;padding:20px;margin:8px 0;}
.card-titulo{font-size:11px;font-weight:600;color:#7986cb;text-transform:uppercase;
             letter-spacing:1px;margin-bottom:4px;}
.card-valor{font-size:26px;font-weight:700;color:#e8eaf6;}
.card-valor.verde{color:#4caf50;} .card-valor.vermelho{color:#ef5350;}
.card-valor.azul{color:#42a5f5;}  .card-valor.laranja{color:#ffa726;}
.stTabs [data-baseweb="tab-list"]{background:#0d1427;border-radius:10px;padding:4px;gap:4px;}
.stTabs [data-baseweb="tab"]{background:transparent;color:#7986cb;border-radius:8px;
                              font-weight:500;font-size:13px;}
.stTabs [aria-selected="true"]{background:linear-gradient(135deg,#1a2a6c,#3949ab)!important;
                                color:white!important;}
.stButton>button{background:linear-gradient(135deg,#1a2a6c,#3949ab);color:white;
                 border:none;border-radius:8px;font-weight:600;padding:8px 20px;}
.stTextInput>div>div>input,.stSelectbox>div>div>div{
    background:#1a2a5e!important;border:1px solid #2a3f7e!important;
    color:#e8eaf6!important;border-radius:8px!important;}
h1,h2,h3{color:#e8eaf6;}
.divider{border:none;border-top:1px solid #2a3f7e;margin:16px 0;}
.badge-pago{display:inline-block;padding:2px 10px;border-radius:20px;
            font-size:11px;font-weight:600;background:#1b5e20;color:#a5d6a7;}
.badge-pendente{display:inline-block;padding:2px 10px;border-radius:20px;
                font-size:11px;font-weight:600;background:#b71c1c;color:#ef9a9a;}
.badge-adriely{display:inline-block;padding:2px 10px;border-radius:20px;
               font-size:11px;font-weight:600;background:#1a237e;color:#9fa8da;}
.badge-eduarda{display:inline-block;padding:2px 10px;border-radius:20px;
               font-size:11px;font-weight:600;background:#1b5e20;color:#a5d6a7;}
</style>
""", unsafe_allow_html=True)

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
      fire(input,integer+','+cents); input._busy=false;
    });
  }
  function apply(){
    window.parent.document.querySelectorAll('input[placeholder="0,00"]').forEach(currencyMask);
  }
  apply();
  new MutationObserver(apply).observe(window.parent.document.body,{childList:true,subtree:true});
})();
</script>
""", height=0)

# ── Persistência ──────────────────────────────────────────────────────────────
DATA_FILE = os.path.join(os.path.dirname(__file__), "financeiro_data.json")

MESES = ["Out/2025","Nov/2025","Dez/2025",
         "Jan/2026","Fev/2026","Mar/2026","Abr/2026","Mai/2026","Jun/2026",
         "Jul/2026","Ago/2026","Set/2026","Out/2026","Nov/2026","Dez/2026",
         "Jan/2027","Fev/2027","Mar/2027","Abr/2027","Mai/2027","Jun/2027",
         "Jul/2027","Ago/2027","Set/2027","Out/2027","Nov/2027","Dez/2027"]

COL_FIXAS = ["Out","Nov","Dez","Jan","Fev","Mar","Abr","Mai",
             "Jun","Jul","Ago","Set","Out2","Nov2","Dez2"]
COL_TO_MES = {
    "Out":"Out/2025","Nov":"Nov/2025","Dez":"Dez/2025",
    "Jan":"Jan/2026","Fev":"Fev/2026","Mar":"Mar/2026","Abr":"Abr/2026",
    "Mai":"Mai/2026","Jun":"Jun/2026","Jul":"Jul/2026","Ago":"Ago/2026",
    "Set":"Set/2026","Out2":"Out/2026","Nov2":"Nov/2026","Dez2":"Dez/2026",
}

def _v(s):
    import re
    if s is None: return 0.0
    s = re.sub(r'[^\d,.]','', str(s))
    if not s: return 0.0
    if ',' in s: s = s.replace('.','').replace(',','.')
    try: return float(s)
    except: return 0.0

def _fmt(v):
    try: return f"R$ {float(v):,.2f}".replace(",","X").replace(".",",").replace("X",".")
    except: return "R$ 0,00"

def _vs(v):
    try: return f"{float(v):,.2f}".replace(",","X").replace(".",",").replace("X",".")
    except: return "0,00"

def calc_acordo(valor):
    """10% do valor + 35% do restante."""
    return round(valor * 0.10 + (valor * 0.90) * 0.35, 2)

def calc_execucao(percebido, sucumbencia):
    """35% do valor percebido + honorários de sucumbência."""
    return round(percebido * 0.35 + sucumbencia, 2)

def dados_iniciais():
    acordos = [
        {"mes":"Out/2025","data_pagamento":"31/10/2025","cliente":"BERNADETE NARDI DE PAULA","reu":"SANTANDER","objeto":"aposentadoria 145353811","processo":"5001026-20.2025.8.13.0329","valor_acordo":5000.00,"honorarios":2075.00,"status":"pago"},
        {"mes":"Jan/2026","data_pagamento":"21/01/2026","cliente":"ANA MARIA DE OLIVEIRA","reu":"ITAÚ","objeto":"seguro cartão","processo":"5001218-50.2025.8.13.0329","valor_acordo":4638.00,"honorarios":1924.00,"status":"pago"},
        {"mes":"Jan/2026","data_pagamento":"21/01/2026","cliente":"MARTA APARECIDA DE PAULA REIS","reu":"ITAU","objeto":"seguro residencial","processo":"5001241-93.2025.8.13.0329","valor_acordo":4155.00,"honorarios":1724.33,"status":"pago"},
        {"mes":"Jan/2026","data_pagamento":"29/01/2026","cliente":"JOSE CARLOS DOS SANTOS","reu":"ITAU","objeto":"seguro lis e sisdeb","processo":"5001339-78.2025.8.13.0329","valor_acordo":4770.00,"honorarios":1979.55,"status":"pago"},
        {"mes":"Jan/2026","data_pagamento":"29/01/2026","cliente":"LENITA APARECIDA PAULA SOUSA","reu":"ITAU","objeto":"SISDEB ITAUPORTOSEGUR","processo":"5001329-34.2025.8.13.0329","valor_acordo":2900.00,"honorarios":1203.50,"status":"pago"},
        {"mes":"Jan/2026","data_pagamento":"30/01/2026","cliente":"MARTA APARECIDA DE PAULA REIS","reu":"ITAU","objeto":"SISDEB ITAUPORTOSEGUR","processo":"5001131-94.2025.8.13.0329","valor_acordo":4000.00,"honorarios":1660.00,"status":"pago"},
        {"mes":"Fev/2026","data_pagamento":"06/02/2026","cliente":"MARTA APARECIDA DE PAULA REIS","reu":"ITAU","objeto":"ITAU SEG VIDA PF","processo":"5001194-22.2025.8.13.0329","valor_acordo":4000.00,"honorarios":1660.00,"status":"pago"},
        {"mes":"Fev/2026","data_pagamento":"12/02/2026","cliente":"MARTA APARECIDA DE PAULA REIS","reu":"ITAU","objeto":"PGTO PROTECAO FAMILIAR","processo":"5001130-12.2025.8.13.0329","valor_acordo":3900.00,"honorarios":1618.50,"status":"pago"},
        {"mes":"Fev/2026","data_pagamento":"24/02/2026","cliente":"ANA MARIA DE OLIVEIRA","reu":"ITAÚ","objeto":"MENSAL COMBINAQUI","processo":"5001143-11.2025.8.13.0329","valor_acordo":3300.00,"honorarios":1369.50,"status":"pago"},
        {"mes":"Mar/2026","data_pagamento":"04/03/2026","cliente":"LENITA APARECIDA PAULA SOUSA","reu":"ITAU","objeto":"ITAU SEG AP PF","processo":"5001330-19.2025.8.13.0329","valor_acordo":5000.00,"honorarios":2075.00,"status":"pago"},
        {"mes":"Mar/2026","data_pagamento":"04/03/2026","cliente":"BERNADETE NARDI DE PAULA","reu":"SANTANDER","objeto":"PENSAO 145353251","processo":"5001232-34.2025.8.13.0329","valor_acordo":3000.00,"honorarios":1245.00,"status":"pago"},
        {"mes":"Mar/2026","data_pagamento":"09/03/2026","cliente":"ROSARIA LOGUERCIOS DOS SANTOS","reu":"ITAU","objeto":"MENSAL COMBINAQUI","processo":"5000000-50.2026.8.13.0329","valor_acordo":5000.00,"honorarios":2075.00,"status":"pago"},
        {"mes":"Mar/2026","data_pagamento":"10/03/2026","cliente":"TEREZINHA IVONE DE SOUSA","reu":"ITAU","objeto":"MENSAL COMBINAQUI","processo":"5000013-49.2026.8.13.0329","valor_acordo":4000.00,"honorarios":1660.00,"status":"pago"},
        {"mes":"Mar/2026","data_pagamento":"10/03/2026","cliente":"LENITA APARECIDA PAULA SOUSA","reu":"ITAU","objeto":"SISDEB","processo":"5001328-49.2025.8.13.0329","valor_acordo":3760.00,"honorarios":1560.40,"status":"pago"},
        {"mes":"Mar/2026","data_pagamento":"11/03/2026","cliente":"CLEIDE DE SOUSA ALVES","reu":"ITAU","objeto":"MENSAL COMBINAQUI","processo":"5001141-41.2025.8.13.0329","valor_acordo":5000.00,"honorarios":2075.00,"status":"pago"},
        {"mes":"Mar/2026","data_pagamento":"16/03/2026","cliente":"MARTA APARECIDA DE PAULA REIS","reu":"ITAU","objeto":"SISDEB","processo":"5001331-04.2025.8.13.0329","valor_acordo":5000.00,"honorarios":2075.00,"status":"pago"},
        {"mes":"Mar/2026","data_pagamento":"23/03/2026","cliente":"MARTA APARECIDA DE PAULA REIS","reu":"ITAU","objeto":"TAR PACOTE","processo":"5000001-35.2026.8.13.0329","valor_acordo":5000.00,"honorarios":2075.00,"status":"pago"},
        {"mes":"Mar/2026","data_pagamento":"26/03/2026","cliente":"MARTA APARECIDA DE PAULA REIS","reu":"ITAU","objeto":"CAP PIC","processo":"5001333-71.2025.8.13.0329","valor_acordo":5600.00,"honorarios":2324.00,"status":"pago"},
        {"mes":"Abr/2026","data_pagamento":"01/04/2026","cliente":"ELISABETE APARECIDA MARANGONI","reu":"ITAU","objeto":"RENEGOCIAÇÕES","processo":"5001363-09.2025.8.13.0329","valor_acordo":8237.44,"honorarios":3418.48,"status":"pago"},
        {"mes":"Abr/2026","data_pagamento":"01/04/2026","cliente":"JOAO DONIZETE VAZ","reu":"ITAU","objeto":"MENSAL COMBINAQUI","processo":"5001243-63.2025.8.13.0329","valor_acordo":6442.64,"honorarios":2673.70,"status":"pendente"},
        {"mes":"Abr/2026","data_pagamento":"17/04/2026","cliente":"CLEIDE DE SOUSA ALVES","reu":"ITAU","objeto":"SEGURO CARTAO","processo":"5001149-18.2025.8.13.0329","valor_acordo":5500.00,"honorarios":2282.50,"status":"pago"},
        {"mes":"Abr/2026","data_pagamento":"17/04/2026","cliente":"MARTA APARECIDA DE PAULA REIS","reu":"ITAU","objeto":"SEGURO CARTAO","processo":"5001193-37.2025.8.13.0329","valor_acordo":4270.00,"honorarios":1772.05,"status":"pago"},
        {"mes":"Abr/2026","data_pagamento":"23/04/2026","cliente":"HELIO DE SOUZA","reu":"PAN","objeto":"344905159-2 / 339148026-0 / 336819430-8 / 334093468-0","processo":"5008533-48.2025.8.13.0647","valor_acordo":11000.00,"honorarios":4565.00,"status":"pago"},
        {"mes":"Mai/2026","data_pagamento":"05/05/2026","cliente":"LENITA APARECIDA PAULA SOUSA","reu":"ITAU","objeto":"SEGURO CARTÃO + ITAU SEG VIDA PF + PGTO PROTECAO FAMILIAR","processo":"5000206-64.2026.8.13.0329","valor_acordo":4320.68,"honorarios":1793.08,"status":"pendente"},
    ]

    execucoes = []

    honorarios_iniciais = [
        {"cliente":"JOSE ALDAIR FERREIRA NUNES","processo":"","valor":2500.00,
         "data_pagamento":"02/03/2026","observacao":"Honorários iniciais pagos","status":"pago"},
        {"cliente":"CRISTINA/MILLENE","processo":"4010523-32.2026.8.26.0506","valor":3000.00,
         "data_pagamento":"","observacao":"Contratação – honorário inicial","status":"pendente"},
    ]

    fixas = {
        "Aluguel":      {"Out":600,"Nov":280.80,"Dez":600,"Jan":600,"Fev":600,"Mar":600,"Abr":600,"Mai":600},
        "Água":         {"Nov":27.18,"Jan":27.28,"Fev":24.78,"Mar":28.46,"Abr":25.77},
        "Força":        {"Dez":103.22,"Jan":98.75,"Mar":94.05},
        "Internet":     {"Out":110.83,"Nov":79.90,"Dez":79.90,"Jan":79.90,"Fev":79.90,"Mar":79.90,"Abr":79.90,"Mai":79.90},
        "Funcionário 1":{},
        "Funcionário 2":{},
    }
    fixas_quem = {
        "Aluguel":"dividido","Água":"dividido","Força":"dividido",
        "Internet":"dividido","Funcionário 1":"dividido","Funcionário 2":"dividido",
    }
    fixas_status = {cat: {c: "pago" for c in COL_FIXAS if fixas[cat].get(c,0) > 0}
                    for cat in fixas}

    variaveis = [
        {"descricao":"Poltronas","valor":750.00,"parcelas":"10x","quem":"Eduarda","onde":"Shopee","status":"pago","meses":{"Out":75,"Nov":75,"Dez":75,"Jan":75,"Fev":75,"Mar":75,"Abr":75,"Mai":75,"Jun":75,"Jul":75}},
        {"descricao":"Cortina 1,7x1,7","valor":320.00,"parcelas":"8x","quem":"Eduarda","onde":"Mercado Livre","status":"pago","meses":{"Nov":40,"Dez":40,"Jan":40,"Fev":40,"Mar":40,"Abr":40,"Mai":40,"Jun":40}},
        {"descricao":"Banner","valor":151.44,"parcelas":"7x","quem":"Eduarda","onde":"Mercado Livre","status":"pago","meses":{"Nov":21.63,"Dez":21.63,"Jan":21.63,"Fev":21.63,"Mar":21.63,"Abr":21.63,"Mai":21.63}},
        {"descricao":"Impressora","valor":1677.00,"parcelas":"10x","quem":"Eduarda","onde":"Mercado Livre","status":"pendente","meses":{"Mar":167.70,"Abr":167.70,"Mai":167.70,"Jun":167.70,"Jul":167.70,"Ago":167.70,"Set":167.70,"Out2":167.70,"Nov2":167.70,"Dez2":167.70}},
        {"descricao":"OAB/MG","valor":950.40,"parcelas":"12x","quem":"Adriely","onde":"OAB","status":"pendente","meses":{"Fev":79.20,"Mar":79.21,"Abr":79.21,"Mai":79.21,"Jun":79.21,"Jul":79.21,"Ago":79.21,"Set":79.21,"Out2":79.21,"Nov2":79.21,"Dez2":79.21}},
        {"descricao":"Envelope/cápsula/porta treco","valor":227.95,"parcelas":"3x","quem":"Adriely","onde":"Shopee","status":"pago","meses":{"Mar":75.98,"Abr":75.98,"Mai":75.98}},
        {"descricao":"Mangueira","valor":35.30,"parcelas":"1x","quem":"Adriely","onde":"Mercado Livre","status":"pago","meses":{"Mai":35.30}},
        {"descricao":"Cápsulas Itallé","valor":89.29,"parcelas":"1x","quem":"Adriely","onde":"Mercado Livre","status":"pago","meses":{"Mai":89.29}},
        {"descricao":"Filtro de água","valor":552.80,"parcelas":"10x","quem":"Eduarda","onde":"Mercado Livre","status":"pendente","meses":{"Mai":55.28,"Jun":55.28,"Jul":55.28,"Ago":55.28,"Set":55.28,"Out2":55.28,"Nov2":55.28,"Dez2":55.28}},
        {"descricao":"Mercado ABC","valor":75.87,"parcelas":"1x","quem":"Adriely","onde":"ABC","status":"pago","meses":{"Abr":75.87}},
        {"descricao":"Terra e pedras","valor":53.00,"parcelas":"1x","quem":"Adriely","onde":"Floricultura","status":"pago","meses":{"Abr":53.00}},
        {"descricao":"Fitas","valor":76.66,"parcelas":"1x","quem":"Eduarda","onde":"Mercado Livre","status":"pago","meses":{"Abr":76.66}},
        {"descricao":"Compras limpeza","valor":46.87,"parcelas":"1x","quem":"Adriely","onde":"ABC","status":"pago","meses":{"Abr":46.87}},
        {"descricao":"Tampa do vaso","valor":73.69,"parcelas":"1x","quem":"Adriely","onde":"Mercado Livre","status":"pago","meses":{"Out":73.69}},
        {"descricao":"Mercado 30/08","valor":68.08,"parcelas":"1x","quem":"Eduarda","onde":"Mercado","status":"pago","meses":{"Out":68.08}},
        {"descricao":"Chaveiro","valor":80.00,"parcelas":"1x","quem":"Adriely","onde":"Chaveiro","status":"pago","meses":{"Out":80.00}},
        {"descricao":"João Gabriel (faxina)","valor":150.00,"parcelas":"1x","quem":"Eduarda","onde":"Faxina","status":"pago","meses":{"Out":150.00}},
        {"descricao":"Bianca (iniciais)","valor":250.00,"parcelas":"1x","quem":"Adriely","onde":"Iniciais","status":"pago","meses":{"Out":250.00}},
        {"descricao":"Felipe (eletricista)","valor":319.20,"parcelas":"1x","quem":"Adriely","onde":"Eletricista","status":"pago","meses":{"Nov":319.20}},
        {"descricao":"Varão Cortina","valor":40.00,"parcelas":"1x","quem":"Eduarda","onde":"Zé Natal","status":"pago","meses":{"Dez":40.00}},
        {"descricao":"Cortina Sala","valor":157.50,"parcelas":"2x","quem":"Eduarda","onde":"Shopee","status":"pago","meses":{"Nov":78.75,"Dez":78.75}},
        {"descricao":"Pasta e impressões","valor":51.85,"parcelas":"1x","quem":"Adriely","onde":"Uno & Due","status":"pago","meses":{"Dez":51.85}},
        {"descricao":"Mercado 29/11","valor":66.46,"parcelas":"1x","quem":"Adriely","onde":"ABC","status":"pago","meses":{"Dez":66.46}},
        {"descricao":"Pasta 03/12","valor":26.90,"parcelas":"1x","quem":"Adriely","onde":"Uno & Due","status":"pago","meses":{"Dez":26.90}},
        {"descricao":"Espelho, nicho e placa","valor":233.91,"parcelas":"3x","quem":"Eduarda","onde":"Shopee","status":"pago","meses":{"Nov":77.97,"Dez":77.97,"Jan":77.97}},
        {"descricao":"Mesa","valor":750.92,"parcelas":"4x","quem":"Eduarda","onde":"Mercado Livre","status":"pago","meses":{"Out":187.70,"Nov":187.70,"Dez":187.70,"Jan":187.70}},
        {"descricao":"Felipe (instalação/campainha)","valor":160.00,"parcelas":"1x","quem":"dividido","onde":"","status":"pago","meses":{"Mar":160.00}},
        {"descricao":"Cadeiras","valor":381.18,"parcelas":"6x","quem":"Adriely","onde":"Shopee","status":"pago","meses":{"Out":63.53,"Nov":63.53,"Dez":63.53,"Jan":63.53,"Fev":63.53,"Mar":63.53}},
        {"descricao":"Placa, fita e tapete","valor":224.59,"parcelas":"3x","quem":"Eduarda","onde":"Shopee","status":"pago","meses":{"Dez":74.86,"Jan":74.86,"Fev":74.86}},
        {"descricao":"Impressão","valor":30.00,"parcelas":"1x","quem":"Adriely","onde":"Tecmania","status":"pago","meses":{"Fev":30.00}},
        {"descricao":"Cartão de visita","valor":69.00,"parcelas":"1x","quem":"Adriely","onde":"Canva","status":"pago","meses":{"Fev":69.00}},
        {"descricao":"Bianca (café)","valor":17.00,"parcelas":"1x","quem":"Adriely","onde":"Via Caffè","status":"pago","meses":{"Fev":17.00}},
        {"descricao":"Impressão Uno & Due","valor":9.60,"parcelas":"1x","quem":"Eduarda","onde":"Uno & Due","status":"pago","meses":{"Fev":9.60}},
        {"descricao":"Vaso de planta","valor":55.44,"parcelas":"1x","quem":"Adriely","onde":"Shopee","status":"pago","meses":{"Abr":55.44}},
        {"descricao":"Mão francesa suporte","valor":40.84,"parcelas":"1x","quem":"Adriely","onde":"Mercado Livre","status":"pago","meses":{"Abr":40.84}},
        {"descricao":"Copos","valor":6.50,"parcelas":"1x","quem":"Adriely","onde":"MegaShopping","status":"pago","meses":{"Abr":6.50}},
        {"descricao":"Cápsula, pendente e porta pasta","valor":134.39,"parcelas":"1x","quem":"Adriely","onde":"Shopee","status":"pago","meses":{"Abr":134.39}},
    ]

    return {
        "acordos": acordos,
        "execucoes": execucoes,
        "honorarios_iniciais": honorarios_iniciais,
        "fixas": fixas,
        "fixas_quem": fixas_quem,
        "fixas_status": fixas_status,
        "variaveis": variaveis,
    }

def carregar():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            d = json.load(f)
        # migrar campos novos se precisar
        if "execucoes" not in d: d["execucoes"] = []
        if "honorarios_iniciais" not in d: d["honorarios_iniciais"] = []
        if "fixas_quem" not in d:
            d["fixas_quem"] = {cat:"dividido" for cat in d.get("fixas",{})}
        if "fixas_status" not in d:
            d["fixas_status"] = {cat:{} for cat in d.get("fixas",{})}
        for a in d.get("acordos", []):
            if "objeto" not in a: a["objeto"] = ""
            if "data_pagamento" not in a: a["data_pagamento"] = ""
        return d
    return dados_iniciais()

def salvar(d):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)

if "dados" not in st.session_state:
    st.session_state.dados = carregar()
d = st.session_state.dados

# ── Cabeçalho ─────────────────────────────────────────────────────────────────
st.markdown("""
<div style='text-align:center;padding:20px 0 6px 0'>
  <h1 style='font-size:26px;font-weight:700;margin:0;
      background:linear-gradient(90deg,#5c6bc0,#42a5f5);
      -webkit-background-clip:text;-webkit-text-fill-color:transparent;'>
    💼 CONTROLE FINANCEIRO – ESCRITÓRIO
  </h1>
  <p style='color:#5c6bc0;font-size:13px;margin-top:4px;'>Sócias: Adriely &amp; Eduarda</p>
</div>
""", unsafe_allow_html=True)

tabs = st.tabs(["📊 Dashboard","🤝 Acordos","⚖️ Execuções","💼 Hon. Iniciais",
                "🏢 Desp. Fixas","🛒 Desp. Variáveis","⚖️ Balanço"])
tab_dash, tab_ac, tab_ex, tab_hi, tab_fix, tab_var, tab_bal = tabs

# ─────────────────────────────────────────────────────────────────────────────
# Helpers de totais
# ─────────────────────────────────────────────────────────────────────────────
def total_honorarios():
    t = sum(float(a.get("honorarios",0)) for a in d["acordos"])
    t += sum(float(e.get("honorarios",0)) for e in d["execucoes"])
    t += sum(float(h.get("valor",0)) for h in d["honorarios_iniciais"] if h.get("status")=="pago")
    return t

def total_honorarios_pendente():
    t = sum(float(a.get("honorarios",0)) for a in d["acordos"] if a.get("status")=="pendente")
    t += sum(float(e.get("honorarios",0)) for e in d["execucoes"] if e.get("status")=="pendente")
    t += sum(float(h.get("valor",0)) for h in d["honorarios_iniciais"] if h.get("status")=="pendente")
    return t

def total_fixas():
    return sum(sum(float(v) for v in cat.values()) for cat in d["fixas"].values())

def total_variaveis():
    return sum(sum(float(v) for v in item.get("meses",{}).values()) for item in d["variaveis"])

# ─────────────────────────────────────────────────────────────────────────────
# DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────
with tab_dash:
    th = total_honorarios()
    tp = total_honorarios_pendente()
    tf = total_fixas()
    tv = total_variaveis()
    saldo = th - tf - tv

    c1,c2,c3,c4,c5 = st.columns(5)
    cards = [
        ("Honorários Recebidos", th, "verde"),
        ("Pendente de Recebimento", tp, "vermelho" if tp>0 else "azul"),
        ("Desp. Fixas", tf, "laranja"),
        ("Desp. Variáveis", tv, "laranja"),
        ("Saldo Líquido", saldo, "verde" if saldo>=0 else "vermelho"),
    ]
    for col,(titulo,val,cor) in zip([c1,c2,c3,c4,c5], cards):
        with col:
            st.markdown(f"""<div class="bloco">
                <div class="card-titulo">{titulo}</div>
                <div class="card-valor {cor}">{_fmt(val)}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Resumo por mês
    st.markdown("### Resumo por Mês")
    honor_mes = {}
    for a in d["acordos"]:
        m = a.get("mes",""); honor_mes[m] = honor_mes.get(m,0) + float(a.get("honorarios",0))
    for e in d["execucoes"]:
        m = e.get("mes",""); honor_mes[m] = honor_mes.get(m,0) + float(e.get("honorarios",0))
    for hi in d.get("honorarios_iniciais",[]):
        if hi.get("status") == "pago":
            dp = hi.get("data_pagamento","")
            if dp and len(dp) == 10:
                try:
                    parts = dp.split("/")
                    meses_abr = ["","Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"]
                    m = f"{meses_abr[int(parts[1])]}/{parts[2]}"
                    honor_mes[m] = honor_mes.get(m,0) + float(hi.get("valor",0))
                except: pass

    fixas_mes = {}
    for cat, meses in d["fixas"].items():
        for col, val in meses.items():
            m = COL_TO_MES.get(col,"")
            fixas_mes[m] = fixas_mes.get(m,0) + float(val or 0)

    var_mes = {}
    for item in d["variaveis"]:
        for col, val in item.get("meses",{}).items():
            m = COL_TO_MES.get(col,"")
            var_mes[m] = var_mes.get(m,0) + float(val or 0)

    meses_com_dados = [m for m in MESES if honor_mes.get(m,0)+fixas_mes.get(m,0)+var_mes.get(m,0) > 0]
    if meses_com_dados:
        linhas = ["| Mês | Honorários | Desp. Fixas | Desp. Variáveis | Saldo |",
                  "|---|---|---|---|---|"]
        for m in meses_com_dados:
            h = honor_mes.get(m,0); f = fixas_mes.get(m,0); v = var_mes.get(m,0)
            s = h-f-v; ic = "🟢" if s>=0 else "🔴"
            linhas.append(f"| {m} | {_fmt(h)} | {_fmt(f)} | {_fmt(v)} | {ic} {_fmt(s)} |")
        st.markdown("\n".join(linhas))

    # Pendentes
    pendentes_ac = [a for a in d["acordos"] if a.get("status")=="pendente"]
    pendentes_ex = [e for e in d["execucoes"] if e.get("status")=="pendente"]
    pendentes_hi = [h for h in d["honorarios_iniciais"] if h.get("status")=="pendente"]
    if pendentes_ac or pendentes_ex or pendentes_hi:
        st.markdown("### ⚠️ Pendentes de Recebimento")
        for p in pendentes_ac + pendentes_ex:
            st.markdown(f"""<div class="bloco" style="border-color:#b71c1c;">
                <span style="color:#ef5350;font-weight:600">{p.get('cliente','')}</span>
                &nbsp;|&nbsp;{p.get('mes','')}
                &nbsp;|&nbsp;Honorários: <strong>{_fmt(p.get('honorarios',0))}</strong>
                &nbsp;|&nbsp;<span style="font-size:11px;color:#7986cb">{p.get('processo','')}</span>
            </div>""", unsafe_allow_html=True)
        for p in pendentes_hi:
            st.markdown(f"""<div class="bloco" style="border-color:#b71c1c;">
                <span style="color:#ef5350;font-weight:600">{p.get('cliente','')}</span>
                &nbsp;|&nbsp;Hon. Inicial
                &nbsp;|&nbsp;Valor: <strong>{_fmt(p.get('valor',0))}</strong>
                &nbsp;|&nbsp;<span style="font-size:11px;color:#7986cb">{p.get('observacao','')}</span>
            </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# ACORDOS
# ─────────────────────────────────────────────────────────────────────────────
with tab_ac:
    st.markdown("### 🤝 Acordos")
    st.markdown("""<div class="bloco" style="border-color:#5c6bc0;padding:12px 16px;margin-bottom:12px;">
        <span style="color:#7986cb;font-size:12px;">
        📐 <strong>Cálculo automático:</strong>
        Honorários = 10% do valor + 35% do restante (= 41,5% do valor do acordo)
        </span>
    </div>""", unsafe_allow_html=True)

    ca, cs = st.columns([6,1])
    with ca:
        if st.button("➕ Novo Acordo"):
            d["acordos"].append({"mes":MESES[0],"data_pagamento":"","cliente":"","reu":"",
                                  "objeto":"","processo":"","valor_acordo":0.0,
                                  "honorarios":0.0,"status":"pendente"})
            salvar(d); st.rerun()
    with cs:
        if st.button("💾 Salvar", key="sv_ac"):
            salvar(d); st.success("Salvo!")

    # cabeçalho
    hdr = st.columns([1.0,1.0,1.6,0.8,2.2,1.5,1.1,1.1,0.9,0.4])
    for col, lbl in zip(hdr,["Mês","Data Pgto","Cliente","Réu","Processo","Objeto","Valor Acordo","Honorários","Status",""]):
        col.markdown(f"<span style='font-size:10px;color:#7986cb;font-weight:600;'>{lbl}</span>",
                     unsafe_allow_html=True)

    to_del = None
    for i, a in enumerate(d["acordos"]):
        cols = st.columns([1.0,1.0,1.6,0.8,2.2,1.5,1.1,1.1,0.9,0.4])
        a["mes"] = cols[0].selectbox("", MESES,
            index=MESES.index(a["mes"]) if a.get("mes") in MESES else 0,
            key=f"ac_mes_{i}", label_visibility="collapsed")
        a["data_pagamento"] = cols[1].text_input("", value=a.get("data_pagamento",""),
            placeholder="DD/MM/AAAA", key=f"ac_dp_{i}", label_visibility="collapsed")
        a["cliente"] = cols[2].text_input("", value=a.get("cliente",""),
            key=f"ac_cli_{i}", label_visibility="collapsed")
        a["reu"] = cols[3].text_input("", value=a.get("reu",""),
            key=f"ac_reu_{i}", label_visibility="collapsed")
        a["processo"] = cols[4].text_input("", value=a.get("processo",""),
            key=f"ac_proc_{i}", label_visibility="collapsed")
        a["objeto"] = cols[5].text_input("", value=a.get("objeto",""),
            key=f"ac_obj_{i}", label_visibility="collapsed")

        va_str = st.session_state.get(f"ac_va_{i}", _vs(a.get("valor_acordo",0)))
        va_new = cols[6].text_input("", value=va_str, placeholder="0,00",
            key=f"ac_va_{i}", label_visibility="collapsed")
        try: va = float(va_new.replace(".","").replace(",",".")) if va_new else 0.0
        except: va = 0.0
        a["valor_acordo"] = va
        a["honorarios"] = calc_acordo(va)

        cols[7].markdown(f"""<div style='padding-top:8px;font-size:13px;font-weight:600;color:#4caf50;'>
            {_fmt(a["honorarios"])}</div>""", unsafe_allow_html=True)

        a["status"] = cols[8].selectbox("", ["pago","pendente"],
            index=0 if a.get("status")=="pago" else 1,
            key=f"ac_st_{i}", label_visibility="collapsed")
        if cols[9].button("🗑️", key=f"ac_del_{i}"): to_del = i

    if to_del is not None:
        d["acordos"].pop(to_del); salvar(d); st.rerun()

    total_ac = sum(float(a.get("honorarios",0)) for a in d["acordos"])
    pago_ac  = sum(float(a.get("honorarios",0)) for a in d["acordos"] if a.get("status")=="pago")
    pend_ac  = total_ac - pago_ac
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    c1,c2,c3 = st.columns(3)
    c1.metric("Total Honorários", _fmt(total_ac))
    c2.metric("Recebido", _fmt(pago_ac))
    c3.metric("Pendente", _fmt(pend_ac))

# ─────────────────────────────────────────────────────────────────────────────
# EXECUÇÕES
# ─────────────────────────────────────────────────────────────────────────────
with tab_ex:
    st.markdown("### ⚖️ Execuções")
    st.markdown("""<div class="bloco" style="border-color:#5c6bc0;padding:12px 16px;margin-bottom:12px;">
        <span style="color:#7986cb;font-size:12px;">
        📐 <strong>Cálculo automático:</strong>
        Honorários = 35% do valor percebido + honorários de sucumbência
        </span>
    </div>""", unsafe_allow_html=True)

    ex_a, ex_s = st.columns([6,1])
    with ex_a:
        if st.button("➕ Nova Execução"):
            d["execucoes"].append({"mes":MESES[0],"cliente":"","reu":"","processo":"",
                                    "valor_percebido":0.0,"sucumbencia":0.0,
                                    "honorarios":0.0,"status":"pendente"})
            salvar(d); st.rerun()
    with ex_s:
        if st.button("💾 Salvar", key="sv_ex"):
            salvar(d); st.success("Salvo!")

    if not d["execucoes"]:
        st.markdown("""<div class="bloco" style="text-align:center;padding:32px;">
            <span style="color:#5c6bc0;font-size:14px;">Nenhuma execução cadastrada ainda.</span>
        </div>""", unsafe_allow_html=True)
    else:
        hdr = st.columns([1.4,1.8,1.2,2.4,1.3,1.3,1.3,1.1,0.5])
        for col, lbl in zip(hdr,["Mês","Cliente","Réu","Processo","Val. Percebido","Sucumbência","Honorários","Status",""]):
            col.markdown(f"<span style='font-size:10px;color:#7986cb;font-weight:600;'>{lbl}</span>",
                         unsafe_allow_html=True)

        to_del_e = None
        for i, e in enumerate(d["execucoes"]):
            cols = st.columns([1.4,1.8,1.2,2.4,1.3,1.3,1.3,1.1,0.5])
            e["mes"] = cols[0].selectbox("", MESES,
                index=MESES.index(e["mes"]) if e.get("mes") in MESES else 0,
                key=f"ex_mes_{i}", label_visibility="collapsed")
            e["cliente"] = cols[1].text_input("", value=e.get("cliente",""),
                key=f"ex_cli_{i}", label_visibility="collapsed")
            e["reu"] = cols[2].text_input("", value=e.get("reu",""),
                key=f"ex_reu_{i}", label_visibility="collapsed")
            e["processo"] = cols[3].text_input("", value=e.get("processo",""),
                key=f"ex_proc_{i}", label_visibility="collapsed")

            vp_str = st.session_state.get(f"ex_vp_{i}", _vs(e.get("valor_percebido",0)))
            vp_new = cols[4].text_input("", value=vp_str, placeholder="0,00",
                key=f"ex_vp_{i}", label_visibility="collapsed")
            try: vp = float(vp_new.replace(".","").replace(",",".")) if vp_new else 0.0
            except: vp = 0.0

            sc_str = st.session_state.get(f"ex_sc_{i}", _vs(e.get("sucumbencia",0)))
            sc_new = cols[5].text_input("", value=sc_str, placeholder="0,00",
                key=f"ex_sc_{i}", label_visibility="collapsed")
            try: sc = float(sc_new.replace(".","").replace(",",".")) if sc_new else 0.0
            except: sc = 0.0

            e["valor_percebido"] = vp
            e["sucumbencia"] = sc
            e["honorarios"] = calc_execucao(vp, sc)

            cols[6].markdown(f"""<div style='padding-top:8px;font-size:14px;font-weight:600;color:#4caf50;'>
                {_fmt(e['honorarios'])}</div>""", unsafe_allow_html=True)
            e["status"] = cols[7].selectbox("", ["pago","pendente"],
                index=0 if e.get("status")=="pago" else 1,
                key=f"ex_st_{i}", label_visibility="collapsed")
            if cols[8].button("🗑️", key=f"ex_del_{i}"): to_del_e = i

        if to_del_e is not None:
            d["execucoes"].pop(to_del_e); salvar(d); st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# HONORÁRIOS INICIAIS
# ─────────────────────────────────────────────────────────────────────────────
with tab_hi:
    st.markdown("### 💼 Honorários Iniciais (Contratação)")

    hi_a, hi_s = st.columns([6,1])
    with hi_a:
        if st.button("➕ Novo Honorário Inicial"):
            d["honorarios_iniciais"].append({"cliente":"","processo":"","valor":0.0,
                                              "data_pagamento":"","observacao":"","status":"pendente"})
            salvar(d); st.rerun()
    with hi_s:
        if st.button("💾 Salvar", key="sv_hi"):
            salvar(d); st.success("Salvo!")

    hdr = st.columns([2,2.5,1.5,1.5,2,1.1,0.5])
    for col, lbl in zip(hdr,["Cliente","Processo","Valor","Data Pagto","Observação","Status",""]):
        col.markdown(f"<span style='font-size:10px;color:#7986cb;font-weight:600;'>{lbl}</span>",
                     unsafe_allow_html=True)

    to_del_h = None
    for i, h in enumerate(d["honorarios_iniciais"]):
        cols = st.columns([2,2.5,1.5,1.5,2,1.1,0.5])
        h["cliente"] = cols[0].text_input("", value=h.get("cliente",""),
            key=f"hi_cli_{i}", label_visibility="collapsed")
        h["processo"] = cols[1].text_input("", value=h.get("processo",""),
            key=f"hi_proc_{i}", label_visibility="collapsed")

        vh_str = st.session_state.get(f"hi_val_{i}", _vs(h.get("valor",0)))
        vh_new = cols[2].text_input("", value=vh_str, placeholder="0,00",
            key=f"hi_val_{i}", label_visibility="collapsed")
        try: vhv = float(vh_new.replace(".","").replace(",",".")) if vh_new else 0.0
        except: vhv = 0.0
        h["valor"] = vhv

        h["data_pagamento"] = cols[3].text_input("", value=h.get("data_pagamento",""),
            placeholder="DD/MM/AAAA", key=f"hi_dt_{i}", label_visibility="collapsed")
        h["observacao"] = cols[4].text_input("", value=h.get("observacao",""),
            key=f"hi_obs_{i}", label_visibility="collapsed")
        h["status"] = cols[5].selectbox("", ["pago","pendente"],
            index=0 if h.get("status")=="pago" else 1,
            key=f"hi_st_{i}", label_visibility="collapsed")
        if cols[6].button("🗑️", key=f"hi_del_{i}"): to_del_h = i

    if to_del_h is not None:
        d["honorarios_iniciais"].pop(to_del_h); salvar(d); st.rerun()

    total_hi   = sum(float(h.get("valor",0)) for h in d["honorarios_iniciais"])
    pago_hi    = sum(float(h.get("valor",0)) for h in d["honorarios_iniciais"] if h.get("status")=="pago")
    pendente_hi= total_hi - pago_hi
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    c1,c2,c3 = st.columns(3)
    c1.metric("Total", _fmt(total_hi))
    c2.metric("Recebido", _fmt(pago_hi))
    c3.metric("Pendente", _fmt(pendente_hi))

# ─────────────────────────────────────────────────────────────────────────────
# DESPESAS FIXAS
# ─────────────────────────────────────────────────────────────────────────────
with tab_fix:
    st.markdown("### 🏢 Despesas Fixas Mensais")
    st.caption("Despesas fixas são divididas 50/50 entre as sócias. Marque o status de pagamento.")

    COLS_VIS = ["Out","Nov","Dez","Jan","Fev","Mar","Abr","Mai"]
    col_lbl  = {"Out":"Out/24","Nov":"Nov/24","Dez":"Dez/24","Jan":"Jan/25",
                "Fev":"Fev/25","Mar":"Mar/25","Abr":"Abr/25","Mai":"Mai/25"}

    fix_nova, fix_sv = st.columns([5,1])
    with fix_nova:
        nova_cat = st.text_input("Nova categoria:", key="nova_fix", placeholder="Ex: Contador")
    if st.button("➕ Adicionar") and nova_cat.strip():
        if nova_cat.strip() not in d["fixas"]:
            d["fixas"][nova_cat.strip()] = {}
            d["fixas_quem"][nova_cat.strip()] = "dividido"
            d["fixas_status"][nova_cat.strip()] = {}
            salvar(d); st.rerun()
    with fix_sv:
        if st.button("💾 Salvar ", key="sv_fix"): salvar(d); st.success("Salvo!")

    # cabeçalho
    hcols = st.columns([2, 1.2] + [1]*len(COLS_VIS) + [1, 0.5])
    for lbl, col in zip(["Categoria","Quem paga"]+[col_lbl[c] for c in COLS_VIS]+["Total",""],hcols):
        col.markdown(f"<span style='font-size:10px;color:#7986cb;font-weight:600;'>{lbl}</span>",
                     unsafe_allow_html=True)

    cats_del = None
    totais_col = {c:0.0 for c in COLS_VIS}

    for cat in list(d["fixas"].keys()):
        row = st.columns([2, 1.2] + [1]*len(COLS_VIS) + [1, 0.5])
        row[0].markdown(f"<div style='padding-top:8px;font-size:13px;'>{cat}</div>",
                        unsafe_allow_html=True)

        quem_opts = ["Adriely","Eduarda","dividido"]
        cur_quem  = d["fixas_quem"].get(cat,"dividido")
        d["fixas_quem"][cat] = row[1].selectbox("", quem_opts,
            index=quem_opts.index(cur_quem) if cur_quem in quem_opts else 2,
            key=f"fq_{cat}", label_visibility="collapsed")

        total_cat = 0.0
        for idx, col in enumerate(COLS_VIS):
            cur = d["fixas"][cat].get(col,0)
            cstr = st.session_state.get(f"fx_{cat}_{col}", _vs(cur))
            nstr = row[2+idx].text_input("", value=cstr, placeholder="0,00",
                key=f"fx_{cat}_{col}", label_visibility="collapsed")
            try: nval = float(nstr.replace(".","").replace(",",".")) if nstr else 0.0
            except: nval = 0.0
            d["fixas"][cat][col] = nval
            total_cat += nval
            totais_col[col] += nval

        row[-2].markdown(f"<div style='padding-top:8px;font-size:13px;font-weight:600;"
                         f"color:#ffa726;'>{_fmt(total_cat)}</div>", unsafe_allow_html=True)
        if row[-1].button("🗑️", key=f"fx_del_{cat}"): cats_del = cat

    # linha de totais
    tot = st.columns([2, 1.2] + [1]*len(COLS_VIS) + [1, 0.5])
    tot[0].markdown("<strong style='color:#7986cb;'>TOTAL</strong>", unsafe_allow_html=True)
    for idx, col in enumerate(COLS_VIS):
        tot[2+idx].markdown(f"<strong style='color:#ffa726;font-size:12px;'>"
                             f"{_fmt(totais_col[col])}</strong>", unsafe_allow_html=True)

    if cats_del:
        del d["fixas"][cats_del]
        d["fixas_quem"].pop(cats_del, None)
        d["fixas_status"].pop(cats_del, None)
        salvar(d); st.rerun()

    # ── Status de pagamento por sócia ──────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### Status de Pagamento por Sócia (mês atual)")
    st.caption("Marque abaixo se cada sócia já pagou sua parte nas despesas fixas deste mês.")

    mes_atual_col = "Abr"  # pode tornar selecionável depois
    col_status = st.columns([3, 2, 2])
    col_status[0].markdown("<span style='font-size:11px;color:#7986cb;font-weight:600;'>Categoria</span>",
                           unsafe_allow_html=True)
    col_status[1].markdown("<span style='font-size:11px;color:#9fa8da;font-weight:600;'>Adriely</span>",
                           unsafe_allow_html=True)
    col_status[2].markdown("<span style='font-size:11px;color:#a5d6a7;font-weight:600;'>Eduarda</span>",
                           unsafe_allow_html=True)

    for cat in d["fixas"]:
        val = d["fixas"][cat].get(mes_atual_col, 0)
        if val <= 0: continue
        cols_s = st.columns([3, 2, 2])
        cols_s[0].markdown(f"<div style='padding-top:6px;'>{cat} — {_fmt(val/2)} cada</div>",
                           unsafe_allow_html=True)
        # Adriely
        st_a_key = f"fxst_a_{cat}"
        st_a_cur = d["fixas_status"].get(cat,{}).get(f"{mes_atual_col}_adriely","pendente")
        st_a_new = cols_s[1].selectbox("", ["pago","pendente"],
            index=0 if st_a_cur=="pago" else 1,
            key=st_a_key, label_visibility="collapsed")
        if cat not in d["fixas_status"]: d["fixas_status"][cat] = {}
        d["fixas_status"][cat][f"{mes_atual_col}_adriely"] = st_a_new
        # Eduarda
        st_e_key = f"fxst_e_{cat}"
        st_e_cur = d["fixas_status"].get(cat,{}).get(f"{mes_atual_col}_eduarda","pendente")
        st_e_new = cols_s[2].selectbox("", ["pago","pendente"],
            index=0 if st_e_cur=="pago" else 1,
            key=st_e_key, label_visibility="collapsed")
        d["fixas_status"][cat][f"{mes_atual_col}_eduarda"] = st_e_new

# ─────────────────────────────────────────────────────────────────────────────
# DESPESAS VARIÁVEIS
# ─────────────────────────────────────────────────────────────────────────────
with tab_var:
    st.markdown("### 🛒 Despesas Variáveis")

    filtro_col1, filtro_col2 = st.columns(2)
    with filtro_col1:
        filtro_q = st.selectbox("Filtrar por sócia:", ["Todas","Adriely","Eduarda","dividido"],
                                key="filt_var")
    with filtro_col2:
        filtro_st = st.selectbox("Filtrar por status:", ["Todos","pago","pendente"], key="filt_st")

    col_va, col_vs = st.columns([6,1])
    with col_va:
        if st.button("➕ Nova Despesa Variável"):
            d["variaveis"].append({"descricao":"","valor":0.0,"parcelas":"1x",
                                    "quem":"Adriely","onde":"","status":"pendente","meses":{}})
            salvar(d); st.rerun()
    with col_vs:
        if st.button("💾 Salvar  ", key="sv_var"): salvar(d); st.success("Salvo!")

    COLS_VIS_V = ["Out","Nov","Dez","Jan","Fev","Mar","Abr","Mai"]
    cl = {"Out":"Out/24","Nov":"Nov/24","Dez":"Dez/24","Jan":"Jan/25",
          "Fev":"Fev/25","Mar":"Mar/25","Abr":"Abr/25","Mai":"Mai/25"}

    hdr_v = st.columns([2.5, 1, 0.9, 1, 1.2, 1] + [0.85]*len(COLS_VIS_V) + [0.9, 0.4])
    for lbl, col in zip(["Descrição","Val. Total","Parcelas","Quem","Onde","Status"]+
                        [cl[c] for c in COLS_VIS_V]+["Total",""], hdr_v):
        col.markdown(f"<span style='font-size:10px;color:#7986cb;font-weight:600;'>{lbl}</span>",
                     unsafe_allow_html=True)

    to_del_v = None
    totais_a = {c:0.0 for c in COLS_VIS_V}
    totais_e = {c:0.0 for c in COLS_VIS_V}
    totais_v_col = {c:0.0 for c in COLS_VIS_V}

    for i, item in enumerate(d["variaveis"]):
        quem = item.get("quem","Adriely")
        st_item = item.get("status","pago")
        if filtro_q != "Todas" and quem != filtro_q: continue
        if filtro_st != "Todos" and st_item != filtro_st: continue

        row = st.columns([2.5, 1, 0.9, 1, 1.2, 1] + [0.85]*len(COLS_VIS_V) + [0.9, 0.4])
        item["descricao"] = row[0].text_input("", value=item.get("descricao",""),
            key=f"vd_{i}", label_visibility="collapsed")

        vv_str = st.session_state.get(f"vv_{i}", _vs(item.get("valor",0)))
        vv_new = row[1].text_input("", value=vv_str, placeholder="0,00",
            key=f"vv_{i}", label_visibility="collapsed")
        try: vvv = float(vv_new.replace(".","").replace(",",".")) if vv_new else 0.0
        except: vvv = 0.0
        item["valor"] = vvv

        item["parcelas"] = row[2].text_input("", value=item.get("parcelas","1x"),
            key=f"vp_{i}", label_visibility="collapsed")
        item["quem"] = row[3].selectbox("", ["Adriely","Eduarda","dividido"],
            index=["Adriely","Eduarda","dividido"].index(quem) if quem in ["Adriely","Eduarda","dividido"] else 0,
            key=f"vq_{i}", label_visibility="collapsed")
        item["onde"] = row[4].text_input("", value=item.get("onde",""),
            key=f"vo_{i}", label_visibility="collapsed")
        item["status"] = row[5].selectbox("", ["pago","pendente"],
            index=0 if st_item=="pago" else 1,
            key=f"vst_{i}", label_visibility="collapsed")

        total_item = 0.0
        for idx, col in enumerate(COLS_VIS_V):
            cur = item.get("meses",{}).get(col,0)
            cstr = st.session_state.get(f"vm_{i}_{col}", _vs(cur))
            cstr_new = row[6+idx].text_input("", value=cstr, placeholder="0,00",
                key=f"vm_{i}_{col}", label_visibility="collapsed")
            try: cval = float(cstr_new.replace(".","").replace(",",".")) if cstr_new else 0.0
            except: cval = 0.0
            if "meses" not in item: item["meses"] = {}
            item["meses"][col] = cval
            total_item += cval
            totais_v_col[col] += cval
            q_now = item.get("quem","Adriely")
            if q_now == "Adriely": totais_a[col] += cval
            elif q_now == "Eduarda": totais_e[col] += cval
            else:
                totais_a[col] += cval/2
                totais_e[col] += cval/2

        row[-2].markdown(f"<div style='padding-top:8px;font-size:12px;font-weight:600;"
                         f"color:#ffa726;'>{_fmt(total_item)}</div>", unsafe_allow_html=True)
        if row[-1].button("🗑️", key=f"vdel_{i}"): to_del_v = i

    if to_del_v is not None:
        d["variaveis"].pop(to_del_v); salvar(d); st.rerun()

    # totais
    tot_v = st.columns([2.5, 1, 0.9, 1, 1.2, 1] + [0.85]*len(COLS_VIS_V) + [0.9, 0.4])
    tot_v[0].markdown("<strong style='color:#7986cb;'>TOTAL</strong>", unsafe_allow_html=True)
    for idx, col in enumerate(COLS_VIS_V):
        tot_v[6+idx].markdown(f"<strong style='color:#ffa726;font-size:11px;'>"
                               f"{_fmt(totais_v_col[col])}</strong>", unsafe_allow_html=True)

    # Pendentes por sócia
    st.markdown("<br>", unsafe_allow_html=True)
    pendentes_var = [item for item in d["variaveis"] if item.get("status")=="pendente"]
    if pendentes_var:
        st.markdown("#### ⚠️ Despesas Pendentes")
        for item in pendentes_var:
            quem = item.get("quem","")
            badge = "badge-adriely" if quem=="Adriely" else ("badge-eduarda" if quem=="Eduarda" else "")
            st.markdown(f"""<div class="bloco" style="border-color:#b71c1c;padding:10px 16px;">
                <span class="{badge}">{quem}</span>&nbsp;
                <strong>{item.get('descricao','')}</strong>&nbsp;
                <span style="color:#7986cb">{item.get('parcelas','')}</span>&nbsp;|&nbsp;
                Valor total: {_fmt(item.get('valor',0))}&nbsp;|&nbsp;
                {item.get('onde','')}
            </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# BALANÇO DAS SÓCIAS
# ─────────────────────────────────────────────────────────────────────────────
with tab_bal:
    st.markdown("### ⚖️ Balanço das Sócias")

    COLS_B = ["Out","Nov","Dez","Jan","Fev","Mar","Abr","Mai"]
    cl_b   = {"Out":"Out/24","Nov":"Nov/24","Dez":"Dez/24","Jan":"Jan/25",
              "Fev":"Fev/25","Mar":"Mar/25","Abr":"Abr/25","Mai":"Mai/25"}

    mes_sel = st.radio("Mês:", COLS_B, horizontal=True,
                        format_func=lambda x: cl_b[x], key="bal_mes")

    mes_full = COL_TO_MES.get(mes_sel,"")

    # honorários do mês
    honor_mes = sum(float(a.get("honorarios",0)) for a in d["acordos"] if a.get("mes")==mes_full)
    honor_mes += sum(float(e.get("honorarios",0)) for e in d["execucoes"] if e.get("mes")==mes_full)

    # gastos do mês por sócia
    def gastos_mes(col):
        a_g, e_g = 0.0, 0.0
        for cat, meses in d["fixas"].items():
            val = float(meses.get(col,0) or 0)
            quem = d["fixas_quem"].get(cat,"dividido")
            if quem == "Adriely": a_g += val
            elif quem == "Eduarda": e_g += val
            else: a_g += val/2; e_g += val/2
        for item in d["variaveis"]:
            val = float(item.get("meses",{}).get(col,0) or 0)
            quem = item.get("quem","")
            if quem == "Adriely": a_g += val
            elif quem == "Eduarda": e_g += val
            else: a_g += val/2; e_g += val/2
        return a_g, e_g

    a_gasto, e_gasto = gastos_mes(mes_sel)
    honor_cada = honor_mes / 2

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    c1,c2,c3 = st.columns(3)
    with c1:
        st.markdown(f"""<div class="bloco">
            <div class="card-titulo">Honorários do Mês</div>
            <div class="card-valor azul">{_fmt(honor_mes)}</div>
            <div style="color:#5c6bc0;font-size:12px;margin-top:4px;">
                Para cada sócia: {_fmt(honor_cada)}
            </div>
        </div>""", unsafe_allow_html=True)
    with c2:
        saldo_a = honor_cada - a_gasto
        cor_a   = "verde" if saldo_a >= 0 else "vermelho"
        st.markdown(f"""<div class="bloco">
            <div class="card-titulo">🔵 Adriely</div>
            <div style="font-size:13px;color:#9fa8da;">Gastou: {_fmt(a_gasto)}</div>
            <div style="font-size:13px;color:#9fa8da;">Recebe: {_fmt(honor_cada)}</div>
            <div class="card-valor {cor_a}" style="font-size:22px;margin-top:6px;">{_fmt(saldo_a)}</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        saldo_e = honor_cada - e_gasto
        cor_e   = "verde" if saldo_e >= 0 else "vermelho"
        st.markdown(f"""<div class="bloco">
            <div class="card-titulo">🟢 Eduarda</div>
            <div style="font-size:13px;color:#9fa8da;">Gastou: {_fmt(e_gasto)}</div>
            <div style="font-size:13px;color:#9fa8da;">Recebe: {_fmt(honor_cada)}</div>
            <div class="card-valor {cor_e}" style="font-size:22px;margin-top:6px;">{_fmt(saldo_e)}</div>
        </div>""", unsafe_allow_html=True)

    # detalhe do mês
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### Gastos do mês por categoria")
    det_a = {"Fixas":0.0, "Variáveis":0.0}
    det_e = {"Fixas":0.0, "Variáveis":0.0}
    for cat, meses in d["fixas"].items():
        val = float(meses.get(mes_sel,0) or 0)
        quem = d["fixas_quem"].get(cat,"dividido")
        if quem=="Adriely": det_a["Fixas"]+=val
        elif quem=="Eduarda": det_e["Fixas"]+=val
        else: det_a["Fixas"]+=val/2; det_e["Fixas"]+=val/2
    for item in d["variaveis"]:
        val = float(item.get("meses",{}).get(mes_sel,0) or 0)
        quem = item.get("quem","")
        if quem=="Adriely": det_a["Variáveis"]+=val
        elif quem=="Eduarda": det_e["Variáveis"]+=val
        else: det_a["Variáveis"]+=val/2; det_e["Variáveis"]+=val/2

    dc1, dc2 = st.columns(2)
    with dc1:
        st.markdown(f"""<div class="bloco">
            <div class="card-titulo">Adriely – Detalhamento</div>
            <div style="margin-top:8px;">
            <div style="display:flex;justify-content:space-between;padding:4px 0;border-bottom:1px solid #1a2a5e;">
                <span style="color:#9fa8da;">Fixas (parte dela)</span>
                <strong>{_fmt(det_a['Fixas'])}</strong>
            </div>
            <div style="display:flex;justify-content:space-between;padding:4px 0;">
                <span style="color:#9fa8da;">Variáveis</span>
                <strong>{_fmt(det_a['Variáveis'])}</strong>
            </div>
            </div>
        </div>""", unsafe_allow_html=True)
    with dc2:
        st.markdown(f"""<div class="bloco">
            <div class="card-titulo">Eduarda – Detalhamento</div>
            <div style="margin-top:8px;">
            <div style="display:flex;justify-content:space-between;padding:4px 0;border-bottom:1px solid #1a2a5e;">
                <span style="color:#9fa8da;">Fixas (parte dela)</span>
                <strong>{_fmt(det_e['Fixas'])}</strong>
            </div>
            <div style="display:flex;justify-content:space-between;padding:4px 0;">
                <span style="color:#9fa8da;">Variáveis</span>
                <strong>{_fmt(det_e['Variáveis'])}</strong>
            </div>
            </div>
        </div>""", unsafe_allow_html=True)

    # Acumulado geral
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### Acumulado Geral (todos os meses)")

    total_honor_all = sum(float(a.get("honorarios",0)) for a in d["acordos"] if a.get("status")=="pago")
    total_honor_all += sum(float(e.get("honorarios",0)) for e in d["execucoes"] if e.get("status")=="pago")
    total_honor_all += sum(float(h.get("valor",0)) for h in d["honorarios_iniciais"] if h.get("status")=="pago")
    honor_cada_total = total_honor_all / 2

    total_a_all, total_e_all = 0.0, 0.0
    for col in COLS_B:
        ag, eg = gastos_mes(col)
        total_a_all += ag
        total_e_all += eg

    bc1, bc2, bc3 = st.columns(3)
    with bc1:
        st.markdown(f"""<div class="bloco">
            <div class="card-titulo">Total Honorários Recebidos</div>
            <div class="card-valor azul">{_fmt(total_honor_all)}</div>
            <div style="color:#5c6bc0;font-size:12px;margin-top:4px;">
                Cada sócia: {_fmt(honor_cada_total)}
            </div>
        </div>""", unsafe_allow_html=True)
    with bc2:
        saldo_at = honor_cada_total - total_a_all
        cor_at   = "verde" if saldo_at>=0 else "vermelho"
        st.markdown(f"""<div class="bloco">
            <div class="card-titulo">🔵 Adriely – Acumulado</div>
            <div style="font-size:13px;color:#9fa8da;">Total gasto: {_fmt(total_a_all)}</div>
            <div class="card-valor {cor_at}" style="font-size:22px;margin-top:6px;">{_fmt(saldo_at)}</div>
        </div>""", unsafe_allow_html=True)
    with bc3:
        saldo_et = honor_cada_total - total_e_all
        cor_et   = "verde" if saldo_et>=0 else "vermelho"
        st.markdown(f"""<div class="bloco">
            <div class="card-titulo">🟢 Eduarda – Acumulado</div>
            <div style="font-size:13px;color:#9fa8da;">Total gasto: {_fmt(total_e_all)}</div>
            <div class="card-valor {cor_et}" style="font-size:22px;margin-top:6px;">{_fmt(saldo_et)}</div>
        </div>""", unsafe_allow_html=True)

    if abs(total_a_all - total_e_all) > 0.01:
        diff = abs(total_a_all - total_e_all)
        mais = "Adriely" if total_a_all > total_e_all else "Eduarda"
        menos = "Eduarda" if mais=="Adriely" else "Adriely"
        st.markdown(f"""<div class="bloco" style="border-color:#ffa726;margin-top:12px;">
            ⚠️ <span style="color:#ffa726;font-weight:600;">Diferença de gastos:</span>
            <strong>{mais}</strong> pagou <strong>{_fmt(diff)}</strong> a mais.
            Para equalizar, <strong>{menos}</strong> deve <strong>{_fmt(diff/2)}</strong> para <strong>{mais}</strong>.
        </div>""", unsafe_allow_html=True)
