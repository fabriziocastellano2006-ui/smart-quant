import json
import os
from datetime import datetime

import numpy as np
import pandas as pd
import requests
import streamlit as st
import streamlit.components.v1 as components
import yfinance as yf

st.set_page_config(page_title="Smart Quant", page_icon="📈", layout="wide")

CARTELLA = os.path.dirname(os.path.abspath(__file__))
CHIAVE_FILE = os.path.join(CARTELLA, "chiave_twelvedata.txt")

ORIZZONTI = {
    "5 minuti": {"yf": "5m", "periodo": "60d", "td": "5min", "tv": "5", "per_anno": 252 * 78},
    "15 minuti": {"yf": "15m", "periodo": "60d", "td": "15min", "tv": "15", "per_anno": 252 * 26},
    "1 ora": {"yf": "1h", "periodo": "730d", "td": "1h", "tv": "60", "per_anno": 252 * 7},
    "Giornaliero": {"yf": "1d", "periodo": "5y", "td": "1day", "tv": "D", "per_anno": 252},
    "Settimanale": {"yf": "1wk", "periodo": "max", "td": "1week", "tv": "W", "per_anno": 52},
}

APP = {
    "analisi": ("📊", "Analisi"),
    "indicatori": ("🧮", "Indicatori"),
    "impostazioni": ("⚙️", "Impostazioni"),
}

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: #f4f6fb; color: #0f172a; }
header[data-testid="stHeader"] { background: transparent; }
.block-container { padding-top: 1.2rem; max-width: 1280px; }

/* Schermata di apertura */
.splash { position: fixed; inset: 0; z-index: 9999; display: flex; flex-direction: column;
  align-items: center; justify-content: center; background: #f4f6fb;
  animation: splashOut .8s ease 2.6s forwards; }
.splash-logo { font-size: 3rem; font-weight: 800; letter-spacing: -.02em;
  background: linear-gradient(90deg, #3b82f6, #10b981);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  animation: logoIn 1.1s cubic-bezier(.2,.8,.2,1) both; }
.splash-barra { width: 200px; height: 4px; border-radius: 4px; background: #dbe4f0; margin-top: 1.4rem; overflow: hidden; }
.splash-barra div { height: 100%; width: 0; background: linear-gradient(90deg, #3b82f6, #10b981);
  animation: caricamento 2s ease .3s forwards; }

/* Etichette e campi di ricerca */
label, label p { color: #475569 !important; font-weight: 600 !important; }
div[data-baseweb="input"], div[data-baseweb="base-input"], div[data-baseweb="select"] > div {
  background-color: #ffffff !important; border: 1px solid #e2e8f0 !important; border-radius: 16px !important;
  box-shadow: 0 2px 8px rgba(15,23,42,.04); }
input { background-color: transparent !important; color: #0f172a !important; -webkit-text-fill-color: #0f172a !important; caret-color: #3b82f6; }
input::placeholder { color: #94a3b8 !important; -webkit-text-fill-color: #94a3b8 !important; opacity: 1 !important; }
div[data-baseweb="select"] span, div[data-baseweb="select"] div { color: #0f172a !important; -webkit-text-fill-color: #0f172a !important; }
div[data-baseweb="popover"] ul, div[data-baseweb="menu"] ul { background-color: #ffffff !important; border-radius: 16px !important; }
div[data-baseweb="popover"] li, div[data-baseweb="menu"] li { color: #0f172a !important; }
div[data-testid="stCaptionContainer"] p { color: #64748b !important; }

/* Sotto-menu a pillole */
div[role="radiogroup"] { gap: .5rem; flex-wrap: wrap; margin: .4rem 0 1.1rem; }
div[role="radiogroup"] > label { background: #ffffff !important; border: 1px solid #e2e8f0; border-radius: 999px;
  padding: .45rem 1.05rem; box-shadow: 0 2px 6px rgba(15,23,42,.04); transition: transform .2s, background .2s; }
div[role="radiogroup"] > label:hover { transform: translateY(-2px); }
div[role="radiogroup"] > label p { color: #334155 !important; }
div[role="radiogroup"] > label:has(input:checked) { background: #3b82f6 !important; border-color: #3b82f6;
  box-shadow: 0 6px 16px rgba(59,130,246,.35); }
div[role="radiogroup"] > label:has(input:checked) p { color: #ffffff !important; }

/* Pulsanti */
div[data-testid="stColumn"], div[data-testid="column"] { animation: fadeUp .6s ease both; }
.stButton > button { background: #ffffff; color: #1d4ed8; border: 1px solid #e2e8f0; border-radius: 18px;
  font-weight: 700; width: 100%; min-height: 3.2rem; font-size: 1rem;
  box-shadow: 0 6px 18px rgba(15,23,42,.06); transition: transform .2s, box-shadow .2s, border-color .2s; }
.stButton > button p { color: inherit !important; }
.stButton > button:hover { transform: translateY(-2px); box-shadow: 0 12px 26px rgba(59,130,246,.18); border-color: #bfdbfe; }
.stButton > button:active { transform: scale(.98); }

.logo { font-weight: 800; color: #0f172a; padding-top: .55rem; font-size: 1.1rem; }
.spazio { height: 1.85rem; }
.hero { padding: .4rem 0 1.1rem; }
.hero h1 { font-size: 2.4rem; font-weight: 800; margin: 0; letter-spacing: -.02em; color: #0f172a; }
.hero p { color: #64748b; margin: .3rem 0 0; font-size: 1rem; }

/* Riquadro prezzo in stile Wallet */
.hero-card { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;
  background: linear-gradient(135deg, #3b82f6 0%, #10b981 100%); color: #ffffff; border-radius: 26px;
  padding: 1.4rem 1.6rem; box-shadow: 0 18px 40px rgba(59,130,246,.25); animation: fadeUp .6s ease-out; }
.titolo { font-size: 1.05rem; font-weight: 700; color: #ffffff; }
.ticker { font-family: Consolas, monospace; font-size: .72rem; color: #ffffff; margin-left: .6rem;
  background: rgba(255,255,255,.2); border-radius: 999px; padding: .15rem .55rem; vertical-align: middle; }
.prezzo { font-family: Consolas, monospace; font-size: 2.6rem; font-weight: 700; color: #ffffff; margin-top: .25rem; }
.prezzo small { font-size: 1rem; color: rgba(255,255,255,.85); margin-left: .4rem; }
.var { font-size: 1rem; font-weight: 700; margin-left: .8rem; background: #ffffff; border-radius: 999px;
  padding: .2rem .7rem; vertical-align: middle; box-shadow: 0 4px 12px rgba(15,23,42,.12); }
.meta { text-align: right; }
.chip { display: inline-block; padding: .3rem .8rem; border-radius: 999px; font-size: .78rem; font-weight: 700;
  color: #ffffff; background: rgba(255,255,255,.2); border: 1px solid rgba(255,255,255,.4); }
.chip.warn { background: rgba(254,249,195,.28); }
.ora { color: rgba(255,255,255,.85); font-size: .8rem; margin-top: .5rem; font-family: Consolas, monospace; }

.sezione { font-size: 1.1rem; font-weight: 800; color: #0f172a; margin: 1.7rem 0 .8rem; letter-spacing: -.01em; }

/* Schede bianche */
.card { background: #ffffff; border: 1px solid #eef2f7; border-radius: 22px; padding: 1.1rem 1.2rem;
  box-shadow: 0 6px 24px rgba(15,23,42,.06); animation: fadeUp .6s ease-out;
  transition: transform .25s, box-shadow .25s; }
.card:hover { transform: translateY(-3px); box-shadow: 0 14px 34px rgba(15,23,42,.10); }
.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: .9rem; }

.kpi { background: #ffffff; border: 1px solid #eef2f7; border-radius: 20px; padding: .9rem 1rem;
  box-shadow: 0 4px 16px rgba(15,23,42,.05); }
.kpi span { display: flex; align-items: center; color: #64748b; font-size: .72rem; text-transform: uppercase;
  letter-spacing: .05em; font-weight: 700; }
.kpi span::before { content: ""; width: 8px; height: 8px; border-radius: 50%; background: #3b82f6; margin-right: .45rem; }
.kpi b { display: block; margin-top: .35rem; font-family: Consolas, monospace; font-size: 1.15rem; color: #0f172a; }

.ind { border-left: 4px solid #cbd5e1; }
.ind.up { border-left-color: #10b981; }
.ind.down { border-left-color: #ef4444; }
.ind small { display: block; color: #64748b; font-size: .7rem; text-transform: uppercase; letter-spacing: .05em; font-weight: 700; }
.ind b { display: block; margin-top: .3rem; font-family: Consolas, monospace; font-size: 1.2rem; color: #0f172a; }
.ind span { display: block; margin-top: .3rem; color: #475569; font-size: .85rem; }

.punteggio { text-align: center; }
.ring { width: 200px; height: 200px; border-radius: 50%; margin: .4rem auto 0; display: flex;
  align-items: center; justify-content: center; animation: spin .9s ease-out; }
.ring-in { width: 164px; height: 164px; border-radius: 50%; background: #ffffff; display: flex;
  flex-direction: column; align-items: center; justify-content: center; }
.num { font-family: Consolas, monospace; font-size: 3rem; font-weight: 800; color: #0f172a; line-height: 1; }
.sub { color: #64748b; font-size: .85rem; }
.badge { display: inline-block; margin-top: 1rem; padding: .4rem 1.2rem; border: 1px solid; border-radius: 999px;
  font-weight: 800; letter-spacing: .06em; background: #ffffff; }
.driver-box { text-align: left; margin-top: .8rem; }
.driver { display: grid; grid-template-columns: 110px 1fr 40px; gap: .8rem; align-items: center; margin: .8rem 0;
  color: #334155; font-weight: 600; }
.driver b { text-align: right; font-family: Consolas, monospace; color: #0f172a; }
.barra { background: #e8edf5; border-radius: 999px; height: 10px; overflow: hidden; }
.riempi { height: 100%; border-radius: 999px; background: linear-gradient(90deg, #3b82f6, #10b981);
  animation: grow 1.2s ease-out; }

.criterio { display: flex; justify-content: space-between; align-items: center; gap: .6rem; border-left: 4px solid #cbd5e1; }
.criterio.ok { border-left-color: #10b981; }
.criterio.ko { border-left-color: #ef4444; }
.criterio small { display: block; color: #64748b; font-size: .7rem; text-transform: uppercase; font-weight: 700; letter-spacing: .05em; }
.criterio b { color: #0f172a; font-size: .95rem; }
.punti { font-family: Consolas, monospace; font-weight: 800; color: #334155; white-space: nowrap; }

table.q { width: 100%; border-collapse: collapse; color: #334155; font-family: Consolas, monospace; font-size: .88rem; }
table.q th { color: #64748b; text-align: right; padding: .55rem .6rem; border-bottom: 1px solid #e2e8f0; font-family: Inter, sans-serif; }
table.q td { text-align: right; padding: .55rem .6rem; border-bottom: 1px solid #f1f5f9; }
table.q th:first-child, table.q td:first-child { text-align: left; }

.nota { color: #64748b; font-size: .82rem; margin-top: 1.6rem; line-height: 1.5; }

@keyframes fadeUp { from { opacity: 0; transform: translateY(16px); } to { opacity: 1; transform: none; } }
@keyframes spin { from { transform: rotate(-120deg) scale(.9); opacity: 0; } to { transform: none; opacity: 1; } }
@keyframes grow { from { width: 0; } }
@keyframes logoIn { from { opacity: 0; transform: scale(.7) translateY(12px); filter: blur(8px); }
  to { opacity: 1; transform: none; filter: none; } }
@keyframes caricamento { to { width: 100%; } }
@keyframes splashOut { to { opacity: 0; visibility: hidden; } }
</style>
"""

SPLASH = """
<div class="splash">
  <div class="splash-logo">Smart Quant</div>
  <div class="splash-barra"><div></div></div>
</div>
"""


def leggi_chiave():
    try:
        return str(st.secrets["TWELVE_DATA_KEY"]).strip()
    except Exception:
        pass
    try:
        with open(CHIAVE_FILE, encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        return ""


def num(valore, decimali=2, suffisso=""):
    if valore is None or (isinstance(valore, float) and np.isnan(valore)):
        return "n.d."
    return f"{valore:,.{decimali}f}{suffisso}"


def intero(valore):
    if valore is None or (isinstance(valore, float) and np.isnan(valore)):
        return "n.d."
    return f"{int(valore):,}"


def pct(x):
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "n.d."
    return f"{x * 100:+.1f}%"


@st.cache_data(ttl=240, show_spinner=False)
def prezzi_twelve(ticker, intervallo, chiave):
    risposta = requests.get(
        "https://api.twelvedata.com/time_series",
        params={"symbol": ticker, "interval": intervallo, "outputsize": 500, "apikey": chiave},
        timeout=20,
    )
    dati = risposta.json()
    if dati.get("status") != "ok":
        raise RuntimeError(dati.get("message", "risposta non valida"))
    df = pd.DataFrame(dati["values"])
    if "volume" not in df.columns:
        df["volume"] = 0
    df["datetime"] = pd.to_datetime(df["datetime"])
    df = df.set_index("datetime").sort_index()
    df = df.astype({"open": float, "high": float, "low": float, "close": float, "volume": float})
    df = df.rename(columns={"open": "Open", "high": "High", "low": "Low", "close": "Close", "volume": "Volume"})
    return df[["Open", "High", "Low", "Close", "Volume"]]


@st.cache_data(ttl=240, show_spinner=False)
def prezzi_yahoo(ticker, intervallo, periodo):
    df = yf.download(ticker, interval=intervallo, period=periodo, auto_adjust=True, progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df.dropna()


@st.cache_data(ttl=86400, show_spinner=False)
def info_titolo(ticker):
    try:
        return yf.Ticker(ticker).info or {}
    except Exception:
        return {}


def carica_prezzi(ticker, orizzonte, chiave):
    cfg = ORIZZONTI[orizzonte]
    nota = ""
    if chiave:
        if ticker.endswith(".MI"):
            nota = "Per la Borsa italiana Twelve Data richiede un piano a pagamento: uso Yahoo Finance."
        else:
            try:
                return prezzi_twelve(ticker, cfg["td"], chiave), "Twelve Data", ""
            except Exception as e:
                nota = f"Twelve Data non disponibile per questo titolo ({e}): uso Yahoo Finance."
    return prezzi_yahoo(ticker, cfg["yf"], cfg["periodo"]), "Yahoo Finance", nota


def analizza(df, info, per_anno):
    close = df["Close"].astype(float)
    n = len(close)
    ultimo = float(close.iloc[-1])
    ma20 = close.rolling(20).mean().iloc[-1]
    ma50 = close.rolling(50).mean().iloc[-1]
    ma200 = close.rolling(200).mean().iloc[-1] if n >= 200 else np.nan

    delta = close.diff()
    guad = delta.clip(lower=0).ewm(alpha=1 / 14, adjust=False).mean()
    perd = (-delta.clip(upper=0)).ewm(alpha=1 / 14, adjust=False).mean()
    rsi_serie = (100 - 100 / (1 + guad / perd.replace(0, np.nan))).mask(perd == 0, 100.0)
    rsi = float(rsi_serie.iloc[-1]) if not np.isnan(rsi_serie.iloc[-1]) else 50.0

    macd = close.ewm(span=12, adjust=False).mean() - close.ewm(span=26, adjust=False).mean()
    segnale = macd.ewm(span=9, adjust=False).mean()

    vol = float(close.pct_change().dropna().std() * np.sqrt(per_anno))
    dd = float((close / close.cummax() - 1).min())
    rend_terzo = ultimo / float(close.iloc[-max(2, n // 3)]) - 1

    criteri = []

    def regola(cat, nome, valido, ok, punti):
        if valido:
            criteri.append({"cat": cat, "nome": nome, "ok": punti if ok else 0,
                            "max": punti, "passato": bool(ok)})

    regola("Tecnico", "Prezzo sopra MA20", not np.isnan(ma20), ultimo > ma20, 5)
    regola("Tecnico", "Prezzo sopra MA50", not np.isnan(ma50), ultimo > ma50, 10)
    regola("Tecnico", "Prezzo sopra MA200", not np.isnan(ma200), ultimo > ma200, 10)
    regola("Tecnico", "MA20 sopra MA50", not np.isnan(ma50), ma20 > ma50, 5)
    regola("Tecnico", "MACD sopra la linea di segnale", True,
           bool(macd.iloc[-1] > segnale.iloc[-1]), 5)
    regola("Tecnico", "RSI in zona neutra (30-70)", True, 30 < rsi < 70, 5)
    regola("Tecnico", "Rendimento nell'ultimo terzo positivo", True, rend_terzo > 0, 10)
    regola("Rischio", "Volatilità annua sotto il 25%", True, vol < 0.25, 15)
    regola("Rischio", "Ribasso massimo sotto il 30%", True, dd > -0.30, 15)

    if info.get("quoteType") == "EQUITY":
        pe = info.get("trailingPE")
        regola("Fondamentale", "P/E tra 0 e 25", pe is not None,
               pe is not None and 0 < pe < 25, 10)
        regola("Fondamentale", "Distribuisce dividendi", True,
               (info.get("dividendYield") or 0) > 0, 5)
        beta = info.get("beta")
        regola("Fondamentale", "Beta sotto 1.2", beta is not None,
               beta is not None and beta < 1.2, 5)

    ottenuti = sum(c["ok"] for c in criteri)
    massimi = sum(c["max"] for c in criteri)
    score = round(ottenuti / massimi * 100) if massimi else 0

    categorie = {}
    for c in criteri:
        g, m = categorie.get(c["cat"], (0, 0))
        categorie[c["cat"]] = (g + c["ok"], m + c["max"])

    return {
        "score": score, "categorie": categorie, "criteri": criteri,
        "vol": vol, "dd": dd, "rsi": rsi, "rend_terzo": rend_terzo,
        "massimo": float(close.max()), "minimo": float(close.min()),
    }


def calcola_indicatori(df, per_anno):
    close = df["Close"].astype(float)
    high = df["High"].astype(float)
    low = df["Low"].astype(float)
    ultimo = float(close.iloc[-1])
    ind = {"ultimo": ultimo, "medie": []}

    for p in (20, 50, 100, 200):
        if len(close) >= p:
            ind["medie"].append((f"SMA {p}", float(close.rolling(p).mean().iloc[-1])))
    for p in (12, 26, 50):
        ind["medie"].append((f"EMA {p}", float(close.ewm(span=p, adjust=False).mean().iloc[-1])))

    delta = close.diff()
    guad = delta.clip(lower=0).ewm(alpha=1 / 14, adjust=False).mean()
    perd = (-delta.clip(upper=0)).ewm(alpha=1 / 14, adjust=False).mean()
    rsi = (100 - 100 / (1 + guad / perd.replace(0, np.nan))).mask(perd == 0, 100.0)
    ind["rsi"] = float(rsi.iloc[-1])

    macd = close.ewm(span=12, adjust=False).mean() - close.ewm(span=26, adjust=False).mean()
    segnale = macd.ewm(span=9, adjust=False).mean()
    ind["macd"] = float(macd.iloc[-1])
    ind["segnale"] = float(segnale.iloc[-1])

    minimo14 = low.rolling(14).min()
    massimo14 = high.rolling(14).max()
    ind["stoch"] = float((100 * (close - minimo14) / (massimo14 - minimo14).replace(0, np.nan)).iloc[-1])
    ind["roc10"] = float(close.pct_change(10).iloc[-1])
    ind["roc20"] = float(close.pct_change(20).iloc[-1])

    chiusura_prec = close.shift(1)
    vero_range = pd.concat([high - low, (high - chiusura_prec).abs(), (low - chiusura_prec).abs()],
                           axis=1).max(axis=1)
    atr = vero_range.ewm(alpha=1 / 14, adjust=False).mean()
    ind["atr"] = float(atr.iloc[-1])
    ind["atr_pct"] = float(atr.iloc[-1] / ultimo)

    media = close.rolling(20).mean()
    dev = close.rolling(20).std()
    alta = media + 2 * dev
    bassa = media - 2 * dev
    ind["bb_alta"] = float(alta.iloc[-1])
    ind["bb_bassa"] = float(bassa.iloc[-1])
    ind["bb_pct"] = float((ultimo - bassa.iloc[-1]) / (alta.iloc[-1] - bassa.iloc[-1]))
    ind["vol"] = float(close.pct_change().dropna().std() * np.sqrt(per_anno))
    return ind


def verdetto(score):
    if score >= 80:
        return "STRONG BUY", "#15803d"
    if score >= 60:
        return "BUY", "#16a34a"
    if score >= 40:
        return "HOLD", "#ca8a04"
    if score >= 20:
        return "SELL", "#ea580c"
    return "STRONG SELL", "#dc2626"


def simbolo_tv(ticker):
    if ticker.endswith(".MI"):
        return "MIL:" + ticker[:-3]
    return ticker


def vai(schermata):
    st.session_state["schermata"] = schermata


def sottomenu(nome, opzioni):
    return st.radio("Sezione", opzioni, horizontal=True, key=f"sub_{nome}", label_visibility="collapsed")


def dashboard_live(funzione):
    if hasattr(st, "fragment"):
        return st.fragment(run_every=300)(funzione)
    return funzione


def griglia(voci):
    celle = "".join(f"<div class='kpi'><span>{k}</span><b>{v}</b></div>" for k, v in voci)
    return f"<div class='grid'>{celle}</div>"


def card_ind(nome, valore, nota="", tono=""):
    return (
        f"<div class='card ind {tono}'><small>{nome}</small>"
        f"<b>{valore}</b><span>{nota}</span></div>"
    )


def dati_titolo(ticker, orizzonte, chiave):
    cfg = ORIZZONTI[orizzonte]
    try:
        df, fonte, nota = carica_prezzi(ticker, orizzonte, chiave)
        info = info_titolo(ticker)
    except Exception as e:
        st.error(f"Impossibile caricare i dati per {ticker}: {e}")
        return None
    if df.empty or len(df) < 60:
        st.error(f"Dati insufficienti ({len(df)} righe ricevute). Prova un orizzonte più lungo o controlla il simbolo.")
        return None
    if nota:
        st.warning(nota)
    return {"df": df, "info": info, "fonte": fonte, "cfg": cfg, "res": analizza(df, info, cfg["per_anno"])}


def tv_html(simbolo, intervallo):
    config = {
        "autosize": True, "symbol": simbolo, "interval": intervallo,
        "timezone": "Europe/Rome", "theme": "light", "style": "1", "locale": "it",
        "toolbar_bg": "#ffffff", "enable_publishing": False,
        "allow_symbol_change": True, "container_id": "tv_chart",
    }
    return (
        "<div style='height:520px;width:100%;border-radius:22px;overflow:hidden;"
        "border:1px solid #eef2f7;background:#ffffff'>"
        "<div id='tv_chart' style='height:520px;width:100%'></div>"
        "<script src='https://s3.tradingview.com/tv.js'></script>"
        f"<script>new TradingView.widget({json.dumps(config)});</script></div>"
    )


def punteggio_html(score, colore, testo, categorie):
    barre = ""
    for cat, (got, mx) in categorie.items():
        p = got / mx * 100 if mx else 0
        barre += (
            f"<div class='driver'><span>{cat}</span>"
            f"<div class='barra'><div class='riempi' style='width:{p:.0f}%'></div></div>"
            f"<b>{p:.0f}</b></div>"
        )
    gradi = score * 3.6
    anello = (
        f"<div class='ring' style='background:conic-gradient({colore} 0deg {gradi:.1f}deg, "
        f"rgba(148,163,184,.18) {gradi:.1f}deg 360deg)'>"
        f"<div class='ring-in'><div class='num'>{score}</div><div class='sub'>su 100</div></div></div>"
    )
    return (
        f"<div class='card punteggio'>{anello}"
        f"<div class='badge' style='color:{colore};border-color:{colore}'>{testo}</div>"
        f"<div class='driver-box'>{barre}</div></div>"
    )


def vista_medie(ind):
    ultimo = ind["ultimo"]
    schede = ""
    for nome, valore in ind["medie"]:
        sopra = ultimo > valore
        distanza = abs(ultimo / valore - 1) * 100
        schede += card_ind(
            nome,
            num(valore),
            f"Prezzo {'sopra' if sopra else 'sotto'} la media di {distanza:.1f}%",
            "up" if sopra else "down",
        )
    st.markdown(f"<div class='grid'>{schede}</div>", unsafe_allow_html=True)


def vista_momentum(ind):
    rsi = ind["rsi"]
    if rsi > 70:
        t_rsi, n_rsi = "down", "Ipercomprato (sopra 70)"
    elif rsi < 30:
        t_rsi, n_rsi = "up", "Ipervenduto (sotto 30)"
    else:
        t_rsi, n_rsi = "", "Zona neutra (30-70)"

    macd, segnale = ind["macd"], ind["segnale"]
    t_macd = "up" if macd > segnale else "down"
    n_macd = "Sopra la linea di segnale" if macd > segnale else "Sotto la linea di segnale"

    k = ind["stoch"]
    if k > 80:
        t_k, n_k = "down", "Area alta (sopra 80)"
    elif k < 20:
        t_k, n_k = "up", "Area bassa (sotto 20)"
    else:
        t_k, n_k = "", "Zona media"

    r10, r20 = ind["roc10"], ind["roc20"]
    schede = (
        card_ind("RSI (14)", num(rsi, 1), n_rsi, t_rsi)
        + card_ind("MACD", num(macd, 3), n_macd, t_macd)
        + card_ind("Stocastico %K (14)", num(k, 1), n_k, t_k)
        + card_ind("Variazione 10 periodi", pct(r10), "Momentum di breve periodo",
                   "up" if r10 > 0 else "down")
        + card_ind("Variazione 20 periodi", pct(r20), "Momentum di medio periodo",
                   "up" if r20 > 0 else "down")
    )
    st.markdown(f"<div class='grid'>{schede}</div>", unsafe_allow_html=True)


def vista_volatilita(ind):
    ultimo = ind["ultimo"]
    alta, bassa, pct_b = ind["bb_alta"], ind["bb_bassa"], ind["bb_pct"]
    if pct_b > 1:
        n_bb, t_bb = "Sopra la banda alta: movimento forte", "down"
    elif pct_b < 0:
        n_bb, t_bb = "Sotto la banda bassa: movimento forte", "up"
    else:
        n_bb, t_bb = "Dentro le bande", ""
    schede = (
        card_ind("ATR (14)", num(ind["atr"]), f"{ind['atr_pct'] * 100:.2f}% del prezzo")
        + card_ind("Banda alta (20, 2 dev.)", num(alta), f"Distanza dal prezzo {pct(alta / ultimo - 1)}")
        + card_ind("Banda bassa (20, 2 dev.)", num(bassa), f"Distanza dal prezzo {pct(bassa / ultimo - 1)}")
        + card_ind("%B Bollinger", num(pct_b * 100, 0, "%"), n_bb, t_bb)
        + card_ind("Volatilità annua", num(ind["vol"] * 100, 1, "%"), "Deviazione standard dei rendimenti")
    )
    st.markdown(f"<div class='grid'>{schede}</div>", unsafe_allow_html=True)


@dashboard_live
def panoramica(ticker, orizzonte, chiave):
    dati = dati_titolo(ticker, orizzonte, chiave)
    if dati is None:
        return
    df, info, res = dati["df"], dati["info"], dati["res"]
    fonte, cfg = dati["fonte"], dati["cfg"]
    testo_v, colore = verdetto(res["score"])

    ultimo = float(df["Close"].iloc[-1])
    data_ultima = df.index[-1].date()
    giorno = df[df.index.date == data_ultima]
    precedenti = df[df.index.date < data_ultima]
    chiusura_prec = float(precedenti["Close"].iloc[-1]) if len(precedenti) else float(df["Close"].iloc[-2])
    var = ultimo / chiusura_prec - 1
    colore_var = "#059669" if var >= 0 else "#dc2626"
    valuta = info.get("currency", "")
    nome = info.get("longName") or info.get("shortName") or ticker
    cap = info.get("marketCap")
    ora = datetime.now().strftime("%H:%M:%S")

    if fonte == "Twelve Data":
        chip = "<span class='chip ok'>● Twelve Data · dati USA</span>"
    else:
        chip = "<span class='chip warn'>● Yahoo Finance · possibili ritardi</span>"

    st.markdown(
        "<div class='hero-card'>"
        f"<div><div class='titolo'>{nome}<span class='ticker'>{ticker}</span></div>"
        f"<div class='prezzo'>{ultimo:,.2f}<small>{valuta}</small>"
        f"<span class='var' style='color:{colore_var}'>{pct(var)}</span></div></div>"
        f"<div class='meta'>{chip}<div class='ora'>aggiornato alle {ora}</div></div>"
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown("<div class='sezione'>Grafico e punteggio</div>", unsafe_allow_html=True)
    col_g, col_p = st.columns([2.4, 1])
    with col_g:
        components.html(tv_html(simbolo_tv(ticker), cfg["tv"]), height=540)
    with col_p:
        st.markdown(punteggio_html(res["score"], colore, testo_v, res["categorie"]), unsafe_allow_html=True)

    st.markdown("<div class='sezione'>Dati di mercato</div>", unsafe_allow_html=True)
    st.markdown(griglia([
        ("Apertura", num(float(giorno["Open"].iloc[0]))),
        ("Massimo sessione", num(float(giorno["High"].max()))),
        ("Minimo sessione", num(float(giorno["Low"].min()))),
        ("Chiusura precedente", num(chiusura_prec)),
        ("Volume sessione", intero(float(giorno["Volume"].sum()))),
        ("Capitalizzazione", f"{cap / 1e9:,.2f} mld" if cap else "n.d."),
        ("P/E", num(info.get("trailingPE"))),
        ("Dividend yield", num(info.get("dividendYield"), suffisso="%")),
        ("Beta", num(info.get("beta"))),
        ("Massimo 52 settimane", num(info.get("fiftyTwoWeekHigh"))),
        ("Minimo 52 settimane", num(info.get("fiftyTwoWeekLow"))),
        ("Settore", info.get("sector") or info.get("category") or "n.d."),
    ]), unsafe_allow_html=True)

    st.markdown(
        "<div class='nota'>Il punteggio usa indicatori storici e non è un consiglio di acquisto o vendita. "
        "Il grafico TradingView usa i suoi dati; i numeri del punteggio arrivano dalla fonte indicata sopra. "
        "Valuta sempre il tuo orizzonte e la tua tolleranza al rischio.</div>",
        unsafe_allow_html=True,
    )


def criteri_titolo(ticker, orizzonte, chiave):
    dati = dati_titolo(ticker, orizzonte, chiave)
    if dati is None:
        return
    schede = "".join(
        f"<div class='card criterio {'ok' if c['passato'] else 'ko'}'>"
        f"<div><small>{c['cat']}</small><b>{c['nome']}</b></div>"
        f"<div class='punti'>{c['ok']}/{c['max']}</div></div>"
        for c in dati["res"]["criteri"]
    )
    st.markdown(f"<div class='grid'>{schede}</div>", unsafe_allow_html=True)


def quotazioni_titolo(ticker, orizzonte, chiave):
    dati = dati_titolo(ticker, orizzonte, chiave)
    if dati is None:
        return
    df = dati["df"]
    colonne = ["Open", "High", "Low", "Close", "Volume"]
    intestazione = "".join(f"<th>{c}</th>" for c in ["Data"] + colonne)
    righe = ""
    for idx, riga in df[colonne].tail(30).iloc[::-1].iterrows():
        data = idx.strftime("%d/%m/%Y %H:%M") if getattr(idx, "hour", 0) else idx.strftime("%d/%m/%Y")
        celle = "".join(
            f"<td>{intero(riga[c])}</td>" if c == "Volume" else f"<td>{num(riga[c])}</td>"
            for c in colonne
        )
        righe += f"<tr><td>{data}</td>{celle}</tr>"
    st.markdown(
        f"<div class='card'><table class='q'><thead><tr>{intestazione}</tr></thead>"
        f"<tbody>{righe}</tbody></table></div>",
        unsafe_allow_html=True,
    )


def app_analisi(ticker, orizzonte, chiave):
    sezione = sottomenu("analisi", ["Panoramica", "Criteri", "Quotazioni"])
    if sezione == "Panoramica":
        panoramica(ticker, orizzonte, chiave)
    elif sezione == "Criteri":
        criteri_titolo(ticker, orizzonte, chiave)
    else:
        quotazioni_titolo(ticker, orizzonte, chiave)


def app_indicatori(ticker, orizzonte, chiave):
    dati = dati_titolo(ticker, orizzonte, chiave)
    if dati is None:
        return
    ind = calcola_indicatori(dati["df"], dati["cfg"]["per_anno"])
    sezione = sottomenu("indicatori", ["Medie mobili", "Momentum", "Volatilità"])
    if sezione == "Medie mobili":
        vista_medie(ind)
    elif sezione == "Momentum":
        vista_momentum(ind)
    else:
        vista_volatilita(ind)


def app_impostazioni(chiave):
    st.markdown(griglia([
        ("Chiave Twelve Data", "Trovata" if chiave else "Non trovata"),
        ("Titoli USA", "Twelve Data se la chiave c'è, altrimenti Yahoo"),
        ("Borsa italiana", "Yahoo Finance"),
        ("Limiti piano gratuito", "800 richieste al giorno, 8 al minuto"),
    ]), unsafe_allow_html=True)
    if st.button("🧹 Svuota la memoria dei dati", key="btn_pulisci"):
        st.cache_data.clear()
        st.success("Memoria svuotata: i prossimi dati verranno ricaricati.")


def mostra_home():
    st.markdown(
        "<div class='hero'><h1>Smart Quant</h1>"
        "<p>Analisi e dati di mercato, tutto in ordine</p></div>",
        unsafe_allow_html=True,
    )
    colonne = st.columns(len(APP))
    for colonna, (chiave_app, (icona, nome)) in zip(colonne, APP.items()):
        with colonna:
            st.button(f"{icona}  {nome}", key=f"tile_{chiave_app}", on_click=vai, args=(chiave_app,))


st.session_state.setdefault("schermata", "home")
st.session_state.setdefault("intro", True)

st.markdown(CSS, unsafe_allow_html=True)
if st.session_state["intro"]:
    st.markdown(SPLASH, unsafe_allow_html=True)
    st.session_state["intro"] = False

chiave = leggi_chiave()
barra = st.columns([1.3, 3, 2, 1])
with barra[0]:
    if st.session_state["schermata"] == "home":
        st.markdown("<div class='logo'>📈 Smart Quant</div>", unsafe_allow_html=True)
    else:
        st.button("← Home", key="btn_home", on_click=vai, args=("home",))
with barra[1]:
    ticker = st.text_input("Titolo o ETF", "AAPL", placeholder="es. AAPL, NVDA, ENEL.MI, SWDA.MI", key="ticker")
    ticker = ticker.strip().upper()
with barra[2]:
    orizzonte = st.selectbox("Orizzonte di analisi", list(ORIZZONTI.keys()), index=3, key="orizzonte")
with barra[3]:
    st.markdown("<div class='spazio'></div>", unsafe_allow_html=True)
    if st.button("⚡ Aggiorna", key="btn_aggiorna"):
        st.cache_data.clear()

schermata = st.session_state["schermata"]
if schermata == "home":
    mostra_home()
elif schermata == "impostazioni":
    app_impostazioni(chiave)
elif not ticker:
    st.info("Scrivi un ticker per iniziare, ad esempio AAPL o ENEL.MI.")
elif schermata == "analisi":
    app_analisi(ticker, orizzonte, chiave)
elif schermata == "indicatori":
    app_indicatori(ticker, orizzonte, chiave)
