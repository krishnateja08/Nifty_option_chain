"""
NIFTY 50 COMPLETE ANALYSIS - SLATE TEAL THEME
═══════════════════════════════════════════════════════════════
THEME    : Slate Teal (Theme 1)
PALETTE  :
  --bg           : #1c2b32   (slate ocean base)
  --surface      : #233039   (card background)
  --surface2     : #2a3c46   (hover / nested)
  --border       : rgba(45,212,191,0.12)
  --accent       : #2dd4bf   (teal)
  --accent2      : #38bdf8   (sky blue)
  --text         : #e2eef2   (primary text)
  --muted        : #7a9aaa   (secondary text)
  --pos          : #4ade80   (green / bullish)
  --neg          : #f87171   (red / bearish)
  --neu          : #fbbf24   (yellow / neutral)
═══════════════════════════════════════════════════════════════
CARD STYLE        : Glassmorphism Frosted — Stat Card + Progress Bar
CHANGE IN OI      : Slate Teal Command Theme
FII/DII SECTION   : Pulse Flow (Teal Palette)
MARKET DIRECTION  : Holographic Glass Widget (Compact)
KEY LEVELS        : 1H Candles · Last 120 bars · ±200 pts from price
AUTO REFRESH      : Silent background fetch every 30s

FULLY AUTOMATED v4:
  - GLOBAL BIAS     → auto from SGX Nifty + S&P500 + Dow Jones
  - VOL AT SUPPORT  → auto from 1H volume at nearest support
  - VOL AT RESIST.  → auto from 1H volume at nearest resistance
  - MACD            → macd_bullish key stored explicitly
  - VOL VIEW (IV)   → auto from India VIX
"""

from curl_cffi import requests
import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta, date
import calendar
import yfinance as yf
import warnings
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import pytz
warnings.filterwarnings('ignore')

NSE_FO_HOLIDAYS = {
    "26-Jan-2025","19-Feb-2025","14-Mar-2025","31-Mar-2025","10-Apr-2025",
    "14-Apr-2025","18-Apr-2025","01-May-2025","15-Aug-2025","27-Aug-2025",
    "02-Oct-2025","20-Oct-2025","21-Oct-2025","05-Nov-2025","19-Nov-2025","25-Dec-2025",
    "15-Jan-2026","26-Jan-2026","03-Mar-2026","26-Mar-2026","31-Mar-2026",
    "03-Apr-2026","14-Apr-2026","01-May-2026","28-May-2026","26-Jun-2026",
    "14-Sep-2026","02-Oct-2026","20-Oct-2026","10-Nov-2026","24-Nov-2026","25-Dec-2026",
}

# ═══════════════════════════════════════════════════════════════════════════════
#  SLATE TEAL CSS VARIABLES — single source of truth for the entire theme
# ═══════════════════════════════════════════════════════════════════════════════

THEME_CSS_VARS = """
    --bg:           #1c2b32;
    --surface:      #233039;
    --surface2:     #2a3c46;
    --surface3:     #324d5c;
    --border:       rgba(45,212,191,0.12);
    --border2:      rgba(45,212,191,0.22);
    --accent:       #2dd4bf;
    --accent2:      #38bdf8;
    --accent-glow:  rgba(45,212,191,0.18);
    --text:         #e2eef2;
    --text2:        #b8d0d8;
    --muted:        #7a9aaa;
    --muted2:       #4a6a7a;
    --pos:          #4ade80;
    --pos-bg:       rgba(74,222,128,0.10);
    --pos-border:   rgba(74,222,128,0.22);
    --neg:          #f87171;
    --neg-bg:       rgba(248,113,113,0.10);
    --neg-border:   rgba(248,113,113,0.22);
    --neu:          #fbbf24;
    --neu-bg:       rgba(251,191,36,0.08);
    --neu-border:   rgba(251,191,36,0.20);
    --info:         #38bdf8;
    --info-bg:      rgba(56,189,248,0.08);
    --info-border:  rgba(56,189,248,0.20);
    --grad-accent:  linear-gradient(135deg,#2dd4bf,#38bdf8);
    --grad-pos:     linear-gradient(90deg,#4ade80,#22c55e);
    --grad-neg:     linear-gradient(90deg,#f87171,#ef4444);
    --grad-neu:     linear-gradient(90deg,#fbbf24,#f59e0b);
    --grad-header:  linear-gradient(135deg,#1c3a45 0%,#1e3040 50%,#1c2b38 100%);
    --shadow-card:  0 4px 20px rgba(0,0,0,0.30);
    --shadow-hover: 0 8px 32px rgba(0,0,0,0.40);
    --radius-card:  14px;
    --radius-sm:    8px;
    --radius-lg:    18px;
"""


# ═══════════════════════════════════════════════════════════════════════════════
#  AUTO-DETECT: GLOBAL BIAS
# ═══════════════════════════════════════════════════════════════════════════════

def auto_global_bias():
    try:
        symbols = ['^NSEI', '^GSPC', '^DJI']
        scores  = []
        details = []
        for sym in symbols:
            try:
                tk   = yf.Ticker(sym)
                hist = tk.history(period='5d', interval='1d')
                if hist.empty or len(hist) < 2:
                    details.append(f"  {sym}: no data"); continue
                prev_close = float(hist['Close'].iloc[-2])
                last_close = float(hist['Close'].iloc[-1])
                if prev_close == 0: continue
                chg_pct = (last_close - prev_close) / prev_close * 100
                if   chg_pct >  0.15: s = +1
                elif chg_pct < -0.15: s = -1
                else:                 s =  0
                scores.append(s)
                details.append(f"  {sym}: {chg_pct:+.2f}% → score {s:+d}")
            except Exception as e:
                details.append(f"  {sym}: error ({e})")
        for line in details: print(line)
        if not scores:
            print("  ⚠️  Global bias: no data — defaulting to neutral")
            return "neutral"
        total = sum(scores)
        bias  = "bullish" if total >= 1 else ("bearish" if total <= -1 else "neutral")
        print(f"  🌐 Global bias score={total:+d} → {bias.upper()}")
        return bias
    except Exception as e:
        print(f"  ⚠️  auto_global_bias failed: {e}")
        return "neutral"


# ═══════════════════════════════════════════════════════════════════════════════
#  AUTO-DETECT: VOL VIEW from India VIX
# ═══════════════════════════════════════════════════════════════════════════════

def auto_vol_view():
    try:
        vix_tk   = yf.Ticker('^INDIAVIX')
        vix_hist = vix_tk.history(period='5d', interval='1d')
        if vix_hist.empty:
            print("  ⚠️  India VIX: no data — defaulting to normal")
            return "normal", None
        vix_val = float(vix_hist['Close'].iloc[-1])
        if   vix_val < 13:  view = 'low'
        elif vix_val > 18:  view = 'high'
        else:               view = 'normal'
        print(f"  📊 India VIX = {vix_val:.2f} → vol_view = {view.upper()}")
        return view, round(vix_val, 2)
    except Exception as e:
        print(f"  ⚠️  auto_vol_view failed: {e}")
        return "normal", None


# ═══════════════════════════════════════════════════════════════════════════════
#  AUTO-DETECT: VOLUME AT SUPPORT / RESISTANCE
# ═══════════════════════════════════════════════════════════════════════════════

def auto_volume_at_levels(support, resistance, current_price):
    try:
        nifty  = yf.Ticker('^NSEI')
        df_1h  = nifty.history(interval='1h', period='60d')
        if df_1h.empty:
            print("  ⚠️  1H data unavailable for volume-at-level calculation")
            return None, None
        df_1h = df_1h.reset_index()
        df_1h['Vol_MA20'] = df_1h['Volume'].rolling(20).mean()

        tol_sup  = support * 0.005
        sup_bars = df_1h[df_1h['Low'] <= support + tol_sup].copy()
        vol_support_pct = None
        if not sup_bars.empty and not sup_bars['Vol_MA20'].isna().all():
            sup_bars = sup_bars.dropna(subset=['Vol_MA20'])
            if not sup_bars.empty:
                last_sup = sup_bars.iloc[-1]
                avg_vol  = last_sup['Vol_MA20']
                cur_vol  = last_sup['Volume']
                if avg_vol > 0:
                    vol_support_pct = round((cur_vol - avg_vol) / avg_vol * 100, 1)
                    print(f"  📦 Vol@Support  : cur={cur_vol:,.0f} | avg={avg_vol:,.0f} | {vol_support_pct:+.1f}%")

        tol_res  = resistance * 0.005
        res_bars = df_1h[df_1h['High'] >= resistance - tol_res].copy()
        vol_resistance_pct = None
        if not res_bars.empty and not res_bars['Vol_MA20'].isna().all():
            res_bars = res_bars.dropna(subset=['Vol_MA20'])
            if not res_bars.empty:
                last_res = res_bars.iloc[-1]
                avg_vol  = last_res['Vol_MA20']
                cur_vol  = last_res['Volume']
                if avg_vol > 0:
                    vol_resistance_pct = round((cur_vol - avg_vol) / avg_vol * 100, 1)
                    print(f"  📦 Vol@Resistance: cur={cur_vol:,.0f} | avg={avg_vol:,.0f} | {vol_resistance_pct:+.1f}%")

        if vol_support_pct    is None: print("  ⚠️  Vol@Support: no bars within 0.5% of support")
        if vol_resistance_pct is None: print("  ⚠️  Vol@Resistance: no bars within 0.5% of resistance")
        return vol_support_pct, vol_resistance_pct
    except Exception as e:
        print(f"  ⚠️  auto_volume_at_levels failed: {e}")
        return None, None


# ═══════════════════════════════════════════════════════════════════════════════
#  FII/DII HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def _last_5_trading_days():
    ist_off = timedelta(hours=5, minutes=30)
    today   = (datetime.utcnow() + ist_off).date()
    days, d = [], today - timedelta(days=1)
    while len(days) < 5:
        if d.weekday() < 5: days.append(d)
        d -= timedelta(days=1)
    days.reverse()
    return days

def _parse_nse_fiidii(raw):
    if not isinstance(raw, list) or not raw: return []
    days = []
    for row in raw[:10]:
        try:
            dt_obj  = datetime.strptime(row.get("date",""), "%d-%b-%Y")
            fii_net = float(row.get("fiiBuyValue",0) or 0) - float(row.get("fiiSellValue",0) or 0)
            dii_net = float(row.get("diiBuyValue",0) or 0) - float(row.get("diiSellValue",0) or 0)
            days.append({'date': dt_obj.strftime("%b %d"), 'day': dt_obj.strftime("%a"),
                         'fii': round(fii_net,2), 'dii': round(dii_net,2)})
        except Exception: continue
    if len(days) < 3: return []
    days = days[:5]; days.reverse()
    return days

def _fetch_from_groww():
    try:
        from bs4 import BeautifulSoup
        import requests as _req
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Referer": "https://groww.in/",
        }
        resp = _req.get("https://groww.in/fii-dii-data", headers=headers, timeout=15)
        if resp.status_code != 200:
            print(f"  ⚠️  Groww HTTP {resp.status_code}"); return []
        soup  = BeautifulSoup(resp.text, "html.parser")
        table = soup.find("table")
        if not table:
            print("  ⚠️  Groww: table not found"); return []
        rows = table.find_all("tr"); days = []
        for row in rows[1:]:
            cols = [td.get_text(strip=True) for td in row.find_all("td")]
            if len(cols) < 7: continue
            try:
                dt_obj  = datetime.strptime(cols[0], "%d %b %Y")
                fii_net = float(cols[3].replace(",","").replace("+",""))
                dii_net = float(cols[6].replace(",","").replace("+",""))
                days.append({'date': dt_obj.strftime("%b %d"), 'day': dt_obj.strftime("%a"),
                             'fii': round(fii_net,2), 'dii': round(dii_net,2)})
            except Exception: continue
            if len(days) == 5: break
        if len(days) >= 3:
            days.reverse()
            print(f"  ✅ FII/DII from Groww: {days[0]['date']} → {days[-1]['date']}")
            return days
        return []
    except Exception as e:
        print(f"  ⚠️  Groww scrape failed: {e}"); return []

def _fetch_from_nse_curl():
    try:
        from curl_cffi import requests as curl_req
        headers = {
            "authority": "www.nseindia.com",
            "accept": "application/json, text/plain, */*",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
            "referer": "https://www.nseindia.com/reports/fii-dii",
            "accept-language": "en-US,en;q=0.9",
        }
        s = curl_req.Session()
        s.get("https://www.nseindia.com/", headers=headers, impersonate="chrome", timeout=12)
        time.sleep(1.2)
        s.get("https://www.nseindia.com/reports/fii-dii", headers=headers, impersonate="chrome", timeout=12)
        time.sleep(0.8)
        resp = s.get("https://www.nseindia.com/api/fiidiiTradeReact", headers=headers, impersonate="chrome", timeout=20)
        if resp.status_code == 200:
            days = _parse_nse_fiidii(resp.json())
            if days:
                print(f"  ✅ FII/DII from NSE: {days[0]['date']} → {days[-1]['date']}")
                return days
    except Exception as e:
        print(f"  ⚠️  NSE curl_cffi failed: {e}")
    return []

def fetch_fii_dii_data():
    days = _fetch_from_groww()
    if days: return days
    days = _fetch_from_nse_curl()
    if days: return days
    print("  📌 FII/DII: using date-corrected fallback")
    tdays       = _last_5_trading_days()
    placeholder = [(-1540.20,2103.50),(823.60,891.40),(-411.80,1478.30),(69.45,1174.21),(-972.13,1666.98)]
    return [{'date': d.strftime('%b %d'), 'day': d.strftime('%a'),
             'fii': placeholder[i][0], 'dii': placeholder[i][1], 'fallback': True}
            for i, d in enumerate(tdays)]

def compute_fii_dii_summary(data):
    fii_vals = [d['fii'] for d in data]
    dii_vals = [d['dii'] for d in data]
    fii_avg  = sum(fii_vals) / len(fii_vals)
    dii_avg  = sum(dii_vals) / len(dii_vals)
    net_avg  = fii_avg + dii_avg
    fii_span = f'<span style="color:var(--neg);font-weight:700;">₹{fii_avg:.0f} Cr/day</span>'
    dii_span = f'<span style="color:var(--accent);font-weight:700;">₹{dii_avg:+.0f} Cr/day</span>'
    net_span = f'<span style="color:var(--accent2);font-weight:700;">₹{net_avg:+.0f} Cr/day</span>'
    if fii_avg > 0 and dii_avg > 0:
        label='STRONGLY BULLISH'; emoji='🚀'; color='var(--pos)'; badge_cls='fii-bull'
        fii_span = f'<span style="color:var(--pos);font-weight:700;">₹{fii_avg:+.0f} Cr/day</span>'
        insight  = (f"Both FIIs (avg {fii_span}) and DIIs (avg {dii_span}) are net buyers — "
                    f"strong dual institutional confirmation. Net combined flow: {net_span}.")
    elif fii_avg < 0 and dii_avg > 0 and dii_avg > abs(fii_avg):
        label='CAUTIOUSLY BULLISH'; emoji='📈'; color='var(--accent)'; badge_cls='fii-cbull'
        insight  = (f"FIIs are net sellers (avg {fii_span}) but DIIs are absorbing strongly (avg {dii_span}). "
                    f"DII support is cushioning downside. Net combined flow: {net_span}.")
    elif fii_avg < 0 and dii_avg > 0:
        label='MIXED / NEUTRAL'; emoji='⚖️'; color='var(--neu)'; badge_cls='fii-neu'
        insight  = (f"FII selling (avg {fii_span}) partly offset by DII buying (avg {dii_span}). "
                    f"Watch for 3+ consecutive days of FII buying. Net combined flow: {net_span}.")
    elif fii_avg < 0 and dii_avg < 0:
        label='BEARISH'; emoji='📉'; color='var(--neg)'; badge_cls='fii-bear'
        dii_span = f'<span style="color:var(--neg);font-weight:700;">₹{dii_avg:.0f} Cr/day</span>'
        insight  = (f"Both FIIs (avg {fii_span}) and DIIs (avg {dii_span}) are net sellers — "
                    f"clear bearish institutional pressure. Net combined flow: {net_span}.")
    else:
        label='NEUTRAL'; emoji='🔄'; color='var(--muted)'; badge_cls='fii-neu'
        insight  = "Mixed signals from institutional participants. Wait for a clearer trend."
    max_abs = max(abs(v) for row in data for v in (row['fii'], row['dii'])) or 1
    return {'fii_avg': fii_avg, 'dii_avg': dii_avg, 'net_avg': net_avg,
            'label': label, 'emoji': emoji, 'color': color,
            'badge_cls': badge_cls, 'insight': insight, 'max_abs': max_abs}


# ═══════════════════════════════════════════════════════════════════════════════
#  STRATEGY CHECKLIST ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

def score_pcr(pcr):
    if pcr is None: return 0, "N/A", "PCR not available"
    if   pcr > 1.2: return +1, f"{pcr:.3f}", f"PCR {pcr:.3f} → above 1.2 — bullish sentiment"
    elif pcr < 0.8: return -1, f"{pcr:.3f}", f"PCR {pcr:.3f} → below 0.8 — bearish sentiment"
    else:           return  0, f"{pcr:.3f}", f"PCR {pcr:.3f} → 0.8–1.2 range — neutral"

def score_rsi(rsi):
    if rsi is None: return 0, "N/A", "RSI not available"
    if   rsi >= 60: return +1, f"{rsi:.1f}", f"RSI {rsi:.1f} → above 60 — bullish momentum"
    elif rsi <= 40: return -1, f"{rsi:.1f}", f"RSI {rsi:.1f} → below 40 — bearish / oversold"
    else:           return  0, f"{rsi:.1f}", f"RSI {rsi:.1f} → 40–60 zone — neutral"

def score_macd(macd_bullish):
    if macd_bullish is None: return 0, "N/A", "MACD data not available"
    if macd_bullish: return +1, "Bullish Crossover", "MACD crossed above signal line"
    else:            return -1, "Bearish Crossover", "MACD crossed below signal line"

def score_trend(sma_20_above, sma_50_above, sma_200_above):
    if sma_200_above is None: return 0, "N/A", "Trend data not available"
    above_count = sum([sma_20_above, sma_50_above, sma_200_above])
    if   above_count == 3: return +1, "Strong Uptrend", "Price above all SMAs (20/50/200)"
    elif above_count >= 2: return +1, "Uptrend",        "Price above majority of SMAs"
    elif above_count == 0: return -1, "Downtrend",      "Price below all SMAs (20/50/200)"
    else:                  return -1, "Weak / Mixed",   "Price below majority of SMAs"

def score_volume(volume_change_pct, location):
    if volume_change_pct is None:
        return 0, "N/A", f"Volume at {location} — no recent bars in zone"
    msg_base = f"Volume {'+' if volume_change_pct>=0 else ''}{volume_change_pct:.0f}% vs avg at {location}"
    if location == "support":
        if   volume_change_pct >=  30: return +1, f"{volume_change_pct:+.0f}%", f"{msg_base} — buyers active (bullish)"
        elif volume_change_pct <= -20: return -1, f"{volume_change_pct:+.0f}%", f"{msg_base} — weak support (bearish)"
        else:                          return  0, f"{volume_change_pct:+.0f}%", f"{msg_base} — no strong signal"
    else:
        if   volume_change_pct >=  30: return -1, f"{volume_change_pct:+.0f}%", f"{msg_base} — sellers active (bearish)"
        elif volume_change_pct <= -20: return +1, f"{volume_change_pct:+.0f}%", f"{msg_base} — weak resistance (bullish)"
        else:                          return  0, f"{volume_change_pct:+.0f}%", f"{msg_base} — no strong signal"

def score_global(global_bias):
    if global_bias is None: return 0, "N/A", "Global bias not available"
    if   global_bias == "bullish": return +1, "Bullish", "Global indices showing bullish bias"
    elif global_bias == "bearish": return -1, "Bearish", "Global indices showing bearish pressure"
    else:                          return  0, "Neutral", "Global indices mixed"

def score_oi_direction(oi_class):
    if oi_class is None: return 0, "N/A", "OI direction data not available"
    if   oi_class == "bullish": return +1, "Bullish OI", "Net OI change — put build-up dominant"
    elif oi_class == "bearish": return -1, "Bearish OI", "Net OI change — call build-up dominant"
    else:                       return  0, "Neutral OI", "OI changes balanced"

BULLISH_MILD   = ["Bull Call Spread","Bull Put Spread","Jade Lizard","The Wheel Strategy (CSP + Covered Call)"]
BULLISH_STRONG = ["Long Call","Bull Call Spread","Bull Call Ladder","Bull Put Spread","Bull Put Ladder",
                  "Synthetic Long","Call Ratio Backspread","Strap (Bullish Bias)"]
BEARISH_MILD   = ["Bear Call Spread","Bear Put Spread","Reverse Jade Lizard"]
BEARISH_STRONG = ["Long Put","Bear Put Spread","Bear Call Spread","Bear Put Ladder","Bear Call Ladder",
                  "Synthetic Short","Put Ratio Backspread","Strip (Bearish Bias)"]
NEUTRAL_LOW_VOL    = ["Short Straddle","Short Strangle","Iron Condor","Iron Butterfly","Condor Spread (Short)"]
NEUTRAL_NORMAL_VOL = ["Iron Condor","Iron Butterfly","Calendar Spread","Diagonal Spread","Butterfly Spread (Short)"]
VOLATILITY_LONG    = ["Long Straddle","Long Strangle","Long Guts","Strap (Bullish Bias)","Strip (Bearish Bias)","Butterfly Spread (Long)"]
ADVANCED_MISC      = ["Call Ratio Spread","Put Ratio Spread","Christmas Tree Spread"]

STRAT_TYPE_MAP = {
    "Long Call":"bullish","Bull Call Spread":"bullish","Bull Call Ladder":"bullish",
    "Bull Put Spread":"bullish","Bull Put Ladder":"bullish","Synthetic Long":"bullish",
    "Call Ratio Backspread":"bullish","Strap (Bullish Bias)":"volatility",
    "Jade Lizard":"bullish","The Wheel Strategy (CSP + Covered Call)":"bullish",
    "Long Put":"bearish","Bear Put Spread":"bearish","Bear Call Spread":"bearish",
    "Bear Put Ladder":"bearish","Bear Call Ladder":"bearish","Synthetic Short":"bearish",
    "Put Ratio Backspread":"bearish","Strip (Bearish Bias)":"volatility",
    "Reverse Jade Lizard":"bearish",
    "Short Straddle":"neutral","Short Strangle":"neutral","Iron Condor":"neutral",
    "Iron Butterfly":"neutral","Condor Spread (Short)":"neutral",
    "Calendar Spread":"neutral","Diagonal Spread":"neutral","Butterfly Spread (Short)":"neutral",
    "Long Straddle":"volatility","Long Strangle":"volatility","Long Guts":"volatility",
    "Butterfly Spread (Long)":"volatility",
    "Call Ratio Spread":"advanced","Put Ratio Spread":"advanced","Christmas Tree Spread":"advanced",
}

def suggest_strategies(total_score, vol_view):
    if   total_score >= 3:  bias = "strong_bullish";  bias_label = "STRONGLY BULLISH"
    elif total_score >= 1:  bias = "mild_bullish";    bias_label = "MILDLY BULLISH"
    elif total_score <= -3: bias = "strong_bearish";  bias_label = "STRONGLY BEARISH"
    elif total_score <= -1: bias = "mild_bearish";    bias_label = "MILDLY BEARISH"
    else:                   bias = "neutral";          bias_label = "NEUTRAL / RANGE-BOUND"
    strats = []
    if   bias == "strong_bullish": strats.extend(BULLISH_STRONG)
    elif bias == "mild_bullish":   strats.extend(BULLISH_MILD)
    elif bias == "strong_bearish": strats.extend(BEARISH_STRONG)
    elif bias == "mild_bearish":   strats.extend(BEARISH_MILD)
    else:
        if   vol_view == "low":  strats.extend(NEUTRAL_LOW_VOL)
        elif vol_view == "high": strats.extend(VOLATILITY_LONG)
        else:                    strats.extend(NEUTRAL_NORMAL_VOL)
    if vol_view == "high" and bias != "neutral": strats.extend(VOLATILITY_LONG)
    strats.extend(ADVANCED_MISC)
    seen = set(); unique = []
    for s in strats:
        if s not in seen: seen.add(s); unique.append(s)
    return bias_label, unique

def build_strategy_checklist_html(html_data, vol_support=None, vol_resistance=None,
                                   global_bias=None, vol_view="normal", india_vix=None):
    d = html_data
    pcr_val   = d.get('pcr') if d.get('has_option_data') else None
    rsi_val   = d.get('rsi')
    macd_bull = d.get('macd_bullish')
    sma20     = d.get('sma_20_above'); sma50 = d.get('sma_50_above'); sma200 = d.get('sma_200_above')
    oi_cls    = d.get('oi_class') if d.get('has_option_data') else None

    signals = [
        ("📊", "PCR (OI Ratio)",       *score_pcr(pcr_val),                        True),
        ("📈", "RSI (14-Day)",          *score_rsi(rsi_val),                         True),
        ("⚡", "MACD Signal",           *score_macd(macd_bull),                      True),
        ("📉", "Market Trend (SMAs)",   *score_trend(sma20, sma50, sma200),          True),
        ("🔄", "OI Direction",          *score_oi_direction(oi_cls),                 True),
        ("🌐", "Global Market Bias",    *score_global(global_bias),                  True),
        ("📦", "Volume at Support",     *score_volume(vol_support, "support"),       True),
        ("📦", "Volume at Resistance",  *score_volume(vol_resistance, "resistance"), True),
    ]

    auto_scores = [s[2] for s in signals if s[5]]
    total_score = sum(auto_scores)
    bull_count  = sum(1 for s in signals if s[2] > 0)
    bear_count  = sum(1 for s in signals if s[2] < 0)
    neu_count   = sum(1 for s in signals if s[2] == 0 and s[3] != "N/A")
    na_count    = sum(1 for s in signals if s[3] == "N/A")

    bias_label, strategy_list = suggest_strategies(total_score, vol_view)

    circumference = 289.0
    arc_pct       = min(1.0, abs(total_score) / max(1, len(signals)))
    dashoffset    = circumference * (1 - arc_pct)

    if   total_score >= 3:  ring_color = "var(--pos)";    bias_gradient = "linear-gradient(135deg,#4ade80,#22c55e)"
    elif total_score >= 1:  ring_color = "var(--accent)"; bias_gradient = "linear-gradient(135deg,#2dd4bf,#38bdf8)"
    elif total_score <= -3: ring_color = "var(--neg)";    bias_gradient = "linear-gradient(135deg,#f87171,#ef4444)"
    elif total_score <= -1: ring_color = "#fb923c";       bias_gradient = "linear-gradient(135deg,#fb923c,#f97316)"
    else:                   ring_color = "var(--neu)";    bias_gradient = "linear-gradient(135deg,#fbbf24,#f59e0b)"

    score_sign = "+" if total_score > 0 else ""

    def sig_card(icon, name, score, display_val, msg, is_auto):
        if display_val == "N/A":
            icon_cls="sig-na"; s_cls="score-na"; s_txt="N/A"
        elif score > 0:
            icon_cls="sig-bull"; s_cls="score-p"; s_txt=f"+{score}"
        elif score < 0:
            icon_cls="sig-bear"; s_cls="score-n"; s_txt=str(score)
        else:
            icon_cls="sig-neu"; s_cls="score-0"; s_txt="0"
        val_html = (f'<div class="sig-val na-val">{display_val}</div>'
                    if display_val == "N/A"
                    else f'<div class="sig-val">{display_val}</div>')
        return f"""
        <div class="sig-card">
            <div class="sig-icon {icon_cls}">{icon}</div>
            <div class="sig-body">
                <div class="sig-name">{name} <span class="auto-badge">AUTO</span></div>
                {val_html}
                <div class="sig-msg">{msg}</div>
            </div>
            <div class="sig-score {s_cls}">{s_txt}</div>
        </div>"""

    sig_cards_html = "".join(sig_card(*s) for s in signals)

    tag_map = {
        "bullish":   ("strat-bull","strat-tag-bull","🟢 Bullish"),
        "bearish":   ("strat-bear","strat-tag-bear","🔴 Bearish"),
        "neutral":   ("strat-neu", "strat-tag-neu", "🟡 Neutral"),
        "volatility":("strat-vol", "strat-tag-vol", "🟣 Volatility"),
        "advanced":  ("strat-misc","strat-tag-misc","🔵 Advanced"),
    }
    strat_cards_html = ""
    for i, s in enumerate(strategy_list, 1):
        stype = STRAT_TYPE_MAP.get(s, "advanced")
        card_cls, tag_cls, tag_txt = tag_map.get(stype, tag_map["advanced"])
        rank = "PRIMARY" if i <= 4 else ("SECONDARY" if i <= 8 else "ADVANCED")
        strat_cards_html += f"""
        <div class="strat-card {card_cls}" data-type="{stype}">
            <div class="strat-num">{i:02d} · {rank}</div>
            <div class="strat-name">{s}</div>
            <span class="strat-tag {tag_cls}">{tag_txt}</span>
        </div>"""

    timestamp = d.get('timestamp', 'N/A')
    na_span   = '<span class="na-inline">N/A</span>'
    val_pcr   = f"{d['pcr']:.3f}" if d.get('has_option_data') and d.get('pcr') else na_span
    val_rsi   = f"{d['rsi']:.1f}" if d.get('rsi') else na_span
    if   d.get('macd_bullish') is True:  val_macd = "Bullish"
    elif d.get('macd_bullish') is False: val_macd = "Bearish"
    else:                                val_macd = na_span
    if d.get('sma_200_above') is None:   val_trend = na_span
    elif d.get('sma_200_above') and d.get('sma_50_above'): val_trend = "Uptrend"
    elif not d.get('sma_200_above') and not d.get('sma_50_above'): val_trend = "Downtrend"
    else: val_trend = "Mixed"
    val_oi_dir = d.get('oi_direction','N/A') if d.get('has_option_data') else na_span
    val_global = global_bias.title() if global_bias else na_span
    val_vol_sup = f"{vol_support:+.0f}%"   if vol_support  is not None else na_span
    val_vol_res = f"{vol_resistance:+.0f}%" if vol_resistance is not None else na_span
    vix_label   = f"{india_vix:.2f}"        if india_vix else na_span
    na_pill     = f'<span class="sc-pill sc-pill-na">— N/A: {na_count}</span>' if na_count > 0 else ''
    score_note  = ("Strong directional conviction — proceed with caution and stop losses."
                   if abs(total_score) >= 3 else
                   "Moderate signal — size positions conservatively."
                   if abs(total_score) >= 1 else
                   "Mixed signals — range-bound strategies preferred.")
    strat_count = len(strategy_list)

    return f"""
    <div class="tab-panel" id="tab-checklist">

        <div class="section">
            <div class="section-title">
                <span>⚙️</span> LIVE DATA INPUTS
                <span class="annot-badge">ALL AUTO-FILLED FROM LIVE DATA</span>
                <span style="font-size:10px;color:var(--muted2);font-weight:400;margin-left:auto;">As of: {timestamp}</span>
            </div>
            <div class="input-summary-grid">
                <div class="inp-auto-card"><div class="inp-s-label">PCR (OI)</div><div class="inp-s-val">{val_pcr}</div><div class="inp-s-src">Option Chain · AUTO</div></div>
                <div class="inp-auto-card"><div class="inp-s-label">RSI (14)</div><div class="inp-s-val">{val_rsi}</div><div class="inp-s-src">Technical · AUTO</div></div>
                <div class="inp-auto-card"><div class="inp-s-label">MACD</div><div class="inp-s-val">{val_macd}</div><div class="inp-s-src">Technical · AUTO</div></div>
                <div class="inp-auto-card"><div class="inp-s-label">Market Trend</div><div class="inp-s-val">{val_trend}</div><div class="inp-s-src">SMA 20/50/200 · AUTO</div></div>
                <div class="inp-auto-card"><div class="inp-s-label">OI Direction</div><div class="inp-s-val">{val_oi_dir}</div><div class="inp-s-src">CHG OI · AUTO</div></div>
                <div class="inp-auto-card"><div class="inp-s-label">Global Bias</div><div class="inp-s-val">{val_global}</div><div class="inp-s-src">S&amp;P500 + Dow · AUTO</div></div>
                <div class="inp-auto-card"><div class="inp-s-label">Vol at Support</div><div class="inp-s-val">{val_vol_sup}</div><div class="inp-s-src">1H Volume · AUTO</div></div>
                <div class="inp-auto-card"><div class="inp-s-label">Vol at Resistance</div><div class="inp-s-val">{val_vol_res}</div><div class="inp-s-src">1H Volume · AUTO</div></div>
                <div class="inp-auto-card"><div class="inp-s-label">India VIX</div><div class="inp-s-val">{vix_label}</div><div class="inp-s-src">IV View: {vol_view.upper()} · AUTO</div></div>
            </div>
        </div>

        <div class="section">
            <div class="section-title">
                <span>📋</span> SIGNAL CHECKLIST
                <span style="font-size:10px;color:var(--muted2);font-weight:400;margin-left:auto;">
                    {bull_count} Bullish &middot; {bear_count} Bearish &middot; {neu_count} Neutral &middot; {na_count} N/A
                </span>
            </div>
            <div class="signal-grid">{sig_cards_html}</div>
            <div class="score-meter">
                <div class="score-ring-wrap">
                    <svg width="120" height="120" viewBox="0 0 110 110">
                        <circle cx="55" cy="55" r="46" fill="none" stroke="rgba(45,212,191,0.08)" stroke-width="9"/>
                        <circle cx="55" cy="55" r="46" fill="none"
                            stroke="{ring_color}" stroke-width="9" stroke-linecap="round"
                            stroke-dasharray="{circumference:.1f}" stroke-dashoffset="{dashoffset:.1f}"
                            style="transform:rotate(-90deg);transform-origin:55px 55px;"/>
                    </svg>
                    <div class="score-ring-label">
                        <div class="score-ring-num" style="color:{ring_color};">{score_sign}{total_score}</div>
                        <div class="score-ring-txt">SCORE</div>
                    </div>
                </div>
                <div class="score-detail">
                    <div class="score-bias-lbl" style="background:{bias_gradient};-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">{bias_label}</div>
                    <div class="score-sub">Score {score_sign}{total_score} from {len(signals)} signals ({na_count} shown as N/A).<br>{score_note}</div>
                    <div class="score-pills">
                        <span class="sc-pill sc-pill-bull">✓ BULL: {bull_count}</span>
                        <span class="sc-pill sc-pill-bear">✗ BEAR: {bear_count}</span>
                        <span class="sc-pill sc-pill-neu">◻ NEU: {neu_count}</span>
                        {na_pill}
                    </div>
                </div>
            </div>
        </div>

        <div class="section">
            <div class="section-title">
                <span>🎯</span> SUGGESTED STRATEGY TYPES
                <span style="font-size:10px;color:var(--muted2);font-weight:400;letter-spacing:1px;">
                    For study &amp; backtesting only &mdash; NOT financial advice
                </span>
            </div>
            <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px;margin-bottom:16px;">
                <div style="font-size:12px;color:var(--muted);">
                    IV View: <strong style="color:{ring_color};">{vol_view.upper()}</strong>
                    &nbsp;&middot;&nbsp; Bias: <strong style="color:{ring_color};">{bias_label}</strong>
                    &nbsp;&middot;&nbsp; <span style="color:var(--muted2);">{strat_count} strategies found</span>
                </div>
                <div style="display:flex;gap:8px;flex-wrap:wrap;">
                    <button class="filter-btn active" onclick="filterStrats('all',this)">All</button>
                    <button class="filter-btn" onclick="filterStrats('bullish',this)">🟢 Bullish</button>
                    <button class="filter-btn" onclick="filterStrats('bearish',this)">🔴 Bearish</button>
                    <button class="filter-btn" onclick="filterStrats('neutral',this)">🟡 Neutral</button>
                    <button class="filter-btn" onclick="filterStrats('volatility',this)">🟣 Volatility</button>
                    <button class="filter-btn" onclick="filterStrats('advanced',this)">🔵 Advanced</button>
                </div>
            </div>
            <div class="strat-grid" id="stratGrid">{strat_cards_html}</div>
        </div>

        <div class="section">
            <div class="section-title"><span>📖</span> SCORING LEGEND</div>
            <div class="logic-box">
                <div class="logic-box-head">HOW THE SCORE WORKS</div>
                <div class="logic-grid">
                    <div class="logic-item"><span class="lc-bull">+1</span> Signal is bullish</div>
                    <div class="logic-item"><span class="lc-bear">−1</span> Signal is bearish</div>
                    <div class="logic-item"><span class="lc-side">0</span> Neutral signal</div>
                    <div class="logic-item"><span class="lc-info">N/A</span> Price not near level</div>
                    <div class="logic-item"><span class="lc-bull">≥ +3</span> Strongly Bullish &middot; <span class="lc-bull">+1/+2</span> Mildly Bullish</div>
                    <div class="logic-item"><span class="lc-bear">≤ −3</span> Strongly Bearish &middot; <span class="lc-bear">−1/−2</span> Mildly Bearish</div>
                    <div class="logic-item"><span class="lc-info">AUTO</span> All 8 signals auto-filled</div>
                    <div class="logic-item"><span class="lc-info">VIX</span> &lt;13 Low · 13–18 Normal · &gt;18 High</div>
                </div>
            </div>
        </div>

        <div class="section">
            <div class="disclaimer">
                <strong>⚠️ DISCLAIMER</strong><br><br>
                This checklist is for <strong>EDUCATIONAL purposes only</strong> &mdash; NOT financial advice.<br>
                Strategy suggestions are based on a rules-based scoring model and have not been backtested.<br>
                Always validate with your own analysis. Consult a SEBI-registered investment advisor.
            </div>
        </div>

    </div>"""


# ═══════════════════════════════════════════════════════════════════════════════
#  MAIN ANALYZER CLASS
# ═══════════════════════════════════════════════════════════════════════════════

class NiftyHTMLAnalyzer:
    def __init__(self):
        self.yf_symbol    = "^NSEI"
        self.nse_symbol   = "NIFTY"
        self.report_lines = []
        self.html_data    = {}

    def log(self, message):
        print(message)
        self.report_lines.append(message)

    def _make_nse_session(self):
        headers = {
            "authority": "www.nseindia.com",
            "accept": "application/json, text/plain, */*",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
            "referer": "https://www.nseindia.com/option-chain",
            "accept-language": "en-US,en;q=0.9",
        }
        session = requests.Session()
        try:
            session.get("https://www.nseindia.com/", headers=headers, impersonate="chrome", timeout=15)
            time.sleep(1.5)
            session.get("https://www.nseindia.com/option-chain", headers=headers, impersonate="chrome", timeout=15)
            time.sleep(1)
        except Exception as e:
            print(f"  ⚠️  Session warm-up: {e}")
        return session, headers

    def get_upcoming_expiry_tuesday(self):
        ist_tz      = pytz.timezone('Asia/Kolkata')
        now_ist     = datetime.now(ist_tz)
        today_ist   = now_ist.date()
        weekday     = today_ist.weekday()
        past_cutoff = (now_ist.hour, now_ist.minute) >= (16, 0)
        if   weekday == 1 and not past_cutoff: days_ahead = 0
        elif weekday == 1 and past_cutoff:     days_ahead = 7
        elif weekday < 1:                      days_ahead = 1 - weekday
        else:                                  days_ahead = 8 - weekday
        raw_tuesday = today_ist + timedelta(days=days_ahead)
        candidate   = raw_tuesday
        for _ in range(6):
            cstr       = candidate.strftime('%d-%b-%Y')
            is_weekend = candidate.weekday() >= 5
            if cstr not in NSE_FO_HOLIDAYS and not is_weekend: break
            candidate -= timedelta(days=1)
        expiry_str    = candidate.strftime('%d-%b-%Y')
        holiday_shifted = (candidate != raw_tuesday)
        shift_note    = f" ⚠️ HOLIDAY SHIFT from {raw_tuesday.strftime('%d-%b-%Y')}" if holiday_shifted else ""
        print(f"  📅 Now (IST): {now_ist.strftime('%A %d-%b-%Y %H:%M')} | Expiry: {expiry_str}{shift_note}")
        return expiry_str

    def fetch_available_expiries(self, session, headers):
        try:
            url  = f"https://www.nseindia.com/api/option-chain-v3?type=Indices&symbol={self.nse_symbol}"
            resp = session.get(url, headers=headers, impersonate="chrome", timeout=20)
            if resp.status_code == 200:
                data     = resp.json()
                expiries = data.get('records', {}).get('expiryDates', [])
                if expiries:
                    print(f"  📅 NSE expiries: {expiries[:5]}")
                    return expiries[0]
        except Exception as e:
            print(f"  ⚠️  Could not fetch expiry list: {e}")
        return None

    def fetch_nse_option_chain_silent(self):
        session, headers = self._make_nse_session()
        real_expiry = self.fetch_available_expiries(session, headers)
        if real_expiry:
            print(f"  🗓️  Fetching chain for: {real_expiry}")
            result = self._fetch_chain_for_expiry(session, headers, real_expiry)
            if result: return result
        computed_expiry = self.get_upcoming_expiry_tuesday()
        if computed_expiry != real_expiry:
            result = self._fetch_chain_for_expiry(session, headers, computed_expiry)
            if result: return result
        if real_expiry and real_expiry != computed_expiry:
            result = self._fetch_chain_for_expiry(session, headers, real_expiry)
            if result: return result
        print("  ❌ Option chain fetch failed.")
        return None

    def _fetch_chain_for_expiry(self, session, headers, expiry):
        api_url = (f"https://www.nseindia.com/api/option-chain-v3"
                   f"?type=Indices&symbol={self.nse_symbol}&expiry={expiry}")
        for attempt in range(1, 3):
            try:
                print(f"    Attempt {attempt}: expiry={expiry}")
                resp = session.get(api_url, headers=headers, impersonate="chrome", timeout=30)
                print(f"    HTTP {resp.status_code}")
                if resp.status_code != 200:
                    time.sleep(2); continue
                json_data  = resp.json()
                data       = json_data.get('records', {}).get('data', [])
                if not data:
                    print(f"    ⚠️  Empty data"); return None
                rows = []
                for item in data:
                    strike = item.get('strikePrice')
                    ce = item.get('CE', {}); pe = item.get('PE', {})
                    rows.append({
                        'Expiry': expiry, 'Strike': strike,
                        'CE_LTP': ce.get('lastPrice',0), 'CE_OI': ce.get('openInterest',0),
                        'CE_Vol': ce.get('totalTradedVolume',0),
                        'PE_LTP': pe.get('lastPrice',0), 'PE_OI': pe.get('openInterest',0),
                        'PE_Vol': pe.get('totalTradedVolume',0),
                        'CE_OI_Change': ce.get('changeinOpenInterest',0),
                        'PE_OI_Change': pe.get('changeinOpenInterest',0),
                    })
                df_full    = pd.DataFrame(rows).sort_values('Strike').reset_index(drop=True)
                underlying = json_data.get('records', {}).get('underlyingValue', 0)
                atm_strike = round(underlying / 50) * 50
                all_strikes = sorted(df_full['Strike'].unique())
                if atm_strike in all_strikes:
                    atm_idx = all_strikes.index(atm_strike)
                else:
                    atm_idx    = min(range(len(all_strikes)), key=lambda i: abs(all_strikes[i] - underlying))
                    atm_strike = all_strikes[atm_idx]
                lower_idx = max(0, atm_idx - 10); upper_idx = min(len(all_strikes)-1, atm_idx+10)
                selected_strikes = all_strikes[lower_idx:upper_idx+1]
                df = df_full[df_full['Strike'].isin(selected_strikes)].reset_index(drop=True)
                print(f"    ✅ Strikes: {len(df_full)} → ATM±10: {len(df)}")
                return {'expiry': expiry, 'df': df, 'raw_data': data,
                        'underlying': underlying, 'atm_strike': atm_strike}
            except Exception as e:
                print(f"    ❌ Attempt {attempt}: {e}"); time.sleep(2)
        return None

    def analyze_option_chain_data(self, oc_data):
        if not oc_data: return None
        df = oc_data['df']
        total_ce_oi  = df['CE_OI'].sum();  total_pe_oi  = df['PE_OI'].sum()
        total_ce_vol = df['CE_Vol'].sum(); total_pe_vol = df['PE_Vol'].sum()
        pcr_oi  = total_pe_oi  / total_ce_oi  if total_ce_oi  > 0 else 0
        pcr_vol = total_pe_vol / total_ce_vol if total_ce_vol > 0 else 0
        total_ce_oi_change = int(df['CE_OI_Change'].sum())
        total_pe_oi_change = int(df['PE_OI_Change'].sum())
        net_oi_change      = total_pe_oi_change - total_ce_oi_change
        if   total_ce_oi_change > 0 and total_pe_oi_change < 0:
            oi_direction,oi_signal,oi_icon,oi_class="Strong Bearish","Call Build-up + Put Unwinding","🔴","bearish"
        elif total_ce_oi_change < 0 and total_pe_oi_change > 0:
            oi_direction,oi_signal,oi_icon,oi_class="Strong Bullish","Put Build-up + Call Unwinding","🟢","bullish"
        elif total_ce_oi_change > 0 and total_pe_oi_change > 0:
            if   total_pe_oi_change > total_ce_oi_change * 1.5:
                oi_direction,oi_signal,oi_icon,oi_class="Bullish","Put Build-up Dominant","🟢","bullish"
            elif total_ce_oi_change > total_pe_oi_change * 1.5:
                oi_direction,oi_signal,oi_icon,oi_class="Bearish","Call Build-up Dominant","🔴","bearish"
            else:
                oi_direction,oi_signal,oi_icon,oi_class="Neutral (High Vol)","Both Calls & Puts Building","🟡","neutral"
        elif total_ce_oi_change < 0 and total_pe_oi_change < 0:
            oi_direction,oi_signal,oi_icon,oi_class="Neutral (Unwinding)","Both Calls & Puts Unwinding","🟡","neutral"
        else:
            if   net_oi_change > 0: oi_direction,oi_signal,oi_icon,oi_class="Moderately Bullish","Net Put Accumulation","🟢","bullish"
            elif net_oi_change < 0: oi_direction,oi_signal,oi_icon,oi_class="Moderately Bearish","Net Call Accumulation","🔴","bearish"
            else:                   oi_direction,oi_signal,oi_icon,oi_class="Neutral","Balanced OI Changes","🟡","neutral"
        max_ce_oi_row = df.loc[df['CE_OI'].idxmax()]; max_pe_oi_row = df.loc[df['PE_OI'].idxmax()]
        df['pain']    = abs(df['CE_OI'] - df['PE_OI']); max_pain_row = df.loc[df['pain'].idxmin()]
        df['Total_OI'] = df['CE_OI'] + df['PE_OI']
        return {
            'expiry': oc_data['expiry'], 'underlying_value': oc_data['underlying'],
            'atm_strike': oc_data['atm_strike'],
            'pcr_oi': round(pcr_oi,3), 'pcr_volume': round(pcr_vol,3),
            'total_ce_oi': int(total_ce_oi), 'total_pe_oi': int(total_pe_oi),
            'max_ce_oi_strike': int(max_ce_oi_row['Strike']),
            'max_ce_oi_value':  int(max_ce_oi_row['CE_OI']),
            'max_pe_oi_strike': int(max_pe_oi_row['Strike']),
            'max_pe_oi_value':  int(max_pe_oi_row['PE_OI']),
            'max_pain': int(max_pain_row['Strike']),
            'total_ce_oi_change': total_ce_oi_change, 'total_pe_oi_change': total_pe_oi_change,
            'net_oi_change': net_oi_change,
            'oi_direction': oi_direction, 'oi_signal': oi_signal,
            'oi_icon': oi_icon, 'oi_class': oi_class, 'df': df,
        }

    def get_technical_data(self):
        try:
            print("Calculating technical indicators...")
            nifty = yf.Ticker(self.yf_symbol)
            df    = nifty.history(period="2y")
            if df.empty:
                print("Warning: Failed to fetch historical data"); return None
            df['SMA_20']  = df['Close'].rolling(20).mean()
            df['SMA_50']  = df['Close'].rolling(50).mean()
            df['SMA_200'] = df['Close'].rolling(200).mean()
            delta = df['Close'].diff()
            gain  = delta.where(delta > 0, 0).rolling(14).mean()
            loss  = (-delta.where(delta < 0, 0)).rolling(14).mean()
            df['RSI']    = 100 - (100 / (1 + gain / loss))
            df['EMA_12'] = df['Close'].ewm(span=12, adjust=False).mean()
            df['EMA_26'] = df['Close'].ewm(span=26, adjust=False).mean()
            df['MACD']   = df['EMA_12'] - df['EMA_26']
            df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
            latest        = df.iloc[-1]
            current_price = latest['Close']
            valid_macd    = df.dropna(subset=['MACD', 'Signal'])
            if len(valid_macd) >= 2:
                macd_bullish = bool(latest['MACD'] > latest['Signal'])
                print(f"  ✓ MACD={latest['MACD']:.3f} | Signal={latest['Signal']:.3f} | {'BULL' if macd_bullish else 'BEAR'}")
            else:
                macd_bullish = None
                print("  ⚠️  MACD: insufficient data")
            print("  Fetching 1H candles for Key Levels...")
            df_1h = nifty.history(interval="1h", period="60d")
            s1 = s2 = r1 = r2 = None
            if not df_1h.empty:
                recent_1h = df_1h.tail(120)
                highs = sorted(recent_1h['High'].values)
                lows  = sorted(recent_1h['Low'].values)
                res_c = [h for h in highs if current_price < h <= current_price + 200]
                sup_c = [l for l in lows  if current_price - 200 <= l < current_price]
                if len(res_c) >= 4:
                    r1 = round(float(np.percentile(res_c, 40)) / 25) * 25
                    r2 = round(float(np.percentile(res_c, 80)) / 25) * 25
                if len(sup_c) >= 4:
                    s1 = round(float(np.percentile(sup_c, 70)) / 25) * 25
                    s2 = round(float(np.percentile(sup_c, 20)) / 25) * 25
                if r1 and r1 <= current_price: r1 = round((current_price + 50) / 25) * 25
                if r2 and r1 and r2 <= r1:     r2 = r1 + 75
                if s1 and s1 >= current_price: s1 = round((current_price - 50) / 25) * 25
                if s2 and s1 and s2 >= s1:     s2 = s1 - 75
                print(f"  ✓ 1H Levels | S2={s2} S1={s1} | Price={current_price:.0f} | R1={r1} R2={r2}")
            recent_d          = df.tail(60)
            resistance        = r1 if r1 else recent_d['High'].quantile(0.90)
            support           = s1 if s1 else recent_d['Low'].quantile(0.10)
            strong_resistance = r2 if r2 else resistance + 100
            strong_support    = s2 if s2 else support - 100
            technical = {
                'current_price':     current_price,
                'sma_20':            latest['SMA_20'],
                'sma_50':            latest['SMA_50'],
                'sma_200':           latest['SMA_200'],
                'rsi':               latest['RSI'],
                'macd':              latest['MACD'],
                'signal':            latest['Signal'],
                'macd_bullish':      macd_bullish,
                'resistance':        resistance,
                'support':           support,
                'strong_resistance': strong_resistance,
                'strong_support':    strong_support,
            }
            print(f"✓ Technical | Price:{technical['current_price']:.2f} | RSI:{technical['rsi']:.1f}")
            return technical
        except Exception as e:
            print(f"Technical error: {e}"); return None

    def calculate_smart_stop_loss(self, current_price, support, resistance, bias):
        if   bias == "BULLISH": return round(max(support - 30, current_price - 150), 0)
        elif bias == "BEARISH": return round(min(resistance + 30, current_price + 150), 0)
        return None

    def generate_analysis_data(self, technical, option_analysis):
        if not technical:
            self.log("⚠️  Technical data unavailable"); return
        current    = technical['current_price']
        support    = technical['support']
        resistance = technical['resistance']
        ist_now    = datetime.now(pytz.timezone('Asia/Kolkata'))
        bullish_score = bearish_score = 0
        for sma in ['sma_20','sma_50','sma_200']:
            if current > technical[sma]: bullish_score += 1
            else:                        bearish_score += 1
        rsi = technical['rsi']
        if   rsi > 70: bearish_score += 1
        elif rsi < 30: bullish_score += 2
        if technical['macd'] > technical['signal']: bullish_score += 1
        else:                                        bearish_score += 1
        if option_analysis:
            pcr = option_analysis['pcr_oi']; max_pain = option_analysis['max_pain']
            if   pcr > 1.2: bullish_score += 2
            elif pcr < 0.7: bearish_score += 2
            if   current > max_pain + 100: bearish_score += 1
            elif current < max_pain - 100: bullish_score += 1
        score_diff = bullish_score - bearish_score
        print(f"  📊 Bullish:{bullish_score} | Bearish:{bearish_score} | Diff:{score_diff}")
        if   score_diff >= 3:  bias,bias_icon,bias_class="BULLISH","📈","bullish"; confidence="HIGH" if score_diff>=4 else "MEDIUM"
        elif score_diff <= -3: bias,bias_icon,bias_class="BEARISH","📉","bearish"; confidence="HIGH" if score_diff<=-4 else "MEDIUM"
        else:                  bias,bias_icon,bias_class="SIDEWAYS","↔️","sideways"; confidence="MEDIUM"
        if   rsi > 70: rsi_status,rsi_badge,rsi_icon="Overbought","bearish","🔴"
        elif rsi < 30: rsi_status,rsi_badge,rsi_icon="Oversold","bullish","🟢"
        else:          rsi_status,rsi_badge,rsi_icon="Neutral","neutral","🟡"
        macd_bullish = technical.get('macd_bullish')
        if macd_bullish is None: macd_bullish = bool(technical['macd'] > technical['signal'])
        if option_analysis:
            pcr = option_analysis['pcr_oi']
            if   pcr > 1.2: pcr_status,pcr_badge,pcr_icon="Bullish","bullish","🟢"
            elif pcr < 0.7: pcr_status,pcr_badge,pcr_icon="Bearish","bearish","🔴"
            else:           pcr_status,pcr_badge,pcr_icon="Neutral","neutral","🟡"
        else:
            pcr_status,pcr_badge,pcr_icon="N/A","neutral","🟡"
        if option_analysis:
            max_ce_strike=option_analysis['max_ce_oi_strike']; max_pe_strike=option_analysis['max_pe_oi_strike']
            atm_strike   =option_analysis['atm_strike']
        else:
            atm_strike=int(current/50)*50; max_ce_strike=atm_strike+200; max_pe_strike=atm_strike-200
        if bias == "BULLISH":
            mid=((support+resistance)/2); entry_low=current-100 if current>mid else current-50
            entry_high=current-50 if current>mid else current; target_1=resistance; target_2=max_ce_strike
            stop_loss=self.calculate_smart_stop_loss(current,support,resistance,"BULLISH")
        elif bias == "BEARISH":
            mid=((support+resistance)/2); entry_low=current
            entry_high=current+100 if current<mid else current+50; target_1=support; target_2=max_pe_strike
            stop_loss=self.calculate_smart_stop_loss(current,support,resistance,"BEARISH")
        else:
            entry_low=support; entry_high=resistance; target_1=resistance; target_2=support; stop_loss=None
        if stop_loss and bias != "SIDEWAYS":
            risk_points=abs(current-stop_loss); reward_points=abs(target_1-current)
            risk_reward_ratio=round(reward_points/risk_points,2) if risk_points>0 else 0
        else:
            risk_points=reward_points=risk_reward_ratio=0
        rsi_pct=min(100,max(0,rsi))
        def sma_bar(v): diff=(current-v)/v*100; return min(100,max(0,50+diff*10))
        macd_pct=min(100,max(0,50+technical['macd']*2))
        pcr_pct =min(100,max(0,(option_analysis['pcr_oi']/2*100))) if option_analysis else 50
        if option_analysis:
            rng=resistance-support if resistance!=support else 1
            mp_pct=min(100,max(0,(option_analysis['max_pain']-support)/rng*100))
            total_oi=option_analysis['total_ce_oi']+option_analysis['total_pe_oi']
            ce_oi_pct=min(100,max(0,option_analysis['total_ce_oi']/total_oi*100)) if total_oi>0 else 50
            pe_oi_pct=100-ce_oi_pct
        else:
            mp_pct=ce_oi_pct=pe_oi_pct=50
        fii_dii_raw  = fetch_fii_dii_data()
        fii_dii_summ = compute_fii_dii_summary(fii_dii_raw)
        self.html_data = {
            'timestamp':          ist_now.strftime('%d-%b-%Y %H:%M IST'),
            'current_price':      current,
            'expiry':             option_analysis['expiry'] if option_analysis else 'N/A',
            'atm_strike':         atm_strike,
            'bias':               bias, 'bias_icon': bias_icon, 'bias_class': bias_class,
            'confidence':         confidence,
            'bullish_score':      bullish_score, 'bearish_score': bearish_score,
            'rsi':                rsi, 'rsi_pct': rsi_pct, 'rsi_status': rsi_status,
            'rsi_badge':          rsi_badge, 'rsi_icon': rsi_icon,
            'sma_20':             technical['sma_20'], 'sma_20_above': current>technical['sma_20'], 'sma_20_pct': sma_bar(technical['sma_20']),
            'sma_50':             technical['sma_50'], 'sma_50_above': current>technical['sma_50'], 'sma_50_pct': sma_bar(technical['sma_50']),
            'sma_200':            technical['sma_200'],'sma_200_above':current>technical['sma_200'],'sma_200_pct':sma_bar(technical['sma_200']),
            'macd':               technical['macd'], 'macd_signal': technical['signal'],
            'macd_bullish':       macd_bullish, 'macd_pct': macd_pct,
            'pcr':                option_analysis['pcr_oi'] if option_analysis else 0,
            'pcr_pct':            pcr_pct, 'pcr_status': pcr_status,
            'pcr_badge':          pcr_badge, 'pcr_icon': pcr_icon,
            'max_pain':           option_analysis['max_pain'] if option_analysis else 0, 'max_pain_pct': mp_pct,
            'max_ce_oi':          max_ce_strike, 'max_pe_oi': max_pe_strike,
            'ce_oi_pct':          ce_oi_pct, 'pe_oi_pct': pe_oi_pct,
            'total_ce_oi_change': option_analysis['total_ce_oi_change'] if option_analysis else 0,
            'total_pe_oi_change': option_analysis['total_pe_oi_change'] if option_analysis else 0,
            'net_oi_change':      option_analysis['net_oi_change'] if option_analysis else 0,
            'oi_direction':       option_analysis['oi_direction'] if option_analysis else 'N/A',
            'oi_signal':          option_analysis['oi_signal']    if option_analysis else 'N/A',
            'oi_icon':            option_analysis['oi_icon']      if option_analysis else '🟡',
            'oi_class':           option_analysis['oi_class']     if option_analysis else 'neutral',
            'support':            support, 'resistance': resistance,
            'strong_support':     technical['strong_support'],
            'strong_resistance':  technical['strong_resistance'],
            'strategy_type':      bias, 'entry_low': entry_low, 'entry_high': entry_high,
            'target_1':           target_1, 'target_2': target_2, 'stop_loss': stop_loss,
            'risk_points':        int(risk_points), 'reward_points': int(reward_points),
            'risk_reward_ratio':  risk_reward_ratio,
            'has_option_data':    option_analysis is not None,
            'fii_dii_data':       fii_dii_raw, 'fii_dii_summ': fii_dii_summ,
        }

    # ─────────────────────────────────────────────────────────────────────────
    #  STAT CARD
    # ─────────────────────────────────────────────────────────────────────────
    def _stat_card(self, icon, label, value, badge_text, badge_class, bar_pct, bar_type, sub_text=""):
        tag_map = {
            'bullish': ('tag-bull','var(--accent)'),
            'bearish': ('tag-bear','var(--neg)'),
            'neutral': ('tag-neu', 'var(--neu)'),
        }
        tag_cls, _ = tag_map.get(badge_class, tag_map['neutral'])
        hi_cls     = 'g-hi' if badge_class == 'bullish' else ('g-red' if badge_class == 'bearish' else '')
        sub_html   = f'<div class="sub">{sub_text}</div>' if sub_text else ''
        return f"""
            <div class="g {hi_cls}">
                <div class="card-top-row">
                    <span class="card-ico">{icon}</span>
                    <div class="lbl">{label}</div>
                </div>
                <span class="val">{value}</span>
                <div class="bar-wrap"><div class="bar-fill {bar_type}" style="width:{bar_pct:.1f}%"></div></div>
                <div class="card-foot">
                    {sub_html}
                    <span class="tag {tag_cls}">{badge_text}</span>
                </div>
            </div>"""

    # ─────────────────────────────────────────────────────────────────────────
    #  MARKET DIRECTION WIDGET
    # ─────────────────────────────────────────────────────────────────────────
    def _market_direction_widget_html(self):
        d = self.html_data
        bias       = d['bias']
        confidence = d['confidence']
        bull_score = d['bullish_score']
        bear_score = d['bearish_score']
        if   bias == 'BULLISH':  dir_gradient = 'linear-gradient(135deg,var(--accent),var(--accent2))'
        elif bias == 'BEARISH':  dir_gradient = 'linear-gradient(135deg,var(--neg),#dc2626)'
        else:                    dir_gradient = 'linear-gradient(135deg,var(--neu),#f59e0b)'
        bull_pill  = f'<span class="md-pill md-pill-bull">BULL {bull_score}</span>'
        bear_pill  = f'<span class="md-pill md-pill-bear">BEAR {bear_score}</span>'
        conf_cls   = ('md-pill-conf-high' if confidence=='HIGH' else
                      'md-pill-conf-med'  if confidence=='MEDIUM' else 'md-pill-conf-low')
        conf_pill  = f'<span class="md-pill {conf_cls}">{confidence} CONFIDENCE</span>'
        return f"""
    <div class="section">
        <div class="section-title"><span>🧭</span> MARKET DIRECTION (Algorithmic)</div>
        <div class="md-widget">
            <div class="md-glow"></div>
            <div class="md-row-top">
                <div class="md-label"><div class="md-live-dot"></div>MARKET DIRECTION &nbsp;·&nbsp; ALGORITHMIC</div>
                <div class="md-pills-top">{bull_pill}{bear_pill}</div>
            </div>
            <div class="md-row-bottom">
                <div class="md-direction" style="background:{dir_gradient};-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">{bias}</div>
                {conf_pill}
            </div>
        </div>
        <div class="logic-box" style="margin-top:14px;">
            <div class="logic-box-head">📊 SCORING LOGIC</div>
            <div class="logic-grid">
                <div class="logic-item"><span class="lc-bull">BULLISH</span><span class="lv">Diff ≥ +3</span> · Above SMAs, oversold RSI, +MACD, PCR &gt; 1.2</div>
                <div class="logic-item"><span class="lc-bear">BEARISH</span><span class="lv">Diff ≤ −3</span> · Below SMAs, overbought RSI, −MACD, PCR &lt; 0.7</div>
                <div class="logic-item"><span class="lc-side">SIDEWAYS</span><span class="lv">Diff −2 to +2</span> · Mixed signals, consolidation</div>
                <div class="logic-item"><span class="lc-info">CONFIDENCE</span> HIGH when gap ≥ 4 &nbsp;·&nbsp; OI scope: ATM ±10 only</div>
            </div>
        </div>
    </div>"""

    # ─────────────────────────────────────────────────────────────────────────
    #  FII/DII SECTION — Slate Teal Pulse Flow
    # ─────────────────────────────────────────────────────────────────────────
    def _fiidii_section_html(self):
        data = self.html_data['fii_dii_data']
        summ = self.html_data['fii_dii_summ']
        badge_map = {
            'fii-bull':  ('var(--pos)',  'var(--pos-bg)',  'var(--pos-border)'),
            'fii-cbull': ('var(--accent)','var(--accent-glow)','var(--border2)'),
            'fii-neu':   ('var(--neu)',  'var(--neu-bg)',  'var(--neu-border)'),
            'fii-bear':  ('var(--neg)',  'var(--neg-bg)',  'var(--neg-border)'),
        }
        s_color,s_bg,s_border = badge_map.get(summ['badge_cls'], badge_map['fii-neu'])
        is_fallback  = any(r.get('fallback') for r in data)
        date_range   = f"{data[0]['date']} – {data[-1]['date']}" if data else ''
        data_src_html = ('<span class="pf-live-badge pf-estimated">⚠ ESTIMATED</span>'
                         if is_fallback else
                         '<span class="pf-live-badge pf-live">● LIVE</span>')
        max_abs = summ['max_abs'] or 1

        def day_card(row):
            fii_v=row['fii']; dii_v=row['dii']; net_v=fii_v+dii_v
            fii_w=round(min(100,abs(fii_v)/max_abs*100),1)
            dii_w=round(min(100,abs(dii_v)/max_abs*100),1)
            fii_col = 'var(--accent2)' if fii_v>=0 else 'var(--neg)'
            fii_bar = 'linear-gradient(90deg,#38bdf8,#0ea5e9)' if fii_v>=0 else 'linear-gradient(90deg,#f87171,#ef4444)'
            dii_col = 'var(--accent)'  if dii_v>=0 else 'var(--neg)'
            dii_bar = 'linear-gradient(90deg,#2dd4bf,#0d9488)' if dii_v>=0 else 'linear-gradient(90deg,#f87171,#ef4444)'
            net_col = 'var(--pos)' if net_v>=0 else 'var(--neg)'
            fii_s='+' if fii_v>=0 else ''; dii_s='+' if dii_v>=0 else ''; net_s='+' if net_v>=0 else ''
            bdr = 'rgba(45,212,191,0.18)' if net_v>=0 else 'rgba(248,113,113,0.18)'
            topL= 'linear-gradient(90deg,transparent,#2dd4bf,transparent)' if net_v>=0 else 'linear-gradient(90deg,transparent,#f87171,transparent)'
            return (f'<div class="pf-card" style="border-color:{bdr};">'
                    f'<div class="pf-card-topline" style="background:{topL};"></div>'
                    f'<div class="pf-card-head"><span class="pf-card-date">{row["date"]}</span><span class="pf-card-day">{row["day"]}</span></div>'
                    f'<div class="pf-block"><div class="pf-block-header"><span class="pf-block-lbl pf-fii-lbl">FII</span><span class="pf-block-val" style="color:{fii_col};">{fii_s}{fii_v:,.0f}</span></div>'
                    f'<div class="pf-bar-track"><div class="pf-bar-fill" style="width:{fii_w}%;background:{fii_bar};"></div></div></div>'
                    f'<div class="pf-divider"></div>'
                    f'<div class="pf-block"><div class="pf-block-header"><span class="pf-block-lbl pf-dii-lbl">DII</span><span class="pf-block-val" style="color:{dii_col};">{dii_s}{dii_v:,.0f}</span></div>'
                    f'<div class="pf-bar-track"><div class="pf-bar-fill" style="width:{dii_w}%;background:{dii_bar};"></div></div></div>'
                    f'<div class="pf-card-net"><span class="pf-net-lbl">NET</span><span class="pf-net-val" style="color:{net_col};">{net_s}{net_v:,.0f}</span></div></div>')

        cards_html  = ''.join(day_card(r) for r in data)
        fa=summ['fii_avg']; da=summ['dii_avg']; na=summ['net_avg']
        fs='+' if fa>=0 else ''; ds='+' if da>=0 else ''; ns='+' if na>=0 else ''
        fc='var(--accent2)' if fa>=0 else 'var(--neg)'
        dc='var(--accent)'  if da>=0 else 'var(--neg)'
        nc='var(--accent2)' if na>=0 else 'var(--neg)'
        verdict_badge = (f'<span class="pf-verdict-badge" style="color:{s_color};background:{s_bg};border:1px solid {s_border};">'
                         f'{summ["emoji"]} {summ["label"]}</span>')
        return (
            '\n<div class="section">\n'
            '    <div class="section-title">\n'
            f'        <span>🏦</span> FII / DII INSTITUTIONAL FLOW\n'
            f'        {data_src_html}\n'
            f'        <span class="pf-date-range">Last 5 Trading Days &nbsp;·&nbsp; {date_range}</span>\n'
            '    </div>\n'
            f'    <div class="pf-grid">{cards_html}</div>\n'
            '    <div class="pf-avg-strip">\n'
            f'        <div class="pf-avg-cell"><div class="pf-avg-eyebrow">FII 5D Avg</div><div class="pf-avg-val" style="color:{fc};">{fs}{fa:,.0f}</div><div class="pf-avg-unit">₹ Cr / day</div></div>\n'
            '        <div class="pf-avg-sep"></div>\n'
            f'        <div class="pf-avg-cell"><div class="pf-avg-eyebrow">DII 5D Avg</div><div class="pf-avg-val" style="color:{dc};">{ds}{da:,.0f}</div><div class="pf-avg-unit">₹ Cr / day</div></div>\n'
            '        <div class="pf-avg-sep"></div>\n'
            f'        <div class="pf-avg-cell"><div class="pf-avg-eyebrow">Net Combined</div><div class="pf-avg-val" style="color:{nc};">{ns}{na:,.0f}</div><div class="pf-avg-unit">₹ Cr / day</div></div>\n'
            '    </div>\n'
            f'    <div class="pf-insight-box" style="background:{s_bg};border:1px solid {s_border};">\n'
            f'        <div class="pf-insight-header"><span class="pf-insight-lbl" style="color:{s_color};">📊 5-DAY INSIGHT &amp; DIRECTION</span>{verdict_badge}</div>\n'
            f'        <div class="pf-insight-text">{summ["insight"]}</div>\n'
            '    </div>\n'
            '</div>\n'
        )

    # ─────────────────────────────────────────────────────────────────────────
    #  OI COMMAND SECTION — Slate Teal palette
    # ─────────────────────────────────────────────────────────────────────────
    def _oi_command_section(self, d):
        oi_cls    = d['oi_class']
        direction = d['oi_direction']
        signal    = d['oi_signal']
        ce_raw    = d['total_ce_oi_change']
        pe_raw    = d['total_pe_oi_change']
        bull_force = 0; bear_force = 0
        if ce_raw < 0: bull_force += abs(ce_raw)
        else:          bear_force += abs(ce_raw)
        if pe_raw > 0: bull_force += abs(pe_raw)
        else:          bear_force += abs(pe_raw)
        total_force = bull_force + bear_force
        bull_pct    = round(bull_force / total_force * 100) if total_force > 0 else 50
        bear_pct    = 100 - bull_pct

        if oi_cls == 'bearish':
            dir_bg='rgba(248,113,113,0.06)'; dir_border='var(--neg-border)'
            dir_bar='linear-gradient(180deg,var(--neg),#dc2626)'
            dir_name_col='var(--neg)'; dir_desc_col='rgba(248,113,113,0.5)'
        elif oi_cls == 'bullish':
            dir_bg='rgba(45,212,191,0.06)'; dir_border='var(--border2)'
            dir_bar='linear-gradient(180deg,var(--accent),#0d9488)'
            dir_name_col='var(--accent)'; dir_desc_col='rgba(45,212,191,0.5)'
        else:
            dir_bg='rgba(251,191,36,0.05)'; dir_border='var(--neu-border)'
            dir_bar='linear-gradient(180deg,var(--neu),#d97706)'
            dir_name_col='var(--neu)'; dir_desc_col='rgba(251,191,36,0.5)'

        ce_val=d['total_ce_oi_change']; pe_val=d['total_pe_oi_change']; net_val=d['net_oi_change']
        ce_is_bear=ce_val>0; pe_is_bull=pe_val>0
        ce_col=  'var(--neg)'    if ce_is_bear else 'var(--pos)'
        ce_dot=  'var(--neg)'    if ce_is_bear else 'var(--accent)'
        ce_lbl=  'Bearish Signal' if ce_is_bear else 'Bullish Signal'
        ce_btn_col=  'var(--neg)' if ce_is_bear else 'var(--accent)'
        ce_btn_bg=   'var(--neg-bg)' if ce_is_bear else 'var(--accent-glow)'
        ce_btn_bdr=  'var(--neg-border)' if ce_is_bear else 'var(--border2)'
        pe_col=  'var(--pos)'    if pe_is_bull else 'var(--neg)'
        pe_dot=  'var(--accent)' if pe_is_bull else 'var(--neg)'
        pe_lbl=  'Bullish Signal' if pe_is_bull else 'Bearish Signal'
        pe_btn_col=  'var(--accent)' if pe_is_bull else 'var(--neg)'
        pe_btn_bg=   'var(--accent-glow)' if pe_is_bull else 'var(--neg-bg)'
        pe_btn_bdr=  'var(--border2)' if pe_is_bull else 'var(--neg-border)'
        if net_val > 0:
            net_col='var(--pos)'; net_dot='var(--accent)'; net_lbl='Bullish Net'
            net_btn_col='var(--accent)'; net_btn_bg='var(--accent-glow)'; net_btn_bdr='var(--border2)'
        elif net_val < 0:
            net_col='var(--neg)'; net_dot='var(--neg)'; net_lbl='Bearish Net'
            net_btn_col='var(--neg)'; net_btn_bg='var(--neg-bg)'; net_btn_bdr='var(--neg-border)'
        else:
            net_col='var(--neu)'; net_dot='var(--neu)'; net_lbl='Balanced'
            net_btn_col='var(--neu)'; net_btn_bg='var(--neu-bg)'; net_btn_bdr='var(--neu-border)'

        def nc_card(label,idc,value,val_col,sub,btn_lbl,btn_col,btn_bg,btn_bdr,icon_char):
            return (f'<div class="nc-card"><div class="nc-card-header">'
                    f'<span class="nc-card-label">{label}</span>'
                    f'<span style="font-size:18px;line-height:1;color:{idc};">{icon_char}</span></div>'
                    f'<div class="nc-card-value" style="color:{val_col};">{value:+,}</div>'
                    f'<div class="nc-card-sub">{sub}</div>'
                    f'<div class="nc-card-btn" style="color:{btn_col};background:{btn_bg};border:1px solid {btn_bdr};">{btn_lbl}</div></div>')

        cards_html = (
            nc_card('CALL OI CHANGE',ce_dot,ce_val,ce_col,'CE open interest Δ',ce_lbl,ce_btn_col,ce_btn_bg,ce_btn_bdr,'🔴' if ce_is_bear else '🟢') +
            nc_card('PUT OI CHANGE', pe_dot,pe_val,pe_col,'PE open interest Δ',pe_lbl,pe_btn_col,pe_btn_bg,pe_btn_bdr,'🟢' if pe_is_bull else '🔴') +
            nc_card('NET OI CHANGE', net_dot,net_val,net_col,'PE Δ − CE Δ',net_lbl,net_btn_col,net_btn_bg,net_btn_bdr,'⚖️')
        )
        dual_meters = (
            f'<div class="nc-meters-panel">'
            f'<div class="nc-meter-row"><div class="nc-meter-head-row"><span class="nc-meter-label">🟢 Bull Strength</span><span class="nc-meter-pct" style="color:var(--accent);">{bull_pct}%</span></div>'
            f'<div class="nc-meter-track"><div class="nc-meter-fill" style="width:{bull_pct}%;background:linear-gradient(90deg,var(--accent),var(--accent2));"></div>'
            f'<div class="nc-meter-head" style="left:{bull_pct}%;background:var(--accent);box-shadow:0 0 8px var(--accent);"></div></div></div>'
            f'<div class="nc-meter-row"><div class="nc-meter-head-row"><span class="nc-meter-label">🔴 Bear Strength</span><span class="nc-meter-pct" style="color:var(--neg);">{bear_pct}%</span></div>'
            f'<div class="nc-meter-track"><div class="nc-meter-fill" style="width:{bear_pct}%;background:linear-gradient(90deg,var(--neg),#f97316);"></div>'
            f'<div class="nc-meter-head" style="left:{bear_pct}%;background:var(--neg);box-shadow:0 0 8px var(--neg);"></div></div></div></div>'
        )
        return (
            '\n<div class="section">\n'
            '    <div class="nc-section-header">\n'
            '        <div class="nc-header-left"><div class="nc-header-icon">📊</div>\n'
            '        <div><div class="nc-header-title">Change in Open Interest</div>\n'
            '        <div class="nc-header-sub">Today\'s Direction Analysis</div></div></div>\n'
            '        <div class="nc-atm-badge">ATM ±10</div>\n'
            '    </div>\n'
            f'    <div class="nc-dir-box" style="background:{dir_bg};border:1px solid {dir_border};">\n'
            '        <div style="display:flex;align-items:stretch;gap:18px;">\n'
            f'            <div class="nc-dir-bar" style="background:{dir_bar};"></div>\n'
            '            <div style="flex:1;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;">\n'
            '                <div>\n'
            '                    <div class="nc-dir-tag">MARKET DIRECTION</div>\n'
            f'                    <div class="nc-dir-name" style="color:{dir_name_col};">{direction}</div>\n'
            f'                    <div class="nc-dir-signal" style="color:{dir_desc_col};">{signal}</div>\n'
            '                </div>\n'
            f'                {dual_meters}\n'
            '            </div>\n'
            '        </div>\n'
            '    </div>\n'
            f'    <div class="nc-cards-grid">{cards_html}</div>\n'
            '    <div class="logic-box" style="margin-top:16px;">\n'
            '        <div class="logic-box-head">📖 HOW TO READ</div>\n'
            '        <div class="logic-grid">\n'
            '            <div class="logic-item"><span class="lc-info">Call OI +</span> Writers selling calls <span class="lc-bear">Bearish</span> &nbsp; <span class="lc-info">Call OI −</span> Unwinding <span class="lc-bull">Bullish</span></div>\n'
            '            <div class="logic-item"><span class="lc-info">Put OI +</span> Writers selling puts <span class="lc-bull">Bullish</span> &nbsp; <span class="lc-info">Put OI −</span> Unwinding <span class="lc-bear">Bearish</span></div>\n'
            '            <div class="logic-item"><span class="lc-info">Net OI</span> = PE Δ − CE Δ &nbsp;·&nbsp; <span class="lc-bull">Positive = Bullish</span> &nbsp; <span class="lc-bear">Negative = Bearish</span></div>\n'
            '            <div class="logic-item"><span class="lc-info">Bull % + Bear %</span> = 100% &nbsp;·&nbsp; relative dominance</div>\n'
            '        </div>\n'
            '    </div>\n'
            '</div>\n'
        )

    # ─────────────────────────────────────────────────────────────────────────
    #  KEY LEVELS SECTION
    # ─────────────────────────────────────────────────────────────────────────
    def _key_levels_section(self, d, _pct_cp, _pts_to_res, _pts_to_sup, _mp_node):
        return f"""
    <div class="section">
        <div class="section-title"><span>📊</span> KEY LEVELS</div>
        <div style="display:flex;justify-content:space-between;margin-bottom:8px;">
            <span style="font-size:11px;color:var(--accent);font-weight:700;letter-spacing:1px;">◀ SUPPORT ZONE</span>
            <span style="font-size:11px;color:var(--neg);font-weight:700;letter-spacing:1px;">RESISTANCE ZONE ▶</span>
        </div>
        <div style="position:relative;height:62px;">
            <div class="rl-node-a" style="left:3%;"><div class="rl-lbl" style="color:var(--accent);">Strong<br>Support</div><div class="rl-val" style="color:var(--accent);">₹{d['strong_support']:,.0f}</div><div class="rl-dot" style="background:var(--accent);margin:6px auto 0;"></div></div>
            <div class="rl-node-a" style="left:22%;"><div class="rl-lbl" style="color:var(--accent2);">Support</div><div class="rl-val" style="color:var(--accent2);">₹{d['support']:,.0f}</div><div class="rl-dot" style="background:var(--accent2);box-shadow:0 0 8px var(--accent2);margin:6px auto 0;"></div></div>
            <div style="position:absolute;left:{_pct_cp}%;transform:translateX(-50%);bottom:4px;background:var(--accent2);color:#0f172a;font-size:11px;font-weight:700;padding:4px 13px;border-radius:6px;white-space:nowrap;z-index:10;box-shadow:0 0 16px rgba(56,189,248,0.5);">▼ NOW &nbsp;₹{d['current_price']:,.0f}</div>
            <div class="rl-node-a" style="left:75%;"><div class="rl-lbl" style="color:#fb923c;">Resistance</div><div class="rl-val" style="color:#fb923c;">₹{d['resistance']:,.0f}</div><div class="rl-dot" style="background:#fb923c;box-shadow:0 0 8px #fb923c;margin:6px auto 0;"></div></div>
            <div class="rl-node-a" style="left:95%;"><div class="rl-lbl" style="color:var(--neg);">Strong<br>Resistance</div><div class="rl-val" style="color:var(--neg);">₹{d['strong_resistance']:,.0f}</div><div class="rl-dot" style="background:var(--neg);margin:6px auto 0;"></div></div>
        </div>
        <div style="position:relative;height:8px;border-radius:4px;background:linear-gradient(90deg,var(--accent) 0%,var(--accent2) 20%,#60a5fa 40%,#fb923c 58%,var(--neg) 100%);box-shadow:0 2px 14px rgba(0,0,0,0.4);">
            <div style="position:absolute;left:{_pct_cp}%;top:50%;transform:translate(-50%,-50%);width:4px;height:22px;background:var(--text);border-radius:2px;box-shadow:0 0 16px rgba(255,255,255,0.8);z-index:10;"></div>
        </div>
        <div style="position:relative;height:58px;">{_mp_node}</div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:4px;">
            <div style="background:var(--neg-bg);border:1px solid var(--neg-border);border-radius:var(--radius-sm);padding:10px 16px;display:flex;justify-content:space-between;align-items:center;">
                <span style="font-size:12px;color:var(--muted);">📍 Distance to Resistance</span>
                <span style="font-size:15px;font-weight:700;color:var(--neg);">+{_pts_to_res:,} pts</span>
            </div>
            <div style="background:var(--info-bg);border:1px solid var(--info-border);border-radius:var(--radius-sm);padding:10px 16px;display:flex;justify-content:space-between;align-items:center;">
                <span style="font-size:12px;color:var(--muted);">📍 Distance to Support</span>
                <span style="font-size:15px;font-weight:700;color:var(--accent2);">−{_pts_to_sup:,} pts</span>
            </div>
        </div>
    </div>"""

    # ─────────────────────────────────────────────────────────────────────────
    #  FULL HTML GENERATOR — Slate Teal Theme
    # ─────────────────────────────────────────────────────────────────────────
    def generate_html_email(self, vol_support=None, vol_resistance=None,
                             global_bias=None, vol_view="normal", india_vix=None):
        d = self.html_data

        # bar / badge helpers
        sma20_bar   = 'bar-teal' if d['sma_20_above']  else 'bar-red'
        sma50_bar   = 'bar-teal' if d['sma_50_above']  else 'bar-red'
        sma200_bar  = 'bar-teal' if d['sma_200_above'] else 'bar-red'
        macd_bar    = 'bar-teal' if d['macd_bullish']  else 'bar-red'
        pcr_bar     = 'bar-teal' if d['pcr_badge'] == 'bullish' else ('bar-red' if d['pcr_badge']=='bearish' else 'bar-gold')
        sma20_badge  = 'bullish' if d['sma_20_above']  else 'bearish'
        sma50_badge  = 'bullish' if d['sma_50_above']  else 'bearish'
        sma200_badge = 'bullish' if d['sma_200_above'] else 'bearish'
        macd_badge   = 'bullish' if d['macd_bullish']  else 'bearish'
        sma20_lbl    = 'Above'  if d['sma_20_above']  else 'Below'
        sma50_lbl    = 'Above'  if d['sma_50_above']  else 'Below'
        sma200_lbl   = 'Above'  if d['sma_200_above'] else 'Below'
        macd_lbl     = 'Bullish' if d['macd_bullish']  else 'Bearish'
        sma20_ico    = '✅' if d['sma_20_above']  else '❌'
        sma50_ico    = '✅' if d['sma_50_above']  else '❌'
        sma200_ico   = '✅' if d['sma_200_above'] else '❌'
        macd_ico     = '🟢' if d['macd_bullish']  else '🔴'

        tech_cards = (
            self._stat_card(d['rsi_icon'],'RSI (14)',    f"{d['rsi']:.1f}",         d['rsi_status'], d['rsi_badge'], d['rsi_pct'], 'bar-gold', '14-period momentum') +
            self._stat_card(sma20_ico,   'SMA 20',      f"₹{d['sma_20']:,.0f}",    sma20_lbl,  sma20_badge,  d['sma_20_pct'],  sma20_bar,  '20-day average') +
            self._stat_card(sma50_ico,   'SMA 50',      f"₹{d['sma_50']:,.0f}",    sma50_lbl,  sma50_badge,  d['sma_50_pct'],  sma50_bar,  '50-day average') +
            self._stat_card(sma200_ico,  'SMA 200',     f"₹{d['sma_200']:,.0f}",   sma200_lbl, sma200_badge, d['sma_200_pct'], sma200_bar, '200-day average') +
            self._stat_card(macd_ico,    'MACD',        f"{d['macd']:.2f}",        macd_lbl,   macd_badge,   d['macd_pct'],    macd_bar,   f"Signal: {d['macd_signal']:.2f}")
        )
        if d['has_option_data']:
            oc_cards = (
                self._stat_card(d['pcr_icon'],'PCR Ratio (OI)', f"{d['pcr']:.3f}",   d['pcr_status'], d['pcr_badge'], d['pcr_pct'],     pcr_bar,    'Put/Call OI ratio') +
                self._stat_card('🎯',         'Max Pain',       f"₹{d['max_pain']:,}",'Expiry Magnet', 'neutral',     d['max_pain_pct'],'bar-gold',  'Price gravity level') +
                self._stat_card('🔴',         'Max Call OI',    f"₹{d['max_ce_oi']:,}",'Resistance',   'bearish',     d['ce_oi_pct'],   'bar-red',   'CE wall') +
                self._stat_card('🟢',         'Max Put OI',     f"₹{d['max_pe_oi']:,}",'Support',      'bullish',     d['pe_oi_pct'],   'bar-teal',  'PE floor')
            )
        else:
            oc_cards = '<div style="color:var(--accent);padding:20px;">Option chain data unavailable</div>'

        # key level helpers
        _ss  = d['strong_support']; _sr = d['strong_resistance']
        _rng = _sr - _ss if _sr != _ss else 1
        def _pct_real(val): return round(max(3, min(97, (val - _ss) / _rng * 100)), 2)
        _pct_cp      = _pct_real(d['current_price'])
        _pts_to_res  = int(d['resistance'] - d['current_price'])
        _pts_to_sup  = int(d['current_price'] - d['support'])
        _mp_node     = ""
        if d['has_option_data']:
            _mp_node = (f'<div class="rl-node-b" style="left:43%;">'
                        f'<div class="rl-dot" style="background:var(--neu);box-shadow:0 0 8px var(--neu);margin:0 auto 5px;"></div>'
                        f'<div class="rl-lbl" style="color:var(--neu);">Max Pain</div>'
                        f'<div class="rl-val" style="color:var(--neu);">₹{d["max_pain"]:,}</div></div>')

        checklist_tab_html = build_strategy_checklist_html(
            d, vol_support=vol_support, vol_resistance=vol_resistance,
            global_bias=global_bias, vol_view=vol_view, india_vix=india_vix,
        )

        auto_refresh_js = """
    <script>
    (function(){
        var INTERVAL=30000, countdown=30;
        function istNow(){return new Date(new Date().toLocaleString('en-US',{timeZone:'Asia/Kolkata'}));}
        function pad(n){return String(n).padStart(2,'0');}
        function fmtTime(d){return pad(d.getHours())+':'+pad(d.getMinutes())+':'+pad(d.getSeconds());}
        function fmtDate(d){var M=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];return pad(d.getDate())+'-'+M[d.getMonth()]+'-'+d.getFullYear();}
        function tick(){
            var now=istNow();
            var clk=document.getElementById('live-ist-clock');
            if(clk) clk.textContent=fmtDate(now)+'  '+fmtTime(now)+' IST';
            countdown--;
            if(countdown<0) countdown=INTERVAL/1000;
            var cd=document.getElementById('refresh-countdown');
            if(cd){var s=countdown%60;var m=Math.floor(countdown/60);cd.textContent=(m>0?m+'m ':'')+s+'s';}
        }
        setInterval(tick,1000); tick();
        function silentRefresh(){
            fetch(window.location.href+'?_t='+Date.now(),{cache:'no-store'})
                .then(function(r){return r.text();})
                .then(function(html){
                    var p=new DOMParser();var newDoc=p.parseFromString(html,'text/html');
                    var nc=newDoc.querySelector('.container');var oc=document.querySelector('.container');
                    if(!nc||!oc) return;
                    var sy=window.scrollY||window.pageYOffset;
                    var at=document.querySelector('.tab-btn.active');
                    var atid=at?at.dataset.tab:'main';
                    oc.innerHTML=nc.innerHTML;
                    window.scrollTo({top:sy,behavior:'instant'});
                    switchTab(atid);
                    var now=istNow();
                    var el=document.getElementById('last-updated');
                    if(el) el.textContent=fmtDate(now)+'  '+fmtTime(now)+' IST';
                    countdown=INTERVAL/1000;
                })
                .catch(function(e){console.warn('Refresh failed:',e);});
        }
        setInterval(silentRefresh,INTERVAL);
    })();
    function switchTab(tab){
        document.querySelectorAll('.tab-panel').forEach(function(p){p.classList.remove('active');});
        document.querySelectorAll('.tab-btn').forEach(function(b){b.classList.remove('active');});
        var panel=document.getElementById('tab-'+tab);
        var btn=document.querySelector('[data-tab="'+tab+'"]');
        if(panel) panel.classList.add('active');
        if(btn)   btn.classList.add('active');
    }
    function filterStrats(type,btn){
        document.querySelectorAll('.filter-btn').forEach(function(b){b.classList.remove('active');});
        btn.classList.add('active');
        document.querySelectorAll('.strat-card').forEach(function(c){
            c.style.display=(type==='all'||c.dataset.type===type)?'':'none';
        });
    }
    </script>"""

        # ── Bias direction colors for Market Direction widget
        if   d['bias'] == 'BULLISH':  bias_color = 'var(--accent)'
        elif d['bias'] == 'BEARISH':  bias_color = 'var(--neg)'
        else:                         bias_color = 'var(--neu)'

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nifty 50 Daily Report — Slate Teal</title>
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Syne:wght@700;800&family=JetBrains+Mono:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        /* ══════════════════════════════════════════
           SLATE TEAL THEME — CSS VARIABLES
        ══════════════════════════════════════════ */
        :root {{{THEME_CSS_VARS}}}

        *{{margin:0;padding:0;box-sizing:border-box;}}
        html{{scroll-behavior:smooth;}}
        body{{
            font-family:'Space Grotesk',sans-serif;
            background:var(--bg);
            min-height:100vh;
            padding:clamp(8px,2vw,24px);
            color:var(--text);
            overflow-x:hidden;
            -webkit-text-size-adjust:100%;
        }}

        /* ── TABS ── */
        .tab-nav{{display:flex;gap:0;border-bottom:2px solid var(--border);overflow-x:auto;scrollbar-width:none;background:var(--surface);}}
        .tab-nav::-webkit-scrollbar{{display:none;}}
        .tab-btn{{display:flex;align-items:center;gap:8px;padding:13px clamp(14px,2.5vw,28px);font-family:'Space Grotesk',sans-serif;font-size:clamp(10px,1.4vw,13px);font-weight:700;letter-spacing:1.5px;text-transform:uppercase;color:var(--muted);cursor:pointer;border:none;background:transparent;border-bottom:3px solid transparent;white-space:nowrap;transition:all 0.25s ease;position:relative;bottom:-2px;}}
        .tab-btn:hover{{color:var(--accent);background:var(--accent-glow);}}
        .tab-btn.active{{color:var(--accent);border-bottom-color:var(--accent);background:var(--accent-glow);}}
        .tab-dot{{width:7px;height:7px;border-radius:50%;background:var(--muted2);flex-shrink:0;transition:all 0.25s;}}
        .tab-btn.active .tab-dot{{background:var(--accent);box-shadow:0 0 8px var(--accent);}}
        .tab-badge{{font-size:9px;padding:2px 7px;border-radius:10px;background:var(--accent-glow);border:1px solid var(--border2);color:var(--accent);}}
        .tab-panel{{display:none;}} .tab-panel.active{{display:block;}}

        /* ── CONTAINER ── */
        .container{{max-width:100%;margin:0 auto;background:var(--surface);border-radius:var(--radius-lg);overflow:hidden;box-shadow:var(--shadow-card);border:1px solid var(--border);min-width:0;}}

        /* ── HEADER ── */
        .header{{background:var(--grad-header);padding:clamp(16px,3vw,28px) clamp(14px,3vw,30px) 0;position:relative;overflow:hidden;}}
        .header::before{{content:'';position:absolute;inset:0;background:radial-gradient(circle at 50% 50%,var(--accent-glow) 0%,transparent 70%);pointer-events:none;}}
        .header h1{{font-family:'Syne',sans-serif;font-size:clamp(16px,3.5vw,28px);font-weight:800;color:var(--accent);text-shadow:0 0 30px var(--accent-glow);letter-spacing:clamp(0.5px,0.3vw,2px);position:relative;z-index:1;word-break:break-word;margin-bottom:clamp(10px,2vw,18px);}}

        /* ── STATUS BAR ── */
        .status-bar{{display:flex;align-items:center;justify-content:center;flex-wrap:wrap;gap:0;background:rgba(0,0,0,0.25);border:1px solid var(--border);border-radius:10px;padding:0;overflow:hidden;position:relative;z-index:1;margin-bottom:16px;}}
        .sb-item{{display:flex;align-items:center;gap:8px;padding:10px clamp(10px,2vw,20px);flex:1 1 auto;min-width:0;border-right:1px solid var(--border);white-space:nowrap;}}
        .sb-item:last-child{{border-right:none;}}
        .sb-dot{{width:8px;height:8px;border-radius:50%;flex-shrink:0;}}
        .sb-dot-gen{{background:var(--pos);box-shadow:0 0 8px var(--pos);}}
        .sb-dot-clock{{background:var(--accent);box-shadow:0 0 8px var(--accent);}}
        .sb-dot-updated{{background:var(--neu);box-shadow:0 0 8px var(--neu);animation:sbpulse 2s ease-in-out infinite;}}
        .sb-dot-cd{{background:var(--accent2);box-shadow:0 0 8px var(--accent2);}}
        @keyframes sbpulse{{50%{{opacity:0.2;}}}}
        .sb-label{{font-family:'JetBrains Mono',monospace;font-size:clamp(8px,1vw,9px);letter-spacing:1.8px;text-transform:uppercase;color:var(--muted2);flex-shrink:0;}}
        .sb-value{{font-family:'JetBrains Mono',monospace;font-size:clamp(10px,1.3vw,12px);font-weight:700;color:var(--text);overflow:hidden;text-overflow:ellipsis;}}
        .sb-value.gen-val{{color:var(--muted);}}
        .sb-value.clock-val{{color:var(--accent);font-size:clamp(11px,1.5vw,13px);}}
        .sb-value.updated-val{{color:var(--neu);}}
        .sb-value.cd-val{{color:var(--accent2);min-width:28px;}}

        /* ── SECTIONS ── */
        .section{{padding:clamp(14px,2.5vw,28px) clamp(12px,2.5vw,26px);border-bottom:1px solid var(--border);}}
        .section:last-child{{border-bottom:none;}}
        .section-title{{font-family:'Syne',sans-serif;font-size:clamp(10px,1.5vw,13px);font-weight:700;letter-spacing:clamp(1px,0.3vw,2.5px);color:var(--accent);text-transform:uppercase;display:flex;align-items:center;gap:10px;margin-bottom:clamp(12px,2vw,20px);padding-bottom:12px;border-bottom:1px solid var(--border);flex-wrap:wrap;}}

        /* ── STAT CARDS ── */
        .g{{background:var(--surface2);border:1px solid var(--border);border-radius:var(--radius-card);position:relative;overflow:hidden;transition:all 0.3s cubic-bezier(0.4,0,0.2,1);min-width:0;}}
        .g::before{{content:'';position:absolute;top:0;left:0;right:0;height:2px;background:linear-gradient(90deg,transparent,var(--accent),transparent);opacity:0.5;z-index:1;}}
        .g:hover{{background:var(--surface3);border-color:var(--border2);box-shadow:var(--shadow-hover);transform:translateY(-3px);}}
        .g-hi{{background:rgba(45,212,191,0.08);border-color:var(--border2);}}
        .g-red{{background:rgba(248,113,113,0.06);border-color:var(--neg-border);}}
        .card-grid{{display:grid;gap:14px;}}
        .grid-5{{grid-template-columns:repeat(5,minmax(0,1fr));}}
        .grid-4{{grid-template-columns:repeat(4,minmax(0,1fr));}}
        .g .card-top-row{{display:flex;align-items:center;gap:10px;margin-bottom:10px;position:relative;z-index:2;padding:14px 16px 0;}}
        .card-ico{{font-size:clamp(16px,2vw,22px);line-height:1;flex-shrink:0;}}
        .lbl{{font-size:clamp(8px,1vw,9px);letter-spacing:2.5px;color:var(--muted);text-transform:uppercase;font-weight:600;line-height:1.3;}}
        .val{{font-family:'Syne',sans-serif;font-size:clamp(16px,2.5vw,22px);font-weight:700;color:var(--text);display:block;margin-bottom:10px;position:relative;z-index:2;padding:0 16px;word-break:break-word;overflow:hidden;text-overflow:ellipsis;}}
        .bar-wrap{{height:4px;background:rgba(0,0,0,0.3);border-radius:2px;margin:0 16px 12px;overflow:hidden;position:relative;z-index:2;}}
        .bar-fill{{height:100%;border-radius:2px;transition:width 1.2s cubic-bezier(0.4,0,0.2,1);}}
        .bar-teal{{background:var(--grad-accent);box-shadow:0 0 8px var(--accent-glow);}}
        .bar-red{{background:var(--grad-neg);}}
        .bar-gold{{background:var(--grad-neu);}}
        .card-foot{{display:flex;justify-content:space-between;align-items:center;padding:0 16px 14px;position:relative;z-index:2;flex-wrap:wrap;gap:4px;}}
        .sub{{font-size:10px;color:var(--muted2);font-family:'JetBrains Mono',monospace;}}
        .tag{{display:inline-flex;align-items:center;padding:3px 11px;border-radius:20px;font-size:clamp(9px,1.2vw,11px);font-weight:700;letter-spacing:0.5px;white-space:nowrap;}}
        .tag-neu{{background:var(--neu-bg);color:var(--neu);border:1px solid var(--neu-border);}}
        .tag-bull{{background:var(--accent-glow);color:var(--accent);border:1px solid var(--border2);}}
        .tag-bear{{background:var(--neg-bg);color:var(--neg);border:1px solid var(--neg-border);}}

        /* ── SNAPSHOT GRID ── */
        .snap-grid{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px;}}
        .snap-card{{padding:18px 16px;}}
        .snap-card .card-top-row{{margin-bottom:8px;padding:0;}}
        .snap-card .val{{font-size:clamp(18px,3vw,24px);padding:0;margin-bottom:0;}}

        /* ── MARKET DIRECTION ── */
        .md-widget{{position:relative;overflow:hidden;background:linear-gradient(135deg,var(--surface2),var(--surface));border:1px solid var(--border);border-radius:var(--radius-card);padding:clamp(12px,2vw,16px) clamp(14px,2vw,20px);display:flex;flex-direction:column;gap:12px;}}
        .md-glow{{position:absolute;top:-80%;left:-80%;width:260%;height:260%;background:conic-gradient(from 180deg,var(--accent) 0deg,var(--accent2) 120deg,var(--pos) 240deg,var(--accent) 360deg);opacity:0.04;animation:md-rotate 10s linear infinite;border-radius:50%;pointer-events:none;}}
        @keyframes md-rotate{{to{{transform:rotate(360deg);}}}}
        .md-row-top{{display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px;position:relative;z-index:1;}}
        .md-label{{display:flex;align-items:center;gap:7px;font-family:'JetBrains Mono',monospace;font-size:clamp(7px,1vw,8px);letter-spacing:3px;color:var(--muted2);text-transform:uppercase;}}
        .md-live-dot{{width:6px;height:6px;border-radius:50%;background:var(--accent);box-shadow:0 0 8px var(--accent);animation:md-pulse 2s ease-in-out infinite;flex-shrink:0;}}
        @keyframes md-pulse{{50%{{opacity:0.25;}}}}
        .md-pills-top{{display:flex;gap:8px;flex-wrap:wrap;}}
        .md-pill{{font-family:'JetBrains Mono',monospace;font-size:clamp(8px,1.2vw,10px);font-weight:700;padding:4px clamp(8px,1.5vw,14px);border-radius:20px;letter-spacing:1px;white-space:nowrap;}}
        .md-pill-bull{{background:var(--accent-glow);border:1px solid var(--border2);color:var(--accent);}}
        .md-pill-bear{{background:var(--neg-bg);border:1px solid var(--neg-border);color:var(--neg);}}
        .md-pill-conf-high{{background:var(--accent-glow);border:1px solid var(--border2);color:var(--accent);}}
        .md-pill-conf-med{{background:var(--neu-bg);border:1px solid var(--neu-border);color:var(--neu);}}
        .md-pill-conf-low{{background:var(--neg-bg);border:1px solid var(--neg-border);color:var(--neg);}}
        .md-row-bottom{{display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px;position:relative;z-index:1;}}
        .md-direction{{font-family:'Syne',sans-serif;font-weight:800;font-size:clamp(22px,5vw,36px);letter-spacing:clamp(1px,0.5vw,3px);line-height:1;}}

        /* ── LOGIC BOX ── */
        .logic-box{{background:var(--accent-glow);border:1px solid var(--border);border-left:3px solid var(--accent);border-radius:10px;padding:10px 16px;margin-top:12px;}}
        .logic-box-head{{font-family:'Syne',sans-serif;font-size:10px;font-weight:700;color:var(--accent);letter-spacing:2px;margin-bottom:7px;}}
        .logic-grid{{display:grid;grid-template-columns:1fr 1fr;gap:5px 20px;}}
        .logic-item{{display:flex;align-items:center;gap:7px;font-size:clamp(10px,1.3vw,11px);color:var(--muted);flex-wrap:wrap;}}
        .logic-item .lv{{font-family:'JetBrains Mono',monospace;font-size:10px;color:var(--muted2);}}
        .lc-bull{{display:inline-flex;align-items:center;font-family:'JetBrains Mono',monospace;font-size:9px;font-weight:600;padding:2px 8px;border-radius:4px;white-space:nowrap;background:var(--pos-bg);color:var(--pos);border:1px solid var(--pos-border);}}
        .lc-bear{{display:inline-flex;align-items:center;font-family:'JetBrains Mono',monospace;font-size:9px;font-weight:600;padding:2px 8px;border-radius:4px;white-space:nowrap;background:var(--neg-bg);color:var(--neg);border:1px solid var(--neg-border);}}
        .lc-side{{display:inline-flex;align-items:center;font-family:'JetBrains Mono',monospace;font-size:9px;font-weight:600;padding:2px 8px;border-radius:4px;white-space:nowrap;background:var(--neu-bg);color:var(--neu);border:1px solid var(--neu-border);}}
        .lc-info{{display:inline-flex;align-items:center;font-family:'JetBrains Mono',monospace;font-size:9px;font-weight:600;padding:2px 8px;border-radius:4px;white-space:nowrap;background:var(--info-bg);color:var(--info);border:1px solid var(--info-border);}}

        /* ── KEY LEVEL NODES ── */
        .rl-node-a{{position:absolute;bottom:0;transform:translateX(-50%);text-align:center;}}
        .rl-node-b{{position:absolute;top:0;transform:translateX(-50%);text-align:center;}}
        .rl-dot{{width:12px;height:12px;border-radius:50%;border:2px solid var(--surface);}}
        .rl-lbl{{font-size:clamp(8px,1.2vw,10px);font-weight:700;text-transform:uppercase;letter-spacing:0.6px;line-height:1.4;white-space:nowrap;color:var(--muted);}}
        .rl-val{{font-size:clamp(10px,1.5vw,13px);font-weight:700;color:var(--text);white-space:nowrap;margin-top:2px;}}

        /* ── FII/DII ── */
        .pf-live-badge{{display:inline-block;padding:2px 10px;border-radius:10px;font-size:10px;font-weight:700;letter-spacing:1px;}}
        .pf-live{{background:var(--pos-bg);color:var(--pos);border:1px solid var(--pos-border);}}
        .pf-estimated{{background:rgba(251,146,60,0.1);color:#fb923c;border:1px solid rgba(251,146,60,0.25);}}
        .pf-date-range{{font-size:11px;color:var(--muted);font-weight:400;letter-spacing:1px;}}
        .pf-grid{{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:14px;margin-bottom:18px;}}
        .pf-card{{background:var(--surface2);border:1px solid var(--border);border-radius:var(--radius-card);padding:16px 14px 14px;display:flex;flex-direction:column;gap:12px;position:relative;overflow:hidden;transition:all 0.25s;min-width:0;}}
        .pf-card:hover{{background:var(--surface3);transform:translateY(-3px);box-shadow:var(--shadow-hover);}}
        .pf-card-topline{{position:absolute;top:0;left:0;right:0;height:1px;}}
        .pf-card-head{{display:flex;justify-content:space-between;align-items:baseline;}}
        .pf-card-date{{font-family:'Syne',sans-serif;font-size:clamp(10px,1.5vw,12px);font-weight:700;color:var(--text);letter-spacing:1px;}}
        .pf-card-day{{font-size:9px;letter-spacing:1.5px;color:var(--muted2);text-transform:uppercase;}}
        .pf-block{{display:flex;flex-direction:column;gap:5px;}}
        .pf-block-header{{display:flex;justify-content:space-between;align-items:baseline;}}
        .pf-block-lbl{{font-size:8px;font-weight:700;letter-spacing:2px;text-transform:uppercase;}}
        .pf-fii-lbl{{color:rgba(56,189,248,0.5);}} .pf-dii-lbl{{color:rgba(45,212,191,0.5);}}
        .pf-block-val{{font-family:'JetBrains Mono',monospace;font-size:clamp(12px,1.8vw,15px);font-weight:700;line-height:1;word-break:break-all;}}
        .pf-bar-track{{height:4px;background:rgba(0,0,0,0.3);border-radius:2px;overflow:hidden;}}
        .pf-bar-fill{{height:100%;border-radius:2px;transition:width 1.2s cubic-bezier(0.4,0,0.2,1);}}
        .pf-divider{{height:1px;background:rgba(255,255,255,0.04);margin:0 -2px;}}
        .pf-card-net{{display:flex;justify-content:space-between;align-items:baseline;padding-top:8px;border-top:1px solid rgba(255,255,255,0.04);margin-top:auto;}}
        .pf-net-lbl{{font-size:8px;letter-spacing:2px;color:var(--muted2);text-transform:uppercase;font-weight:700;}}
        .pf-net-val{{font-family:'JetBrains Mono',monospace;font-size:clamp(11px,1.5vw,13px);font-weight:700;word-break:break-all;}}
        .pf-avg-strip{{display:grid;grid-template-columns:1fr auto 1fr auto 1fr;align-items:center;background:rgba(0,0,0,0.2);border:1px solid var(--border);border-radius:14px;padding:18px 24px;margin-bottom:16px;}}
        .pf-avg-cell{{text-align:center;min-width:0;}}
        .pf-avg-eyebrow{{font-size:8px;letter-spacing:2.5px;color:var(--muted2);text-transform:uppercase;margin-bottom:6px;font-weight:700;}}
        .pf-avg-val{{font-family:'Syne',sans-serif;font-size:clamp(18px,3vw,26px);font-weight:800;line-height:1;letter-spacing:-0.5px;word-break:break-word;}}
        .pf-avg-unit{{font-size:9px;color:var(--muted2);margin-top:3px;letter-spacing:1px;}}
        .pf-avg-sep{{width:1px;height:48px;background:linear-gradient(180deg,transparent,var(--border),transparent);margin:0 16px;flex-shrink:0;}}
        .pf-insight-box{{border-radius:12px;padding:16px 18px;}}
        .pf-insight-header{{display:flex;align-items:center;gap:10px;margin-bottom:10px;flex-wrap:wrap;}}
        .pf-insight-lbl{{font-size:9px;letter-spacing:2px;font-weight:700;text-transform:uppercase;}}
        .pf-verdict-badge{{display:inline-block;padding:3px 14px;border-radius:20px;font-size:clamp(10px,1.5vw,11px);font-weight:800;letter-spacing:1px;white-space:nowrap;}}
        .pf-insight-text{{font-size:clamp(12px,1.5vw,13px);color:var(--text2);line-height:1.85;font-weight:500;}}

        /* ── OI COMMAND ── */
        .nc-section-header{{display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px;margin-bottom:18px;padding-bottom:14px;border-bottom:1px solid var(--border);}}
        .nc-header-left{{display:flex;align-items:center;gap:14px;}}
        .nc-header-icon{{width:44px;height:44px;border-radius:10px;background:linear-gradient(135deg,var(--surface2),var(--surface3));border:1px solid var(--border2);display:flex;align-items:center;justify-content:center;font-size:20px;flex-shrink:0;box-shadow:0 4px 14px var(--accent-glow);}}
        .nc-header-title{{font-family:'Syne',sans-serif;font-size:clamp(13px,2vw,17px);font-weight:700;color:var(--text);letter-spacing:0.3px;}}
        .nc-header-sub{{font-size:11px;font-weight:400;color:var(--muted);margin-top:2px;letter-spacing:0.5px;}}
        .nc-atm-badge{{background:var(--surface2);color:var(--accent2);font-family:'JetBrains Mono',monospace;font-size:12px;font-weight:700;padding:6px 16px;border-radius:20px;letter-spacing:1.5px;border:1px solid var(--border2);box-shadow:0 2px 10px var(--accent-glow);white-space:nowrap;}}
        .nc-dir-box{{border-radius:var(--radius-card);padding:clamp(14px,2vw,20px) clamp(14px,2vw,22px);margin-bottom:18px;box-shadow:var(--shadow-card);}}
        .nc-dir-bar{{width:4px;border-radius:2px;flex-shrink:0;min-height:60px;}}
        .nc-dir-tag{{font-family:'JetBrains Mono',monospace;font-size:9px;font-weight:700;letter-spacing:2.5px;color:var(--muted2);text-transform:uppercase;margin-bottom:6px;}}
        .nc-dir-name{{font-family:'Syne',sans-serif;font-size:clamp(18px,3vw,28px);font-weight:700;line-height:1;margin-bottom:6px;letter-spacing:-0.5px;}}
        .nc-dir-signal{{font-family:'Space Grotesk',sans-serif;font-size:clamp(10px,1.3vw,12px);font-weight:400;}}
        .nc-meters-panel{{display:flex;flex-direction:column;gap:14px;min-width:180px;justify-content:center;}}
        .nc-meter-row{{display:flex;flex-direction:column;gap:5px;}}
        .nc-meter-head-row{{display:flex;justify-content:space-between;align-items:center;}}
        .nc-meter-label{{font-family:'JetBrains Mono',monospace;font-size:9px;font-weight:700;letter-spacing:2px;color:var(--muted2);text-transform:uppercase;}}
        .nc-meter-track{{position:relative;height:8px;background:rgba(0,0,0,0.35);border-radius:4px;overflow:visible;width:clamp(120px,20vw,200px);}}
        .nc-meter-fill{{height:100%;border-radius:4px;}}
        .nc-meter-head{{position:absolute;top:50%;transform:translate(-50%,-50%);width:14px;height:14px;border-radius:50%;border:2px solid var(--surface);}}
        .nc-meter-pct{{font-family:'Syne',sans-serif;font-size:clamp(12px,1.8vw,15px);font-weight:700;letter-spacing:0.5px;}}
        .nc-cards-grid{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px;}}
        .nc-card{{background:var(--surface2);border:1px solid var(--border);border-radius:var(--radius-card);padding:clamp(12px,2vw,18px);transition:all 0.3s ease;position:relative;overflow:hidden;min-width:0;}}
        .nc-card::before{{content:'';position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,var(--border2),transparent);}}
        .nc-card:hover{{border-color:var(--border2);background:var(--surface3);transform:translateY(-3px);box-shadow:var(--shadow-hover);}}
        .nc-card-header{{display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;flex-wrap:wrap;gap:4px;}}
        .nc-card-label{{font-family:'JetBrains Mono',monospace;font-size:clamp(8px,1.2vw,10px);font-weight:700;letter-spacing:2px;color:var(--muted);text-transform:uppercase;}}
        .nc-card-value{{font-family:'Syne',sans-serif;font-size:clamp(20px,3.5vw,30px);font-weight:700;line-height:1;margin-bottom:6px;letter-spacing:-0.5px;word-break:break-word;}}
        .nc-card-sub{{font-family:'JetBrains Mono',monospace;font-size:10px;color:var(--muted2);margin-bottom:14px;}}
        .nc-card-btn{{display:block;width:100%;padding:9px 14px;border-radius:7px;text-align:center;font-family:'Space Grotesk',sans-serif;font-size:clamp(11px,1.5vw,13px);font-weight:700;letter-spacing:0.5px;cursor:default;}}

        /* ── STRATEGY CHECKLIST ── */
        .annot-badge{{font-size:9px;padding:2px 10px;border-radius:8px;background:var(--pos-bg);border:1px solid var(--pos-border);color:var(--pos);font-family:'JetBrains Mono',monospace;letter-spacing:1px;font-weight:700;white-space:nowrap;}}
        .input-summary-grid{{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:12px;margin-bottom:20px;}}
        .inp-auto-card{{border-radius:12px;padding:14px 16px;border:1px solid var(--border);background:var(--accent-glow);transition:all 0.2s;}}
        .inp-s-label{{font-size:9px;letter-spacing:2px;text-transform:uppercase;font-weight:700;margin-bottom:6px;color:var(--muted);}}
        .inp-s-val{{font-family:'Syne',sans-serif;font-size:clamp(14px,2vw,18px);font-weight:700;color:var(--text);margin-bottom:4px;line-height:1.2;}}
        .inp-s-src{{font-size:9px;font-family:'JetBrains Mono',monospace;color:var(--muted2);}}
        .na-inline{{color:var(--muted2);font-family:'JetBrains Mono',monospace;font-size:13px;}}
        .signal-grid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;margin-bottom:20px;}}
        .sig-card{{background:var(--surface2);border:1px solid var(--border);border-radius:12px;padding:14px 16px;display:flex;align-items:flex-start;gap:14px;transition:all 0.2s;}}
        .sig-card:hover{{background:var(--surface3);border-color:var(--border2);}}
        .sig-icon{{width:38px;height:38px;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:18px;flex-shrink:0;}}
        .sig-bull{{background:var(--pos-bg);border:1px solid var(--pos-border);}}
        .sig-bear{{background:var(--neg-bg);border:1px solid var(--neg-border);}}
        .sig-neu{{background:var(--neu-bg);border:1px solid var(--neu-border);}}
        .sig-na{{background:rgba(122,154,170,0.06);border:1px solid rgba(122,154,170,0.12);}}
        .sig-body{{flex:1;min-width:0;}}
        .sig-name{{font-size:9px;letter-spacing:1.5px;color:var(--muted);text-transform:uppercase;font-weight:700;margin-bottom:4px;display:flex;align-items:center;gap:6px;flex-wrap:wrap;}}
        .sig-val{{font-family:'Syne',sans-serif;font-size:15px;font-weight:700;color:var(--text);margin-bottom:3px;}}
        .sig-val.na-val{{color:var(--muted2);font-family:'JetBrains Mono',monospace;font-size:13px;}}
        .sig-msg{{font-size:11px;color:var(--muted);line-height:1.5;}}
        .sig-score{{font-family:'JetBrains Mono',monospace;font-size:13px;font-weight:700;padding:3px 9px;border-radius:6px;flex-shrink:0;margin-top:2px;}}
        .score-p{{background:var(--pos-bg);color:var(--pos);border:1px solid var(--pos-border);}}
        .score-n{{background:var(--neg-bg);color:var(--neg);border:1px solid var(--neg-border);}}
        .score-0{{background:var(--neu-bg);color:var(--neu);border:1px solid var(--neu-border);}}
        .score-na{{background:rgba(122,154,170,0.06);color:var(--muted2);border:1px solid rgba(122,154,170,0.12);}}
        .auto-badge{{font-size:8px;padding:1px 6px;border-radius:4px;background:var(--pos-bg);border:1px solid var(--pos-border);color:var(--pos);font-weight:700;letter-spacing:0.5px;}}
        .score-meter{{background:rgba(0,0,0,0.2);border:1px solid var(--border);border-radius:16px;padding:22px 24px;display:flex;align-items:center;gap:24px;flex-wrap:wrap;}}
        .score-ring-wrap{{position:relative;flex-shrink:0;width:120px;height:120px;}}
        .score-ring-label{{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);text-align:center;}}
        .score-ring-num{{font-family:'Syne',sans-serif;font-size:26px;font-weight:800;line-height:1;}}
        .score-ring-txt{{font-size:8px;letter-spacing:2px;color:var(--muted2);text-transform:uppercase;}}
        .score-detail{{flex:1;min-width:200px;}}
        .score-bias-lbl{{font-family:'Syne',sans-serif;font-size:clamp(16px,3vw,24px);font-weight:800;letter-spacing:2px;margin-bottom:8px;}}
        .score-sub{{font-size:12px;color:var(--muted);line-height:1.6;margin-bottom:8px;}}
        .score-pills{{display:flex;gap:8px;flex-wrap:wrap;}}
        .sc-pill{{font-family:'JetBrains Mono',monospace;font-size:10px;font-weight:700;padding:4px 12px;border-radius:20px;letter-spacing:1px;}}
        .sc-pill-bull{{background:var(--pos-bg);border:1px solid var(--pos-border);color:var(--pos);}}
        .sc-pill-bear{{background:var(--neg-bg);border:1px solid var(--neg-border);color:var(--neg);}}
        .sc-pill-neu{{background:var(--neu-bg);border:1px solid var(--neu-border);color:var(--neu);}}
        .sc-pill-na{{background:rgba(122,154,170,0.06);border:1px solid rgba(122,154,170,0.12);color:var(--muted2);}}
        .strat-grid{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;}}
        .strat-card{{background:var(--surface2);border:1px solid var(--border);border-radius:var(--radius-card);padding:16px;position:relative;overflow:hidden;transition:all 0.25s;}}
        .strat-card::before{{content:'';position:absolute;top:0;left:0;right:0;height:2px;}}
        .strat-bull::before{{background:linear-gradient(90deg,transparent,var(--pos),transparent);}}
        .strat-bear::before{{background:linear-gradient(90deg,transparent,var(--neg),transparent);}}
        .strat-neu::before{{background:linear-gradient(90deg,transparent,var(--neu),transparent);}}
        .strat-vol::before{{background:linear-gradient(90deg,transparent,#a855f7,transparent);}}
        .strat-misc::before{{background:linear-gradient(90deg,transparent,var(--accent),transparent);}}
        .strat-card:hover{{transform:translateY(-3px);box-shadow:var(--shadow-hover);border-color:var(--border2);}}
        .strat-num{{font-family:'JetBrains Mono',monospace;font-size:9px;color:var(--muted2);margin-bottom:6px;letter-spacing:1px;}}
        .strat-name{{font-family:'Syne',sans-serif;font-size:clamp(12px,1.5vw,14px);font-weight:700;color:var(--text);margin-bottom:8px;line-height:1.3;}}
        .strat-tag{{display:inline-flex;align-items:center;gap:5px;padding:3px 10px;border-radius:20px;font-size:9px;font-weight:700;letter-spacing:1px;}}
        .strat-tag-bull{{background:var(--pos-bg);border:1px solid var(--pos-border);color:var(--pos);}}
        .strat-tag-bear{{background:var(--neg-bg);border:1px solid var(--neg-border);color:var(--neg);}}
        .strat-tag-neu{{background:var(--neu-bg);border:1px solid var(--neu-border);color:var(--neu);}}
        .strat-tag-vol{{background:rgba(168,85,247,0.1);border:1px solid rgba(168,85,247,0.25);color:#c084fc;}}
        .strat-tag-misc{{background:var(--info-bg);border:1px solid var(--info-border);color:var(--info);}}
        .filter-btn{{padding:6px 14px;border-radius:20px;font-size:10px;font-weight:700;letter-spacing:1px;cursor:pointer;border:1px solid var(--border);background:transparent;color:var(--muted);transition:all 0.2s;font-family:'Space Grotesk',sans-serif;}}
        .filter-btn.active,.filter-btn:hover{{background:var(--accent-glow);border-color:var(--border2);color:var(--accent);}}

        /* ── DISCLAIMER + FOOTER ── */
        .disclaimer{{background:var(--neu-bg);padding:22px;border-radius:12px;border-left:4px solid var(--neu);font-size:clamp(11px,1.5vw,13px);color:var(--neu);line-height:1.8;}}
        .footer{{text-align:center;padding:24px;color:var(--muted2);font-size:clamp(10px,1.3vw,12px);background:rgba(0,0,0,0.15);border-top:1px solid var(--border);}}

        /* ── RESPONSIVE ── */
        @media(max-width:1024px){{
            .grid-5{{grid-template-columns:repeat(3,minmax(0,1fr));}}
            .grid-4{{grid-template-columns:repeat(2,minmax(0,1fr));}}
            .pf-grid{{grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;}}
            .nc-cards-grid{{grid-template-columns:repeat(3,minmax(0,1fr));}}
            .nc-meter-track{{width:140px;}}
            .input-summary-grid{{grid-template-columns:repeat(3,minmax(0,1fr));}}
        }}
        @media(max-width:600px){{
            .grid-5,.grid-4{{grid-template-columns:minmax(0,1fr);}}
            .snap-grid{{grid-template-columns:repeat(2,minmax(0,1fr));}}
            .logic-grid{{grid-template-columns:1fr;}}
            .pf-grid{{grid-template-columns:repeat(2,minmax(0,1fr));}}
            .nc-cards-grid{{grid-template-columns:minmax(0,1fr);}}
            .nc-meters-panel{{min-width:unset;width:100%;}}
            .nc-meter-track{{width:100%;max-width:280px;}}
            .pf-avg-strip{{grid-template-columns:1fr;}}
            .pf-avg-sep{{display:none;}}
            .pf-date-range{{display:none;}}
            .signal-grid{{grid-template-columns:1fr;}}
            .strat-grid{{grid-template-columns:1fr;}}
            .input-summary-grid{{grid-template-columns:repeat(2,minmax(0,1fr));}}
            .score-meter{{flex-direction:column;}}
        }}
        @media(max-width:400px){{
            .snap-grid{{grid-template-columns:minmax(0,1fr);}}
            .pf-grid{{grid-template-columns:minmax(0,1fr);}}
            .input-summary-grid{{grid-template-columns:1fr;}}
        }}
    </style>
</head>
<body>
<div class="container">

    <!-- ══ HEADER ══ -->
    <div class="header">
        <h1>📊 NIFTY 50 DAILY REPORT</h1>
        <div class="status-bar">
            <div class="sb-item">
                <span class="sb-dot sb-dot-gen"></span>
                <span class="sb-label">Generated</span>
                <span class="sb-value gen-val">{d['timestamp']}</span>
            </div>
            <div class="sb-item">
                <span class="sb-dot sb-dot-clock"></span>
                <span class="sb-label">IST Now</span>
                <span class="sb-value clock-val" id="live-ist-clock">--:--:--</span>
            </div>
            <div class="sb-item">
                <span class="sb-dot sb-dot-updated"></span>
                <span class="sb-label">Last Updated</span>
                <span class="sb-value updated-val" id="last-updated">{d['timestamp']}</span>
            </div>
            <div class="sb-item">
                <span class="sb-dot sb-dot-cd"></span>
                <span class="sb-label">Next Refresh</span>
                <span class="sb-value cd-val" id="refresh-countdown">30s</span>
            </div>
        </div>

        <div class="tab-nav" id="tabNav">
            <button class="tab-btn active" data-tab="main" onclick="switchTab('main')">
                <span class="tab-dot"></span>
                📈 Main Analysis
                <span class="tab-badge">LIVE</span>
            </button>
            <button class="tab-btn" data-tab="checklist" onclick="switchTab('checklist')">
                <span class="tab-dot"></span>
                🧠 Strategy Checklist
                <span class="tab-badge">AUTO</span>
            </button>
        </div>
    </div>

    <!-- ══ MAIN TAB ══ -->
    <div class="tab-panel active" id="tab-main">

        <!-- Market Snapshot -->
        <div class="section">
            <div class="section-title"><span>📈</span> MARKET SNAPSHOT</div>
            <div class="snap-grid">
                <div class="g snap-card g-hi">
                    <div class="card-top-row"><span class="card-ico">💹</span><div class="lbl">NIFTY 50 SPOT</div></div>
                    <span class="val">₹{d['current_price']:,.2f}</span>
                </div>
                <div class="g snap-card">
                    <div class="card-top-row"><span class="card-ico">🎯</span><div class="lbl">ATM STRIKE</div></div>
                    <span class="val">₹{d['atm_strike']:,}</span>
                </div>
                <div class="g snap-card">
                    <div class="card-top-row"><span class="card-ico">📅</span><div class="lbl">EXPIRY DATE</div></div>
                    <span class="val" style="font-size:18px">{d['expiry']}</span>
                </div>
            </div>
        </div>
"""
        # Inject OI section if data available
        if d['has_option_data']:
            html += self._oi_command_section(d)

        # Key Levels
        html += self._key_levels_section(d, _pct_cp, _pts_to_res, _pts_to_sup, _mp_node)

        # FII/DII
        html += self._fiidii_section_html()

        # Market Direction
        html += self._market_direction_widget_html()

        # Technicals
        html += f"""
        <div class="section">
            <div class="section-title"><span>🔍</span> TECHNICAL INDICATORS</div>
            <div class="card-grid grid-5">{tech_cards}</div>
        </div>
"""
        # Option Chain Cards
        if d['has_option_data']:
            html += f"""
        <div class="section">
            <div class="section-title">
                <span>🎯</span> OPTION CHAIN ANALYSIS
                <span style="font-size:11px;color:var(--muted);font-weight:400;letter-spacing:1px;">(ATM ±10 Strikes Only)</span>
            </div>
            <div class="card-grid grid-4">{oc_cards}</div>
        </div>
"""
        html += """
        <div class="section">
            <div class="disclaimer">
                <strong>⚠️ DISCLAIMER</strong><br><br>
                This report is for <strong>EDUCATIONAL purposes only</strong> — NOT financial advice.<br>
                Always use stop losses and consult a SEBI registered investment advisor.<br>
                Past performance does not guarantee future results.
            </div>
        </div>
    </div><!-- /tab-main -->
"""
        html += checklist_tab_html
        html += f"""
    <div class="footer">
        <p>Automated Nifty 50 · Option Chain + Technical Analysis · Fully Auto Strategy Checklist</p>
        <p style="margin-top:6px;color:var(--muted2);">
            © 2026 · <span style="color:var(--accent);">Slate Teal Theme</span> ·
            Teal Command OI · Pulse Flow FII/DII · 100% Auto Signals · Educational Purposes Only
        </p>
    </div>
</div>
{auto_refresh_js}
</body>
</html>"""
        return html

    # ─────────────────────────────────────────────────────────────────────────
    #  SAVE + EMAIL
    # ─────────────────────────────────────────────────────────────────────────
    def save_html_to_file(self, filename='index.html', vol_support=None, vol_resistance=None,
                           global_bias=None, vol_view="normal", india_vix=None):
        try:
            print(f"\n📄 Saving HTML to {filename}...")
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self.generate_html_email(
                    vol_support=vol_support, vol_resistance=vol_resistance,
                    global_bias=global_bias, vol_view=vol_view, india_vix=india_vix,
                ))
            print(f"   ✅ Saved {filename}")
            metadata = {
                'timestamp':         self.html_data['timestamp'],
                'current_price':     float(self.html_data['current_price']),
                'bias':              self.html_data['bias'],
                'confidence':        self.html_data['confidence'],
                'rsi':               float(self.html_data['rsi']),
                'pcr':               float(self.html_data['pcr']) if self.html_data['has_option_data'] else None,
                'stop_loss':         float(self.html_data['stop_loss']) if self.html_data['stop_loss'] else None,
                'risk_reward_ratio': self.html_data.get('risk_reward_ratio', 0),
                'global_bias':       global_bias,
                'vol_view':          vol_view,
                'india_vix':         india_vix,
                'theme':             'Slate Teal',
            }
            with open('latest_report.json', 'w') as f:
                json.dump(metadata, f, indent=2)
            print("   ✅ Saved latest_report.json")
            return True
        except Exception as e:
            print(f"\n❌ Save failed: {e}"); return False

    def send_html_email_report(self, vol_support=None, vol_resistance=None,
                                global_bias=None, vol_view="normal", india_vix=None):
        gmail_user     = os.getenv('GMAIL_USER')
        gmail_password = os.getenv('GMAIL_APP_PASSWORD')
        recipient1     = os.getenv('RECIPIENT_EMAIL_1')
        recipient2     = os.getenv('RECIPIENT_EMAIL_2')
        if not all([gmail_user, gmail_password, recipient1, recipient2]):
            print("\n⚠️  Email credentials not set. Skipping."); return False
        try:
            ist_now = datetime.now(pytz.timezone('Asia/Kolkata'))
            msg = MIMEMultipart('alternative')
            msg['From']    = gmail_user
            msg['To']      = f"{recipient1}, {recipient2}"
            msg['Subject'] = f"📊 Nifty 50 Slate Teal Report — {ist_now.strftime('%d-%b-%Y %H:%M IST')}"
            msg.attach(MIMEText(self.generate_html_email(
                vol_support, vol_resistance, global_bias, vol_view, india_vix), 'html'))
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(gmail_user, gmail_password)
                server.send_message(msg)
            print("   ✅ Email sent!"); return True
        except Exception as e:
            print(f"\n❌ Email failed: {e}"); return False

    def generate_full_report(self):
        ist_now = datetime.now(pytz.timezone('Asia/Kolkata'))
        print("=" * 70)
        print("NIFTY 50 DAILY REPORT — SLATE TEAL THEME · FULLY AUTO")
        print(f"Generated: {ist_now.strftime('%d-%b-%Y %H:%M IST')}")
        print("=" * 70)
        oc_data = self.fetch_nse_option_chain_silent()
        option_analysis = self.analyze_option_chain_data(oc_data) if oc_data else None
        if option_analysis:
            print(f"✅ Option data | Expiry: {option_analysis['expiry']} | Spot: {option_analysis['underlying_value']}")
        else:
            print("⚠️  No option data — technical-only mode")
        print("\nFetching technical data...")
        technical = self.get_technical_data()
        self.generate_analysis_data(technical, option_analysis)
        return option_analysis


# ═══════════════════════════════════════════════════════════════════════════════
#  MAIN — Zero manual inputs. Everything auto-detected.
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    try:
        print("\n🚀 Starting Nifty 50 Analysis — Slate Teal Theme · Fully Automated v4\n")
        analyzer = NiftyHTMLAnalyzer()
        option_analysis = analyzer.generate_full_report()

        print("\n📊 Auto-detecting India VIX...")
        vol_view, india_vix = auto_vol_view()

        print("\n🌐 Auto-detecting Global Bias (S&P500 + Dow + Nifty trend)...")
        global_bias = auto_global_bias()

        d          = analyzer.html_data
        support    = d.get('support')
        resistance = d.get('resistance')
        current    = d.get('current_price')
        print(f"\n📦 Auto-computing Volume at S={support} and R={resistance}...")
        vol_support, vol_resistance = auto_volume_at_levels(support, resistance, current)

        print("\n" + "=" * 70)
        print("AUTO-FILL SUMMARY")
        print(f"  India VIX    : {india_vix} → vol_view = {vol_view.upper()}")
        print(f"  Global Bias  : {global_bias.upper()}")
        print(f"  Vol@Support  : {vol_support}")
        print(f"  Vol@Resist.  : {vol_resistance}")
        print("=" * 70)

        save_ok = analyzer.save_html_to_file(
            'index.html',
            vol_support=vol_support, vol_resistance=vol_resistance,
            global_bias=global_bias, vol_view=vol_view, india_vix=india_vix,
        )

        if save_ok:
            analyzer.send_html_email_report(vol_support, vol_resistance, global_bias, vol_view, india_vix)
        else:
            print("\n⚠️  Skipping email due to save failure")

        print("\n✅ Done! Open index.html in your browser.\n")

    except Exception as e:
        print(f"\n❌ Critical Error: {e}")
        import traceback; traceback.print_exc()


if __name__ == "__main__":
    main()
