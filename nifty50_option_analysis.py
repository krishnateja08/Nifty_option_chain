"""
NIFTY 50 COMPLETE ANALYSIS - DEEP OCEAN THEME
CARD STYLE: Glassmorphism Frosted — Stat Card + Progress Bar (Layout 4)
CHANGE IN OPEN INTEREST: Navy Command Theme (v3)
FII/DII SECTION: Theme 3 · Pulse Flow
MARKET DIRECTION: Holographic Glass Widget (Compact)
KEY LEVELS: 1H Candles · Last 120 bars · ±200 pts from price · Rounded to 25
AUTO REFRESH: Silent background fetch every 30s · No flicker · No scroll jump

FIX v2: Expiry date now time-aware:
     - Tuesday before 4:00 PM IST  → use TODAY's expiry
     - Tuesday after  4:00 PM IST  → roll to NEXT Tuesday
     - Any other day               → nearest upcoming Tuesday

FIX v1: Net OI = PE Δ - CE Δ (corrected from PE + CE)
     Net label now matches actual calculation.
     Bullish when Net > 0, Bearish when Net < 0.
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

def _last_5_trading_days():
    ist_off = timedelta(hours=5, minutes=30)
    today   = (datetime.utcnow() + ist_off).date()
    days, d = [], today - timedelta(days=1)
    while len(days) < 5:
        if d.weekday() < 5:
            days.append(d)
        d -= timedelta(days=1)
    days.reverse()
    return days

def _parse_nse_fiidii(raw):
    if not isinstance(raw, list) or not raw:
        return []
    days = []
    for row in raw[:10]:
        try:
            dt_obj  = datetime.strptime(row.get("date", ""), "%d-%b-%Y")
            fii_net = float(row.get("fiiBuyValue",  0) or 0) - float(row.get("fiiSellValue", 0) or 0)
            dii_net = float(row.get("diiBuyValue",  0) or 0) - float(row.get("diiSellValue", 0) or 0)
            days.append({'date': dt_obj.strftime("%b %d"), 'day': dt_obj.strftime("%a"),
                         'fii': round(fii_net, 2), 'dii': round(dii_net, 2)})
        except Exception:
            continue
    if len(days) < 3:
        return []
    days = days[:5]
    days.reverse()
    return days

def _fetch_from_groww():
    try:
        from bs4 import BeautifulSoup
        import requests as _req
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://groww.in/",
        }
        resp = _req.get("https://groww.in/fii-dii-data", headers=headers, timeout=15)
        if resp.status_code != 200:
            print(f"  ⚠️  Groww HTTP {resp.status_code}"); return []
        soup  = BeautifulSoup(resp.text, "html.parser")
        table = soup.find("table")
        if not table:
            print("  ⚠️  Groww: table not found"); return []
        rows  = table.find_all("tr")
        days  = []
        for row in rows[1:]:
            cols = [td.get_text(strip=True) for td in row.find_all("td")]
            if len(cols) < 7: continue
            try:
                dt_obj  = datetime.strptime(cols[0], "%d %b %Y")
                fii_net = float(cols[3].replace(",", "").replace("+", ""))
                dii_net = float(cols[6].replace(",", "").replace("+", ""))
                days.append({'date': dt_obj.strftime("%b %d"), 'day': dt_obj.strftime("%a"),
                             'fii': round(fii_net, 2), 'dii': round(dii_net, 2)})
            except Exception:
                continue
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
                print(f"  ✅ FII/DII from NSE (curl_cffi): {days[0]['date']} → {days[-1]['date']}")
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
    tdays = _last_5_trading_days()
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
    fii_span = f'<span style="color:#ff5252;font-weight:700;">₹{fii_avg:.0f} Cr/day</span>'
    dii_span = f'<span style="color:#40c4ff;font-weight:700;">₹{dii_avg:+.0f} Cr/day</span>'
    net_span = f'<span style="color:#b388ff;font-weight:700;">₹{net_avg:+.0f} Cr/day</span>'
    if fii_avg > 0 and dii_avg > 0:
        label='STRONGLY BULLISH'; emoji='🚀'; color='#00e676'; badge_cls='fii-bull'
        fii_span = f'<span style="color:#00e676;font-weight:700;">₹{fii_avg:+.0f} Cr/day</span>'
        insight=(f"Both FIIs (avg {fii_span}) and DIIs (avg {dii_span}) are net buyers — "
                 f"strong dual institutional confirmation. Net combined flow: {net_span}.")
    elif fii_avg < 0 and dii_avg > 0 and dii_avg > abs(fii_avg):
        label='CAUTIOUSLY BULLISH'; emoji='📈'; color='#69f0ae'; badge_cls='fii-cbull'
        insight=(f"FIIs are net sellers (avg {fii_span}) but DIIs are absorbing strongly (avg {dii_span}). "
                 f"DII support is cushioning downside — FII return is key for breakout. Net combined flow: {net_span}.")
    elif fii_avg < 0 and dii_avg > 0:
        label='MIXED / NEUTRAL'; emoji='⚖️'; color='#ffd740'; badge_cls='fii-neu'
        insight=(f"FII selling (avg {fii_span}) is partly offset by DII buying (avg {dii_span}). "
                 f"Watch for 3+ consecutive days of FII buying for trend confirmation. Net combined flow: {net_span}.")
    elif fii_avg < 0 and dii_avg < 0:
        label='BEARISH'; emoji='📉'; color='#ff5252'; badge_cls='fii-bear'
        dii_span=f'<span style="color:#ff5252;font-weight:700;">₹{dii_avg:.0f} Cr/day</span>'
        insight=(f"Both FIIs (avg {fii_span}) and DIIs (avg {dii_span}) are net sellers — "
                 f"clear bearish institutional pressure. Exercise caution. Net combined flow: {net_span}.")
    else:
        label='NEUTRAL'; emoji='🔄'; color='#b0bec5'; badge_cls='fii-neu'
        insight="Mixed signals from institutional participants. Wait for a clearer trend."
    max_abs = max(abs(v) for row in data for v in (row['fii'], row['dii'])) or 1
    return {'fii_avg': fii_avg, 'dii_avg': dii_avg, 'net_avg': net_avg,
            'label': label, 'emoji': emoji, 'color': color,
            'badge_cls': badge_cls, 'insight': insight, 'max_abs': max_abs}


class NiftyHTMLAnalyzer:
    def __init__(self):
        self.yf_symbol  = "^NSEI"
        self.nse_symbol = "NIFTY"
        self.report_lines = []
        self.html_data    = {}

    def log(self, message):
        print(message)
        self.report_lines.append(message)

    def _make_nse_session(self):
        headers = {
            "authority": "www.nseindia.com",
            "accept": "application/json, text/plain, */*",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
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
            print(f"  ⚠️  Session warm-up warning: {e}")
        return session, headers

    def get_upcoming_expiry_tuesday(self):
        """
        Returns the correct weekly expiry (Tuesday) based on current IST time.

        Rules:
          - If today IS Tuesday AND current IST time is BEFORE 4:00 PM
            → use TODAY as expiry (NSE market closes 3:30 PM, data valid till ~4 PM)
          - If today IS Tuesday AND current IST time is 4:00 PM or LATER
            → today's expiry session is done; roll forward to NEXT Tuesday
          - Any other weekday → nearest upcoming Tuesday
        """
        ist_tz    = pytz.timezone('Asia/Kolkata')
        now_ist   = datetime.now(ist_tz)
        today_ist = now_ist.date()
        weekday   = today_ist.weekday()   # Mon=0, Tue=1, Wed=2 … Sun=6

        # After 4:00 PM IST, today's expiry data is stale — roll to next week
        past_cutoff = (now_ist.hour, now_ist.minute) >= (16, 0)

        if weekday == 1 and not past_cutoff:
            days_ahead = 0   # Today IS Tuesday, before 4 PM → use today's expiry
        elif weekday == 1 and past_cutoff:
            days_ahead = 7   # Today IS Tuesday, after  4 PM → next Tuesday
        elif weekday < 1:
            days_ahead = 1 - weekday   # Monday → tomorrow (Tuesday)
        else:
            days_ahead = 8 - weekday   # Wed–Sun → next Tuesday

        expiry_date = today_ist + timedelta(days=days_ahead)
        expiry_str  = expiry_date.strftime('%d-%b-%Y')
        print(f"  📅 Now (IST): {now_ist.strftime('%A %d-%b-%Y %H:%M')} | "
              f"Past 4PM cutoff: {past_cutoff} | Expiry: {expiry_str}")
        return expiry_str

    def fetch_available_expiries(self, session, headers):
        try:
            url  = f"https://www.nseindia.com/api/option-chain-v3?type=Indices&symbol={self.nse_symbol}"
            resp = session.get(url, headers=headers, impersonate="chrome", timeout=20)
            if resp.status_code == 200:
                data     = resp.json()
                expiries = data.get('records', {}).get('expiryDates', [])
                if expiries:
                    print(f"  📅 NSE available expiries: {expiries[:5]}")
                    return expiries[0]
        except Exception as e:
            print(f"  ⚠️  Could not fetch expiry list: {e}")
        return None

    def fetch_nse_option_chain_silent(self):
        session, headers = self._make_nse_session()
        selected_expiry  = self.get_upcoming_expiry_tuesday()
        print(f"  🗓️  Fetching option chain for: {selected_expiry}")
        result = self._fetch_chain_for_expiry(session, headers, selected_expiry)
        if result is None:
            print(f"  ⚠️  No data for {selected_expiry}. Trying NSE expiry list...")
            real_expiry = self.fetch_available_expiries(session, headers)
            if real_expiry and real_expiry != selected_expiry:
                print(f"  🔄 Retrying with: {real_expiry}")
                result = self._fetch_chain_for_expiry(session, headers, real_expiry)
        if result is None:
            print("  ❌ Option chain fetch failed after all attempts.")
        return result

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
                    print(f"    ⚠️  Empty data for expiry={expiry}"); return None
                rows = []
                for item in data:
                    strike = item.get('strikePrice')
                    ce = item.get('CE', {}); pe = item.get('PE', {})
                    rows.append({
                        'Expiry': expiry, 'Strike': strike,
                        'CE_LTP': ce.get('lastPrice', 0), 'CE_OI': ce.get('openInterest', 0),
                        'CE_Vol': ce.get('totalTradedVolume', 0),
                        'PE_LTP': pe.get('lastPrice', 0), 'PE_OI': pe.get('openInterest', 0),
                        'PE_Vol': pe.get('totalTradedVolume', 0),
                        'CE_OI_Change': ce.get('changeinOpenInterest', 0),
                        'PE_OI_Change': pe.get('changeinOpenInterest', 0),
                    })
                df_full    = pd.DataFrame(rows).sort_values('Strike').reset_index(drop=True)
                underlying = json_data.get('records', {}).get('underlyingValue', 0)
                atm_strike = round(underlying / 50) * 50
                all_strikes = sorted(df_full['Strike'].unique())
                if atm_strike in all_strikes:
                    atm_idx = all_strikes.index(atm_strike)
                else:
                    atm_idx = min(range(len(all_strikes)), key=lambda i: abs(all_strikes[i] - underlying))
                    atm_strike = all_strikes[atm_idx]
                lower_idx = max(0, atm_idx - 10); upper_idx = min(len(all_strikes) - 1, atm_idx + 10)
                selected_strikes = all_strikes[lower_idx: upper_idx + 1]
                df = df_full[df_full['Strike'].isin(selected_strikes)].reset_index(drop=True)
                print(f"    ✅ Strikes: {len(df_full)} → ATM±10 filtered: {len(df)}")
                return {'expiry': expiry, 'df': df, 'raw_data': data,
                        'underlying': underlying, 'atm_strike': atm_strike}
            except Exception as e:
                print(f"    ❌ Attempt {attempt} error: {e}"); time.sleep(2)
        return None

    def analyze_option_chain_data(self, oc_data):
        if not oc_data: return None
        df = oc_data['df']
        total_ce_oi  = df['CE_OI'].sum(); total_pe_oi  = df['PE_OI'].sum()
        total_ce_vol = df['CE_Vol'].sum(); total_pe_vol = df['PE_Vol'].sum()
        pcr_oi  = total_pe_oi  / total_ce_oi  if total_ce_oi  > 0 else 0
        pcr_vol = total_pe_vol / total_ce_vol if total_ce_vol > 0 else 0
        total_ce_oi_change = int(df['CE_OI_Change'].sum())
        total_pe_oi_change = int(df['PE_OI_Change'].sum())

        # Net OI = PE Δ - CE Δ  →  Positive = Bullish, Negative = Bearish
        net_oi_change = total_pe_oi_change - total_ce_oi_change

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
        top_ce_strikes = df.nlargest(5,'CE_OI')[['Strike','CE_OI','CE_LTP']].to_dict('records')
        top_pe_strikes = df.nlargest(5,'PE_OI')[['Strike','PE_OI','PE_LTP']].to_dict('records')
        return {
            'expiry': oc_data['expiry'], 'underlying_value': oc_data['underlying'],
            'atm_strike': oc_data['atm_strike'],
            'pcr_oi': round(pcr_oi,3), 'pcr_volume': round(pcr_vol,3),
            'total_ce_oi': int(total_ce_oi), 'total_pe_oi': int(total_pe_oi),
            'max_ce_oi_strike': int(max_ce_oi_row['Strike']), 'max_ce_oi_value': int(max_ce_oi_row['CE_OI']),
            'max_pe_oi_strike': int(max_pe_oi_row['Strike']), 'max_pe_oi_value': int(max_pe_oi_row['PE_OI']),
            'max_pain': int(max_pain_row['Strike']),
            'top_ce_strikes': top_ce_strikes, 'top_pe_strikes': top_pe_strikes,
            'total_ce_oi_change': total_ce_oi_change, 'total_pe_oi_change': total_pe_oi_change,
            'net_oi_change': net_oi_change,
            'oi_direction': oi_direction, 'oi_signal': oi_signal,
            'oi_icon': oi_icon, 'oi_class': oi_class, 'df': df,
        }

    def get_technical_data(self):
        try:
            print("Calculating technical indicators...")
            nifty = yf.Ticker(self.yf_symbol)
            df = nifty.history(period="1y")
            if df.empty: print("Warning: Failed to fetch historical data"); return None
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
            latest = df.iloc[-1]
            current_price = latest['Close']
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
            else:
                print("  ⚠️  1H data unavailable — falling back to daily levels")
            recent_d = df.tail(60)
            resistance = r1 if r1 else recent_d['High'].quantile(0.90)
            support    = s1 if s1 else recent_d['Low'].quantile(0.10)
            strong_resistance = r2 if r2 else resistance + 100
            strong_support    = s2 if s2 else support - 100
            technical = {
                'current_price':    current_price,
                'sma_20':           latest['SMA_20'],
                'sma_50':           latest['SMA_50'],
                'sma_200':          latest['SMA_200'],
                'rsi':              latest['RSI'],
                'macd':             latest['MACD'],
                'signal':           latest['Signal'],
                'resistance':       resistance,
                'support':          support,
                'strong_resistance':strong_resistance,
                'strong_support':   strong_support,
            }
            print(f"✓ Technical | Price: {technical['current_price']:.2f} | RSI: {technical['rsi']:.1f}")
            return technical
        except Exception as e:
            print(f"Technical error: {e}"); return None

    def calculate_smart_stop_loss(self, current_price, support, resistance, bias):
        if bias == "BULLISH": return round(max(support - 30, current_price - 150), 0)
        elif bias == "BEARISH": return round(min(resistance + 30, current_price + 150), 0)
        return None

    def select_best_technical_strategy(self, bias, option_strategies):
        name_map = {"BULLISH": "Bull Call Spread", "BEARISH": "Bear Put Spread", "SIDEWAYS": "Iron Condor"}
        target   = name_map.get(bias, "")
        for s in option_strategies:
            if s['name'] == target: return s
        return option_strategies[0]

    def select_best_oi_strategy(self, oi_direction, atm_strike):
        if "Strong Bullish" in oi_direction or oi_direction == "Bullish":
            return {'name':'Long Call','market_bias':'Bullish','type':'Debit','risk':'High',
                    'max_profit':'Unlimited','max_loss':'Premium Paid',
                    'description':f'Buy {atm_strike} CE','best_for':'Put build-up indicates bullish momentum',
                    'signal':'🟢 Institutional buying interest detected','time_horizon':'Intraday to 1-2 days'}
        elif "Strong Bearish" in oi_direction or oi_direction == "Bearish":
            return {'name':'Long Put','market_bias':'Bearish','type':'Debit','risk':'High',
                    'max_profit':'Huge (to ₹0)','max_loss':'Premium Paid',
                    'description':f'Buy {atm_strike} PE','best_for':'Call build-up indicates bearish momentum',
                    'signal':'🔴 Institutional selling interest detected','time_horizon':'Intraday to 1-2 days'}
        elif "High Vol" in oi_direction:
            return {'name':'Long Straddle','market_bias':'Volatile','type':'Debit','risk':'High',
                    'max_profit':'Unlimited','max_loss':'Premium Paid',
                    'description':f'Buy {atm_strike} CE + {atm_strike} PE',
                    'best_for':'Both Calls & Puts building',
                    'signal':'🟡 Big move expected, direction uncertain','time_horizon':'Intraday'}
        elif "Unwinding" in oi_direction:
            return {'name':'Iron Butterfly','market_bias':'Neutral','type':'Credit','risk':'Low',
                    'max_profit':'Premium Received','max_loss':'Capped',
                    'description':f'Sell {atm_strike} CE + PE, Buy {atm_strike+100} CE + {atm_strike-100} PE',
                    'best_for':'Unwinding suggests reduced volatility',
                    'signal':'🟡 Position squaring, range-bound expected','time_horizon':'Intraday'}
        else:
            return {'name':'Vertical Spread','market_bias':'Moderate','type':'Debit','risk':'Moderate',
                    'max_profit':'Capped','max_loss':'Limited',
                    'description':f'Vertical spread near {atm_strike}',
                    'best_for':'Balanced OI changes',
                    'signal':'🟡 Moderate directional move expected','time_horizon':'1-2 days'}

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
            else: bearish_score += 1
        rsi = technical['rsi']
        if   rsi > 70: bearish_score += 1
        elif rsi < 30: bullish_score += 2
        if technical['macd'] > technical['signal']: bullish_score += 1
        else: bearish_score += 1
        if option_analysis:
            pcr = option_analysis['pcr_oi']; max_pain = option_analysis['max_pain']
            if   pcr > 1.2: bullish_score += 2
            elif pcr < 0.7: bearish_score += 2
            if   current > max_pain+100: bearish_score += 1
            elif current < max_pain-100: bullish_score += 1
        score_diff = bullish_score - bearish_score
        print(f"  📊 Bullish: {bullish_score} | Bearish: {bearish_score} | Diff: {score_diff}")
        if   score_diff >= 3:  bias,bias_icon,bias_class="BULLISH","📈","bullish"; confidence="HIGH" if score_diff >= 4 else "MEDIUM"
        elif score_diff <= -3: bias,bias_icon,bias_class="BEARISH","📉","bearish"; confidence="HIGH" if score_diff <= -4 else "MEDIUM"
        else:                  bias,bias_icon,bias_class="SIDEWAYS","↔️","sideways"; confidence="MEDIUM"
        if   rsi > 70: rsi_status,rsi_badge,rsi_icon="Overbought","bearish","🔴"
        elif rsi < 30: rsi_status,rsi_badge,rsi_icon="Oversold","bullish","🟢"
        else:          rsi_status,rsi_badge,rsi_icon="Neutral","neutral","🟡"
        macd_bullish = technical['macd'] > technical['signal']
        if option_analysis:
            pcr = option_analysis['pcr_oi']
            if   pcr > 1.2: pcr_status,pcr_badge,pcr_icon="Bullish","bullish","🟢"
            elif pcr < 0.7: pcr_status,pcr_badge,pcr_icon="Bearish","bearish","🔴"
            else:           pcr_status,pcr_badge,pcr_icon="Neutral","neutral","🟡"
        else:
            pcr_status,pcr_badge,pcr_icon="N/A","neutral","🟡"
        if option_analysis:
            max_ce_strike=option_analysis['max_ce_oi_strike']; max_pe_strike=option_analysis['max_pe_oi_strike']
            atm_strike=option_analysis['atm_strike']
        else:
            atm_strike=int(current/50)*50; max_ce_strike=atm_strike+200; max_pe_strike=atm_strike-200
        if bias == "BULLISH":
            mid=((support+resistance)/2); entry_low=current-100 if current>mid else current-50
            entry_high=current-50 if current>mid else current; target_1=resistance; target_2=max_ce_strike
            stop_loss=self.calculate_smart_stop_loss(current,support,resistance,"BULLISH")
            option_strategies=[
                {'name':'Long Call','market_bias':'Bullish','type':'Debit','risk':'High','max_profit':'Unlimited','max_loss':'Premium Paid','description':f'Buy {atm_strike} CE','best_for':'Strong upward momentum expected'},
                {'name':'Bull Call Spread','market_bias':'Bullish','type':'Debit','risk':'Moderate','max_profit':'Capped','max_loss':'Premium Paid','description':f'Buy {atm_strike} CE, Sell {atm_strike+200} CE','best_for':'Moderate upside with limited risk'},
                {'name':'Bull Put Spread','market_bias':'Bullish','type':'Credit','risk':'Moderate','max_profit':'Premium Received','max_loss':'Capped','description':f'Sell {atm_strike-100} PE, Buy {atm_strike-200} PE','best_for':'Expect market to stay above support'},
            ]
        elif bias == "BEARISH":
            mid=((support+resistance)/2); entry_low=current
            entry_high=current+100 if current<mid else current+50; target_1=support; target_2=max_pe_strike
            stop_loss=self.calculate_smart_stop_loss(current,support,resistance,"BEARISH")
            option_strategies=[
                {'name':'Long Put','market_bias':'Bearish','type':'Debit','risk':'High','max_profit':'Huge (to ₹0)','max_loss':'Premium Paid','description':f'Buy {atm_strike} PE','best_for':'Strong downward momentum expected'},
                {'name':'Bear Put Spread','market_bias':'Bearish','type':'Debit','risk':'Moderate','max_profit':'Capped','max_loss':'Premium Paid','description':f'Buy {atm_strike} PE, Sell {atm_strike-200} PE','best_for':'Moderate downside with limited risk'},
                {'name':'Bear Call Spread','market_bias':'Bearish','type':'Credit','risk':'Moderate','max_profit':'Premium Received','max_loss':'Capped','description':f'Sell {atm_strike+100} CE, Buy {atm_strike+200} CE','best_for':'Expect market to stay below resistance'},
            ]
        else:
            entry_low=support; entry_high=resistance; target_1=resistance; target_2=support; stop_loss=None
            option_strategies=[
                {'name':'Iron Condor','market_bias':'Neutral','type':'Credit','risk':'Low','max_profit':'Premium Received','max_loss':'Capped','description':f'Sell {atm_strike+100} CE + Buy {atm_strike+200} CE, Sell {atm_strike-100} PE + Buy {atm_strike-200} PE','best_for':'Expect low volatility, range-bound market'},
                {'name':'Iron Butterfly','market_bias':'Neutral','type':'Credit','risk':'Low','max_profit':'Premium Received','max_loss':'Capped','description':f'Sell {atm_strike} CE + Sell {atm_strike} PE, Buy {atm_strike+100} CE + Buy {atm_strike-100} PE','best_for':'Expect price to remain near ATM strike'},
                {'name':'Short Straddle','market_bias':'Neutral','type':'Credit','risk':'Very High','max_profit':'Premium Received','max_loss':'Unlimited','description':f'Sell {atm_strike} CE + Sell {atm_strike} PE','best_for':'ONLY for experienced traders!'},
                {'name':'Long Strangle','market_bias':'Volatile','type':'Debit','risk':'High','max_profit':'Unlimited','max_loss':'Premium Paid','description':f'Buy {atm_strike+100} CE + Buy {atm_strike-100} PE','best_for':'Expect big move but unsure of direction'},
            ]
        if stop_loss and bias != "SIDEWAYS":
            risk_points=abs(current-stop_loss); reward_points=abs(target_1-current)
            risk_reward_ratio=round(reward_points/risk_points,2) if risk_points>0 else 0
        else:
            risk_points=reward_points=risk_reward_ratio=0
        rsi_pct=min(100,max(0,rsi))
        def sma_bar(sma_val):
            diff=(current-sma_val)/sma_val*100; return min(100,max(0,50+diff*10))
        macd_val=technical['macd']; macd_pct=min(100,max(0,50+macd_val*2))
        pcr_pct=min(100,max(0,(option_analysis['pcr_oi']/2*100))) if option_analysis else 50
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
            'timestamp': ist_now.strftime('%d-%b-%Y %H:%M IST'),
            'current_price': current, 'expiry': option_analysis['expiry'] if option_analysis else 'N/A',
            'atm_strike': atm_strike, 'bias': bias, 'bias_icon': bias_icon, 'bias_class': bias_class,
            'confidence': confidence, 'bullish_score': bullish_score, 'bearish_score': bearish_score,
            'rsi': rsi, 'rsi_pct': rsi_pct, 'rsi_status': rsi_status, 'rsi_badge': rsi_badge, 'rsi_icon': rsi_icon,
            'sma_20': technical['sma_20'], 'sma_20_above': current>technical['sma_20'], 'sma_20_pct': sma_bar(technical['sma_20']),
            'sma_50': technical['sma_50'], 'sma_50_above': current>technical['sma_50'], 'sma_50_pct': sma_bar(technical['sma_50']),
            'sma_200': technical['sma_200'], 'sma_200_above': current>technical['sma_200'], 'sma_200_pct': sma_bar(technical['sma_200']),
            'macd': technical['macd'], 'macd_signal': technical['signal'], 'macd_bullish': macd_bullish, 'macd_pct': macd_pct,
            'pcr': option_analysis['pcr_oi'] if option_analysis else 0, 'pcr_pct': pcr_pct,
            'pcr_status': pcr_status, 'pcr_badge': pcr_badge, 'pcr_icon': pcr_icon,
            'max_pain': option_analysis['max_pain'] if option_analysis else 0, 'max_pain_pct': mp_pct,
            'max_ce_oi': max_ce_strike, 'max_pe_oi': max_pe_strike,
            'ce_oi_pct': ce_oi_pct, 'pe_oi_pct': pe_oi_pct,
            'total_ce_oi_change': option_analysis['total_ce_oi_change'] if option_analysis else 0,
            'total_pe_oi_change': option_analysis['total_pe_oi_change'] if option_analysis else 0,
            'net_oi_change': option_analysis['net_oi_change'] if option_analysis else 0,
            'oi_direction': option_analysis['oi_direction'] if option_analysis else 'N/A',
            'oi_signal': option_analysis['oi_signal'] if option_analysis else 'N/A',
            'oi_icon': option_analysis['oi_icon'] if option_analysis else '🟡',
            'oi_class': option_analysis['oi_class'] if option_analysis else 'neutral',
            'support': support, 'resistance': resistance,
            'strong_support': technical['strong_support'], 'strong_resistance': technical['strong_resistance'],
            'strategy_type': bias, 'entry_low': entry_low, 'entry_high': entry_high,
            'target_1': target_1, 'target_2': target_2, 'stop_loss': stop_loss,
            'risk_points': int(risk_points), 'reward_points': int(reward_points),
            'risk_reward_ratio': risk_reward_ratio,
            'option_strategies': option_strategies,
            'recommended_technical_strategy': self.select_best_technical_strategy(bias, option_strategies),
            'recommended_oi_strategy': self.select_best_oi_strategy(
                option_analysis['oi_direction'] if option_analysis else 'Neutral', atm_strike
            ) if option_analysis else None,
            'top_ce_strikes': option_analysis['top_ce_strikes'] if option_analysis else [],
            'top_pe_strikes': option_analysis['top_pe_strikes'] if option_analysis else [],
            'has_option_data': option_analysis is not None,
            'fii_dii_data': fii_dii_raw, 'fii_dii_summ': fii_dii_summ,
        }

    def _bar_color_class(self, badge):
        return {'bullish':'bar-teal','bearish':'bar-red','neutral':'bar-gold'}.get(badge,'bar-teal')

    def _stat_card(self, icon, label, value, badge_text, badge_class, bar_pct, bar_type, sub_text=""):
        tag_map = {'bullish':('tag-bull','#00e5ff'),'bearish':('tag-bear','#ff5252'),'neutral':('tag-neu','#ffb74d')}
        tag_cls,_ = tag_map.get(badge_class,tag_map['neutral'])
        hi_cls = 'g-hi' if badge_class=='bullish' else ('g-red' if badge_class=='bearish' else '')
        sub_html = f'<div class="sub">{sub_text}</div>' if sub_text else ''
        return f"""
            <div class="g {hi_cls}">
                <div class="card-top-row"><span class="card-ico">{icon}</span><div class="lbl">{label}</div></div>
                <span class="val">{value}</span>
                <div class="bar-wrap"><div class="bar-fill {bar_type}" style="width:{bar_pct:.1f}%"></div></div>
                <div class="card-foot">{sub_html}<span class="tag {tag_cls}">{badge_text}</span></div>
            </div>"""

    def _market_direction_widget_html(self):
        d = self.html_data
        bias       = d['bias']
        confidence = d['confidence']
        bull_score = d['bullish_score']
        bear_score = d['bearish_score']
        if bias == 'BULLISH':
            dir_gradient = 'linear-gradient(135deg, #4ecdc4, #2ecc8a)'
        elif bias == 'BEARISH':
            dir_gradient = 'linear-gradient(135deg, #ff6b6b, #cc3333)'
        else:
            dir_gradient = 'linear-gradient(135deg, #ffcd3c, #f7931e)'
        bull_pill = f'<span class="md-pill md-pill-bull">BULL {bull_score}</span>'
        bear_pill = f'<span class="md-pill md-pill-bear">BEAR {bear_score}</span>'
        if confidence == 'HIGH':
            conf_cls = 'md-pill-conf-high'
        elif confidence == 'MEDIUM':
            conf_cls = 'md-pill-conf-med'
        else:
            conf_cls = 'md-pill-conf-low'
        conf_pill = f'<span class="md-pill {conf_cls}">{confidence} CONFIDENCE</span>'
        return f"""
    <div class="section">
        <div class="section-title"><span>&#129517;</span> MARKET DIRECTION (Algorithmic)</div>
        <div class="md-widget">
            <div class="md-glow"></div>
            <div class="md-row-top">
                <div class="md-label">
                    <div class="md-live-dot"></div>
                    MARKET DIRECTION &nbsp;·&nbsp; ALGORITHMIC
                </div>
                <div class="md-pills-top">
                    {bull_pill}
                    {bear_pill}
                </div>
            </div>
            <div class="md-row-bottom">
                <div class="md-direction" style="background:{dir_gradient};-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">{bias}</div>
                {conf_pill}
            </div>
        </div>
        <div class="logic-box" style="margin-top:14px;">
            <div class="logic-box-head">&#128202; SCORING LOGIC</div>
            <div class="logic-grid">
                <div class="logic-item"><span class="lc-bull">BULLISH</span><span class="lv">Diff &ge; +3</span> &middot; Above SMAs, oversold RSI, +MACD, PCR &gt; 1.2</div>
                <div class="logic-item"><span class="lc-bear">BEARISH</span><span class="lv">Diff &le; &minus;3</span> &middot; Below SMAs, overbought RSI, &minus;MACD, PCR &lt; 0.7</div>
                <div class="logic-item"><span class="lc-side">SIDEWAYS</span><span class="lv">Diff &minus;2 to +2</span> &middot; Mixed signals, consolidation</div>
                <div class="logic-item"><span class="lc-info">CONFIDENCE</span> HIGH when gap &ge; 4 &nbsp;&middot;&nbsp; OI scope: ATM &plusmn;10 only</div>
            </div>
        </div>
    </div>
"""

    def _fiidii_section_html(self):
        data = self.html_data['fii_dii_data']
        summ = self.html_data['fii_dii_summ']
        badge_map = {
            'fii-bull':  ('#00e676','rgba(0,230,118,0.12)','rgba(0,230,118,0.3)'),
            'fii-cbull': ('#69f0ae','rgba(105,240,174,0.10)','rgba(105,240,174,0.28)'),
            'fii-neu':   ('#ffd740','rgba(255,215,64,0.10)','rgba(255,215,64,0.28)'),
            'fii-bear':  ('#ff5252','rgba(255,82,82,0.10)','rgba(255,82,82,0.28)'),
        }
        s_color,s_bg,s_border = badge_map.get(summ['badge_cls'],badge_map['fii-neu'])
        is_fallback = any(r.get('fallback') for r in data)
        date_range  = f"{data[0]['date']} \u2013 {data[-1]['date']}" if data else ''
        data_src_html = (
            '<span class="pf-live-badge pf-estimated">\u26a0 ESTIMATED</span>'
            if is_fallback else
            '<span class="pf-live-badge pf-live">\u25cf LIVE</span>'
        )
        max_abs = summ['max_abs'] or 1

        def day_card(row):
            fii_v=row['fii']; dii_v=row['dii']; net_v=fii_v+dii_v
            fii_w=round(min(100,abs(fii_v)/max_abs*100),1)
            dii_w=round(min(100,abs(dii_v)/max_abs*100),1)
            fii_col  ='#00d4ff' if fii_v>=0 else '#ff4444'
            fii_bar  ='linear-gradient(90deg,#00d4ff,#0090ff)' if fii_v>=0 else 'linear-gradient(90deg,#ff4444,#ff0055)'
            dii_col  ='#ffb300' if dii_v>=0 else '#ff4444'
            dii_bar  ='linear-gradient(90deg,#ffb300,#ff8f00)' if dii_v>=0 else 'linear-gradient(90deg,#ff4444,#ff0055)'
            net_col  ='#34d399' if net_v>=0 else '#f87171'
            fii_sign ='+' if fii_v>=0 else ''
            dii_sign ='+' if dii_v>=0 else ''
            net_sign ='+' if net_v>=0 else ''
            bdr ='rgba(0,212,255,0.18)' if net_v>=0 else 'rgba(255,68,68,0.18)'
            topL='linear-gradient(90deg,transparent,#00d4ff,transparent)' if net_v>=0 else 'linear-gradient(90deg,transparent,#ff4444,transparent)'
            return (
                f'<div class="pf-card" style="border-color:{bdr};">'
                f'<div class="pf-card-topline" style="background:{topL};"></div>'
                f'<div class="pf-card-head">'
                f'<span class="pf-card-date">{row["date"]}</span>'
                f'<span class="pf-card-day">{row["day"]}</span>'
                f'</div>'
                f'<div class="pf-block">'
                f'<div class="pf-block-header">'
                f'<span class="pf-block-lbl pf-fii-lbl">FII</span>'
                f'<span class="pf-block-val" style="color:{fii_col};">{fii_sign}{fii_v:,.0f}</span>'
                f'</div>'
                f'<div class="pf-bar-track"><div class="pf-bar-fill" style="width:{fii_w}%;background:{fii_bar};"></div></div>'
                f'</div>'
                f'<div class="pf-divider"></div>'
                f'<div class="pf-block">'
                f'<div class="pf-block-header">'
                f'<span class="pf-block-lbl pf-dii-lbl">DII</span>'
                f'<span class="pf-block-val" style="color:{dii_col};">{dii_sign}{dii_v:,.0f}</span>'
                f'</div>'
                f'<div class="pf-bar-track"><div class="pf-bar-fill" style="width:{dii_w}%;background:{dii_bar};"></div></div>'
                f'</div>'
                f'<div class="pf-card-net">'
                f'<span class="pf-net-lbl">NET</span>'
                f'<span class="pf-net-val" style="color:{net_col};">{net_sign}{net_v:,.0f}</span>'
                f'</div>'
                f'</div>'
            )

        cards_html = ''.join(day_card(r) for r in data)
        fa=summ['fii_avg']; da=summ['dii_avg']; na=summ['net_avg']
        fs='+' if fa>=0 else ''; ds='+' if da>=0 else ''; ns='+' if na>=0 else ''
        fc='#00d4ff' if fa>=0 else '#ff4444'
        dc='#ffb300' if da>=0 else '#ff4444'
        nc='#c084fc' if na>=0 else '#f87171'
        verdict_badge = (
            f'<span class="pf-verdict-badge" style="color:{s_color};background:{s_bg};border:1px solid {s_border};">'
            f'{summ["emoji"]} {summ["label"]}</span>'
        )
        return (
            '\n<div class="section">\n'
            '    <div class="section-title">\n'
            '        <span>\U0001f3e6</span> FII / DII INSTITUTIONAL FLOW\n'
            f'        {data_src_html}\n'
            f'        <span class="pf-date-range">Last 5 Trading Days &nbsp;\u00b7&nbsp; {date_range}</span>\n'
            '    </div>\n'
            f'    <div class="pf-grid">{cards_html}</div>\n'
            '    <div class="pf-avg-strip">\n'
            '        <div class="pf-avg-cell">\n'
            '            <div class="pf-avg-eyebrow">FII 5D Avg</div>\n'
            f'            <div class="pf-avg-val" style="color:{fc};">{fs}{fa:,.0f}</div>\n'
            '            <div class="pf-avg-unit">&#8377; Cr / day</div>\n'
            '        </div>\n'
            '        <div class="pf-avg-sep"></div>\n'
            '        <div class="pf-avg-cell">\n'
            '            <div class="pf-avg-eyebrow">DII 5D Avg</div>\n'
            f'            <div class="pf-avg-val" style="color:{dc};">{ds}{da:,.0f}</div>\n'
            '            <div class="pf-avg-unit">&#8377; Cr / day</div>\n'
            '        </div>\n'
            '        <div class="pf-avg-sep"></div>\n'
            '        <div class="pf-avg-cell">\n'
            '            <div class="pf-avg-eyebrow">Net Combined</div>\n'
            f'            <div class="pf-avg-val" style="color:{nc};">{ns}{na:,.0f}</div>\n'
            '            <div class="pf-avg-unit">&#8377; Cr / day</div>\n'
            '        </div>\n'
            '    </div>\n'
            f'    <div class="pf-insight-box" style="background:{s_bg};border:1px solid {s_border};">\n'
            '        <div class="pf-insight-header">\n'
            f'            <span class="pf-insight-lbl" style="color:{s_color};">&#128202; 5-DAY INSIGHT &amp; DIRECTION</span>\n'
            f'            {verdict_badge}\n'
            '        </div>\n'
            f'        <div class="pf-insight-text">{summ["insight"]}</div>\n'
            '    </div>\n'
            '</div>\n'
        )

    def _oi_navy_command_section(self, d):
        oi_cls=d['oi_class']; direction=d['oi_direction']; signal=d['oi_signal']
        ce_raw=d['total_ce_oi_change']; pe_raw=d['total_pe_oi_change']
        bull_force=0; bear_force=0
        if ce_raw < 0: bull_force += abs(ce_raw)
        else:          bear_force += abs(ce_raw)
        if pe_raw > 0: bull_force += abs(pe_raw)
        else:          bear_force += abs(pe_raw)
        total_force=bull_force+bear_force
        bull_pct=round(bull_force/total_force*100) if total_force>0 else 50
        bear_pct=100-bull_pct
        if oi_cls=='bearish':
            dir_bg='rgba(30,10,14,0.92)';dir_border='rgba(239,68,68,0.35)'
            dir_left_bar='linear-gradient(180deg,#ef4444,#b91c1c)';dir_name_col='#fb7185';dir_desc_col='rgba(251,113,133,0.5)'
        elif oi_cls=='bullish':
            dir_bg='rgba(10,30,20,0.92)';dir_border='rgba(16,185,129,0.35)'
            dir_left_bar='linear-gradient(180deg,#10b981,#047857)';dir_name_col='#34d399';dir_desc_col='rgba(52,211,153,0.5)'
        else:
            dir_bg='rgba(20,20,10,0.92)';dir_border='rgba(251,191,36,0.3)'
            dir_left_bar='linear-gradient(180deg,#f59e0b,#d97706)';dir_name_col='#fbbf24';dir_desc_col='rgba(251,191,36,0.5)'
        ce_val=d['total_ce_oi_change']; pe_val=d['total_pe_oi_change']
        net_val=d['net_oi_change']
        ce_is_bear=ce_val>0; pe_is_bull=pe_val>0
        ce_col='#fb7185' if ce_is_bear else '#34d399'; ce_dot_col='#ef4444' if ce_is_bear else '#10b981'
        ce_lbl='Bearish Signal' if ce_is_bear else 'Bullish Signal'
        ce_btn_col='#ef4444' if ce_is_bear else '#10b981'
        ce_btn_bg='rgba(239,68,68,0.12)' if ce_is_bear else 'rgba(16,185,129,0.12)'
        ce_btn_bdr='rgba(239,68,68,0.4)' if ce_is_bear else 'rgba(16,185,129,0.4)'
        pe_col='#34d399' if pe_is_bull else '#fb7185'; pe_dot_col='#10b981' if pe_is_bull else '#ef4444'
        pe_lbl='Bullish Signal' if pe_is_bull else 'Bearish Signal'
        pe_btn_col='#10b981' if pe_is_bull else '#ef4444'
        pe_btn_bg='rgba(16,185,129,0.12)' if pe_is_bull else 'rgba(239,68,68,0.12)'
        pe_btn_bdr='rgba(16,185,129,0.4)' if pe_is_bull else 'rgba(239,68,68,0.4)'
        if net_val > 0:
            net_col='#34d399';net_dot_col='#10b981';net_lbl='Bullish Net'
            net_btn_col='#10b981';net_btn_bg='rgba(16,185,129,0.12)';net_btn_bdr='rgba(16,185,129,0.4)'
        elif net_val < 0:
            net_col='#fb7185';net_dot_col='#ef4444';net_lbl='Bearish Net'
            net_btn_col='#ef4444';net_btn_bg='rgba(239,68,68,0.12)';net_btn_bdr='rgba(239,68,68,0.4)'
        else:
            net_col='#fbbf24';net_dot_col='#f59e0b';net_lbl='Balanced'
            net_btn_col='#f59e0b';net_btn_bg='rgba(245,158,11,0.12)';net_btn_bdr='rgba(245,158,11,0.4)'

        def nc_card(label,idc,value,val_col,sub,btn_lbl,btn_col,btn_bg,btn_bdr,icon_char):
            return (f'<div class="nc-card"><div class="nc-card-header">'
                    f'<span class="nc-card-label">{label}</span>'
                    f'<span style="font-size:18px;line-height:1;color:{idc};">{icon_char}</span></div>'
                    f'<div class="nc-card-value" style="color:{val_col};">{value:+,}</div>'
                    f'<div class="nc-card-sub">{sub}</div>'
                    f'<div class="nc-card-btn" style="color:{btn_col};background:{btn_bg};border:1px solid {btn_bdr};">{btn_lbl}</div></div>')

        cards_html = (
            nc_card('CALL OI CHANGE',ce_dot_col,ce_val,ce_col,'CE open interest \u0394',ce_lbl,ce_btn_col,ce_btn_bg,ce_btn_bdr,'🔴' if ce_is_bear else '🟢') +
            nc_card('PUT OI CHANGE',pe_dot_col,pe_val,pe_col,'PE open interest \u0394',pe_lbl,pe_btn_col,pe_btn_bg,pe_btn_bdr,'🟢' if pe_is_bull else '🔴') +
            nc_card('NET OI CHANGE',net_dot_col,net_val,net_col,'PE \u0394 \u2212 CE \u0394',net_lbl,net_btn_col,net_btn_bg,net_btn_bdr,'\u2696\ufe0f')
        )

        dual_meters = (
            f'<div class="nc-meters-panel">'
            f'<div class="nc-meter-row"><div class="nc-meter-head-row">'
            f'<span class="nc-meter-label">\U0001f7e2 Bull Strength</span>'
            f'<span class="nc-meter-pct" style="color:#34d399;">{bull_pct}%</span></div>'
            f'<div class="nc-meter-track">'
            f'<div class="nc-meter-fill" style="width:{bull_pct}%;background:linear-gradient(90deg,#10b981,#34d399);"></div>'
            f'<div class="nc-meter-head" style="left:{bull_pct}%;background:#34d399;box-shadow:0 0 8px #34d399;"></div>'
            f'</div></div>'
            f'<div class="nc-meter-row"><div class="nc-meter-head-row">'
            f'<span class="nc-meter-label">\U0001f534 Bear Strength</span>'
            f'<span class="nc-meter-pct" style="color:#fb7185;">{bear_pct}%</span></div>'
            f'<div class="nc-meter-track">'
            f'<div class="nc-meter-fill" style="width:{bear_pct}%;background:linear-gradient(90deg,#ef4444,#f97316);"></div>'
            f'<div class="nc-meter-head" style="left:{bear_pct}%;background:#fb7185;box-shadow:0 0 8px #fb7185;"></div>'
            f'</div></div></div>'
        )

        return (
            '\n<div class="section">\n'
            '    <div class="nc-section-header">\n'
            '        <div class="nc-header-left"><div class="nc-header-icon">\U0001f4ca</div>\n'
            '        <div><div class="nc-header-title">Change in Open Interest</div>\n'
            '        <div class="nc-header-sub">Today\'s Direction Analysis</div></div></div>\n'
            '        <div class="nc-atm-badge">ATM \u00b110</div>\n'
            '    </div>\n'
            f'    <div class="nc-dir-box" style="background:{dir_bg};border:1px solid {dir_border};">\n'
            '        <div style="display:flex;align-items:stretch;gap:18px;">\n'
            f'            <div class="nc-dir-bar" style="background:{dir_left_bar};"></div>\n'
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
            '        <div class="logic-box-head">\U0001f4d6 HOW TO READ</div>\n'
            '        <div class="logic-grid">\n'
            '            <div class="logic-item"><span class="lc-info">Call OI +</span> Writers selling calls <span class="lc-bear">Bearish</span>&nbsp;&nbsp;<span class="lc-info">Call OI \u2212</span> Unwinding <span class="lc-bull">Bullish</span></div>\n'
            '            <div class="logic-item"><span class="lc-info">Put OI +</span> Writers selling puts <span class="lc-bull">Bullish</span>&nbsp;&nbsp;<span class="lc-info">Put OI \u2212</span> Unwinding <span class="lc-bear">Bearish</span></div>\n'
            '            <div class="logic-item"><span class="lc-info">Net OI</span> = PE \u0394 \u2212 CE \u0394 &nbsp;\u00b7&nbsp; <span class="lc-bull">Positive = Bullish</span> &nbsp;<span class="lc-bear">Negative = Bearish</span></div>\n'
            '            <div class="logic-item"><span class="lc-info">Bull % + Bear %</span> = 100% &nbsp;\u00b7&nbsp; relative dominance</div>\n'
            '        </div>\n'
            '    </div>\n'
            '</div>\n'
        )

    def _key_levels_visual_section(self, d, _pct_cp, _pts_to_res, _pts_to_sup, _mp_node):
        return f"""
    <div class="section">
        <div class="section-title"><span>&#128202;</span> KEY LEVELS</div>
        <div style="display:flex;justify-content:space-between;margin-bottom:8px;">
            <span style="font-size:11px;color:#26c6da;font-weight:700;letter-spacing:1px;">&#9668; SUPPORT ZONE</span>
            <span style="font-size:11px;color:#f44336;font-weight:700;letter-spacing:1px;">RESISTANCE ZONE &#9658;</span>
        </div>
        <div style="position:relative;height:62px;">
            <div class="rl-node-a" style="left:3%;"><div class="rl-lbl" style="color:#26c6da;">Strong<br>Support</div><div class="rl-val" style="color:#26c6da;">&#8377;{d['strong_support']:,.0f}</div><div class="rl-dot" style="background:#26c6da;margin:6px auto 0;"></div></div>
            <div class="rl-node-a" style="left:22%;"><div class="rl-lbl" style="color:#00bcd4;">Support</div><div class="rl-val" style="color:#00bcd4;">&#8377;{d['support']:,.0f}</div><div class="rl-dot" style="background:#00bcd4;box-shadow:0 0 8px #00bcd4;margin:6px auto 0;"></div></div>
            <div style="position:absolute;left:{_pct_cp}%;transform:translateX(-50%);bottom:4px;background:#4fc3f7;color:#000;font-size:11px;font-weight:700;padding:4px 13px;border-radius:6px;white-space:nowrap;z-index:10;box-shadow:0 0 16px rgba(79,195,247,0.7);">&#9660; NOW &nbsp;&#8377;{d['current_price']:,.0f}</div>
            <div class="rl-node-a" style="left:75%;"><div class="rl-lbl" style="color:#ff7043;">Resistance</div><div class="rl-val" style="color:#ff7043;">&#8377;{d['resistance']:,.0f}</div><div class="rl-dot" style="background:#ff7043;box-shadow:0 0 8px #ff7043;margin:6px auto 0;"></div></div>
            <div class="rl-node-a" style="left:95%;"><div class="rl-lbl" style="color:#f44336;">Strong<br>Resistance</div><div class="rl-val" style="color:#f44336;">&#8377;{d['strong_resistance']:,.0f}</div><div class="rl-dot" style="background:#f44336;margin:6px auto 0;"></div></div>
        </div>
        <div style="position:relative;height:8px;border-radius:4px;background:linear-gradient(90deg,#26c6da 0%,#00bcd4 20%,#4fc3f7 40%,#ffb74d 58%,#ff7043 76%,#f44336 100%);box-shadow:0 2px 14px rgba(0,0,0,0.5);">
            <div style="position:absolute;left:{_pct_cp}%;top:50%;transform:translate(-50%,-50%);width:4px;height:22px;background:#fff;border-radius:2px;box-shadow:0 0 16px rgba(255,255,255,1);z-index:10;"></div>
        </div>
        <div style="position:relative;height:58px;">{_mp_node}</div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:4px;">
            <div style="background:rgba(244,67,54,0.08);border:1px solid rgba(244,67,54,0.25);border-radius:8px;padding:10px 16px;display:flex;justify-content:space-between;align-items:center;">
                <span style="font-size:12px;color:#b0bec5;">&#128205; Distance to Resistance</span>
                <span style="font-size:15px;font-weight:700;color:#f44336;">+{_pts_to_res:,} pts</span>
            </div>
            <div style="background:rgba(0,188,212,0.08);border:1px solid rgba(0,188,212,0.25);border-radius:8px;padding:10px 16px;display:flex;justify-content:space-between;align-items:center;">
                <span style="font-size:12px;color:#b0bec5;">&#128205; Distance to Support</span>
                <span style="font-size:15px;font-weight:700;color:#00bcd4;">\u2212{_pts_to_sup:,} pts</span>
            </div>
        </div>
    </div>
"""

    def generate_html_email(self):
        d=self.html_data
        sma20_bar ='bar-teal' if d['sma_20_above']  else 'bar-red'
        sma50_bar ='bar-teal' if d['sma_50_above']  else 'bar-red'
        sma200_bar='bar-teal' if d['sma_200_above'] else 'bar-red'
        macd_bar  ='bar-teal' if d['macd_bullish']  else 'bar-red'
        pcr_bar=self._bar_color_class(d['pcr_badge'])
        sma20_badge ='bullish' if d['sma_20_above']  else 'bearish'
        sma50_badge ='bullish' if d['sma_50_above']  else 'bearish'
        sma200_badge='bullish' if d['sma_200_above'] else 'bearish'
        macd_badge  ='bullish' if d['macd_bullish']  else 'bearish'
        sma20_lbl ='Above'  if d['sma_20_above']  else 'Below'
        sma50_lbl ='Above'  if d['sma_50_above']  else 'Below'
        sma200_lbl='Above'  if d['sma_200_above'] else 'Below'
        macd_lbl  ='Bullish' if d['macd_bullish']  else 'Bearish'
        sma20_ico ='\u2705' if d['sma_20_above']  else '\u274c'
        sma50_ico ='\u2705' if d['sma_50_above']  else '\u274c'
        sma200_ico='\u2705' if d['sma_200_above'] else '\u274c'
        macd_ico  ='\U0001f7e2' if d['macd_bullish'] else '\U0001f534'
        tech_cards=(
            self._stat_card(d['rsi_icon'],'RSI (14)',f"{d['rsi']:.1f}",d['rsi_status'],d['rsi_badge'],d['rsi_pct'],'bar-gold','14-period momentum')+
            self._stat_card(sma20_ico,'SMA 20',f"\u20b9{d['sma_20']:,.0f}",sma20_lbl,sma20_badge,d['sma_20_pct'],sma20_bar,'20-day average')+
            self._stat_card(sma50_ico,'SMA 50',f"\u20b9{d['sma_50']:,.0f}",sma50_lbl,sma50_badge,d['sma_50_pct'],sma50_bar,'50-day average')+
            self._stat_card(sma200_ico,'SMA 200',f"\u20b9{d['sma_200']:,.0f}",sma200_lbl,sma200_badge,d['sma_200_pct'],sma200_bar,'200-day average')+
            self._stat_card(macd_ico,'MACD',f"{d['macd']:.2f}",macd_lbl,macd_badge,d['macd_pct'],macd_bar,f"Signal: {d['macd_signal']:.2f}")
        )
        if d['has_option_data']:
            oc_cards=(
                self._stat_card(d['pcr_icon'],'PCR Ratio (OI)',f"{d['pcr']:.3f}",d['pcr_status'],d['pcr_badge'],d['pcr_pct'],pcr_bar,'Put/Call OI ratio')+
                self._stat_card('\U0001f3af','Max Pain',f"\u20b9{d['max_pain']:,}",'Expiry Magnet','neutral',d['max_pain_pct'],'bar-gold','Price gravity level')+
                self._stat_card('\U0001f534','Max Call OI',f"\u20b9{d['max_ce_oi']:,}",'Resistance','bearish',d['ce_oi_pct'],'bar-red','CE wall')+
                self._stat_card('\U0001f7e2','Max Put OI',f"\u20b9{d['max_pe_oi']:,}",'Support','bullish',d['pe_oi_pct'],'bar-teal','PE floor')
            )
        else:
            oc_cards='<div style="color:#80deea;padding:20px;">Option chain data unavailable</div>'
        _ss=d['strong_support']; _sr=d['strong_resistance']
        _rng=_sr-_ss if _sr!=_ss else 1
        def _pct_real(val): return round(max(3,min(97,(val-_ss)/_rng*100)),2)
        _pct_cp=_pct_real(d['current_price'])
        _pts_to_res=int(d['resistance']-d['current_price'])
        _pts_to_sup=int(d['current_price']-d['support'])
        _mp_node=""
        if d['has_option_data']:
            _mp_node=(f'<div class="rl-node-b" style="left:43%;">'
                      f'<div class="rl-dot" style="background:#ffb74d;box-shadow:0 0 8px #ffb74d;margin:0 auto 5px;"></div>'
                      f'<div class="rl-lbl" style="color:#ffb74d;">Max Pain</div>'
                      f'<div class="rl-val" style="color:#ffb74d;">\u20b9{d["max_pain"]:,}</div></div>')

        auto_refresh_js = """
    <script>
    (function() {
        var REFRESH_INTERVAL = 30000;
        var countdown        = REFRESH_INTERVAL / 1000;
        var lastRefreshEl    = document.getElementById('last-refresh-val');
        var countdownEl      = document.getElementById('refresh-countdown');
        var nowClockEl       = document.getElementById('ist-clock');

        function updateClock() {
            var now = new Date();
            var ist = new Date(now.toLocaleString('en-US', {timeZone: 'Asia/Kolkata'}));
            var h   = String(ist.getHours()).padStart(2,'0');
            var m   = String(ist.getMinutes()).padStart(2,'0');
            var s   = String(ist.getSeconds()).padStart(2,'0');
            if (nowClockEl) nowClockEl.textContent = h + ':' + m + ':' + s + ' IST';
        }
        setInterval(updateClock, 1000);
        updateClock();

        function updateCountdown() {
            if (countdownEl) countdownEl.textContent = countdown + 's';
            countdown--;
            if (countdown < 0) countdown = REFRESH_INTERVAL / 1000;
        }
        setInterval(updateCountdown, 1000);
        updateCountdown();

        function silentRefresh() {
            var scrollY = window.scrollY || window.pageYOffset;
            fetch(window.location.href + '?_t=' + Date.now(), {cache: 'no-store'})
                .then(function(r) { return r.text(); })
                .then(function(html) {
                    var parser   = new DOMParser();
                    var newDoc   = parser.parseFromString(html, 'text/html');
                    var newBody  = newDoc.querySelector('.container');
                    var oldBody  = document.querySelector('.container');
                    if (newBody && oldBody) {
                        oldBody.innerHTML = newBody.innerHTML;
                        window.scrollTo({top: scrollY, behavior: 'instant'});
                        var now = new Date();
                        var ist = new Date(now.toLocaleString('en-US', {timeZone: 'Asia/Kolkata'}));
                        var h   = String(ist.getHours()).padStart(2,'0');
                        var m   = String(ist.getMinutes()).padStart(2,'0');
                        var s   = String(ist.getSeconds()).padStart(2,'0');
                        var el  = document.getElementById('last-refresh-val');
                        if (el) el.textContent = h + ':' + m + ':' + s + ' IST';
                        lastRefreshEl = document.getElementById('last-refresh-val');
                        countdownEl   = document.getElementById('refresh-countdown');
                        nowClockEl    = document.getElementById('ist-clock');
                        countdown     = REFRESH_INTERVAL / 1000;
                    }
                })
                .catch(function(e) { console.warn('Silent refresh failed:', e); });
        }
        setInterval(silentRefresh, REFRESH_INTERVAL);
    })();
    </script>
"""

        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nifty 50 Daily Report</title>
    <link href="https://fonts.googleapis.com/css2?family=Oxanium:wght@400;600;700;800&family=Rajdhani:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600;700&family=Outfit:wght@300;400;500;600;700&family=Space+Mono:wght@400;700&family=Orbitron:wght@700;900&display=swap" rel="stylesheet">
    <style>
        *{{margin:0;padding:0;box-sizing:border-box;}}
        body{{font-family:'Rajdhani',sans-serif;background:linear-gradient(135deg,#0f2027 0%,#203a43 50%,#2c5364 100%);min-height:100vh;padding:20px;color:#b0bec5;}}
        .container{{max-width:1200px;margin:0 auto;background:rgba(15,32,39,0.85);backdrop-filter:blur(20px);border-radius:20px;overflow:hidden;box-shadow:0 20px 60px rgba(0,0,0,0.5);border:1px solid rgba(79,195,247,0.18);}}
        .header{{background:linear-gradient(135deg,#0f2027,#203a43);padding:40px 30px;text-align:center;border-bottom:2px solid rgba(79,195,247,0.3);position:relative;overflow:hidden;}}
        .header::before{{content:'';position:absolute;inset:0;background:radial-gradient(circle at 50% 50%,rgba(79,195,247,0.08) 0%,transparent 70%);pointer-events:none;}}
        .header h1{{font-family:'Oxanium',sans-serif;font-size:30px;font-weight:800;color:#4fc3f7;text-shadow:0 0 30px rgba(79,195,247,0.5);letter-spacing:2px;position:relative;z-index:1;}}
        .header p{{color:#80deea;font-size:13px;margin-top:8px;position:relative;z-index:1;}}
        .refresh-bar{{display:flex;align-items:center;justify-content:center;gap:24px;flex-wrap:wrap;margin-top:16px;padding:10px 20px;background:rgba(0,0,0,0.25);border-radius:10px;border:1px solid rgba(79,195,247,0.12);position:relative;z-index:1;}}
        .refresh-item{{display:flex;align-items:center;gap:7px;font-family:'JetBrains Mono',monospace;font-size:11px;}}
        .refresh-dot{{width:7px;height:7px;border-radius:50%;background:#00e676;box-shadow:0 0 8px #00e676;animation:rb-pulse 2s ease-in-out infinite;flex-shrink:0;}}
        .refresh-dot.clock-dot{{background:#4fc3f7;box-shadow:0 0 8px #4fc3f7;animation:none;}}
        .refresh-dot.cd-dot{{background:#ffb74d;box-shadow:0 0 8px #ffb74d;animation:none;}}
        @keyframes rb-pulse{{50%{{opacity:0.2;}}}}
        .refresh-label{{color:rgba(128,222,234,0.45);letter-spacing:1.5px;text-transform:uppercase;font-size:9px;}}
        .refresh-value{{color:#e0f7fa;font-weight:700;letter-spacing:0.5px;}}
        .refresh-sep{{width:1px;height:22px;background:rgba(79,195,247,0.15);}}
        .section{{padding:28px 26px;border-bottom:1px solid rgba(79,195,247,0.08);}}
        .section:last-child{{border-bottom:none;}}
        .section-title{{font-family:'Oxanium',sans-serif;font-size:13px;font-weight:700;letter-spacing:2.5px;color:#4fc3f7;text-transform:uppercase;display:flex;align-items:center;gap:10px;margin-bottom:20px;padding-bottom:12px;border-bottom:1px solid rgba(79,195,247,0.18);flex-wrap:wrap;}}
        .section-title span{{font-size:18px;}}
        .g{{background:rgba(255,255,255,0.04);backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);border:1px solid rgba(79,195,247,0.18);border-radius:16px;position:relative;overflow:hidden;transition:all 0.35s cubic-bezier(0.4,0,0.2,1);}}
        .g::before{{content:'';position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,rgba(255,255,255,0.25),transparent);z-index:1;}}
        .g::after{{content:'';position:absolute;top:-60%;left:-30%;width:50%;height:200%;background:linear-gradient(105deg,transparent,rgba(255,255,255,0.04),transparent);transform:skewX(-15deg);transition:left 0.6s ease;z-index:0;}}
        .g:hover::after{{left:130%;}}
        .g:hover{{background:rgba(79,195,247,0.09);border-color:rgba(79,195,247,0.45);box-shadow:0 12px 40px rgba(0,0,0,0.35),inset 0 1px 0 rgba(255,255,255,0.1);transform:translateY(-4px);}}
        .g-hi{{background:rgba(79,195,247,0.09);border-color:rgba(79,195,247,0.35);}}
        .g-red{{background:rgba(244,67,54,0.06);border-color:rgba(244,67,54,0.25);}}
        .g-red:hover{{background:rgba(244,67,54,0.1);border-color:rgba(244,67,54,0.45);}}
        .card-grid{{display:grid;gap:14px;}}
        .grid-5{{grid-template-columns:repeat(5,1fr);}}
        .grid-4{{grid-template-columns:repeat(4,1fr);}}
        .g .card-top-row{{display:flex;align-items:center;gap:10px;margin-bottom:10px;position:relative;z-index:2;padding:14px 16px 0;}}
        .card-ico{{font-size:22px;line-height:1;}}
        .lbl{{font-size:9px;letter-spacing:2.5px;color:rgba(128,222,234,0.65);text-transform:uppercase;font-weight:600;line-height:1.3;}}
        .val{{font-family:'Oxanium',sans-serif;font-size:24px;font-weight:700;color:#fff;display:block;margin-bottom:10px;position:relative;z-index:2;padding:0 16px;}}
        .bar-wrap{{height:5px;background:rgba(0,0,0,0.35);border-radius:3px;margin:0 16px 12px;overflow:hidden;position:relative;z-index:2;}}
        .bar-fill{{height:100%;border-radius:3px;transition:width 1.2s cubic-bezier(0.4,0,0.2,1);}}
        .bar-teal{{background:linear-gradient(90deg,#00bcd4,#4fc3f7);box-shadow:0 0 8px rgba(79,195,247,0.6);}}
        .bar-red{{background:linear-gradient(90deg,#f44336,#ff5722);box-shadow:0 0 8px rgba(244,67,54,0.5);}}
        .bar-gold{{background:linear-gradient(90deg,#ffb74d,#ffd54f);box-shadow:0 0 8px rgba(255,183,77,0.5);}}
        .card-foot{{display:flex;justify-content:space-between;align-items:center;padding:0 16px 14px;position:relative;z-index:2;}}
        .sub{{font-size:10px;color:#455a64;font-family:'JetBrains Mono',monospace;}}
        .tag{{display:inline-flex;align-items:center;padding:3px 11px;border-radius:20px;font-size:11px;font-weight:700;letter-spacing:0.5px;font-family:'Rajdhani',sans-serif;}}
        .tag-neu{{background:rgba(255,183,77,0.15);color:#ffb74d;border:1px solid rgba(255,183,77,0.35);}}
        .tag-bull{{background:rgba(0,229,255,0.12);color:#00e5ff;border:1px solid rgba(0,229,255,0.35);}}
        .tag-bear{{background:rgba(255,82,82,0.12);color:#ff5252;border:1px solid rgba(255,82,82,0.35);}}
        .md-widget{{position:relative;overflow:hidden;background:linear-gradient(135deg,rgba(255,255,255,0.07),rgba(255,255,255,0.02));border:1px solid rgba(255,255,255,0.1);border-radius:16px;padding:16px 20px;backdrop-filter:blur(20px);display:flex;flex-direction:column;gap:12px;}}
        .md-glow{{position:absolute;top:-80%;left:-80%;width:260%;height:260%;background:conic-gradient(from 180deg,#ff6b35 0deg,#ffcd3c 120deg,#4ecdc4 240deg,#ff6b35 360deg);opacity:0.05;animation:md-rotate 8s linear infinite;border-radius:50%;pointer-events:none;}}
        @keyframes md-rotate{{to{{transform:rotate(360deg);}}}}
        .md-row-top{{display:flex;align-items:center;justify-content:space-between;position:relative;z-index:1;}}
        .md-label{{display:flex;align-items:center;gap:7px;font-family:'Space Mono',monospace;font-size:8px;letter-spacing:3px;color:rgba(255,255,255,0.3);text-transform:uppercase;}}
        .md-live-dot{{width:6px;height:6px;border-radius:50%;background:#4ecdc4;box-shadow:0 0 8px #4ecdc4;animation:md-pulse 2s ease-in-out infinite;flex-shrink:0;}}
        @keyframes md-pulse{{50%{{opacity:0.25;}}}}
        .md-pills-top{{display:flex;gap:8px;}}
        .md-pill{{font-family:'Space Mono',monospace;font-size:10px;font-weight:700;padding:4px 14px;border-radius:20px;letter-spacing:1px;}}
        .md-pill-bull{{background:rgba(78,205,196,0.12);border:1px solid rgba(78,205,196,0.4);color:#4ecdc4;}}
        .md-pill-bear{{background:rgba(255,100,100,0.12);border:1px solid rgba(255,100,100,0.4);color:#ff6b6b;}}
        .md-pill-conf-high{{background:rgba(78,205,196,0.12);border:1px solid rgba(78,205,196,0.35);color:#4ecdc4;}}
        .md-pill-conf-med{{background:rgba(255,205,60,0.12);border:1px solid rgba(255,205,60,0.35);color:#ffcd3c;}}
        .md-pill-conf-low{{background:rgba(255,107,107,0.12);border:1px solid rgba(255,107,107,0.35);color:#ff6b6b;}}
        .md-row-bottom{{display:flex;align-items:center;justify-content:space-between;position:relative;z-index:1;}}
        .md-direction{{font-family:'Orbitron',monospace;font-weight:900;font-size:36px;letter-spacing:3px;line-height:1;}}
        .logic-box{{background:rgba(79,195,247,0.04);border:1px solid rgba(79,195,247,0.14);border-left:3px solid #4fc3f7;border-radius:10px;padding:10px 16px;margin-top:12px;}}
        .logic-box-head{{font-family:'Oxanium',sans-serif;font-size:10px;font-weight:700;color:#4fc3f7;letter-spacing:2px;margin-bottom:7px;}}
        .logic-grid{{display:grid;grid-template-columns:1fr 1fr;gap:5px 20px;}}
        .logic-item{{display:flex;align-items:center;gap:7px;font-size:11px;color:rgba(176,190,197,0.6);flex-wrap:wrap;}}
        .logic-item .lv{{font-family:'JetBrains Mono',monospace;font-size:10px;color:rgba(176,190,197,0.4);}}
        .lc-bull{{display:inline-flex;align-items:center;font-family:'JetBrains Mono',monospace;font-size:9px;font-weight:600;padding:2px 8px;border-radius:4px;white-space:nowrap;background:rgba(0,230,118,0.1);color:#00e676;border:1px solid rgba(0,230,118,0.28);}}
        .lc-bear{{display:inline-flex;align-items:center;font-family:'JetBrains Mono',monospace;font-size:9px;font-weight:600;padding:2px 8px;border-radius:4px;white-space:nowrap;background:rgba(255,82,82,0.1);color:#ff5252;border:1px solid rgba(255,82,82,0.28);}}
        .lc-side{{display:inline-flex;align-items:center;font-family:'JetBrains Mono',monospace;font-size:9px;font-weight:600;padding:2px 8px;border-radius:4px;white-space:nowrap;background:rgba(255,183,77,0.1);color:#ffb74d;border:1px solid rgba(255,183,77,0.28);}}
        .lc-info{{display:inline-flex;align-items:center;font-family:'JetBrains Mono',monospace;font-size:9px;font-weight:600;padding:2px 8px;border-radius:4px;white-space:nowrap;background:rgba(79,195,247,0.08);color:#4fc3f7;border:1px solid rgba(79,195,247,0.22);}}
        .rl-node-a{{position:absolute;bottom:0;transform:translateX(-50%);text-align:center;}}
        .rl-node-b{{position:absolute;top:0;transform:translateX(-50%);text-align:center;}}
        .rl-dot{{width:12px;height:12px;border-radius:50%;border:2px solid rgba(10,20,35,0.9);}}
        .rl-lbl{{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:0.6px;line-height:1.4;white-space:nowrap;color:#b0bec5;}}
        .rl-val{{font-size:13px;font-weight:700;color:#fff;white-space:nowrap;margin-top:2px;}}
        .pf-live-badge{{display:inline-block;padding:2px 10px;border-radius:10px;font-size:10px;font-weight:700;letter-spacing:1px;}}
        .pf-live{{background:rgba(0,230,118,0.1);color:#00e676;border:1px solid rgba(0,230,118,0.3);}}
        .pf-estimated{{background:rgba(255,138,101,0.1);color:#ff8a65;border:1px solid rgba(255,138,101,0.3);}}
        .pf-date-range{{font-size:11px;color:#80deea;font-weight:400;letter-spacing:1px;}}
        .pf-grid{{display:grid;grid-template-columns:repeat(5,1fr);gap:14px;margin-bottom:18px;}}
        .pf-card{{background:rgba(255,255,255,0.03);border:1px solid rgba(0,212,255,0.18);border-radius:16px;padding:16px 14px 14px;display:flex;flex-direction:column;gap:12px;position:relative;overflow:hidden;transition:all 0.25s cubic-bezier(0.4,0,0.2,1);}}
        .pf-card:hover{{background:rgba(255,255,255,0.06);transform:translateY(-3px);box-shadow:0 12px 32px rgba(0,0,0,0.35);}}
        .pf-card-topline{{position:absolute;top:0;left:0;right:0;height:1px;}}
        .pf-card-head{{display:flex;justify-content:space-between;align-items:baseline;}}
        .pf-card-date{{font-family:'Oxanium',sans-serif;font-size:12px;font-weight:700;color:#e0f7fa;letter-spacing:1px;}}
        .pf-card-day{{font-size:9px;letter-spacing:1.5px;color:rgba(128,222,234,0.3);text-transform:uppercase;}}
        .pf-block{{display:flex;flex-direction:column;gap:5px;}}
        .pf-block-header{{display:flex;justify-content:space-between;align-items:baseline;}}
        .pf-block-lbl{{font-size:8px;font-weight:700;letter-spacing:2px;text-transform:uppercase;}}
        .pf-fii-lbl{{color:rgba(0,212,255,0.5);}}
        .pf-dii-lbl{{color:rgba(255,179,0,0.5);}}
        .pf-block-val{{font-family:'JetBrains Mono',monospace;font-size:15px;font-weight:700;line-height:1;}}
        .pf-bar-track{{height:4px;background:rgba(0,0,0,0.35);border-radius:2px;overflow:hidden;}}
        .pf-bar-fill{{height:100%;border-radius:2px;transition:width 1.2s cubic-bezier(0.4,0,0.2,1);}}
        .pf-divider{{height:1px;background:rgba(255,255,255,0.04);margin:0 -2px;}}
        .pf-card-net{{display:flex;justify-content:space-between;align-items:baseline;padding-top:8px;border-top:1px solid rgba(255,255,255,0.05);margin-top:auto;}}
        .pf-net-lbl{{font-size:8px;letter-spacing:2px;color:rgba(255,255,255,0.2);text-transform:uppercase;font-weight:700;}}
        .pf-net-val{{font-family:'JetBrains Mono',monospace;font-size:13px;font-weight:700;}}
        .pf-avg-strip{{display:grid;grid-template-columns:1fr auto 1fr auto 1fr;align-items:center;background:rgba(6,13,20,0.75);border:1px solid rgba(79,195,247,0.1);border-radius:14px;padding:18px 24px;margin-bottom:16px;}}
        .pf-avg-cell{{text-align:center;}}
        .pf-avg-eyebrow{{font-size:8px;letter-spacing:2.5px;color:rgba(0,229,255,0.4);text-transform:uppercase;margin-bottom:6px;font-weight:700;}}
        .pf-avg-val{{font-family:'Oxanium',sans-serif;font-size:26px;font-weight:800;line-height:1;letter-spacing:-0.5px;}}
        .pf-avg-unit{{font-size:9px;color:#37474f;margin-top:3px;letter-spacing:1px;}}
        .pf-avg-sep{{width:1px;height:48px;background:linear-gradient(180deg,transparent,rgba(79,195,247,0.2),transparent);margin:0 16px;}}
        .pf-insight-box{{border-radius:12px;padding:16px 18px;}}
        .pf-insight-header{{display:flex;align-items:center;gap:10px;margin-bottom:10px;flex-wrap:wrap;}}
        .pf-insight-lbl{{font-size:9px;letter-spacing:2px;font-weight:700;text-transform:uppercase;}}
        .pf-verdict-badge{{display:inline-block;padding:3px 14px;border-radius:20px;font-size:11px;font-weight:800;letter-spacing:1px;}}
        .pf-insight-text{{font-size:13px;color:#cfd8dc;line-height:1.85;font-weight:500;}}
        .sb-wrap{{background:rgba(6,13,20,0.85);border:1px solid rgba(79,195,247,0.15);border-radius:12px;overflow:hidden;margin-bottom:14px;box-shadow:0 4px 24px rgba(0,0,0,0.3);}}
        .sb-header{{padding:11px 18px;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid rgba(79,195,247,0.1);}}
        .sb-header.cyan{{background:rgba(79,195,247,0.08);border-left:4px solid #4fc3f7;}}
        .sb-header.gold{{background:rgba(255,183,77,0.08);border-left:4px solid #ffb74d;}}
        .sb-h-title{{font-family:'Oxanium',sans-serif;font-size:13px;font-weight:700;color:#4fc3f7;letter-spacing:1px;}}
        .sb-h-title.gold{{color:#ffb74d;}}
        .sb-h-badge{{font-size:9px;padding:3px 12px;border-radius:10px;font-weight:700;letter-spacing:1px;}}
        .sb-h-badge.cyan{{background:rgba(79,195,247,0.12);color:#4fc3f7;border:1px solid rgba(79,195,247,0.3);}}
        .sb-h-badge.gold{{background:rgba(255,183,77,0.12);color:#ffb74d;border:1px solid rgba(255,183,77,0.3);}}
        .sb-body{{display:grid;grid-template-columns:repeat(5,1fr);}}
        .sb-cell{{padding:12px 10px;text-align:center;border-right:1px solid rgba(79,195,247,0.06);}}
        .sb-cell:last-child{{border-right:none;}}
        .sb-lbl{{font-size:9px;letter-spacing:1.5px;color:#80a0b8;text-transform:uppercase;margin-bottom:5px;font-weight:600;}}
        .sb-val{{font-family:'Oxanium',sans-serif;font-size:14px;font-weight:700;color:#e0f7fa;}}
        .sb-val.green{{color:#00e676;}}.sb-val.cyan{{color:#00bcd4;}}.sb-val.gold{{color:#ffb74d;}}.sb-val.red{{color:#ff5252;}}.sb-val.small{{font-size:11px;}}
        .sb-signal{{padding:10px 16px;background:rgba(79,195,247,0.05);border-top:1px solid rgba(79,195,247,0.06);border-bottom:1px solid rgba(79,195,247,0.06);font-size:14px;color:#ffffff;font-weight:500;display:flex;align-items:center;gap:10px;}}
        .sb-signal .sig-lbl{{font-size:10px;letter-spacing:2px;color:#4fc3f7;text-transform:uppercase;flex-shrink:0;font-weight:700;}}
        .sb-footer{{padding:11px 16px;background:rgba(0,0,0,0.25);font-family:'JetBrains Mono',monospace;font-size:13px;color:#ffffff;font-weight:500;display:flex;gap:10px;align-items:baseline;flex-wrap:wrap;}}
        .sb-footer .sf-lbl{{font-size:10px;letter-spacing:2px;color:#4fc3f7;text-transform:uppercase;flex-shrink:0;font-family:'Rajdhani',sans-serif;font-weight:700;}}
        .sb-footer .sf-why{{font-size:13px;color:#ffffff;font-style:italic;font-family:'Rajdhani',sans-serif;font-weight:500;margin-left:auto;}}
        .strikes-table{{width:100%;border-collapse:collapse;margin-top:18px;border-radius:10px;overflow:hidden;}}
        .strikes-table th{{background:linear-gradient(135deg,#4fc3f7,#26c6da);color:#000;padding:14px;text-align:left;font-weight:700;font-size:12px;text-transform:uppercase;}}
        .strikes-table td{{padding:14px;border-bottom:1px solid rgba(79,195,247,0.08);color:#b0bec5;font-size:13px;}}
        .strikes-table tr:hover{{background:rgba(79,195,247,0.06);}}
        .strikes-table tbody tr:last-child td{{border-bottom:none;}}
        .snap-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;}}
        .snap-card{{padding:18px 16px;}}
        .snap-card .card-top-row{{margin-bottom:8px;padding:0;}}
        .snap-card .val{{font-size:26px;padding:0;margin-bottom:0;}}
        .disclaimer{{background:rgba(255,183,77,0.1);backdrop-filter:blur(8px);padding:22px;border-radius:12px;border-left:4px solid #ffb74d;font-size:13px;color:#ffb74d;line-height:1.8;}}
        .footer{{text-align:center;padding:24px;color:#546e7a;font-size:12px;background:rgba(10,20,28,0.4);}}
        .nc-section-header{{display:flex;align-items:center;justify-content:space-between;margin-bottom:18px;padding-bottom:14px;border-bottom:1px solid rgba(79,195,247,0.14);}}
        .nc-header-left{{display:flex;align-items:center;gap:14px;}}
        .nc-header-icon{{width:44px;height:44px;border-radius:10px;background:linear-gradient(135deg,#1e3a5f,#1a3052);border:1px solid rgba(79,195,247,0.3);display:flex;align-items:center;justify-content:center;font-size:20px;flex-shrink:0;box-shadow:0 4px 14px rgba(79,195,247,0.15);}}
        .nc-header-title{{font-family:'Outfit',sans-serif;font-size:17px;font-weight:700;color:#93c5fd;letter-spacing:0.3px;}}
        .nc-header-sub{{font-family:'Outfit',sans-serif;font-size:11px;font-weight:400;color:rgba(79,195,247,0.45);margin-top:2px;letter-spacing:0.5px;}}
        .nc-atm-badge{{background:#1f2a42;color:#60a5fa;font-family:'Outfit',sans-serif;font-size:12px;font-weight:700;padding:6px 16px;border-radius:20px;letter-spacing:1.5px;border:1px solid rgba(96,165,250,0.25);box-shadow:0 2px 10px rgba(96,165,250,0.1);}}
        .nc-dir-box{{border-radius:14px;padding:20px 22px;margin-bottom:18px;box-shadow:0 4px 24px rgba(0,0,0,0.3);}}
        .nc-dir-bar{{width:4px;border-radius:2px;flex-shrink:0;min-height:60px;}}
        .nc-dir-tag{{font-family:'Outfit',sans-serif;font-size:9px;font-weight:700;letter-spacing:2.5px;color:rgba(148,163,184,0.5);text-transform:uppercase;margin-bottom:6px;}}
        .nc-dir-name{{font-family:'Outfit',sans-serif;font-size:28px;font-weight:700;line-height:1;margin-bottom:6px;letter-spacing:-0.5px;}}
        .nc-dir-signal{{font-family:'Outfit',sans-serif;font-size:12px;font-weight:400;}}
        .nc-meters-panel{{display:flex;flex-direction:column;gap:14px;min-width:200px;justify-content:center;}}
        .nc-meter-row{{display:flex;flex-direction:column;gap:5px;}}
        .nc-meter-head-row{{display:flex;justify-content:space-between;align-items:center;}}
        .nc-meter-label{{font-family:'Outfit',sans-serif;font-size:9px;font-weight:700;letter-spacing:2px;color:rgba(148,163,184,0.45);text-transform:uppercase;}}
        .nc-meter-track{{position:relative;height:8px;background:rgba(0,0,0,0.4);border-radius:4px;overflow:visible;width:200px;}}
        .nc-meter-fill{{height:100%;border-radius:4px;}}
        .nc-meter-head{{position:absolute;top:50%;transform:translate(-50%,-50%);width:14px;height:14px;border-radius:50%;border:2px solid rgba(10,18,30,0.85);}}
        .nc-meter-pct{{font-family:'Oxanium',sans-serif;font-size:15px;font-weight:700;letter-spacing:0.5px;}}
        .nc-cards-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;}}
        .nc-card{{background:rgba(20,28,45,0.85);border:1px solid rgba(79,195,247,0.12);border-radius:14px;padding:18px 18px 14px;transition:all 0.3s ease;position:relative;overflow:hidden;}}
        .nc-card::before{{content:'';position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,rgba(255,255,255,0.1),transparent);}}
        .nc-card:hover{{border-color:rgba(79,195,247,0.3);background:rgba(25,35,55,0.9);transform:translateY(-3px);box-shadow:0 10px 30px rgba(0,0,0,0.3);}}
        .nc-card-header{{display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;}}
        .nc-card-label{{font-family:'Outfit',sans-serif;font-size:10px;font-weight:700;letter-spacing:2px;color:rgba(148,163,184,0.6);text-transform:uppercase;}}
        .nc-card-value{{font-family:'Oxanium',sans-serif;font-size:30px;font-weight:700;line-height:1;margin-bottom:6px;letter-spacing:-0.5px;}}
        .nc-card-sub{{font-family:'JetBrains Mono',monospace;font-size:10px;color:rgba(100,116,139,0.7);margin-bottom:14px;}}
        .nc-card-btn{{display:block;width:100%;padding:9px 14px;border-radius:7px;text-align:center;font-family:'Outfit',sans-serif;font-size:13px;font-weight:700;letter-spacing:0.5px;cursor:default;}}
        @media(max-width:1024px){{
            body{{padding:16px;}}.container{{border-radius:16px;}}.header{{padding:28px 20px;}}.header h1{{font-size:24px;}}
            .section{{padding:22px 18px;}}.grid-5{{grid-template-columns:repeat(3,1fr);}}.grid-4{{grid-template-columns:repeat(2,1fr);}}
            .snap-grid{{grid-template-columns:repeat(3,1fr);}}.sb-body{{grid-template-columns:repeat(3,1fr);}}
            .sb-cell:nth-child(4),.sb-cell:nth-child(5){{border-top:1px solid rgba(79,195,247,0.06);}}.val{{font-size:20px;}}
            .pf-grid{{grid-template-columns:repeat(3,1fr);gap:10px;}}.pf-block-val{{font-size:13px;}}.pf-avg-val{{font-size:22px;}}
            .nc-cards-grid{{grid-template-columns:repeat(3,1fr);}}.nc-dir-name{{font-size:22px;}}.nc-meter-track{{width:140px;}}.nc-card-value{{font-size:24px;}}
            .strikes-wrap{{grid-template-columns:1fr !important;}}
        }}
        @media(max-width:600px){{
            body{{padding:8px;}}.container{{border-radius:12px;}}.header{{padding:20px 14px;}}.header h1{{font-size:18px;}}.header p{{font-size:11px;}}
            .section{{padding:16px 12px;}}.section-title{{font-size:11px;letter-spacing:1.5px;gap:6px;}}.grid-5,.grid-4{{grid-template-columns:1fr;}}
            .snap-grid{{grid-template-columns:1fr;}}.val{{font-size:20px;}}.sb-body{{grid-template-columns:1fr 1fr;}}
            .logic-grid{{grid-template-columns:1fr;}}
            .sb-cell{{border-right:none !important;border-bottom:1px solid rgba(79,195,247,0.06);}}.sb-cell:last-child{{border-bottom:none;}}
            .sb-footer{{font-size:11px;flex-direction:column;gap:6px;}}.sb-footer .sf-why{{margin-left:0;}}
            div[style*="grid-template-columns:1fr 1fr"]{{grid-template-columns:1fr !important;}}
            .strikes-wrap{{grid-template-columns:1fr !important;}}.strikes-table th,.strikes-table td{{padding:10px 8px;font-size:11px;}}
            .pf-grid{{grid-template-columns:repeat(2,1fr);gap:10px;}}
            .pf-avg-strip{{grid-template-columns:1fr;gap:12px;padding:14px;}}
            .pf-avg-sep{{display:none;}}
            .pf-avg-cell{{text-align:left;display:flex;align-items:center;justify-content:space-between;gap:12px;}}
            .pf-avg-eyebrow{{margin-bottom:0;}}.pf-avg-val{{font-size:20px;}}.pf-insight-text{{font-size:12px;}}.pf-date-range{{display:none;}}
            .md-direction{{font-size:24px;letter-spacing:1px;}}
            .md-label{{font-size:7px;letter-spacing:2px;}}
            .nc-section-header{{flex-direction:column;align-items:flex-start;gap:10px;}}.nc-atm-badge{{align-self:flex-end;}}
            .nc-cards-grid{{grid-template-columns:1fr;}}.nc-dir-name{{font-size:20px;}}
            .nc-meters-panel{{min-width:unset;width:100%;}}.nc-meter-track{{width:100%;}}.nc-card-value{{font-size:26px;}}
            .refresh-bar{{gap:12px;padding:8px 12px;}}
            .refresh-sep{{display:none;}}
        }}
        @media(max-width:380px){{
            .header h1{{font-size:15px;}}.sb-body{{grid-template-columns:1fr;}}.section{{padding:12px 10px;}}.val{{font-size:17px;}}
            .pf-grid{{grid-template-columns:1fr;}}.pf-block-val{{font-size:16px;}}
            .nc-dir-name{{font-size:17px;}}.nc-card-value{{font-size:22px;}}
            .md-direction{{font-size:20px;}}
        }}
    </style>
</head>
<body>
<div class="container">
    <div class="header">
        <h1>&#128202; NIFTY 50 DAILY REPORT</h1>
        <p>Data Generated: {d['timestamp']}</p>
        <div class="refresh-bar">
            <div class="refresh-item">
                <div class="refresh-dot clock-dot"></div>
                <span class="refresh-label">IST Now</span>
                <span class="refresh-value" id="ist-clock">--:--:-- IST</span>
            </div>
            <div class="refresh-sep"></div>
            <div class="refresh-item">
                <div class="refresh-dot"></div>
                <span class="refresh-label">Last Refresh</span>
                <span class="refresh-value" id="last-refresh-val">{d['timestamp'].replace(' IST','')}</span>
            </div>
            <div class="refresh-sep"></div>
            <div class="refresh-item">
                <div class="refresh-dot cd-dot"></div>
                <span class="refresh-label">Next in</span>
                <span class="refresh-value" id="refresh-countdown">30s</span>
            </div>
        </div>
    </div>
    <div class="section">
        <div class="section-title"><span>&#128200;</span> MARKET SNAPSHOT</div>
        <div class="snap-grid">
            <div class="g snap-card g-hi"><div class="card-top-row"><span class="card-ico">&#128185;</span><div class="lbl">NIFTY 50 SPOT</div></div><span class="val">&#8377;{d['current_price']:,.2f}</span></div>
            <div class="g snap-card"><div class="card-top-row"><span class="card-ico">&#127919;</span><div class="lbl">ATM STRIKE</div></div><span class="val">&#8377;{d['atm_strike']:,}</span></div>
            <div class="g snap-card"><div class="card-top-row"><span class="card-ico">&#128197;</span><div class="lbl">EXPIRY DATE</div></div><span class="val" style="font-size:20px">{d['expiry']}</span></div>
        </div>
    </div>
"""
        if d['has_option_data']:
            html += self._oi_navy_command_section(d)
        html += self._key_levels_visual_section(d,_pct_cp,_pts_to_res,_pts_to_sup,_mp_node)
        html += self._fiidii_section_html()
        html += self._market_direction_widget_html()
        html += f"""
    <div class="section">
        <div class="section-title"><span>&#128269;</span> TECHNICAL INDICATORS</div>
        <div class="card-grid grid-5">{tech_cards}</div>
    </div>
"""
        if d['has_option_data']:
            html += f"""
    <div class="section">
        <div class="section-title"><span>&#127919;</span> OPTION CHAIN ANALYSIS <span style="font-size:11px;color:#80deea;font-weight:400;letter-spacing:1px;">(ATM \u00b110 Strikes Only)</span></div>
        <div class="card-grid grid-4">{oc_cards}</div>
    </div>
"""
        html += self._generate_recommendations_html(d)
        if d['has_option_data'] and (d['top_ce_strikes'] or d['top_pe_strikes']):
            html += """
    <div class="section">
        <div class="section-title"><span>&#128203;</span> TOP 5 STRIKES BY OPEN INTEREST <span style="font-size:11px;color:#80deea;font-weight:400;letter-spacing:1px;">(ATM \u00b110 Only)</span></div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;" class="strikes-wrap">
            <div><h3 style="color:#00bcd4;margin-bottom:14px;font-size:15px;font-family:'Oxanium',sans-serif;">&#128222; CALL OPTIONS (CE)</h3>
            <table class="strikes-table"><thead><tr><th>#</th><th>Strike</th><th>OI</th><th>LTP</th></tr></thead><tbody>
"""
            for i,s in enumerate(d['top_ce_strikes'],1):
                html += f"<tr><td><strong>{i}</strong></td><td><strong>&#8377;{int(s['Strike']):,}</strong></td><td>{int(s['CE_OI']):,}</td><td style='color:#00bcd4;font-weight:700;font-family:Oxanium,sans-serif;'>&#8377;{s['CE_LTP']:.2f}</td></tr>\n"
            html += """</tbody></table></div>
            <div><h3 style="color:#f44336;margin-bottom:14px;font-size:15px;font-family:'Oxanium',sans-serif;">&#128201; PUT OPTIONS (PE)</h3>
            <table class="strikes-table"><thead><tr><th>#</th><th>Strike</th><th>OI</th><th>LTP</th></tr></thead><tbody>
"""
            for i,s in enumerate(d['top_pe_strikes'],1):
                html += f"<tr><td><strong>{i}</strong></td><td><strong>&#8377;{int(s['Strike']):,}</strong></td><td>{int(s['PE_OI']):,}</td><td style='color:#f44336;font-weight:700;font-family:Oxanium,sans-serif;'>&#8377;{s['PE_LTP']:.2f}</td></tr>\n"
            html += "</tbody></table></div></div></div>\n"
        html += """
    <div class="section">
        <div class="disclaimer"><strong>\u26a0\ufe0f DISCLAIMER</strong><br><br>
        This report is for <strong>EDUCATIONAL purposes only</strong> \u2014 NOT financial advice.<br>
        Always use stop losses and consult a SEBI registered investment advisor.<br>
        Past performance does not guarantee future results.</div>
    </div>
    <div class="footer">
        <p>Automated Nifty 50 Option Chain + Technical Analysis Report</p>
        <p style="margin-top:6px;">\u00a9 2026 \u00b7 Glassmorphism UI \u00b7 Deep Ocean Theme \u00b7 Navy Command OI \u00b7 Pulse Flow FII/DII \u00b7 Holographic Glass Market Direction \u00b7 For Educational Purposes Only</p>
    </div>
</div>
"""
        html += auto_refresh_js
        html += "\n</body></html>"
        return html

    def _generate_recommendations_html(self, d):
        ts=d['recommended_technical_strategy']
        def bias_color(b):
            b=b.lower()
            if 'bull' in b: return 'green'
            if 'bear' in b: return 'red'
            if 'vol' in b: return 'gold'
            return 'gold'
        def risk_color(r):
            r=r.lower()
            if 'low' in r: return 'cyan'
            if 'high' in r or 'very' in r: return 'red'
            return 'gold'
        def profit_color(p):
            return 'green' if ('unlimited' in p.lower() or 'receiv' in p.lower()) else 'cyan'
        def loss_color(l):
            return 'red' if 'unlimit' in l.lower() else 'gold'
        html = """
    <div class="section">
        <div class="section-title"><span>&#128161;</span> TRADING RECOMMENDATIONS (Dual Strategy)</div>
        <p style="color:#90a4ae;font-size:13px;margin-bottom:16px;letter-spacing:0.5px;">
            Two independent strategy recommendations based on
            <strong style="color:#4fc3f7;">Technical Analysis</strong> and
            <strong style="color:#ffb74d;">OI Momentum</strong>.
        </p>
"""
        html += f"""
        <div class="sb-wrap">
            <div class="sb-header cyan"><span class="sb-h-title">1\ufe0f\u20e3 TECHNICAL ANALYSIS STRATEGY &nbsp;\u00b7&nbsp; {ts['name']}</span><span class="sb-h-badge cyan">Positional \u00b7 1\u20135 Days</span></div>
            <div class="sb-body">
                <div class="sb-cell"><div class="sb-lbl">Market Bias</div><div class="sb-val {bias_color(ts['market_bias'])}">{ts['market_bias']}</div></div>
                <div class="sb-cell"><div class="sb-lbl">Type</div><div class="sb-val cyan">{ts['type']}</div></div>
                <div class="sb-cell"><div class="sb-lbl">Risk</div><div class="sb-val {risk_color(ts['risk'])}">{ts['risk']}</div></div>
                <div class="sb-cell"><div class="sb-lbl">Max Profit</div><div class="sb-val {profit_color(ts['max_profit'])} small">{ts['max_profit']}</div></div>
                <div class="sb-cell"><div class="sb-lbl">Max Loss</div><div class="sb-val {loss_color(ts['max_loss'])} small">{ts['max_loss']}</div></div>
            </div>
            <div class="sb-footer"><span class="sf-lbl">&#128203; Setup</span><span>{ts['description']}</span><span class="sf-why">&#128161; {ts['best_for']}</span></div>
        </div>
"""
        if d['recommended_oi_strategy']:
            oi=d['recommended_oi_strategy']
            html += f"""
        <div class="sb-wrap">
            <div class="sb-header gold"><span class="sb-h-title gold">2\ufe0f\u20e3 OI MOMENTUM STRATEGY &nbsp;\u00b7&nbsp; {oi['name']}</span><span class="sb-h-badge gold">{oi.get('time_horizon','Intraday')}</span></div>
            <div class="sb-signal"><span class="sig-lbl">&#128202; OI Signal</span><span style="color:#ffffff;font-weight:500;">{oi.get('signal','Market signal detected')}</span></div>
            <div class="sb-body">
                <div class="sb-cell"><div class="sb-lbl">Market Bias</div><div class="sb-val {bias_color(oi['market_bias'])}">{oi['market_bias']}</div></div>
                <div class="sb-cell"><div class="sb-lbl">Type</div><div class="sb-val cyan">{oi['type']}</div></div>
                <div class="sb-cell"><div class="sb-lbl">Risk</div><div class="sb-val {risk_color(oi['risk'])}">{oi['risk']}</div></div>
                <div class="sb-cell"><div class="sb-lbl">Max Profit</div><div class="sb-val {profit_color(oi['max_profit'])} small">{oi['max_profit']}</div></div>
                <div class="sb-cell"><div class="sb-lbl">Max Loss</div><div class="sb-val {loss_color(oi['max_loss'])} small">{oi['max_loss']}</div></div>
            </div>
            <div class="sb-footer"><span class="sf-lbl">&#128203; Setup</span><span>{oi['description']}</span><span class="sf-why">&#128161; {oi['best_for']}</span></div>
        </div>
"""
        return html

    def save_html_to_file(self, filename='index.html'):
        try:
            print(f"\n📄 Saving HTML to {filename}...")
            with open(filename,'w',encoding='utf-8') as f:
                f.write(self.generate_html_email())
            print(f"   ✅ Saved {filename}")
            metadata = {
                'timestamp': self.html_data['timestamp'],
                'current_price': float(self.html_data['current_price']),
                'bias': self.html_data['bias'],
                'confidence': self.html_data['confidence'],
                'rsi': float(self.html_data['rsi']),
                'pcr': float(self.html_data['pcr']) if self.html_data['has_option_data'] else None,
                'stop_loss': float(self.html_data['stop_loss']) if self.html_data['stop_loss'] else None,
                'risk_reward_ratio': self.html_data.get('risk_reward_ratio',0),
            }
            with open('latest_report.json','w') as f:
                json.dump(metadata,f,indent=2)
            print("   ✅ Saved latest_report.json")
            return True
        except Exception as e:
            print(f"\n❌ Save failed: {e}"); return False

    def send_html_email_report(self):
        gmail_user=os.getenv('GMAIL_USER'); gmail_password=os.getenv('GMAIL_APP_PASSWORD')
        recipient1=os.getenv('RECIPIENT_EMAIL_1'); recipient2=os.getenv('RECIPIENT_EMAIL_2')
        if not all([gmail_user,gmail_password,recipient1,recipient2]):
            print("\n⚠️  Email credentials not set. Skipping."); return False
        try:
            ist_now=datetime.now(pytz.timezone('Asia/Kolkata'))
            msg=MIMEMultipart('alternative')
            msg['From']=gmail_user; msg['To']=f"{recipient1}, {recipient2}"
            msg['Subject']=f"📊 Nifty 50 OI & Technical Report — {ist_now.strftime('%d-%b-%Y %H:%M IST')}"
            msg.attach(MIMEText(self.generate_html_email(),'html'))
            with smtplib.SMTP_SSL('smtp.gmail.com',465) as server:
                server.login(gmail_user,gmail_password); server.send_message(msg)
            print("   ✅ Email sent!"); return True
        except Exception as e:
            print(f"\n❌ Email failed: {e}"); return False

    def generate_full_report(self):
        ist_now=datetime.now(pytz.timezone('Asia/Kolkata'))
        print("="*70)
        print("NIFTY 50 DAILY REPORT — GLASSMORPHISM UI · NAVY COMMAND OI · PULSE FLOW FII/DII · HOLOGRAPHIC MARKET DIRECTION")
        print(f"Generated: {ist_now.strftime('%d-%b-%Y %H:%M IST')}")
        print("="*70)
        oc_data=self.fetch_nse_option_chain_silent()
        option_analysis=self.analyze_option_chain_data(oc_data) if oc_data else None
        if option_analysis:
            print(f"✅ Option data | Expiry: {option_analysis['expiry']} | Spot: {option_analysis['underlying_value']}")
        else:
            print("⚠️  No option data — technical-only mode")
        print("\nFetching technical data...")
        technical=self.get_technical_data()
        self.generate_analysis_data(technical,option_analysis)
        return option_analysis


def main():
    try:
        print("\n🚀 Starting Nifty 50 Analysis...\n")
        analyzer=NiftyHTMLAnalyzer()
        analyzer.generate_full_report()
        print("\n"+"="*70)
        save_ok=analyzer.save_html_to_file('index.html')
        if save_ok:
            analyzer.send_html_email_report()
        else:
            print("\n⚠️  Skipping email due to save failure")
        print("\n✅ Done! Open index.html in your browser.\n")
    except Exception as e:
        print(f"\n❌ Critical Error: {e}")
        import traceback; traceback.print_exc()


if __name__ == "__main__":
    main()
