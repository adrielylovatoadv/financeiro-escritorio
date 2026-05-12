import streamlit as st
import json
import os
import io
import streamlit.components.v1 as _components
from datetime import date as _date
import pandas as pd

st.set_page_config(page_title="Financeiro – Escritório", page_icon="💼", layout="wide")

# ── Login ─────────────────────────────────────────────────────────────────────
_senha_correta = st.secrets.get("SENHA", "escritorio2024") if hasattr(st, "secrets") else "escritorio2024"
if "logado" not in st.session_state:
    st.session_state["logado"] = False
if not st.session_state["logado"]:
    st.markdown("""<div style="max-width:380px;margin:80px auto;background:white;border-radius:14px;
        padding:36px;box-shadow:0 4px 24px rgba(0,0,0,0.12);text-align:center;">
        <h2 style="color:#1a3a6b;margin-bottom:6px;">💼 Financeiro Escritório</h2>
        <p style="color:#718096;margin-bottom:24px;">Sócias: Adriely & Eduarda</p>
    </div>""", unsafe_allow_html=True)
    with st.form("login_fin"):
        st.markdown("### 🔐 Acesso")
        _senha = st.text_input("Senha", type="password")
        if st.form_submit_button("Entrar", use_container_width=True):
            if _senha == _senha_correta:
                st.session_state["logado"] = True
                st.rerun()
            else:
                st.error("Senha incorreta.")
    st.stop()

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

# Dia 10 de cada mês – usamos para auto-marcar fixas como pagas
COL_DATE10 = {
    "Out":  _date(2025,10,10), "Nov":  _date(2025,11,10), "Dez":  _date(2025,12,10),
    "Jan":  _date(2026, 1,10), "Fev":  _date(2026, 2,10), "Mar":  _date(2026, 3,10),
    "Abr":  _date(2026, 4,10), "Mai":  _date(2026, 5,10), "Jun":  _date(2026, 6,10),
    "Jul":  _date(2026, 7,10), "Ago":  _date(2026, 8,10), "Set":  _date(2026, 9,10),
    "Out2": _date(2026,10,10), "Nov2": _date(2026,11,10), "Dez2": _date(2026,12,10),
}

# Status: cores e ciclos
ST_COR   = {"pago": "🟢", "pendente": "🔴", "repasse": "🟡"}
ST_CICLO3 = {"pago": "repasse", "repasse": "pendente", "pendente": "pago"}   # receitas
ST_CICLO2 = {"pago": "pendente", "pendente": "pago"}                          # despesas

LEGENDA_RECEITAS = """<div style='font-size:11px;color:#7986cb;margin-bottom:8px;'>
  🟢 recebido &nbsp;|&nbsp; 🔴 não recebido &nbsp;|&nbsp; 🟡 recebido – repasse ao cliente pendente
  &nbsp;&nbsp;<em>(clique na bolinha para alterar)</em></div>"""

LEGENDA_DESPESAS = """<div style='font-size:11px;color:#7986cb;margin-bottom:8px;'>
  🟢 pago &nbsp;|&nbsp; 🔴 não pago &nbsp;&nbsp;<em>(clique na bolinha para alterar)</em></div>"""

def _st3(col, key, item, campo="status"):
    """Botão de status 3 estados (receitas): 🟢 pago · 🟡 repasse · 🔴 pendente"""
    cur = item.get(campo, "pendente")
    if cur not in ST_COR: cur = "pendente"
    if col.button(ST_COR[cur], key=key):
        item[campo] = ST_CICLO3[cur]
        return True
    return False

def _st2(col, key, item, campo="status"):
    """Botão de status 2 estados (despesas): 🟢 pago · 🔴 pendente"""
    cur = item.get(campo, "pendente")
    if cur not in ("pago","pendente"): cur = "pendente"
    if col.button(ST_COR[cur], key=key):
        item[campo] = ST_CICLO2[cur]
        return True
    return False

def _v(s):
    import re
    if s is None: return 0.0
    s = re.sub(r'[^\d,.]','', str(s))
    if not s: return 0.0
    if ',' in s: s = s.replace('.','').replace(',','.')
    try: return float(s)
    except: return 0.0

def _to_excel(df: pd.DataFrame) -> bytes:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        df.to_excel(w, index=False)
    return buf.getvalue()

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
        {"mes":"Mar/2026","data_pagamento":"04/03/2026","cliente":"BERNADETE NARDI DE PAULA","reu":"SANTANDER","objeto":"PENSAO 145353251 · falta R$ 352,64 em cobrança","processo":"5001232-34.2025.8.13.0329","valor_acordo":3000.00,"honorarios":1245.00,"status":"pago"},
        {"mes":"Mar/2026","data_pagamento":"09/03/2026","cliente":"ROSARIA LOGUERCIOS DOS SANTOS","reu":"ITAU","objeto":"MENSAL COMBINAQUI · R$ 4.500,00 recebido · falta R$ 636,68 em cobrança","processo":"5000000-50.2026.8.13.0329","valor_acordo":5000.00,"honorarios":2075.00,"status":"pago"},
        {"mes":"Mar/2026","data_pagamento":"10/03/2026","cliente":"TEREZINHA IVONE DE SOUSA","reu":"ITAU","objeto":"MENSAL COMBINAQUI","processo":"5000013-49.2026.8.13.0329","valor_acordo":4000.00,"honorarios":1660.00,"status":"pago"},
        {"mes":"Mar/2026","data_pagamento":"10/03/2026","cliente":"LENITA APARECIDA PAULA SOUSA","reu":"ITAU","objeto":"SISDEB","processo":"5001328-49.2025.8.13.0329","valor_acordo":3760.00,"honorarios":1560.40,"status":"pago"},
        {"mes":"Mar/2026","data_pagamento":"11/03/2026","cliente":"CLEIDE DE SOUSA ALVES","reu":"ITAU","objeto":"MENSAL COMBINAQUI","processo":"5001141-41.2025.8.13.0329","valor_acordo":5000.00,"honorarios":2075.00,"status":"pago"},
        {"mes":"Mar/2026","data_pagamento":"16/03/2026","cliente":"MARTA APARECIDA DE PAULA REIS","reu":"ITAU","objeto":"SISDEB","processo":"5001331-04.2025.8.13.0329","valor_acordo":5000.00,"honorarios":2075.00,"status":"pago"},
        {"mes":"Mar/2026","data_pagamento":"23/03/2026","cliente":"MARTA APARECIDA DE PAULA REIS","reu":"ITAU","objeto":"TAR PACOTE","processo":"5000001-35.2026.8.13.0329","valor_acordo":5000.00,"honorarios":2075.00,"status":"pago"},
        {"mes":"Mar/2026","data_pagamento":"26/03/2026","cliente":"MARTA APARECIDA DE PAULA REIS","reu":"ITAU","objeto":"CAP PIC","processo":"5001333-71.2025.8.13.0329","valor_acordo":5600.00,"honorarios":2324.00,"status":"pago"},
        {"mes":"Abr/2026","data_pagamento":"01/04/2026","cliente":"ELISABETE APARECIDA MARANGONI","reu":"ITAU","objeto":"RENEGOCIAÇÕES","processo":"5001363-09.2025.8.13.0329","valor_acordo":8237.44,"honorarios":3418.48,"status":"pago"},
        {"mes":"Abr/2026","data_pagamento":"01/04/2026","cliente":"JOAO DONIZETE VAZ","reu":"ITAU","objeto":"MENSAL COMBINAQUI","processo":"5001243-63.2025.8.13.0329","valor_acordo":6442.64,"honorarios":2673.70,"status":"pago"},
        {"mes":"Abr/2026","data_pagamento":"17/04/2026","cliente":"CLEIDE DE SOUSA ALVES","reu":"ITAU","objeto":"SEGURO CARTAO","processo":"5001149-18.2025.8.13.0329","valor_acordo":5500.00,"honorarios":2282.50,"status":"pago"},
        {"mes":"Abr/2026","data_pagamento":"17/04/2026","cliente":"MARTA APARECIDA DE PAULA REIS","reu":"ITAU","objeto":"SEGURO CARTAO","processo":"5001193-37.2025.8.13.0329","valor_acordo":4270.00,"honorarios":1772.05,"status":"pago"},
        {"mes":"Abr/2026","data_pagamento":"23/04/2026","cliente":"HELIO DE SOUZA","reu":"PAN","objeto":"344905159-2 / 339148026-0 / 336819430-8 / 334093468-0","processo":"5008533-48.2025.8.13.0647","valor_acordo":11000.00,"honorarios":4565.00,"status":"pago"},
        {"mes":"Mai/2026","data_pagamento":"05/05/2026","cliente":"LENITA APARECIDA PAULA SOUSA","reu":"ITAU","objeto":"SEGURO CARTÃO + ITAU SEG VIDA PF + PGTO PROTECAO FAMILIAR","processo":"5000206-64.2026.8.13.0329","valor_acordo":4320.68,"honorarios":1793.08,"status":"pago"},
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
        "finalizados_sem_honor": _finalizados_iniciais(),
    }

def _finalizados_iniciais():
    return [
        {"cliente":"MARCIA MARQUES SILVA ESTEVÃO","reu":"CAMPOS ELISIOS",
         "processo":"5000059-38.2026.8.13.0329","objeto":"OBRIGAÇÃO DE FAZER",
         "data_finalizacao":"","motivo":"Extinção"},
        {"cliente":"MATHEUS SERRAGLIA REIS AMENT","reu":"ITAU",
         "processo":"4006494-36.2026.8.26.0506","objeto":"TAR PACOTE",
         "data_finalizacao":"","motivo":"Cancelado"},
        {"cliente":"HELIO DE SOUZA","reu":"BANRISUL",
         "processo":"5008843-54.2025.8.13.0647","objeto":"13176708",
         "data_finalizacao":"","motivo":"Desistência"},
        {"cliente":"JOSE CARLOS DOS SANTOS","reu":"QI SOCIE",
         "processo":"5001251-40.2025.8.13.0329","objeto":"0023336525JCD",
         "data_finalizacao":"","motivo":"Desistência"},
        {"cliente":"RUTH FELICIANA DA SILVA SOUZA","reu":"SANTANDER",
         "processo":"5007260-34.2025.8.13.0647","objeto":"RMC n. 877742182-0",
         "data_finalizacao":"","motivo":"Improcedência"},
        {"cliente":"HELIO DE SOUZA","reu":"BMG",
         "processo":"5007845-86.2025.8.13.0647","objeto":"RMC 8932388 e 11105568",
         "data_finalizacao":"","motivo":"Desistência"},
        {"cliente":"ANA MARIA DE OLIVEIRA","reu":"FACTA",
         "processo":"5001079-98.2025.8.13.0329","objeto":"73773620",
         "data_finalizacao":"","motivo":"Desistência"},
        {"cliente":"MATHEUS SERRAGLIA REIS AMENT","reu":"ITAU",
         "processo":"4014073-35.2026.8.26.0506","objeto":"TAR PACOTE",
         "data_finalizacao":"","motivo":"Desistência"},
        {"cliente":"ANA MARIA DE OLIVEIRA","reu":"ITAU",
         "processo":"5000918-88.2025.8.13.0329",
         "objeto":"647932633 / 633079531 / 638223061 / 599824559",
         "data_finalizacao":"","motivo":"Desistência"},
    ]

def _auto_pago_fixas(d):
    """Marca despesas fixas como pagas para meses cujo dia 10 já passou."""
    hoje = _date.today()
    for cat in d.get("fixas", {}):
        if cat not in d["fixas_status"]: d["fixas_status"][cat] = {}
        for col, dt10 in COL_DATE10.items():
            if d["fixas"][cat].get(col, 0) > 0 and hoje >= dt10:
                d["fixas_status"][cat][f"{col}_adriely"] = "pago"
                d["fixas_status"][cat][f"{col}_eduarda"] = "pago"

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
        if "finalizados_sem_honor" not in d:
            d["finalizados_sem_honor"] = _finalizados_iniciais()
        if not d.get("_migrated_residuais"):
            _res = {
                "5001232-34.2025.8.13.0329": "PENSAO 145353251 · falta R$ 352,64 em cobrança",
                "5000000-50.2026.8.13.0329": "MENSAL COMBINAQUI · R$ 4.500,00 recebido · falta R$ 636,68 em cobrança",
            }
            for a in d.get("acordos", []):
                if a.get("processo") in _res:
                    a["objeto"] = _res[a["processo"]]
            d["_migrated_residuais"] = True
        for a in d.get("acordos", []):
            if "objeto" not in a: a["objeto"] = ""
            if "data_pagamento" not in a: a["data_pagamento"] = ""
        _auto_pago_fixas(d)
        return d
    di = dados_iniciais()
    _auto_pago_fixas(di)
    return di

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
                "🏢 Desp. Fixas","🛒 Desp. Variáveis","⚖️ Balanço","📁 Finalizados s/ Hon."])
tab_dash, tab_ac, tab_ex, tab_hi, tab_fix, tab_var, tab_bal, tab_fin = tabs

# ─────────────────────────────────────────────────────────────────────────────
# Helpers de totais
# ─────────────────────────────────────────────────────────────────────────────
def total_recebido():
    """Soma dos valor_acordo dos acordos já recebidos (pago ou repasse)."""
    return sum(float(a.get("valor_acordo",0)) for a in d["acordos"]
               if a.get("status") in ("pago","repasse"))

def total_honorarios_recebidos():
    """Honorários já recebidos (status pago ou repasse)."""
    t = sum(float(a.get("honorarios",0)) for a in d["acordos"]
            if a.get("status") in ("pago","repasse"))
    t += sum(float(e.get("honorarios",0)) for e in d["execucoes"]
             if e.get("status") in ("pago","repasse"))
    t += sum(float(h.get("valor",0)) for h in d["honorarios_iniciais"]
             if h.get("status")=="pago")
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
    tr  = total_recebido()
    thr = total_honorarios_recebidos()
    tp  = total_honorarios_pendente()
    tf  = total_fixas()
    tv  = total_variaveis()
    saldo = thr - tf - tv

    c1,c2,c3,c4 = st.columns(4)
    cards = [
        ("Total Recebido", tr, "azul"),
        ("Honorários Recebidos", thr, "verde"),
        ("Pendente de Recebimento", tp, "vermelho" if tp>0 else "azul"),
        ("Saldo Líquido", saldo, "verde" if saldo>=0 else "vermelho"),
    ]
    for col,(titulo,val,cor) in zip([c1,c2,c3,c4], cards):
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
    st.markdown("""<div class="bloco" style="border-color:#5c6bc0;padding:12px 16px;margin-bottom:4px;">
        <span style="color:#7986cb;font-size:12px;">
        📐 <strong>Cálculo automático:</strong>
        Honorários = 10% do valor + 35% do restante (= 41,5% do valor do acordo)
        </span>
    </div>""", unsafe_allow_html=True)
    st.markdown(LEGENDA_RECEITAS, unsafe_allow_html=True)

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

    # cabeçalho (sem coluna Processo)
    hdr = st.columns([1.0,1.0,2.0,0.8,2.0,1.1,1.1,0.5,0.4])
    for col, lbl in zip(hdr,["Mês","Data Pgto","Cliente","Réu","Objeto","Valor Acordo","Honorários","","Del"]):
        col.markdown(f"<span style='font-size:10px;color:#7986cb;font-weight:600;'>{lbl}</span>",
                     unsafe_allow_html=True)

    to_del = None; mudou_ac = False
    for i, a in enumerate(d["acordos"]):
        cols = st.columns([1.0,1.0,2.0,0.8,2.0,1.1,1.1,0.5,0.4])
        a["mes"] = cols[0].selectbox("", MESES,
            index=MESES.index(a["mes"]) if a.get("mes") in MESES else 0,
            key=f"ac_mes_{i}", label_visibility="collapsed")
        a["data_pagamento"] = cols[1].text_input("", value=a.get("data_pagamento",""),
            placeholder="DD/MM/AAAA", key=f"ac_dp_{i}", label_visibility="collapsed")
        a["cliente"] = cols[2].text_input("", value=a.get("cliente",""),
            key=f"ac_cli_{i}", label_visibility="collapsed")
        a["reu"] = cols[3].text_input("", value=a.get("reu",""),
            key=f"ac_reu_{i}", label_visibility="collapsed")
        a["objeto"] = cols[4].text_input("", value=a.get("objeto",""),
            key=f"ac_obj_{i}", label_visibility="collapsed")

        va_str = st.session_state.get(f"ac_va_{i}", _vs(a.get("valor_acordo",0)))
        va_new = cols[5].text_input("", value=va_str, placeholder="0,00",
            key=f"ac_va_{i}", label_visibility="collapsed")
        try: va = float(va_new.replace(".","").replace(",",".")) if va_new else 0.0
        except: va = 0.0
        a["valor_acordo"] = va
        a["honorarios"] = calc_acordo(va)

        cols[6].markdown(f"""<div style='padding-top:8px;font-size:13px;font-weight:600;color:#4caf50;'>
            {_fmt(a["honorarios"])}</div>""", unsafe_allow_html=True)

        if _st3(cols[7], f"ac_st_{i}", a): mudou_ac = True
        if cols[8].button("🗑️", key=f"ac_del_{i}"): to_del = i

    if mudou_ac: salvar(d); st.rerun()

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

    if d["acordos"]:
        df_ac = pd.DataFrame([{
            "Mês": a.get("mes",""), "Data Pagamento": a.get("data_pagamento",""),
            "Cliente": a.get("cliente",""), "Réu": a.get("reu",""),
            "Objeto": a.get("objeto",""),
            "Valor Acordo (R$)": float(a.get("valor_acordo",0)),
            "Honorários (R$)": float(a.get("honorarios",0)),
            "Status": a.get("status",""),
        } for a in d["acordos"]])
        st.download_button("⬇️ Baixar Excel", data=_to_excel(df_ac),
            file_name="acordos.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="dl_ac")

# ─────────────────────────────────────────────────────────────────────────────
# EXECUÇÕES
# ─────────────────────────────────────────────────────────────────────────────
with tab_ex:
    st.markdown("### ⚖️ Execuções")
    st.markdown("""<div class="bloco" style="border-color:#5c6bc0;padding:12px 16px;margin-bottom:4px;">
        <span style="color:#7986cb;font-size:12px;">
        📐 <strong>Cálculo automático:</strong>
        Honorários = 35% do valor percebido + honorários de sucumbência
        </span>
    </div>""", unsafe_allow_html=True)
    st.markdown(LEGENDA_RECEITAS, unsafe_allow_html=True)

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
        hdr = st.columns([1.4,2.2,1.2,1.8,1.8,1.8,0.5,0.5])
        for col, lbl in zip(hdr,["Mês","Cliente","Réu","Val. Percebido","Sucumbência","Honorários","",""]):
            col.markdown(f"<span style='font-size:10px;color:#7986cb;font-weight:600;'>{lbl}</span>",
                         unsafe_allow_html=True)

        to_del_e = None; mudou_ex = False
        for i, e in enumerate(d["execucoes"]):
            cols = st.columns([1.4,2.2,1.2,1.8,1.8,1.8,0.5,0.5])
            e["mes"] = cols[0].selectbox("", MESES,
                index=MESES.index(e["mes"]) if e.get("mes") in MESES else 0,
                key=f"ex_mes_{i}", label_visibility="collapsed")
            e["cliente"] = cols[1].text_input("", value=e.get("cliente",""),
                key=f"ex_cli_{i}", label_visibility="collapsed")
            e["reu"] = cols[2].text_input("", value=e.get("reu",""),
                key=f"ex_reu_{i}", label_visibility="collapsed")

            vp_str = st.session_state.get(f"ex_vp_{i}", _vs(e.get("valor_percebido",0)))
            vp_new = cols[3].text_input("", value=vp_str, placeholder="0,00",
                key=f"ex_vp_{i}", label_visibility="collapsed")
            try: vp = float(vp_new.replace(".","").replace(",",".")) if vp_new else 0.0
            except: vp = 0.0

            sc_str = st.session_state.get(f"ex_sc_{i}", _vs(e.get("sucumbencia",0)))
            sc_new = cols[4].text_input("", value=sc_str, placeholder="0,00",
                key=f"ex_sc_{i}", label_visibility="collapsed")
            try: sc = float(sc_new.replace(".","").replace(",",".")) if sc_new else 0.0
            except: sc = 0.0

            e["valor_percebido"] = vp
            e["sucumbencia"] = sc
            e["honorarios"] = calc_execucao(vp, sc)

            cols[5].markdown(f"""<div style='padding-top:8px;font-size:14px;font-weight:600;color:#4caf50;'>
                {_fmt(e['honorarios'])}</div>""", unsafe_allow_html=True)
            if _st3(cols[6], f"ex_st_{i}", e): mudou_ex = True
            if cols[7].button("🗑️", key=f"ex_del_{i}"): to_del_e = i

        if mudou_ex: salvar(d); st.rerun()
        if to_del_e is not None:
            d["execucoes"].pop(to_del_e); salvar(d); st.rerun()

    if d["execucoes"]:
        st.markdown("<hr class='divider'>", unsafe_allow_html=True)
        df_ex = pd.DataFrame([{
            "Mês": e.get("mes",""), "Cliente": e.get("cliente",""),
            "Réu": e.get("reu",""),
            "Val. Percebido (R$)": float(e.get("valor_percebido",0)),
            "Sucumbência (R$)": float(e.get("sucumbencia",0)),
            "Honorários (R$)": float(e.get("honorarios",0)),
            "Status": e.get("status",""),
        } for e in d["execucoes"]])
        st.download_button("⬇️ Baixar Excel", data=_to_excel(df_ex),
            file_name="execucoes.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="dl_ex")

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

    st.markdown(LEGENDA_DESPESAS, unsafe_allow_html=True)

    hdr = st.columns([3,1.8,1.8,2.5,0.5,0.5])
    for col, lbl in zip(hdr,["Cliente","Valor","Data Pagto","Observação","","Del"]):
        col.markdown(f"<span style='font-size:10px;color:#7986cb;font-weight:600;'>{lbl}</span>",
                     unsafe_allow_html=True)

    to_del_h = None; mudou_hi = False
    for i, h in enumerate(d["honorarios_iniciais"]):
        cols = st.columns([3,1.8,1.8,2.5,0.5,0.5])
        h["cliente"] = cols[0].text_input("", value=h.get("cliente",""),
            key=f"hi_cli_{i}", label_visibility="collapsed")

        vh_str = st.session_state.get(f"hi_val_{i}", _vs(h.get("valor",0)))
        vh_new = cols[1].text_input("", value=vh_str, placeholder="0,00",
            key=f"hi_val_{i}", label_visibility="collapsed")
        try: vhv = float(vh_new.replace(".","").replace(",",".")) if vh_new else 0.0
        except: vhv = 0.0
        h["valor"] = vhv

        h["data_pagamento"] = cols[2].text_input("", value=h.get("data_pagamento",""),
            placeholder="DD/MM/AAAA", key=f"hi_dt_{i}", label_visibility="collapsed")
        h["observacao"] = cols[3].text_input("", value=h.get("observacao",""),
            key=f"hi_obs_{i}", label_visibility="collapsed")
        if _st2(cols[4], f"hi_st_{i}", h): mudou_hi = True
        if cols[5].button("🗑️", key=f"hi_del_{i}"): to_del_h = i

    if mudou_hi: salvar(d); st.rerun()
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
    col_lbl  = {"Out":"Out/25","Nov":"Nov/25","Dez":"Dez/25","Jan":"Jan/26",
                "Fev":"Fev/26","Mar":"Mar/26","Abr":"Abr/26","Mai":"Mai/26"}

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

    _hj = _date.today()
    _m2c = {(2025,10):"Out",(2025,11):"Nov",(2025,12):"Dez",
            (2026,1):"Jan",(2026,2):"Fev",(2026,3):"Mar",(2026,4):"Abr",(2026,5):"Mai",
            (2026,6):"Jun",(2026,7):"Jul",(2026,8):"Ago",(2026,9):"Set",
            (2026,10):"Out2",(2026,11):"Nov2",(2026,12):"Dez2"}
    mes_atual_col = _m2c.get((_hj.year, _hj.month), "Mai")
    col_status = st.columns([3, 2, 2])
    col_status[0].markdown("<span style='font-size:11px;color:#7986cb;font-weight:600;'>Categoria</span>",
                           unsafe_allow_html=True)
    col_status[1].markdown("<span style='font-size:11px;color:#9fa8da;font-weight:600;'>Adriely</span>",
                           unsafe_allow_html=True)
    col_status[2].markdown("<span style='font-size:11px;color:#a5d6a7;font-weight:600;'>Eduarda</span>",
                           unsafe_allow_html=True)

    st.markdown(LEGENDA_DESPESAS, unsafe_allow_html=True)
    mudou_fix_st = False
    for cat in d["fixas"]:
        val = d["fixas"][cat].get(mes_atual_col, 0)
        if val <= 0: continue
        cols_s = st.columns([3, 1, 1])
        cols_s[0].markdown(f"<div style='padding-top:8px;'>{cat} — {_fmt(val/2)} cada</div>",
                           unsafe_allow_html=True)
        if cat not in d["fixas_status"]: d["fixas_status"][cat] = {}
        # Adriely
        fa = {"status": d["fixas_status"][cat].get(f"{mes_atual_col}_adriely","pendente")}
        if _st2(cols_s[1], f"fxst_a_{cat}", fa):
            d["fixas_status"][cat][f"{mes_atual_col}_adriely"] = fa["status"]
            mudou_fix_st = True
        else:
            d["fixas_status"][cat][f"{mes_atual_col}_adriely"] = fa["status"]
        # Eduarda
        fe = {"status": d["fixas_status"][cat].get(f"{mes_atual_col}_eduarda","pendente")}
        if _st2(cols_s[2], f"fxst_e_{cat}", fe):
            d["fixas_status"][cat][f"{mes_atual_col}_eduarda"] = fe["status"]
            mudou_fix_st = True
        else:
            d["fixas_status"][cat][f"{mes_atual_col}_eduarda"] = fe["status"]
    if mudou_fix_st: salvar(d); st.rerun()

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
    st.markdown(LEGENDA_DESPESAS, unsafe_allow_html=True)

    col_va, col_vs = st.columns([6,1])
    with col_va:
        if st.button("➕ Nova Despesa Variável"):
            d["variaveis"].append({"descricao":"","valor":0.0,"parcelas":"1x",
                                    "quem":"Adriely","onde":"","status":"pendente","meses":{}})
            salvar(d); st.rerun()
    with col_vs:
        if st.button("💾 Salvar  ", key="sv_var"): salvar(d); st.success("Salvo!")

    COLS_VIS_V = ["Out","Nov","Dez","Jan","Fev","Mar","Abr","Mai"]
    cl = {"Out":"Out/25","Nov":"Nov/25","Dez":"Dez/25","Jan":"Jan/26",
          "Fev":"Fev/26","Mar":"Mar/26","Abr":"Abr/26","Mai":"Mai/26"}

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
        if _st2(row[5], f"vst_{i}", item): salvar(d); st.rerun()

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
    cl_b   = {"Out":"Out/25","Nov":"Nov/25","Dez":"Dez/25","Jan":"Jan/26",
              "Fev":"Fev/26","Mar":"Mar/26","Abr":"Abr/26","Mai":"Mai/26"}

    mes_sel = st.radio("Mês:", COLS_B, horizontal=True,
                        format_func=lambda x: cl_b[x], key="bal_mes")

    mes_full = COL_TO_MES.get(mes_sel,"")

    # honorários do mês (excluindo repasses)
    honor_mes = sum(
        float(a.get("honorarios", 0)) for a in d["acordos"]
        if a.get("mes") == mes_full and a.get("status", "") != "repasse"
    )
    honor_mes += sum(
        float(e.get("honorarios", 0)) for e in d["execucoes"]
        if e.get("mes") == mes_full and e.get("status", "") != "repasse"
    )
    # honorários iniciais pagos no mês
    _mes_num = {"Out":"10/2025","Nov":"11/2025","Dez":"12/2025",
                "Jan":"01/2026","Fev":"02/2026","Mar":"03/2026",
                "Abr":"04/2026","Mai":"05/2026"}
    _mes_ref = _mes_num.get(mes_sel, "")
    honor_mes += sum(
        float(h.get("valor", 0)) for h in d.get("honorarios_iniciais", [])
        if h.get("status") == "pago" and _mes_ref in str(h.get("data_pagamento", ""))
    )

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

# ─────────────────────────────────────────────────────────────────────────────
# PROCESSOS FINALIZADOS SEM HONORÁRIO
# ─────────────────────────────────────────────────────────────────────────────
with tab_fin:
    st.markdown("### 📁 Processos Finalizados sem Honorário")
    st.markdown("""<div class="bloco" style="border-color:#5c6bc0;padding:12px 16px;margin-bottom:12px;">
        <span style="color:#7986cb;font-size:12px;">
        Processos encerrados nos quais não houve recebimento de honorários
        (improcedência, acordo sem honorário, desistência, etc.)
        </span>
    </div>""", unsafe_allow_html=True)

    fin_a, fin_s = st.columns([6,1])
    with fin_a:
        if st.button("➕ Novo Processo"):
            d["finalizados_sem_honor"].append({
                "cliente":"","reu":"","processo":"",
                "objeto":"","data_finalizacao":"","motivo":"Outro"
            })
            salvar(d); st.rerun()
    with fin_s:
        if st.button("💾 Salvar", key="sv_fin"):
            salvar(d); st.success("Salvo!")

    if not d["finalizados_sem_honor"]:
        st.markdown("""<div class="bloco" style="text-align:center;padding:32px;">
            <span style="color:#5c6bc0;font-size:14px;">Nenhum processo cadastrado ainda.</span>
        </div>""", unsafe_allow_html=True)
    else:
        hdr = st.columns([1.8,1.0,2.4,1.8,1.2,1.6,0.4])
        for col, lbl in zip(hdr, ["Cliente","Réu","Processo","Objeto","Data Final.","Motivo",""]):
            col.markdown(f"<span style='font-size:10px;color:#7986cb;font-weight:600;'>{lbl}</span>",
                         unsafe_allow_html=True)

        to_del_fin = None
        MOTIVOS = ["Improcedência","Acordo sem honorário","Desistência","Extinção","Cancelado","Prescrição","Outro"]
        for i, p in enumerate(d["finalizados_sem_honor"]):
            cols = st.columns([1.8,1.0,2.4,1.8,1.2,1.6,0.4])
            p["cliente"] = cols[0].text_input("", value=p.get("cliente",""),
                key=f"fin_cli_{i}", label_visibility="collapsed")
            p["reu"] = cols[1].text_input("", value=p.get("reu",""),
                key=f"fin_reu_{i}", label_visibility="collapsed")
            p["processo"] = cols[2].text_input("", value=p.get("processo",""),
                key=f"fin_proc_{i}", label_visibility="collapsed")
            p["objeto"] = cols[3].text_input("", value=p.get("objeto",""),
                key=f"fin_obj_{i}", label_visibility="collapsed")
            p["data_finalizacao"] = cols[4].text_input("", value=p.get("data_finalizacao",""),
                placeholder="DD/MM/AAAA", key=f"fin_dt_{i}", label_visibility="collapsed")
            cur_mot = p.get("motivo","Outro")
            p["motivo"] = cols[5].selectbox("", MOTIVOS,
                index=MOTIVOS.index(cur_mot) if cur_mot in MOTIVOS else len(MOTIVOS)-1,
                key=f"fin_mot_{i}", label_visibility="collapsed")
            if cols[6].button("🗑️", key=f"fin_del_{i}"): to_del_fin = i

        if to_del_fin is not None:
            d["finalizados_sem_honor"].pop(to_del_fin); salvar(d); st.rerun()

        st.markdown("<hr class='divider'>", unsafe_allow_html=True)
        st.markdown(f"<span style='color:#7986cb;font-size:13px;'>Total de processos: "
                    f"<strong style='color:#e8eaf6;'>{len(d['finalizados_sem_honor'])}</strong></span>",
                    unsafe_allow_html=True)
        df_fin = pd.DataFrame([{
            "Cliente": p.get("cliente",""), "Réu": p.get("reu",""),
            "Processo": p.get("processo",""), "Objeto": p.get("objeto",""),
            "Data Finalização": p.get("data_finalizacao",""),
            "Motivo": p.get("motivo",""),
        } for p in d["finalizados_sem_honor"]])
        st.download_button("⬇️ Baixar Excel", data=_to_excel(df_fin),
            file_name="finalizados_sem_honorario.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="dl_fin")

# ── Rodapé / Advogado ─────────────────────────────────────────────────────────
st.markdown("<br><hr class='divider'>", unsafe_allow_html=True)
st.markdown("""<div style='text-align:center;color:#5c6bc0;font-size:12px;padding:8px 0;'>
    ADRIELY NAVES LOVATO – OAB/SP 492.370 &nbsp;|&nbsp; OAB/MG 244.799
</div>""", unsafe_allow_html=True)
