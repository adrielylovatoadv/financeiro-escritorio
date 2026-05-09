"""
L&E ADV — Controle Jurídico Mobile
Advocacia Adriely & Eduarda
Versão: 1.0
"""

import json
import os
import re
import copy
from datetime import date, datetime
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.properties import StringProperty, ListProperty, BooleanProperty, ObjectProperty
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton, MDIconButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.list import MDList, TwoLineListItem, ThreeLineListItem, TwoLineIconListItem
from kivymd.uix.bottomnavigation import MDBottomNavigation, MDBottomNavigationItem

# ─────────────────────────────────────────────────────────
# CONSTANTES
# ─────────────────────────────────────────────────────────
SENHA = "escritorio2024"
MESES = [
    "Out/2025", "Nov/2025", "Dez/2025",
    "Jan/2026", "Fev/2026", "Mar/2026", "Abr/2026", "Mai/2026", "Jun/2026",
    "Jul/2026", "Ago/2026", "Set/2026", "Out/2026", "Nov/2026", "Dez/2026",
    "Jan/2027", "Fev/2027", "Mar/2027", "Abr/2027", "Mai/2027", "Jun/2027",
    "Jul/2027", "Ago/2027", "Set/2027", "Out/2027", "Nov/2027", "Dez/2027",
]
COL_FIXAS = ["Out", "Nov", "Dez", "Jan", "Fev", "Mar", "Abr", "Mai",
             "Jun", "Jul", "Ago", "Set", "Out2", "Nov2", "Dez2"]
COL_TO_MES = {
    "Out": "Out/2025", "Nov": "Nov/2025", "Dez": "Dez/2025",
    "Jan": "Jan/2026", "Fev": "Fev/2026", "Mar": "Mar/2026",
    "Abr": "Abr/2026", "Mai": "Mai/2026", "Jun": "Jun/2026",
    "Jul": "Jul/2026", "Ago": "Ago/2026", "Set": "Set/2026",
    "Out2": "Out/2026", "Nov2": "Nov/2026", "Dez2": "Dez/2026",
}

TRIBUNAIS = ["TJMG (CGJ/MG)", "TJSP"]
MOTIVOS_FIN = ["Improcedência", "Acordo sem honorário", "Desistência",
               "Extinção", "Cancelado", "Prescrição", "Outro"]

# ─────────────────────────────────────────────────────────
# UTILITÁRIOS
# ─────────────────────────────────────────────────────────
def _v(s):
    if s is None:
        return 0.0
    s = re.sub(r"[^\d,.]", "", str(s))
    if not s:
        return 0.0
    if "," in s:
        s = s.replace(".", "").replace(",", ".")
    try:
        return float(s)
    except Exception:
        return 0.0


def _fmt(v):
    try:
        return "R$ {:,.2f}".format(float(v)).replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "R$ 0,00"


def _vs(v):
    try:
        return "{:,.2f}".format(float(v)).replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "0,00"


def calc_acordo(valor):
    return round(valor * 0.10 + (valor * 0.90) * 0.35, 2)


def calc_execucao(percebido, sucumbencia):
    return round(percebido * 0.35 + sucumbencia, 2)


def fmt_brl(v):
    try:
        return "R$ {:,.2f}".format(float(v)).replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "R$ 0,00"


def fmt_pct(v):
    try:
        return "{:.4f}%".format(float(v)).replace(".", ",")
    except Exception:
        return "0,0000%"


# ─────────────────────────────────────────────────────────
# CÁLCULO JURÍDICO (índices)
# ─────────────────────────────────────────────────────────
def month_key(year, month):
    return f"{year:04d}-{month:02d}"


def next_month(year, month):
    return (year + 1, 1) if month == 12 else (year, month + 1)


def iter_months(start, end):
    cy, cm = start.year, start.month
    ey, em = end.year, end.month
    while (cy, cm) < (ey, em):
        yield cy, cm
        cy, cm = next_month(cy, cm)


def get_correction_index(year, month, indices):
    key = month_key(year, month)
    if (year < 2024) or (year == 2024 and month <= 8):
        val = indices.get("inpc", {}).get(key)
    else:
        val = indices.get("ipcae", {}).get(key)
    return val if val is not None else 0.0


def get_interest_rate(year, month, indices):
    if (year, month) <= (2002, 12):
        return 0.5
    elif (year, month) <= (2024, 8):
        return 1.0
    else:
        val = indices.get("selic", {}).get(month_key(year, month))
        return val if val is not None else 1.0


def calculate_charge(value, date_charge, date_calc, indices):
    if date_charge >= date_calc:
        return {"corrected": value, "correction_factor": 1.0,
                "interest_pct": 0.0, "interest_value": 0.0,
                "total": value, "months": 0}
    correction_factor = 1.0
    total_interest_pct = 0.0
    months_count = 0
    for year, month in iter_months(date_charge, date_calc):
        idx = get_correction_index(year, month, indices)
        correction_factor *= 1.0 + idx / 100.0
        total_interest_pct += get_interest_rate(year, month, indices)
        months_count += 1
    corrected = value * correction_factor
    interest_value = corrected * total_interest_pct / 100.0
    return {"corrected": corrected, "correction_factor": correction_factor,
            "interest_pct": total_interest_pct, "interest_value": interest_value,
            "total": corrected + interest_value, "months": months_count}


# ─────────────────────────────────────────────────────────
# CAMADA DE DADOS
# ─────────────────────────────────────────────────────────
def get_data_path(filename):
    app = MDApp.get_running_app()
    return os.path.join(app.user_data_dir, filename)


def _dados_iniciais():
    return {
        "acordos": [],
        "execucoes": [],
        "honorarios_iniciais": [],
        "fixas": {
            "Aluguel": {"Jan": 600, "Fev": 600, "Mar": 600, "Abr": 600, "Mai": 600},
            "Internet": {"Jan": 79.90, "Fev": 79.90, "Mar": 79.90, "Abr": 79.90, "Mai": 79.90},
        },
        "fixas_quem": {"Aluguel": "dividido", "Internet": "dividido"},
        "fixas_status": {"Aluguel": {}, "Internet": {}},
        "variaveis": [],
        "finalizados_sem_honor": [],
    }


def carregar_financeiro():
    path = get_data_path("financeiro_data.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            d = json.load(f)
    else:
        # tenta copiar do bundle inicial
        bundle = os.path.join(os.path.dirname(__file__), "data", "financeiro_data.json")
        if os.path.exists(bundle):
            with open(bundle, "r", encoding="utf-8") as f:
                d = json.load(f)
        else:
            d = _dados_iniciais()
    # campos novos
    for k in ["execucoes", "honorarios_iniciais", "finalizados_sem_honor"]:
        if k not in d:
            d[k] = []
    if "fixas_quem" not in d:
        d["fixas_quem"] = {cat: "dividido" for cat in d.get("fixas", {})}
    if "fixas_status" not in d:
        d["fixas_status"] = {cat: {} for cat in d.get("fixas", {})}
    return d


def salvar_financeiro(d):
    path = get_data_path("financeiro_data.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)


def carregar_indices():
    path = get_data_path("indices_juridicos.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    bundle = os.path.join(os.path.dirname(__file__), "data", "indices_juridicos.json")
    if os.path.exists(bundle):
        with open(bundle, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"inpc": {}, "ipcae": {}, "selic": {}}


# ─────────────────────────────────────────────────────────
# KV STRING
# ─────────────────────────────────────────────────────────
KV = """
#:import NoTransition kivy.uix.screenmanager.NoTransition
#:import dp kivy.metrics.dp

<RoundCard@MDCard>:
    radius: [12]
    elevation: 2
    padding: dp(14)
    md_bg_color: 0.051, 0.106, 0.118, 1

<SectionLabel@MDLabel>:
    font_style: "H6"
    theme_text_color: "Custom"
    text_color: 0.56, 0.647, 0.988, 1
    bold: True
    size_hint_y: None
    height: dp(36)

<SmallLabel@MDLabel>:
    font_style: "Caption"
    theme_text_color: "Custom"
    text_color: 0.47, 0.522, 0.796, 1

<NavButton@MDRaisedButton>:
    size_hint_x: None
    width: dp(100)
    md_bg_color: 0.102, 0.165, 0.369, 1
    theme_text_color: "Custom"
    text_color: 1, 1, 1, 1
    font_size: "12sp"

# ── LOGIN ─────────────────────────────────────────────────
<LoginScreen>:
    name: "login"
    MDBoxLayout:
        orientation: "vertical"
        md_bg_color: 0.039, 0.059, 0.118, 1
        MDBoxLayout:
            size_hint_y: None
            height: dp(60)
        MDCard:
            size_hint: None, None
            size: dp(320), dp(320)
            pos_hint: {"center_x": .5, "center_y": .55}
            radius: [16]
            elevation: 8
            padding: dp(28)
            md_bg_color: 0.051, 0.106, 0.235, 1
            orientation: "vertical"
            spacing: dp(16)
            MDLabel:
                text: "⚖️"
                font_size: "42sp"
                halign: "center"
                size_hint_y: None
                height: dp(50)
            MDLabel:
                text: "L&E ADV"
                font_style: "H5"
                bold: True
                halign: "center"
                theme_text_color: "Custom"
                text_color: 0.902, 0.914, 0.965, 1
                size_hint_y: None
                height: dp(36)
            MDLabel:
                text: "Adriely & Eduarda"
                font_style: "Caption"
                halign: "center"
                theme_text_color: "Custom"
                text_color: 0.47, 0.522, 0.796, 1
                size_hint_y: None
                height: dp(20)
            MDTextField:
                id: senha_input
                hint_text: "Senha"
                password: True
                mode: "rectangle"
                size_hint_y: None
                height: dp(52)
                on_text_validate: root.fazer_login()
            MDRaisedButton:
                text: "ENTRAR"
                size_hint_x: 1
                md_bg_color: 0.102, 0.165, 0.616, 1
                on_release: root.fazer_login()

# ── TELA PRINCIPAL ─────────────────────────────────────────
<MainScreen>:
    name: "main"
    MDBottomNavigation:
        id: bottom_nav
        panel_color: 0.051, 0.082, 0.157, 1
        text_color_active: 0.396, 0.490, 0.988, 1
        MDBottomNavigationItem:
            name: "financeiro"
            text: "Financeiro"
            icon: "briefcase"
            FinanceiroTab:
                id: fin_tab
        MDBottomNavigationItem:
            name: "calculadora"
            text: "Calculadora"
            icon: "calculator-variant"
            CalculadoraTab:
                id: calc_tab
        MDBottomNavigationItem:
            name: "controle"
            text: "Controle"
            icon: "folder-multiple"
            ControleTab:
                id: ctrl_tab

# ── FINANCEIRO ─────────────────────────────────────────────
<FinanceiroTab>:
    MDBoxLayout:
        orientation: "vertical"
        md_bg_color: 0.039, 0.059, 0.118, 1
        # Barra de sub-navegação
        ScrollView:
            size_hint_y: None
            height: dp(48)
            do_scroll_y: False
            MDBoxLayout:
                orientation: "horizontal"
                size_hint_x: None
                width: dp(680)
                padding: dp(6), dp(6)
                spacing: dp(6)
                NavButton:
                    text: "Dashboard"
                    on_release: root.goto("dashboard")
                NavButton:
                    text: "Acordos"
                    on_release: root.goto("acordos")
                NavButton:
                    text: "Execuções"
                    on_release: root.goto("execucoes")
                NavButton:
                    text: "Honorários"
                    on_release: root.goto("honorarios")
                NavButton:
                    text: "Despesas"
                    on_release: root.goto("despesas")
                NavButton:
                    text: "Balanço"
                    on_release: root.goto("balanco")
                NavButton:
                    text: "Finalizados"
                    on_release: root.goto("finalizados")
        # Conteúdo
        ScreenManager:
            id: fin_screens
            transition: NoTransition()

# ── CALCULADORA ────────────────────────────────────────────
<CalculadoraTab>:
    MDBoxLayout:
        orientation: "vertical"
        md_bg_color: 0.039, 0.059, 0.118, 1
        MDScrollView:
            MDBoxLayout:
                orientation: "vertical"
                padding: dp(12)
                spacing: dp(10)
                size_hint_y: None
                height: self.minimum_height
                # Cabeçalho
                MDBoxLayout:
                    size_hint_y: None
                    height: dp(56)
                    MDLabel:
                        text: "⚖️  Calculadora Jurídica"
                        font_style: "H6"
                        bold: True
                        theme_text_color: "Custom"
                        text_color: 0.902, 0.914, 0.965, 1
                # Modo
                RoundCard:
                    size_hint_y: None
                    height: dp(90)
                    orientation: "vertical"
                    spacing: dp(4)
                    SectionLabel:
                        text: "Modalidade"
                    MDBoxLayout:
                        size_hint_y: None
                        height: dp(40)
                        spacing: dp(8)
                        MDRaisedButton:
                            id: btn_inicial
                            text: "Petição Inicial"
                            size_hint_x: 1
                            md_bg_color: 0.102, 0.165, 0.616, 1
                            on_release: root.set_modo("inicial")
                        MDRaisedButton:
                            id: btn_exec
                            text: "Execução"
                            size_hint_x: 1
                            md_bg_color: 0.051, 0.106, 0.235, 1
                            on_release: root.set_modo("execucao")
                # Dados do processo
                RoundCard:
                    size_hint_y: None
                    height: dp(280)
                    orientation: "vertical"
                    spacing: dp(8)
                    SectionLabel:
                        text: "Dados do Processo"
                    MDTextField:
                        id: numero_proc
                        hint_text: "Número do Processo"
                        mode: "rectangle"
                        size_hint_y: None
                        height: dp(48)
                    MDTextField:
                        id: exequente
                        hint_text: "Exequente / Autor"
                        mode: "rectangle"
                        size_hint_y: None
                        height: dp(48)
                    MDTextField:
                        id: executado
                        hint_text: "Executado / Réu"
                        mode: "rectangle"
                        size_hint_y: None
                        height: dp(48)
                    MDTextField:
                        id: data_calc
                        hint_text: "Data do Cálculo (DD/MM/AAAA)"
                        mode: "rectangle"
                        size_hint_y: None
                        height: dp(48)
                # Lançamentos
                RoundCard:
                    size_hint_y: None
                    height: self.minimum_height
                    orientation: "vertical"
                    spacing: dp(8)
                    SectionLabel:
                        text: "Lançamentos de Cobrança"
                    MDBoxLayout:
                        size_hint_y: None
                        height: dp(40)
                        spacing: dp(8)
                        MDRaisedButton:
                            text: "➕ Adicionar"
                            size_hint_x: 1
                            md_bg_color: 0.102, 0.165, 0.369, 1
                            on_release: root.add_lancamento()
                        MDRaisedButton:
                            text: "🗑️ Limpar"
                            size_hint_x: 0.5
                            md_bg_color: 0.369, 0.071, 0.071, 1
                            on_release: root.limpar_lancamentos()
                    MDBoxLayout:
                        id: lancamentos_box
                        orientation: "vertical"
                        size_hint_y: None
                        height: self.minimum_height
                        spacing: dp(4)
                # Controles extras (modo inicial)
                RoundCard:
                    id: ctrl_inicial_card
                    size_hint_y: None
                    height: dp(110)
                    orientation: "vertical"
                    spacing: dp(8)
                    SectionLabel:
                        text: "Repetição de Indébito"
                    MDBoxLayout:
                        size_hint_y: None
                        height: dp(36)
                        MDCheckbox:
                            id: chk_dobro
                            active: True
                            size_hint_x: None
                            width: dp(36)
                        MDLabel:
                            text: "Repetição em dobro (CDC art. 42)"
                            theme_text_color: "Custom"
                            text_color: 0.902, 0.914, 0.965, 1
                    MDTextField:
                        id: dano_moral
                        hint_text: "Dano Moral (R$) — opcional"
                        mode: "rectangle"
                        size_hint_y: None
                        height: dp(44)
                # Controles extras (modo execução)
                RoundCard:
                    id: ctrl_exec_card
                    size_hint_y: None
                    height: dp(110)
                    opacity: 0
                    orientation: "vertical"
                    spacing: dp(8)
                    SectionLabel:
                        text: "Execução"
                    MDTextField:
                        id: honor_pct
                        hint_text: "Honorários advocatícios (%)"
                        mode: "rectangle"
                        size_hint_y: None
                        height: dp(44)
                    MDBoxLayout:
                        size_hint_y: None
                        height: dp(36)
                        MDCheckbox:
                            id: chk_multa523
                            active: False
                            size_hint_x: None
                            width: dp(36)
                        MDLabel:
                            text: "Multa art. 523 CPC (10%)"
                            theme_text_color: "Custom"
                            text_color: 0.902, 0.914, 0.965, 1
                # Botão calcular
                MDRaisedButton:
                    text: "CALCULAR"
                    size_hint_x: 1
                    size_hint_y: None
                    height: dp(50)
                    md_bg_color: 0.102, 0.165, 0.616, 1
                    font_size: "16sp"
                    bold: True
                    on_release: root.calcular()
                # Resultado
                RoundCard:
                    id: resultado_card
                    size_hint_y: None
                    height: self.minimum_height
                    orientation: "vertical"
                    spacing: dp(6)
                    MDBoxLayout:
                        id: resultado_box
                        orientation: "vertical"
                        size_hint_y: None
                        height: self.minimum_height

# ── CONTROLE ───────────────────────────────────────────────
<ControleTab>:
    MDBoxLayout:
        orientation: "vertical"
        md_bg_color: 0.039, 0.059, 0.118, 1
        MDBoxLayout:
            size_hint_y: None
            height: dp(60)
        MDCard:
            size_hint: None, None
            size: dp(300), dp(200)
            pos_hint: {"center_x": .5, "center_y": .55}
            radius: [16]
            elevation: 4
            padding: dp(24)
            md_bg_color: 0.051, 0.106, 0.235, 1
            orientation: "vertical"
            spacing: dp(12)
            MDLabel:
                text: "📋"
                font_size: "40sp"
                halign: "center"
                size_hint_y: None
                height: dp(50)
            MDLabel:
                id: ctrl_status_label
                text: "Controle Processual"
                font_style: "H6"
                bold: True
                halign: "center"
                theme_text_color: "Custom"
                text_color: 0.902, 0.914, 0.965, 1
                size_hint_y: None
                height: dp(32)
            MDLabel:
                id: ctrl_info_label
                text: "Módulo em carregamento..."
                font_style: "Body2"
                halign: "center"
                theme_text_color: "Custom"
                text_color: 0.47, 0.522, 0.796, 1
"""


# ─────────────────────────────────────────────────────────
# TELAS DE FINANCEIRO (sub-telas)
# ─────────────────────────────────────────────────────────
class DashboardScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "dashboard"

    def on_enter(self):
        self.build_ui()

    def build_ui(self):
        self.clear_widgets()
        app = MDApp.get_running_app()
        d = app.dados

        tr = sum(float(a.get("valor_acordo", 0)) for a in d["acordos"]
                 if a.get("status") in ("pago", "repasse"))
        thr = (sum(float(a.get("honorarios", 0)) for a in d["acordos"]
                   if a.get("status") in ("pago", "repasse")) +
               sum(float(e.get("honorarios", 0)) for e in d["execucoes"]
                   if e.get("status") in ("pago", "repasse")) +
               sum(float(h.get("valor", 0)) for h in d["honorarios_iniciais"]
                   if h.get("status") == "pago"))
        tp = (sum(float(a.get("honorarios", 0)) for a in d["acordos"]
                  if a.get("status") == "pendente") +
              sum(float(e.get("honorarios", 0)) for e in d["execucoes"]
                  if e.get("status") == "pendente") +
              sum(float(h.get("valor", 0)) for h in d["honorarios_iniciais"]
                  if h.get("status") == "pendente"))
        tf = sum(sum(float(v) for v in cat.values())
                 for cat in d["fixas"].values())
        tv = sum(sum(float(v) for v in item.get("meses", {}).values())
                 for item in d["variaveis"])
        saldo = thr - tf - tv

        scroll = MDScrollView()
        box = MDBoxLayout(orientation="vertical", padding=dp(12),
                          spacing=dp(10), size_hint_y=None)
        box.bind(minimum_height=box.setter("height"))

        # título
        lbl = MDLabel(text="📊  Dashboard", font_style="H6", bold=True,
                      theme_text_color="Custom",
                      text_color=(0.902, 0.914, 0.965, 1),
                      size_hint_y=None, height=dp(48))
        box.add_widget(lbl)

        cards_data = [
            ("Total Recebido", _fmt(tr), (0.259, 0.647, 0.961, 1)),
            ("Honorários Recebidos", _fmt(thr), (0.298, 0.686, 0.314, 1)),
            ("Pendente de Recebimento", _fmt(tp), (0.937, 0.325, 0.314, 1)),
            ("Saldo Líquido", _fmt(saldo),
             (0.298, 0.686, 0.314, 1) if saldo >= 0 else (0.937, 0.325, 0.314, 1)),
        ]

        for titulo, valor, cor in cards_data:
            card = MDCard(orientation="vertical", size_hint_y=None,
                          height=dp(80), radius=[10], elevation=2,
                          padding=dp(14),
                          md_bg_color=(0.051, 0.106, 0.235, 1))
            card.add_widget(MDLabel(text=titulo, font_style="Caption",
                                    theme_text_color="Custom",
                                    text_color=(0.47, 0.522, 0.796, 1),
                                    size_hint_y=None, height=dp(20)))
            card.add_widget(MDLabel(text=valor, font_style="H6", bold=True,
                                    theme_text_color="Custom",
                                    text_color=cor,
                                    size_hint_y=None, height=dp(32)))
            box.add_widget(card)

        # Totais despesas
        desp_card = MDCard(orientation="vertical", size_hint_y=None,
                           height=dp(100), radius=[10], elevation=2,
                           padding=dp(14),
                           md_bg_color=(0.051, 0.106, 0.235, 1))
        desp_card.add_widget(MDLabel(text="Despesas", font_style="Caption",
                                     theme_text_color="Custom",
                                     text_color=(0.47, 0.522, 0.796, 1),
                                     size_hint_y=None, height=dp(18)))
        desp_card.add_widget(MDLabel(text=f"Fixas: {_fmt(tf)}",
                                     theme_text_color="Custom",
                                     text_color=(0.996, 0.655, 0.149, 1),
                                     size_hint_y=None, height=dp(24)))
        desp_card.add_widget(MDLabel(text=f"Variáveis: {_fmt(tv)}",
                                     theme_text_color="Custom",
                                     text_color=(0.996, 0.655, 0.149, 1),
                                     size_hint_y=None, height=dp(24)))
        box.add_widget(desp_card)

        # Pendentes
        pendentes = ([a for a in d["acordos"] if a.get("status") == "pendente"] +
                     [e for e in d["execucoes"] if e.get("status") == "pendente"] +
                     [h for h in d["honorarios_iniciais"] if h.get("status") == "pendente"])
        if pendentes:
            box.add_widget(MDLabel(text="⚠️ Pendentes de Recebimento",
                                   font_style="Subtitle1", bold=True,
                                   theme_text_color="Custom",
                                   text_color=(0.937, 0.325, 0.314, 1),
                                   size_hint_y=None, height=dp(36)))
            for p in pendentes[:10]:
                nome = p.get("cliente", "")
                val = _fmt(p.get("honorarios", p.get("valor", 0)))
                pc = MDCard(orientation="vertical", size_hint_y=None,
                            height=dp(70), radius=[8], elevation=1,
                            padding=dp(10),
                            md_bg_color=(0.18, 0.039, 0.039, 1))
                pc.add_widget(MDLabel(text=nome, bold=True,
                                      theme_text_color="Custom",
                                      text_color=(0.937, 0.325, 0.314, 1),
                                      size_hint_y=None, height=dp(24)))
                pc.add_widget(MDLabel(text=f"{p.get('mes', '')} | {val}",
                                      theme_text_color="Custom",
                                      text_color=(0.902, 0.914, 0.965, 1),
                                      size_hint_y=None, height=dp(22)))
                box.add_widget(pc)

        scroll.add_widget(box)
        self.add_widget(scroll)
        self.md_bg_color = (0.039, 0.059, 0.118, 1)


class AcordosScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "acordos"
        self.dialog = None

    def on_enter(self):
        self.build_ui()

    def build_ui(self):
        self.clear_widgets()
        app = MDApp.get_running_app()
        d = app.dados

        main_box = MDBoxLayout(orientation="vertical",
                               md_bg_color=(0.039, 0.059, 0.118, 1))

        # header
        hdr = MDBoxLayout(size_hint_y=None, height=dp(52),
                          padding=(dp(12), dp(4)),
                          md_bg_color=(0.039, 0.059, 0.118, 1))
        hdr.add_widget(MDLabel(text="🤝  Acordos",
                               font_style="H6", bold=True,
                               theme_text_color="Custom",
                               text_color=(0.902, 0.914, 0.965, 1)))
        btn_add = MDRaisedButton(text="➕ Novo", size_hint_x=None,
                                 width=dp(90), size_hint_y=None, height=dp(36),
                                 md_bg_color=(0.102, 0.165, 0.369, 1))
        btn_add.bind(on_release=lambda x: self.abrir_form(-1))
        hdr.add_widget(btn_add)
        main_box.add_widget(hdr)

        scroll = MDScrollView()
        box = MDBoxLayout(orientation="vertical", padding=dp(8),
                          spacing=dp(8), size_hint_y=None)
        box.bind(minimum_height=box.setter("height"))

        st_icons = {"pago": "🟢", "pendente": "🔴", "repasse": "🟡"}

        for i, a in enumerate(d["acordos"]):
            card = MDCard(orientation="vertical", size_hint_y=None,
                          height=dp(100), radius=[10], elevation=2,
                          padding=dp(10),
                          md_bg_color=(0.051, 0.106, 0.235, 1))

            row1 = MDBoxLayout(size_hint_y=None, height=dp(26))
            st_icon = st_icons.get(a.get("status", "pendente"), "🔴")
            row1.add_widget(MDLabel(
                text=f"{st_icon}  {a.get('cliente', '—')}",
                bold=True, theme_text_color="Custom",
                text_color=(0.902, 0.914, 0.965, 1)))

            row2 = MDBoxLayout(size_hint_y=None, height=dp(22))
            row2.add_widget(MDLabel(
                text=f"{a.get('mes', '')} | {a.get('reu', '')}",
                font_style="Caption",
                theme_text_color="Custom",
                text_color=(0.47, 0.522, 0.796, 1)))

            row3 = MDBoxLayout(size_hint_y=None, height=dp(30))
            row3.add_widget(MDLabel(
                text=f"Acordo: {_fmt(a.get('valor_acordo', 0))}  |  Hon.: {_fmt(a.get('honorarios', 0))}",
                theme_text_color="Custom",
                text_color=(0.259, 0.647, 0.961, 1)))
            btn_edit = MDIconButton(icon="pencil", theme_icon_color="Custom",
                                    icon_color=(0.47, 0.522, 0.796, 1),
                                    size_hint_x=None, width=dp(36))
            btn_del = MDIconButton(icon="delete", theme_icon_color="Custom",
                                   icon_color=(0.937, 0.325, 0.314, 1),
                                   size_hint_x=None, width=dp(36))
            idx = i
            btn_edit.bind(on_release=lambda x, i=idx: self.abrir_form(i))
            btn_del.bind(on_release=lambda x, i=idx: self.deletar(i))
            row3.add_widget(btn_edit)
            row3.add_widget(btn_del)

            card.add_widget(row1)
            card.add_widget(row2)
            card.add_widget(row3)
            box.add_widget(card)

        if not d["acordos"]:
            box.add_widget(MDLabel(
                text="Nenhum acordo cadastrado.\nClique em ➕ Novo para adicionar.",
                halign="center", theme_text_color="Custom",
                text_color=(0.47, 0.522, 0.796, 1),
                size_hint_y=None, height=dp(80)))

        scroll.add_widget(box)
        main_box.add_widget(scroll)
        self.add_widget(main_box)

    def abrir_form(self, idx):
        app = MDApp.get_running_app()
        d = app.dados
        novo = idx == -1
        item = {} if novo else copy.deepcopy(d["acordos"][idx])

        f_mes = MDTextField(hint_text="Mês (ex: Mai/2026)",
                            text=item.get("mes", MESES[0]),
                            mode="rectangle", size_hint_y=None, height=dp(48))
        f_data = MDTextField(hint_text="Data Pagto (DD/MM/AAAA)",
                             text=item.get("data_pagamento", ""),
                             mode="rectangle", size_hint_y=None, height=dp(48))
        f_cli = MDTextField(hint_text="Cliente",
                            text=item.get("cliente", ""),
                            mode="rectangle", size_hint_y=None, height=dp(48))
        f_reu = MDTextField(hint_text="Réu",
                            text=item.get("reu", ""),
                            mode="rectangle", size_hint_y=None, height=dp(48))
        f_proc = MDTextField(hint_text="Processo",
                             text=item.get("processo", ""),
                             mode="rectangle", size_hint_y=None, height=dp(48))
        f_obj = MDTextField(hint_text="Objeto",
                            text=item.get("objeto", ""),
                            mode="rectangle", size_hint_y=None, height=dp(48))
        f_val = MDTextField(hint_text="Valor Acordo (R$)",
                            text=_vs(item.get("valor_acordo", 0)),
                            mode="rectangle", size_hint_y=None, height=dp(48))

        form = MDBoxLayout(orientation="vertical", spacing=dp(8),
                           size_hint_y=None, height=dp(380))
        for f in [f_mes, f_data, f_cli, f_reu, f_proc, f_obj, f_val]:
            form.add_widget(f)

        def salvar(x):
            va = _v(f_val.text)
            entry = {
                "mes": f_mes.text.strip() or MESES[0],
                "data_pagamento": f_data.text.strip(),
                "cliente": f_cli.text.strip(),
                "reu": f_reu.text.strip(),
                "processo": f_proc.text.strip(),
                "objeto": f_obj.text.strip(),
                "valor_acordo": va,
                "honorarios": calc_acordo(va),
                "status": item.get("status", "pendente"),
            }
            if novo:
                d["acordos"].append(entry)
            else:
                d["acordos"][idx] = entry
            salvar_financeiro(d)
            self.dialog.dismiss()
            self.build_ui()

        self.dialog = MDDialog(
            title="Novo Acordo" if novo else "Editar Acordo",
            type="custom",
            content_cls=form,
            buttons=[
                MDFlatButton(text="CANCELAR",
                             on_release=lambda x: self.dialog.dismiss()),
                MDRaisedButton(text="SALVAR", on_release=salvar),
            ],
        )
        self.dialog.open()

    def deletar(self, idx):
        app = MDApp.get_running_app()
        d = app.dados

        def confirmar(x):
            d["acordos"].pop(idx)
            salvar_financeiro(d)
            dlg.dismiss()
            self.build_ui()

        dlg = MDDialog(
            title="Confirmar exclusão",
            text="Remover este acordo?",
            buttons=[
                MDFlatButton(text="NÃO", on_release=lambda x: dlg.dismiss()),
                MDRaisedButton(text="SIM", on_release=confirmar,
                               md_bg_color=(0.369, 0.071, 0.071, 1)),
            ],
        )
        dlg.open()


class ExecucoesScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "execucoes"
        self.dialog = None

    def on_enter(self):
        self.build_ui()

    def build_ui(self):
        self.clear_widgets()
        app = MDApp.get_running_app()
        d = app.dados

        main_box = MDBoxLayout(orientation="vertical",
                               md_bg_color=(0.039, 0.059, 0.118, 1))

        hdr = MDBoxLayout(size_hint_y=None, height=dp(52),
                          padding=(dp(12), dp(4)),
                          md_bg_color=(0.039, 0.059, 0.118, 1))
        hdr.add_widget(MDLabel(text="⚖️  Execuções",
                               font_style="H6", bold=True,
                               theme_text_color="Custom",
                               text_color=(0.902, 0.914, 0.965, 1)))
        btn_add = MDRaisedButton(text="➕ Nova", size_hint_x=None,
                                 width=dp(90), size_hint_y=None, height=dp(36),
                                 md_bg_color=(0.102, 0.165, 0.369, 1))
        btn_add.bind(on_release=lambda x: self.abrir_form(-1))
        hdr.add_widget(btn_add)
        main_box.add_widget(hdr)

        scroll = MDScrollView()
        box = MDBoxLayout(orientation="vertical", padding=dp(8),
                          spacing=dp(8), size_hint_y=None)
        box.bind(minimum_height=box.setter("height"))

        st_icons = {"pago": "🟢", "pendente": "🔴", "repasse": "🟡"}

        for i, e in enumerate(d["execucoes"]):
            card = MDCard(orientation="vertical", size_hint_y=None,
                          height=dp(100), radius=[10], elevation=2,
                          padding=dp(10),
                          md_bg_color=(0.051, 0.106, 0.235, 1))
            st_icon = st_icons.get(e.get("status", "pendente"), "🔴")
            r1 = MDBoxLayout(size_hint_y=None, height=dp(26))
            r1.add_widget(MDLabel(text=f"{st_icon}  {e.get('cliente', '—')}",
                                  bold=True, theme_text_color="Custom",
                                  text_color=(0.902, 0.914, 0.965, 1)))
            r2 = MDBoxLayout(size_hint_y=None, height=dp(22))
            r2.add_widget(MDLabel(text=f"{e.get('mes', '')} | {e.get('reu', '')}",
                                  font_style="Caption",
                                  theme_text_color="Custom",
                                  text_color=(0.47, 0.522, 0.796, 1)))
            r3 = MDBoxLayout(size_hint_y=None, height=dp(30))
            r3.add_widget(MDLabel(
                text=f"Percebido: {_fmt(e.get('valor_percebido', 0))}  |  Hon.: {_fmt(e.get('honorarios', 0))}",
                theme_text_color="Custom",
                text_color=(0.259, 0.647, 0.961, 1)))
            btn_e = MDIconButton(icon="pencil", theme_icon_color="Custom",
                                 icon_color=(0.47, 0.522, 0.796, 1),
                                 size_hint_x=None, width=dp(36))
            btn_d = MDIconButton(icon="delete", theme_icon_color="Custom",
                                 icon_color=(0.937, 0.325, 0.314, 1),
                                 size_hint_x=None, width=dp(36))
            ei = i
            btn_e.bind(on_release=lambda x, i=ei: self.abrir_form(i))
            btn_d.bind(on_release=lambda x, i=ei: self.deletar(i))
            r3.add_widget(btn_e)
            r3.add_widget(btn_d)
            for r in [r1, r2, r3]:
                card.add_widget(r)
            box.add_widget(card)

        if not d["execucoes"]:
            box.add_widget(MDLabel(
                text="Nenhuma execução cadastrada.\nClique em ➕ Nova para adicionar.",
                halign="center", theme_text_color="Custom",
                text_color=(0.47, 0.522, 0.796, 1),
                size_hint_y=None, height=dp(80)))

        scroll.add_widget(box)
        main_box.add_widget(scroll)
        self.add_widget(main_box)

    def abrir_form(self, idx):
        app = MDApp.get_running_app()
        d = app.dados
        novo = idx == -1
        item = {} if novo else copy.deepcopy(d["execucoes"][idx])

        f_mes = MDTextField(hint_text="Mês", text=item.get("mes", MESES[0]),
                            mode="rectangle", size_hint_y=None, height=dp(48))
        f_cli = MDTextField(hint_text="Cliente", text=item.get("cliente", ""),
                            mode="rectangle", size_hint_y=None, height=dp(48))
        f_reu = MDTextField(hint_text="Réu", text=item.get("reu", ""),
                            mode="rectangle", size_hint_y=None, height=dp(48))
        f_proc = MDTextField(hint_text="Processo", text=item.get("processo", ""),
                             mode="rectangle", size_hint_y=None, height=dp(48))
        f_vp = MDTextField(hint_text="Valor Percebido (R$)",
                           text=_vs(item.get("valor_percebido", 0)),
                           mode="rectangle", size_hint_y=None, height=dp(48))
        f_suc = MDTextField(hint_text="Sucumbência (R$)",
                            text=_vs(item.get("sucumbencia", 0)),
                            mode="rectangle", size_hint_y=None, height=dp(48))

        form = MDBoxLayout(orientation="vertical", spacing=dp(8),
                           size_hint_y=None, height=dp(312))
        for f in [f_mes, f_cli, f_reu, f_proc, f_vp, f_suc]:
            form.add_widget(f)

        def salvar(x):
            vp = _v(f_vp.text)
            sc = _v(f_suc.text)
            entry = {
                "mes": f_mes.text.strip() or MESES[0],
                "cliente": f_cli.text.strip(),
                "reu": f_reu.text.strip(),
                "processo": f_proc.text.strip(),
                "valor_percebido": vp, "sucumbencia": sc,
                "honorarios": calc_execucao(vp, sc),
                "status": item.get("status", "pendente"),
            }
            if novo:
                d["execucoes"].append(entry)
            else:
                d["execucoes"][idx] = entry
            salvar_financeiro(d)
            self.dialog.dismiss()
            self.build_ui()

        self.dialog = MDDialog(
            title="Nova Execução" if novo else "Editar Execução",
            type="custom", content_cls=form,
            buttons=[
                MDFlatButton(text="CANCELAR",
                             on_release=lambda x: self.dialog.dismiss()),
                MDRaisedButton(text="SALVAR", on_release=salvar),
            ],
        )
        self.dialog.open()

    def deletar(self, idx):
        app = MDApp.get_running_app()
        d = app.dados

        def confirmar(x):
            d["execucoes"].pop(idx)
            salvar_financeiro(d)
            dlg.dismiss()
            self.build_ui()

        dlg = MDDialog(title="Confirmar exclusão", text="Remover esta execução?",
                       buttons=[
                           MDFlatButton(text="NÃO", on_release=lambda x: dlg.dismiss()),
                           MDRaisedButton(text="SIM", on_release=confirmar,
                                          md_bg_color=(0.369, 0.071, 0.071, 1)),
                       ])
        dlg.open()


class HonorariosScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "honorarios"
        self.dialog = None

    def on_enter(self):
        self.build_ui()

    def build_ui(self):
        self.clear_widgets()
        app = MDApp.get_running_app()
        d = app.dados

        main_box = MDBoxLayout(orientation="vertical",
                               md_bg_color=(0.039, 0.059, 0.118, 1))

        hdr = MDBoxLayout(size_hint_y=None, height=dp(52),
                          padding=(dp(12), dp(4)),
                          md_bg_color=(0.039, 0.059, 0.118, 1))
        hdr.add_widget(MDLabel(text="💼  Honorários Iniciais",
                               font_style="H6", bold=True,
                               theme_text_color="Custom",
                               text_color=(0.902, 0.914, 0.965, 1)))
        btn_add = MDRaisedButton(text="➕", size_hint_x=None,
                                 width=dp(56), size_hint_y=None, height=dp(36),
                                 md_bg_color=(0.102, 0.165, 0.369, 1))
        btn_add.bind(on_release=lambda x: self.abrir_form(-1))
        hdr.add_widget(btn_add)
        main_box.add_widget(hdr)

        scroll = MDScrollView()
        box = MDBoxLayout(orientation="vertical", padding=dp(8),
                          spacing=dp(8), size_hint_y=None)
        box.bind(minimum_height=box.setter("height"))

        for i, h in enumerate(d["honorarios_iniciais"]):
            st = h.get("status", "pendente")
            ic = "🟢" if st == "pago" else "🔴"
            card = MDCard(orientation="vertical", size_hint_y=None,
                          height=dp(100), radius=[10], elevation=2,
                          padding=dp(10),
                          md_bg_color=(0.051, 0.106, 0.235, 1))
            r1 = MDBoxLayout(size_hint_y=None, height=dp(26))
            r1.add_widget(MDLabel(text=f"{ic}  {h.get('cliente', '—')}",
                                  bold=True, theme_text_color="Custom",
                                  text_color=(0.902, 0.914, 0.965, 1)))
            r2 = MDBoxLayout(size_hint_y=None, height=dp(22))
            r2.add_widget(MDLabel(text=h.get("observacao", ""),
                                  font_style="Caption",
                                  theme_text_color="Custom",
                                  text_color=(0.47, 0.522, 0.796, 1)))
            r3 = MDBoxLayout(size_hint_y=None, height=dp(30))
            r3.add_widget(MDLabel(text=f"Valor: {_fmt(h.get('valor', 0))}  |  {h.get('data_pagamento', '')}",
                                  theme_text_color="Custom",
                                  text_color=(0.259, 0.647, 0.961, 1)))
            btn_e = MDIconButton(icon="pencil", theme_icon_color="Custom",
                                 icon_color=(0.47, 0.522, 0.796, 1),
                                 size_hint_x=None, width=dp(36))
            btn_d = MDIconButton(icon="delete", theme_icon_color="Custom",
                                 icon_color=(0.937, 0.325, 0.314, 1),
                                 size_hint_x=None, width=dp(36))
            hi = i
            btn_e.bind(on_release=lambda x, i=hi: self.abrir_form(i))
            btn_d.bind(on_release=lambda x, i=hi: self.deletar(i))
            r3.add_widget(btn_e)
            r3.add_widget(btn_d)
            for r in [r1, r2, r3]:
                card.add_widget(r)
            box.add_widget(card)

        if not d["honorarios_iniciais"]:
            box.add_widget(MDLabel(text="Nenhum honorário cadastrado.",
                                   halign="center", theme_text_color="Custom",
                                   text_color=(0.47, 0.522, 0.796, 1),
                                   size_hint_y=None, height=dp(60)))

        scroll.add_widget(box)
        main_box.add_widget(scroll)
        self.add_widget(main_box)

    def abrir_form(self, idx):
        app = MDApp.get_running_app()
        d = app.dados
        novo = idx == -1
        item = {} if novo else copy.deepcopy(d["honorarios_iniciais"][idx])

        f_cli = MDTextField(hint_text="Cliente", text=item.get("cliente", ""),
                            mode="rectangle", size_hint_y=None, height=dp(48))
        f_proc = MDTextField(hint_text="Processo", text=item.get("processo", ""),
                             mode="rectangle", size_hint_y=None, height=dp(48))
        f_val = MDTextField(hint_text="Valor (R$)",
                            text=_vs(item.get("valor", 0)),
                            mode="rectangle", size_hint_y=None, height=dp(48))
        f_dt = MDTextField(hint_text="Data Pagto (DD/MM/AAAA)",
                           text=item.get("data_pagamento", ""),
                           mode="rectangle", size_hint_y=None, height=dp(48))
        f_obs = MDTextField(hint_text="Observação",
                            text=item.get("observacao", ""),
                            mode="rectangle", size_hint_y=None, height=dp(48))

        form = MDBoxLayout(orientation="vertical", spacing=dp(8),
                           size_hint_y=None, height=dp(260))
        for f in [f_cli, f_proc, f_val, f_dt, f_obs]:
            form.add_widget(f)

        def salvar(x):
            entry = {
                "cliente": f_cli.text.strip(),
                "processo": f_proc.text.strip(),
                "valor": _v(f_val.text),
                "data_pagamento": f_dt.text.strip(),
                "observacao": f_obs.text.strip(),
                "status": item.get("status", "pendente"),
            }
            if novo:
                d["honorarios_iniciais"].append(entry)
            else:
                d["honorarios_iniciais"][idx] = entry
            salvar_financeiro(d)
            self.dialog.dismiss()
            self.build_ui()

        self.dialog = MDDialog(
            title="Honorário Inicial",
            type="custom", content_cls=form,
            buttons=[
                MDFlatButton(text="CANCELAR",
                             on_release=lambda x: self.dialog.dismiss()),
                MDRaisedButton(text="SALVAR", on_release=salvar),
            ],
        )
        self.dialog.open()

    def deletar(self, idx):
        app = MDApp.get_running_app()
        d = app.dados

        def confirmar(x):
            d["honorarios_iniciais"].pop(idx)
            salvar_financeiro(d)
            dlg.dismiss()
            self.build_ui()

        dlg = MDDialog(title="Confirmar", text="Remover este honorário?",
                       buttons=[
                           MDFlatButton(text="NÃO", on_release=lambda x: dlg.dismiss()),
                           MDRaisedButton(text="SIM", on_release=confirmar,
                                          md_bg_color=(0.369, 0.071, 0.071, 1)),
                       ])
        dlg.open()


class DespesasScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "despesas"
        self.dialog = None

    def on_enter(self):
        self.build_ui()

    def build_ui(self):
        self.clear_widgets()
        app = MDApp.get_running_app()
        d = app.dados

        main_box = MDBoxLayout(orientation="vertical",
                               md_bg_color=(0.039, 0.059, 0.118, 1))
        hdr = MDBoxLayout(size_hint_y=None, height=dp(52),
                          padding=(dp(12), dp(4)),
                          md_bg_color=(0.039, 0.059, 0.118, 1))
        hdr.add_widget(MDLabel(text="🏢  Despesas",
                               font_style="H6", bold=True,
                               theme_text_color="Custom",
                               text_color=(0.902, 0.914, 0.965, 1)))
        btn_add = MDRaisedButton(text="➕ Variável", size_hint_x=None,
                                 width=dp(110), size_hint_y=None, height=dp(36),
                                 md_bg_color=(0.102, 0.165, 0.369, 1))
        btn_add.bind(on_release=lambda x: self.abrir_form_variavel(-1))
        hdr.add_widget(btn_add)
        main_box.add_widget(hdr)

        scroll = MDScrollView()
        box = MDBoxLayout(orientation="vertical", padding=dp(8),
                          spacing=dp(10), size_hint_y=None)
        box.bind(minimum_height=box.setter("height"))

        # Fixas resumo
        total_fixas = sum(sum(float(v) for v in cat.values())
                          for cat in d["fixas"].values())
        box.add_widget(MDLabel(text="🏢 Despesas Fixas",
                               font_style="Subtitle1", bold=True,
                               theme_text_color="Custom",
                               text_color=(0.47, 0.522, 0.796, 1),
                               size_hint_y=None, height=dp(30)))

        for cat, meses in d["fixas"].items():
            total_cat = sum(float(v) for v in meses.values())
            if total_cat == 0:
                continue
            card = MDCard(orientation="vertical", size_hint_y=None,
                          height=dp(60), radius=[8], elevation=1,
                          padding=dp(10),
                          md_bg_color=(0.051, 0.106, 0.235, 1))
            card.add_widget(MDLabel(text=cat, bold=True,
                                    theme_text_color="Custom",
                                    text_color=(0.902, 0.914, 0.965, 1),
                                    size_hint_y=None, height=dp(22)))
            card.add_widget(MDLabel(text=f"Total: {_fmt(total_cat)}  |  {d['fixas_quem'].get(cat, 'dividido')}",
                                    font_style="Caption",
                                    theme_text_color="Custom",
                                    text_color=(0.996, 0.655, 0.149, 1),
                                    size_hint_y=None, height=dp(20)))
            box.add_widget(card)

        box.add_widget(MDLabel(text=f"Total Fixas: {_fmt(total_fixas)}",
                               bold=True, theme_text_color="Custom",
                               text_color=(0.996, 0.655, 0.149, 1),
                               size_hint_y=None, height=dp(28)))

        # Variáveis
        box.add_widget(MDLabel(text="🛒 Despesas Variáveis",
                               font_style="Subtitle1", bold=True,
                               theme_text_color="Custom",
                               text_color=(0.47, 0.522, 0.796, 1),
                               size_hint_y=None, height=dp(30)))

        for i, item in enumerate(d["variaveis"]):
            st = item.get("status", "pendente")
            ic = "🟢" if st == "pago" else "🔴"
            card = MDCard(orientation="vertical", size_hint_y=None,
                          height=dp(80), radius=[8], elevation=1,
                          padding=dp(10),
                          md_bg_color=(0.051, 0.106, 0.235, 1))
            r1 = MDBoxLayout(size_hint_y=None, height=dp(24))
            r1.add_widget(MDLabel(text=f"{ic}  {item.get('descricao', '')}",
                                  bold=True, theme_text_color="Custom",
                                  text_color=(0.902, 0.914, 0.965, 1)))
            r2 = MDBoxLayout(size_hint_y=None, height=dp(22))
            quem = item.get("quem", "")
            cor_q = (0.396, 0.490, 0.988, 1) if quem == "Adriely" else (0.298, 0.686, 0.314, 1)
            r2.add_widget(MDLabel(
                text=f"{quem}  |  {item.get('parcelas', '')}  |  {_fmt(item.get('valor', 0))}",
                font_style="Caption", theme_text_color="Custom",
                text_color=(0.996, 0.655, 0.149, 1)))
            btn_d = MDIconButton(icon="delete", theme_icon_color="Custom",
                                 icon_color=(0.937, 0.325, 0.314, 1),
                                 size_hint_x=None, width=dp(36))
            vi = i
            btn_d.bind(on_release=lambda x, i=vi: self.deletar_variavel(i))
            r2.add_widget(btn_d)
            for r in [r1, r2]:
                card.add_widget(r)
            box.add_widget(card)

        total_var = sum(item.get("valor", 0) for item in d["variaveis"])
        box.add_widget(MDLabel(text=f"Total Variáveis: {_fmt(total_var)}",
                               bold=True, theme_text_color="Custom",
                               text_color=(0.996, 0.655, 0.149, 1),
                               size_hint_y=None, height=dp(28)))

        scroll.add_widget(box)
        main_box.add_widget(scroll)
        self.add_widget(main_box)

    def abrir_form_variavel(self, idx):
        app = MDApp.get_running_app()
        d = app.dados
        novo = idx == -1
        item = {} if novo else copy.deepcopy(d["variaveis"][idx])

        f_desc = MDTextField(hint_text="Descrição", text=item.get("descricao", ""),
                             mode="rectangle", size_hint_y=None, height=dp(48))
        f_val = MDTextField(hint_text="Valor Total (R$)",
                            text=_vs(item.get("valor", 0)),
                            mode="rectangle", size_hint_y=None, height=dp(48))
        f_parc = MDTextField(hint_text="Parcelas (ex: 3x)",
                             text=item.get("parcelas", "1x"),
                             mode="rectangle", size_hint_y=None, height=dp(48))
        f_onde = MDTextField(hint_text="Onde (loja)",
                             text=item.get("onde", ""),
                             mode="rectangle", size_hint_y=None, height=dp(48))

        form = MDBoxLayout(orientation="vertical", spacing=dp(8),
                           size_hint_y=None, height=dp(208))
        for f in [f_desc, f_val, f_parc, f_onde]:
            form.add_widget(f)

        def salvar(x):
            entry = {
                "descricao": f_desc.text.strip(),
                "valor": _v(f_val.text),
                "parcelas": f_parc.text.strip() or "1x",
                "quem": "Adriely",
                "onde": f_onde.text.strip(),
                "status": "pendente",
                "meses": {},
            }
            if novo:
                d["variaveis"].append(entry)
            else:
                d["variaveis"][idx] = entry
            salvar_financeiro(d)
            self.dialog.dismiss()
            self.build_ui()

        self.dialog = MDDialog(
            title="Despesa Variável",
            type="custom", content_cls=form,
            buttons=[
                MDFlatButton(text="CANCELAR",
                             on_release=lambda x: self.dialog.dismiss()),
                MDRaisedButton(text="SALVAR", on_release=salvar),
            ],
        )
        self.dialog.open()

    def deletar_variavel(self, idx):
        app = MDApp.get_running_app()
        d = app.dados

        def confirmar(x):
            d["variaveis"].pop(idx)
            salvar_financeiro(d)
            dlg.dismiss()
            self.build_ui()

        dlg = MDDialog(title="Confirmar", text="Remover esta despesa?",
                       buttons=[
                           MDFlatButton(text="NÃO", on_release=lambda x: dlg.dismiss()),
                           MDRaisedButton(text="SIM", on_release=confirmar,
                                          md_bg_color=(0.369, 0.071, 0.071, 1)),
                       ])
        dlg.open()


class BalancoScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "balanco"

    def on_enter(self):
        self.build_ui()

    def build_ui(self):
        self.clear_widgets()
        app = MDApp.get_running_app()
        d = app.dados

        main_box = MDBoxLayout(orientation="vertical",
                               md_bg_color=(0.039, 0.059, 0.118, 1))
        hdr = MDLabel(text="⚖️  Balanço das Sócias",
                      font_style="H6", bold=True,
                      theme_text_color="Custom",
                      text_color=(0.902, 0.914, 0.965, 1),
                      size_hint_y=None, height=dp(52),
                      padding=(dp(12), dp(8)))
        main_box.add_widget(hdr)

        scroll = MDScrollView()
        box = MDBoxLayout(orientation="vertical", padding=dp(12),
                          spacing=dp(10), size_hint_y=None)
        box.bind(minimum_height=box.setter("height"))

        COLS_B = ["Out", "Nov", "Dez", "Jan", "Fev", "Mar", "Abr", "Mai"]
        cl_b = {"Out": "Out/25", "Nov": "Nov/25", "Dez": "Dez/25",
                "Jan": "Jan/26", "Fev": "Fev/26", "Mar": "Mar/26",
                "Abr": "Abr/26", "Mai": "Mai/26"}

        def gastos_mes(col):
            a_g, e_g = 0.0, 0.0
            for cat, meses in d["fixas"].items():
                val = float(meses.get(col, 0) or 0)
                quem = d["fixas_quem"].get(cat, "dividido")
                if quem == "Adriely":
                    a_g += val
                elif quem == "Eduarda":
                    e_g += val
                else:
                    a_g += val / 2
                    e_g += val / 2
            for item in d["variaveis"]:
                val = float(item.get("meses", {}).get(col, 0) or 0)
                quem = item.get("quem", "")
                if quem == "Adriely":
                    a_g += val
                elif quem == "Eduarda":
                    e_g += val
                else:
                    a_g += val / 2
                    e_g += val / 2
            return a_g, e_g

        total_honor = (
            sum(float(a.get("honorarios", 0)) for a in d["acordos"] if a.get("status") == "pago") +
            sum(float(e.get("honorarios", 0)) for e in d["execucoes"] if e.get("status") == "pago") +
            sum(float(h.get("valor", 0)) for h in d["honorarios_iniciais"] if h.get("status") == "pago")
        )
        honor_cada = total_honor / 2

        total_a = sum(gastos_mes(c)[0] for c in COLS_B)
        total_e = sum(gastos_mes(c)[1] for c in COLS_B)

        saldo_a = honor_cada - total_a
        saldo_e = honor_cada - total_e

        for titulo, gasto, saldo in [
            ("🔵 Adriely", total_a, saldo_a),
            ("🟢 Eduarda", total_e, saldo_e),
        ]:
            cor = (0.298, 0.686, 0.314, 1) if saldo >= 0 else (0.937, 0.325, 0.314, 1)
            card = MDCard(orientation="vertical", size_hint_y=None,
                          height=dp(100), radius=[10], elevation=2,
                          padding=dp(14),
                          md_bg_color=(0.051, 0.106, 0.235, 1))
            card.add_widget(MDLabel(text=titulo, bold=True,
                                    theme_text_color="Custom",
                                    text_color=(0.902, 0.914, 0.965, 1),
                                    size_hint_y=None, height=dp(26)))
            card.add_widget(MDLabel(text=f"Honorários: {_fmt(honor_cada)}  |  Gastos: {_fmt(gasto)}",
                                    font_style="Caption",
                                    theme_text_color="Custom",
                                    text_color=(0.47, 0.522, 0.796, 1),
                                    size_hint_y=None, height=dp(22)))
            card.add_widget(MDLabel(text=f"Saldo: {_fmt(saldo)}",
                                    font_style="H6", bold=True,
                                    theme_text_color="Custom",
                                    text_color=cor,
                                    size_hint_y=None, height=dp(30)))
            box.add_widget(card)

        if abs(total_a - total_e) > 0.01:
            diff = abs(total_a - total_e)
            mais = "Adriely" if total_a > total_e else "Eduarda"
            menos = "Eduarda" if mais == "Adriely" else "Adriely"
            card = MDCard(orientation="vertical", size_hint_y=None,
                          height=dp(70), radius=[8], elevation=1,
                          padding=dp(12),
                          md_bg_color=(0.18, 0.118, 0.039, 1))
            card.add_widget(MDLabel(text="⚠️ Diferença de gastos",
                                    bold=True, theme_text_color="Custom",
                                    text_color=(0.996, 0.655, 0.149, 1),
                                    size_hint_y=None, height=dp(24)))
            card.add_widget(MDLabel(
                text=f"{menos} deve {_fmt(diff/2)} para {mais}",
                theme_text_color="Custom",
                text_color=(0.902, 0.914, 0.965, 1),
                size_hint_y=None, height=dp(22)))
            box.add_widget(card)

        scroll.add_widget(box)
        main_box.add_widget(scroll)
        self.add_widget(main_box)


class FinalizadosScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "finalizados"
        self.dialog = None

    def on_enter(self):
        self.build_ui()

    def build_ui(self):
        self.clear_widgets()
        app = MDApp.get_running_app()
        d = app.dados

        main_box = MDBoxLayout(orientation="vertical",
                               md_bg_color=(0.039, 0.059, 0.118, 1))
        hdr = MDBoxLayout(size_hint_y=None, height=dp(52),
                          padding=(dp(12), dp(4)),
                          md_bg_color=(0.039, 0.059, 0.118, 1))
        hdr.add_widget(MDLabel(text="📁  Finalizados s/ Honorário",
                               font_style="H6", bold=True,
                               theme_text_color="Custom",
                               text_color=(0.902, 0.914, 0.965, 1)))
        btn_add = MDRaisedButton(text="➕", size_hint_x=None,
                                 width=dp(56), size_hint_y=None, height=dp(36),
                                 md_bg_color=(0.102, 0.165, 0.369, 1))
        btn_add.bind(on_release=lambda x: self.abrir_form(-1))
        hdr.add_widget(btn_add)
        main_box.add_widget(hdr)

        scroll = MDScrollView()
        box = MDBoxLayout(orientation="vertical", padding=dp(8),
                          spacing=dp(8), size_hint_y=None)
        box.bind(minimum_height=box.setter("height"))

        for i, p in enumerate(d["finalizados_sem_honor"]):
            card = MDCard(orientation="vertical", size_hint_y=None,
                          height=dp(90), radius=[8], elevation=1,
                          padding=dp(10),
                          md_bg_color=(0.051, 0.106, 0.235, 1))
            r1 = MDBoxLayout(size_hint_y=None, height=dp(24))
            r1.add_widget(MDLabel(text=p.get("cliente", "—"),
                                  bold=True, theme_text_color="Custom",
                                  text_color=(0.902, 0.914, 0.965, 1)))
            r2 = MDBoxLayout(size_hint_y=None, height=dp(20))
            r2.add_widget(MDLabel(text=f"{p.get('reu', '')} | {p.get('motivo', '')}",
                                  font_style="Caption",
                                  theme_text_color="Custom",
                                  text_color=(0.47, 0.522, 0.796, 1)))
            r3 = MDBoxLayout(size_hint_y=None, height=dp(24))
            r3.add_widget(MDLabel(text=p.get("processo", ""),
                                  font_style="Caption",
                                  theme_text_color="Custom",
                                  text_color=(0.47, 0.522, 0.796, 1)))
            btn_d = MDIconButton(icon="delete", theme_icon_color="Custom",
                                 icon_color=(0.937, 0.325, 0.314, 1),
                                 size_hint_x=None, width=dp(36))
            pi = i
            btn_d.bind(on_release=lambda x, i=pi: self.deletar(i))
            r3.add_widget(btn_d)
            for r in [r1, r2, r3]:
                card.add_widget(r)
            box.add_widget(card)

        if not d["finalizados_sem_honor"]:
            box.add_widget(MDLabel(text="Nenhum processo finalizado cadastrado.",
                                   halign="center", theme_text_color="Custom",
                                   text_color=(0.47, 0.522, 0.796, 1),
                                   size_hint_y=None, height=dp(60)))

        scroll.add_widget(box)
        main_box.add_widget(scroll)
        self.add_widget(main_box)

    def abrir_form(self, idx):
        app = MDApp.get_running_app()
        d = app.dados
        novo = idx == -1
        item = {} if novo else copy.deepcopy(d["finalizados_sem_honor"][idx])

        f_cli = MDTextField(hint_text="Cliente", text=item.get("cliente", ""),
                            mode="rectangle", size_hint_y=None, height=dp(48))
        f_reu = MDTextField(hint_text="Réu", text=item.get("reu", ""),
                            mode="rectangle", size_hint_y=None, height=dp(48))
        f_proc = MDTextField(hint_text="Processo", text=item.get("processo", ""),
                             mode="rectangle", size_hint_y=None, height=dp(48))
        f_obj = MDTextField(hint_text="Objeto", text=item.get("objeto", ""),
                            mode="rectangle", size_hint_y=None, height=dp(48))
        f_dt = MDTextField(hint_text="Data Finalização",
                           text=item.get("data_finalizacao", ""),
                           mode="rectangle", size_hint_y=None, height=dp(48))
        f_mot = MDTextField(hint_text="Motivo (Improcedência, Desistência...)",
                            text=item.get("motivo", "Outro"),
                            mode="rectangle", size_hint_y=None, height=dp(48))

        form = MDBoxLayout(orientation="vertical", spacing=dp(8),
                           size_hint_y=None, height=dp(312))
        for f in [f_cli, f_reu, f_proc, f_obj, f_dt, f_mot]:
            form.add_widget(f)

        def salvar(x):
            entry = {
                "cliente": f_cli.text.strip(),
                "reu": f_reu.text.strip(),
                "processo": f_proc.text.strip(),
                "objeto": f_obj.text.strip(),
                "data_finalizacao": f_dt.text.strip(),
                "motivo": f_mot.text.strip() or "Outro",
            }
            if novo:
                d["finalizados_sem_honor"].append(entry)
            else:
                d["finalizados_sem_honor"][idx] = entry
            salvar_financeiro(d)
            self.dialog.dismiss()
            self.build_ui()

        self.dialog = MDDialog(
            title="Processo Finalizado",
            type="custom", content_cls=form,
            buttons=[
                MDFlatButton(text="CANCELAR",
                             on_release=lambda x: self.dialog.dismiss()),
                MDRaisedButton(text="SALVAR", on_release=salvar),
            ],
        )
        self.dialog.open()

    def deletar(self, idx):
        app = MDApp.get_running_app()
        d = app.dados

        def confirmar(x):
            d["finalizados_sem_honor"].pop(idx)
            salvar_financeiro(d)
            dlg.dismiss()
            self.build_ui()

        dlg = MDDialog(title="Confirmar", text="Remover este processo?",
                       buttons=[
                           MDFlatButton(text="NÃO", on_release=lambda x: dlg.dismiss()),
                           MDRaisedButton(text="SIM", on_release=confirmar,
                                          md_bg_color=(0.369, 0.071, 0.071, 1)),
                       ])
        dlg.open()


# ─────────────────────────────────────────────────────────
# WIDGET PRINCIPAL DO FINANCEIRO
# ─────────────────────────────────────────────────────────
class FinanceiroTab(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_kv_post(self, base_widget):
        sm = self.ids.fin_screens
        for cls in [DashboardScreen, AcordosScreen, ExecucoesScreen,
                    HonorariosScreen, DespesasScreen, BalancoScreen,
                    FinalizadosScreen]:
            sm.add_widget(cls())
        sm.current = "dashboard"

    def goto(self, name):
        sm = self.ids.fin_screens
        sm.current = name


# ─────────────────────────────────────────────────────────
# CALCULADORA TAB
# ─────────────────────────────────────────────────────────
class LancamentoRow(MDBoxLayout):
    def __init__(self, idx, app_ref, **kwargs):
        super().__init__(orientation="horizontal", size_hint_y=None,
                         height=dp(48), spacing=dp(4), **kwargs)
        self.idx = idx
        self.app_ref = app_ref

        self.f_data = MDTextField(hint_text="DD/MM/AAAA",
                                   mode="rectangle",
                                   size_hint_y=None, height=dp(44))
        self.f_val = MDTextField(hint_text="Valor R$",
                                  mode="rectangle",
                                  size_hint_y=None, height=dp(44))
        btn_del = MDIconButton(icon="close", theme_icon_color="Custom",
                               icon_color=(0.937, 0.325, 0.314, 1),
                               size_hint_x=None, width=dp(40))
        btn_del.bind(on_release=self.remover)

        self.add_widget(self.f_data)
        self.add_widget(self.f_val)
        self.add_widget(btn_del)

    def remover(self, *args):
        self.app_ref.calc_tab.remove_lancamento(self)

    def get_data(self):
        try:
            d = datetime.strptime(self.f_data.text.strip(), "%d/%m/%Y").date()
        except ValueError:
            d = date.today()
        return {"data": d, "valor": _v(self.f_val.text)}


class CalculadoraTab(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.modo = "inicial"
        self.lancamento_rows = []

    def on_kv_post(self, base_widget):
        self.ids.data_calc.text = date.today().strftime("%d/%m/%Y")
        self._add_lancamento_row()

    def set_modo(self, modo):
        self.modo = modo
        if modo == "inicial":
            self.ids.btn_inicial.md_bg_color = (0.102, 0.165, 0.616, 1)
            self.ids.btn_exec.md_bg_color = (0.051, 0.106, 0.235, 1)
            self.ids.ctrl_inicial_card.opacity = 1
            self.ids.ctrl_inicial_card.height = dp(110)
            self.ids.ctrl_exec_card.opacity = 0
            self.ids.ctrl_exec_card.height = 0
        else:
            self.ids.btn_exec.md_bg_color = (0.102, 0.165, 0.616, 1)
            self.ids.btn_inicial.md_bg_color = (0.051, 0.106, 0.235, 1)
            self.ids.ctrl_exec_card.opacity = 1
            self.ids.ctrl_exec_card.height = dp(110)
            self.ids.ctrl_inicial_card.opacity = 0
            self.ids.ctrl_inicial_card.height = 0

    def add_lancamento(self):
        self._add_lancamento_row()

    def _add_lancamento_row(self):
        app = MDApp.get_running_app()
        row = LancamentoRow(len(self.lancamento_rows), app)
        self.lancamento_rows.append(row)
        self.ids.lancamentos_box.add_widget(row)
        self.ids.lancamentos_box.height = len(self.lancamento_rows) * dp(52)

    def remove_lancamento(self, row):
        if len(self.lancamento_rows) <= 1:
            return
        self.lancamento_rows.remove(row)
        self.ids.lancamentos_box.remove_widget(row)
        self.ids.lancamentos_box.height = len(self.lancamento_rows) * dp(52)

    def limpar_lancamentos(self):
        self.ids.lancamentos_box.clear_widgets()
        self.lancamento_rows = []
        self._add_lancamento_row()

    def calcular(self):
        app = MDApp.get_running_app()
        indices = app.indices

        try:
            data_calc = datetime.strptime(self.ids.data_calc.text.strip(), "%d/%m/%Y").date()
        except ValueError:
            data_calc = date.today()

        charges = [row.get_data() for row in self.lancamento_rows]
        charges = [c for c in charges if c["valor"] > 0]

        if not charges:
            Snackbar(text="Adicione pelo menos um lançamento com valor.").open()
            return

        results = []
        for c in charges:
            res = calculate_charge(c["valor"], c["data"], data_calc, indices)
            results.append({"original": c["valor"], **res})

        sub_principal = sum(r["corrected"] for r in results)
        sub_juros = sum(r["interest_value"] for r in results)
        sub_base = sub_principal + sub_juros

        box = self.ids.resultado_box
        box.clear_widgets()
        box.height = 0

        def add_linha(texto, cor=(0.902, 0.914, 0.965, 1), bold=False, h=dp(24)):
            lbl = MDLabel(text=texto, theme_text_color="Custom",
                          text_color=cor, bold=bold,
                          size_hint_y=None, height=h)
            box.add_widget(lbl)
            box.height += h

        add_linha("📊 Resultado do Cálculo", (0.396, 0.490, 0.988, 1),
                  bold=True, h=dp(32))
        add_linha(f"Lançamentos: {len(results)}", h=dp(22))
        add_linha(f"Subtotal Corrigido: {fmt_brl(sub_principal)}",
                  (0.259, 0.647, 0.961, 1), h=dp(22))
        add_linha(f"Subtotal Juros: {fmt_brl(sub_juros)}",
                  (0.259, 0.647, 0.961, 1), h=dp(22))

        if self.modo == "inicial":
            dobro = self.ids.chk_dobro.active
            dano = _v(self.ids.dano_moral.text) if self.ids.dano_moral.text else 0
            fator = 2.0 if dobro else 1.0
            sub_material = sub_base * fator
            total = sub_material + dano

            if dobro:
                add_linha(f"× 2 (CDC art. 42): {fmt_brl(sub_material)}",
                          (0.996, 0.655, 0.149, 1), h=dp(22))
            if dano > 0:
                add_linha(f"+ Dano Moral: {fmt_brl(dano)}",
                          (0.996, 0.655, 0.149, 1), h=dp(22))
            add_linha(f"VALOR DA CAUSA: {fmt_brl(total)}",
                      (0.298, 0.686, 0.314, 1), bold=True, h=dp(30))

        else:
            try:
                hp = float(self.ids.honor_pct.text.replace(",", ".")) if self.ids.honor_pct.text else 20.0
            except ValueError:
                hp = 20.0
            hv = sub_base * hp / 100.0
            sub_com_honor = sub_base + hv
            multa523 = self.ids.chk_multa523.active
            multa_val = sub_com_honor * 0.10 if multa523 else 0
            total = sub_com_honor + multa_val

            add_linha(f"Honorários {hp:.1f}%: {fmt_brl(hv)}",
                      (0.996, 0.655, 0.149, 1), h=dp(22))
            if multa523:
                add_linha(f"Multa art.523 (10%): {fmt_brl(multa_val)}",
                          (0.996, 0.655, 0.149, 1), h=dp(22))
            add_linha(f"TOTAL GERAL: {fmt_brl(total)}",
                      (0.298, 0.686, 0.314, 1), bold=True, h=dp(30))

        has_indices = bool(indices.get("inpc") or indices.get("ipcae") or indices.get("selic"))
        if not has_indices:
            add_linha("⚠️ Índices BCB não carregados — correção sem variação",
                      (0.996, 0.655, 0.149, 1), h=dp(22))


# ─────────────────────────────────────────────────────────
# CONTROLE TAB
# ─────────────────────────────────────────────────────────
class ControleTab(MDBoxLayout):
    pass


# ─────────────────────────────────────────────────────────
# TELAS PRINCIPAIS
# ─────────────────────────────────────────────────────────
class LoginScreen(MDScreen):
    def fazer_login(self):
        senha = self.ids.senha_input.text
        if senha == SENHA:
            app = MDApp.get_running_app()
            app.root.current = "main"
            self.ids.senha_input.text = ""
        else:
            Snackbar(text="Senha incorreta.").open()
            self.ids.senha_input.text = ""


class MainScreen(MDScreen):
    pass


# ─────────────────────────────────────────────────────────
# APP PRINCIPAL
# ─────────────────────────────────────────────────────────
class LEADVApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dados = {}
        self.indices = {}

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Indigo"
        self.theme_cls.primary_hue = "700"
        Builder.load_string(KV)
        sm = ScreenManager(transition=NoTransition())
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(MainScreen(name="main"))
        return sm

    def on_start(self):
        self.dados = carregar_financeiro()
        self.indices = carregar_indices()

    def on_stop(self):
        salvar_financeiro(self.dados)


if __name__ == "__main__":
    LEADVApp().run()
