"""
NIFTY 50 COMPLETE ANALYSIS - DEEP OCEAN THEME
CARD STYLE: Glassmorphism Frosted — Stat Card + Progress Bar (Layout 4)
FIXES:
  1. Expiry: TUESDAY weekly - always picks NEXT Tuesday (never today)
  2. Auto-fallback: if NSE returns empty, fetches real expiry list
  3. SIDEWAYS targets: T1=Resistance, T2=Support (distinct values)
  4. Stop loss fallback text for neutral strategies
  5. Option chain filtered to ATM ±10 strikes only
  6. [NEW] Glassmorphism Stat Card + Progress Bar layout for all indicator cards
"""

from curl_cffi import requests
import pandas as pd
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


class NiftyHTMLAnalyzer:
    def __init__(self):
        self.yf_symbol  = "^NSEI"
        self.nse_symbol = "NIFTY"
        self.report_lines = []
        self.html_data    = {}

    def log(self, message):
        print(message)
        self.report_lines.append(message)

    # ─────────────────────────────────────────────
    #  NSE SESSION
    # ─────────────────────────────────────────────
    def _make_nse_session(self):
        headers = {
            "authority":       "www.nseindia.com",
            "accept":          "application/json, text/plain, */*",
            "user-agent":      (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "referer":         "https://www.nseindia.com/option-chain",
            "accept-language": "en-US,en;q=0.9",
        }
        session = requests.Session()
        try:
            session.get("https://www.nseindia.com/",            headers=headers, impersonate="chrome", timeout=15)
            time.sleep(1.5)
            session.get("https://www.nseindia.com/option-chain", headers=headers, impersonate="chrome", timeout=15)
            time.sleep(1)
        except Exception as e:
            print(f"  ⚠️  Session warm-up warning: {e}")
        return session, headers

    # ─────────────────────────────────────────────
    #  EXPIRY DETECTION
    # ─────────────────────────────────────────────
    def get_upcoming_expiry_tuesday(self):
        ist_tz    = pytz.timezone('Asia/Kolkata')
        today_ist = datetime.now(ist_tz).date()
        weekday   = today_ist.weekday()          # Mon=0, Tue=1 … Sun=6
        days_ahead = 7 if weekday == 1 else (1 - weekday) % 7 or 7
        next_tuesday = today_ist + timedelta(days=days_ahead)
        expiry_str   = next_tuesday.strftime('%d-%b-%Y')
        print(f"  📅 Today (IST): {today_ist.strftime('%A %d-%b-%Y')} | Expiry: {expiry_str}")
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

    # ─────────────────────────────────────────────
    #  OPTION CHAIN FETCH
    # ─────────────────────────────────────────────
    def fetch_nse_option_chain_silent(self):
        session, headers    = self._make_nse_session()
        selected_expiry     = self.get_upcoming_expiry_tuesday()
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
        api_url = (
            f"https://www.nseindia.com/api/option-chain-v3"
            f"?type=Indices&symbol={self.nse_symbol}&expiry={expiry}"
        )
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
                    print(f"    ⚠️  Empty data for expiry={expiry}")
                    return None

                rows = []
                for item in data:
                    strike = item.get('strikePrice')
                    ce = item.get('CE', {})
                    pe = item.get('PE', {})
                    rows.append({
                        'Expiry':       expiry,
                        'Strike':       strike,
                        'CE_LTP':       ce.get('lastPrice', 0),
                        'CE_OI':        ce.get('openInterest', 0),
                        'CE_Vol':       ce.get('totalTradedVolume', 0),
                        'PE_LTP':       pe.get('lastPrice', 0),
                        'PE_OI':        pe.get('openInterest', 0),
                        'PE_Vol':       pe.get('totalTradedVolume', 0),
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
                    atm_idx    = min(range(len(all_strikes)), key=lambda i: abs(all_strikes[i] - underlying))
                    atm_strike = all_strikes[atm_idx]

                lower_idx        = max(0, atm_idx - 10)
                upper_idx        = min(len(all_strikes) - 1, atm_idx + 10)
                selected_strikes = all_strikes[lower_idx : upper_idx + 1]
                df = df_full[df_full['Strike'].isin(selected_strikes)].reset_index(drop=True)

                print(f"    ✅ Strikes: {len(df_full)} → ATM±10 filtered: {len(df)}")
                print(f"    📍 ATM: {atm_strike} | Range: {selected_strikes[0]}–{selected_strikes[-1]}")
                print(f"    💹 Underlying: {underlying}")

                return {
                    'expiry':     expiry,
                    'df':         df,
                    'raw_data':   data,
                    'underlying': underlying,
                    'atm_strike': atm_strike,
                }
            except Exception as e:
                print(f"    ❌ Attempt {attempt} error: {e}")
                time.sleep(2)
        return None

    # ─────────────────────────────────────────────
    #  OPTION CHAIN ANALYSIS
    # ─────────────────────────────────────────────
    def analyze_option_chain_data(self, oc_data):
        if not oc_data:
            return None

        df = oc_data['df']
        total_ce_oi  = df['CE_OI'].sum()
        total_pe_oi  = df['PE_OI'].sum()
        total_ce_vol = df['CE_Vol'].sum()
        total_pe_vol = df['PE_Vol'].sum()

        pcr_oi  = total_pe_oi  / total_ce_oi  if total_ce_oi  > 0 else 0
        pcr_vol = total_pe_vol / total_ce_vol if total_ce_vol > 0 else 0

        total_ce_oi_change = int(df['CE_OI_Change'].sum())
        total_pe_oi_change = int(df['PE_OI_Change'].sum())
        net_oi_change      = total_pe_oi_change - total_ce_oi_change

        if   total_ce_oi_change > 0 and total_pe_oi_change < 0:
            oi_direction, oi_signal, oi_icon, oi_class = "Strong Bearish",        "Call Build-up + Put Unwinding",   "🔴", "bearish"
        elif total_ce_oi_change < 0 and total_pe_oi_change > 0:
            oi_direction, oi_signal, oi_icon, oi_class = "Strong Bullish",        "Put Build-up + Call Unwinding",   "🟢", "bullish"
        elif total_ce_oi_change > 0 and total_pe_oi_change > 0:
            if   total_pe_oi_change > total_ce_oi_change * 1.5:
                oi_direction, oi_signal, oi_icon, oi_class = "Bullish",           "Put Build-up Dominant",           "🟢", "bullish"
            elif total_ce_oi_change > total_pe_oi_change * 1.5:
                oi_direction, oi_signal, oi_icon, oi_class = "Bearish",           "Call Build-up Dominant",          "🔴", "bearish"
            else:
                oi_direction, oi_signal, oi_icon, oi_class = "Neutral (High Vol)","Both Calls & Puts Building",      "🟡", "neutral"
        elif total_ce_oi_change < 0 and total_pe_oi_change < 0:
            oi_direction, oi_signal, oi_icon, oi_class = "Neutral (Unwinding)",   "Both Calls & Puts Unwinding",     "🟡", "neutral"
        else:
            if   net_oi_change > 0:
                oi_direction, oi_signal, oi_icon, oi_class = "Moderately Bullish","Net Put Accumulation",            "🟢", "bullish"
            elif net_oi_change < 0:
                oi_direction, oi_signal, oi_icon, oi_class = "Moderately Bearish","Net Call Accumulation",           "🔴", "bearish"
            else:
                oi_direction, oi_signal, oi_icon, oi_class = "Neutral",           "Balanced OI Changes",             "🟡", "neutral"

        max_ce_oi_row = df.loc[df['CE_OI'].idxmax()]
        max_pe_oi_row = df.loc[df['PE_OI'].idxmax()]
        df['pain']    = abs(df['CE_OI'] - df['PE_OI'])
        max_pain_row  = df.loc[df['pain'].idxmin()]
        df['Total_OI'] = df['CE_OI'] + df['PE_OI']

        top_ce_strikes = df.nlargest(5, 'CE_OI')[['Strike','CE_OI','CE_LTP']].to_dict('records')
        top_pe_strikes = df.nlargest(5, 'PE_OI')[['Strike','PE_OI','PE_LTP']].to_dict('records')

        return {
            'expiry':             oc_data['expiry'],
            'underlying_value':   oc_data['underlying'],
            'atm_strike':         oc_data['atm_strike'],
            'pcr_oi':             round(pcr_oi, 3),
            'pcr_volume':         round(pcr_vol, 3),
            'total_ce_oi':        int(total_ce_oi),
            'total_pe_oi':        int(total_pe_oi),
            'max_ce_oi_strike':   int(max_ce_oi_row['Strike']),
            'max_ce_oi_value':    int(max_ce_oi_row['CE_OI']),
            'max_pe_oi_strike':   int(max_pe_oi_row['Strike']),
            'max_pe_oi_value':    int(max_pe_oi_row['PE_OI']),
            'max_pain':           int(max_pain_row['Strike']),
            'top_ce_strikes':     top_ce_strikes,
            'top_pe_strikes':     top_pe_strikes,
            'total_ce_oi_change': total_ce_oi_change,
            'total_pe_oi_change': total_pe_oi_change,
            'net_oi_change':      net_oi_change,
            'oi_direction':       oi_direction,
            'oi_signal':          oi_signal,
            'oi_icon':            oi_icon,
            'oi_class':           oi_class,
            'df':                 df,
        }

    # ─────────────────────────────────────────────
    #  TECHNICAL ANALYSIS
    # ─────────────────────────────────────────────
    def get_technical_data(self):
        try:
            print("Calculating technical indicators...")
            nifty = yf.Ticker(self.yf_symbol)
            df    = nifty.history(period="1y")
            if df.empty:
                print("Warning: Failed to fetch historical data")
                return None

            df['SMA_20']  = df['Close'].rolling(20).mean()
            df['SMA_50']  = df['Close'].rolling(50).mean()
            df['SMA_200'] = df['Close'].rolling(200).mean()

            delta        = df['Close'].diff()
            gain         = delta.where(delta > 0, 0).rolling(14).mean()
            loss         = (-delta.where(delta < 0, 0)).rolling(14).mean()
            df['RSI']    = 100 - (100 / (1 + gain / loss))
            df['EMA_12'] = df['Close'].ewm(span=12, adjust=False).mean()
            df['EMA_26'] = df['Close'].ewm(span=26, adjust=False).mean()
            df['MACD']   = df['EMA_12'] - df['EMA_26']
            df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()

            latest = df.iloc[-1]
            recent = df.tail(60)

            technical = {
                'current_price': latest['Close'],
                'sma_20':        latest['SMA_20'],
                'sma_50':        latest['SMA_50'],
                'sma_200':       latest['SMA_200'],
                'rsi':           latest['RSI'],
                'macd':          latest['MACD'],
                'signal':        latest['Signal'],
                'resistance':    recent['High'].quantile(0.90),
                'support':       recent['Low'].quantile(0.10),
            }
            print(f"✓ Technical | Price: {technical['current_price']:.2f} | RSI: {technical['rsi']:.1f}")
            return technical
        except Exception as e:
            print(f"Technical error: {e}")
            return None

    # ─────────────────────────────────────────────
    #  HELPERS
    # ─────────────────────────────────────────────
    def calculate_smart_stop_loss(self, current_price, support, resistance, bias):
        if bias == "BULLISH":
            return round(max(support - 30, current_price - 150), 0)
        elif bias == "BEARISH":
            return round(min(resistance + 30, current_price + 150), 0)
        return None

    def select_best_technical_strategy(self, bias, option_strategies):
        name_map = {"BULLISH": "Bull Call Spread", "BEARISH": "Bear Put Spread", "SIDEWAYS": "Iron Condor"}
        target   = name_map.get(bias, "")
        for s in option_strategies:
            if s['name'] == target:
                return s
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

    # ─────────────────────────────────────────────
    #  MAIN ANALYSIS DATA
    # ─────────────────────────────────────────────
    def generate_analysis_data(self, technical, option_analysis):
        if not technical:
            self.log("⚠️  Technical data unavailable")
            return

        current    = technical['current_price']
        support    = technical['support']
        resistance = technical['resistance']
        ist_now    = datetime.now(pytz.timezone('Asia/Kolkata'))

        bullish_score = bearish_score = 0
        for sma in ['sma_20','sma_50','sma_200']:
            if current > technical[sma]: bullish_score += 1
            else:                         bearish_score += 1

        rsi = technical['rsi']
        if   rsi > 70: bearish_score += 1
        elif rsi < 30: bullish_score += 2

        if technical['macd'] > technical['signal']: bullish_score += 1
        else:                                        bearish_score += 1

        if option_analysis:
            pcr      = option_analysis['pcr_oi']
            max_pain = option_analysis['max_pain']
            if   pcr > 1.2:              bullish_score += 2
            elif pcr < 0.7:              bearish_score += 2
            if   current > max_pain+100: bearish_score += 1
            elif current < max_pain-100: bullish_score += 1

        score_diff = bullish_score - bearish_score
        print(f"  📊 Bullish: {bullish_score} | Bearish: {bearish_score} | Diff: {score_diff}")

        if   score_diff >= 3:  bias, bias_icon, bias_class = "BULLISH",  "📈", "bullish"; confidence = "HIGH" if score_diff >= 4 else "MEDIUM"
        elif score_diff <= -3: bias, bias_icon, bias_class = "BEARISH",  "📉", "bearish"; confidence = "HIGH" if score_diff <= -4 else "MEDIUM"
        else:                  bias, bias_icon, bias_class = "SIDEWAYS", "↔️",  "sideways"; confidence = "MEDIUM"

        if   rsi > 70: rsi_status, rsi_badge, rsi_icon = "Overbought", "bearish", "🔴"
        elif rsi < 30: rsi_status, rsi_badge, rsi_icon = "Oversold",   "bullish", "🟢"
        else:          rsi_status, rsi_badge, rsi_icon = "Neutral",    "neutral", "🟡"

        macd_bullish = technical['macd'] > technical['signal']

        if option_analysis:
            pcr = option_analysis['pcr_oi']
            if   pcr > 1.2: pcr_status, pcr_badge, pcr_icon = "Bullish", "bullish", "🟢"
            elif pcr < 0.7: pcr_status, pcr_badge, pcr_icon = "Bearish", "bearish", "🔴"
            else:           pcr_status, pcr_badge, pcr_icon = "Neutral", "neutral", "🟡"
        else:
            pcr_status, pcr_badge, pcr_icon = "N/A", "neutral", "🟡"

        if option_analysis:
            max_ce_strike = option_analysis['max_ce_oi_strike']
            max_pe_strike = option_analysis['max_pe_oi_strike']
            atm_strike    = option_analysis['atm_strike']
        else:
            atm_strike    = int(current/50)*50
            max_ce_strike = atm_strike + 200
            max_pe_strike = atm_strike - 200

        if bias == "BULLISH":
            mid = (support + resistance) / 2
            entry_low  = current - 100 if current > mid else current - 50
            entry_high = current - 50  if current > mid else current
            target_1   = resistance
            target_2   = max_ce_strike
            stop_loss  = self.calculate_smart_stop_loss(current, support, resistance, "BULLISH")
            option_strategies = [
                {'name':'Long Call',       'market_bias':'Bullish','type':'Debit', 'risk':'High',
                 'max_profit':'Unlimited', 'max_loss':'Premium Paid',
                 'description':f'Buy {atm_strike} CE','best_for':'Strong upward momentum expected'},
                {'name':'Bull Call Spread','market_bias':'Bullish','type':'Debit', 'risk':'Moderate',
                 'max_profit':'Capped',    'max_loss':'Premium Paid',
                 'description':f'Buy {atm_strike} CE, Sell {atm_strike+200} CE','best_for':'Moderate upside with limited risk'},
                {'name':'Bull Put Spread', 'market_bias':'Bullish','type':'Credit','risk':'Moderate',
                 'max_profit':'Premium Received','max_loss':'Capped',
                 'description':f'Sell {atm_strike-100} PE, Buy {atm_strike-200} PE','best_for':'Expect market to stay above support'},
            ]
        elif bias == "BEARISH":
            mid = (support + resistance) / 2
            entry_low  = current
            entry_high = current + 100 if current < mid else current + 50
            target_1   = support
            target_2   = max_pe_strike
            stop_loss  = self.calculate_smart_stop_loss(current, support, resistance, "BEARISH")
            option_strategies = [
                {'name':'Long Put',        'market_bias':'Bearish','type':'Debit', 'risk':'High',
                 'max_profit':'Huge (to ₹0)','max_loss':'Premium Paid',
                 'description':f'Buy {atm_strike} PE','best_for':'Strong downward momentum expected'},
                {'name':'Bear Put Spread', 'market_bias':'Bearish','type':'Debit', 'risk':'Moderate',
                 'max_profit':'Capped',    'max_loss':'Premium Paid',
                 'description':f'Buy {atm_strike} PE, Sell {atm_strike-200} PE','best_for':'Moderate downside with limited risk'},
                {'name':'Bear Call Spread','market_bias':'Bearish','type':'Credit','risk':'Moderate',
                 'max_profit':'Premium Received','max_loss':'Capped',
                 'description':f'Sell {atm_strike+100} CE, Buy {atm_strike+200} CE','best_for':'Expect market to stay below resistance'},
            ]
        else:
            entry_low  = support
            entry_high = resistance
            target_1   = resistance
            target_2   = support
            stop_loss  = None
            option_strategies = [
                {'name':'Iron Condor',    'market_bias':'Neutral', 'type':'Credit','risk':'Low',
                 'max_profit':'Premium Received','max_loss':'Capped',
                 'description':f'Sell {atm_strike+100} CE + Buy {atm_strike+200} CE, Sell {atm_strike-100} PE + Buy {atm_strike-200} PE',
                 'best_for':'Expect low volatility, range-bound market'},
                {'name':'Iron Butterfly', 'market_bias':'Neutral', 'type':'Credit','risk':'Low',
                 'max_profit':'Premium Received','max_loss':'Capped',
                 'description':f'Sell {atm_strike} CE + Sell {atm_strike} PE, Buy {atm_strike+100} CE + Buy {atm_strike-100} PE',
                 'best_for':'Expect price to remain near ATM strike'},
                {'name':'Short Straddle', 'market_bias':'Neutral', 'type':'Credit','risk':'Very High',
                 'max_profit':'Premium Received','max_loss':'Unlimited',
                 'description':f'Sell {atm_strike} CE + Sell {atm_strike} PE','best_for':'ONLY for experienced traders!'},
                {'name':'Long Strangle',  'market_bias':'Volatile','type':'Debit', 'risk':'High',
                 'max_profit':'Unlimited','max_loss':'Premium Paid',
                 'description':f'Buy {atm_strike+100} CE + Buy {atm_strike-100} PE','best_for':'Expect big move but unsure of direction'},
            ]

        if stop_loss and bias != "SIDEWAYS":
            risk_points       = abs(current - stop_loss)
            reward_points     = abs(target_1 - current)
            risk_reward_ratio = round(reward_points / risk_points, 2) if risk_points > 0 else 0
        else:
            risk_points = reward_points = risk_reward_ratio = 0

        # ── RSI progress bar (0-100 scale)
        rsi_pct = min(100, max(0, rsi))

        # ── SMA bars: % distance from price (capped ±5%)
        def sma_bar(sma_val):
            diff = (current - sma_val) / sma_val * 100
            return min(100, max(0, 50 + diff * 10))

        # ── MACD bar (center at 50, scale ±50)
        macd_val  = technical['macd']
        macd_pct  = min(100, max(0, 50 + macd_val * 2))

        # ── PCR bar (0–2 scale → 0–100%)
        pcr_pct   = min(100, max(0, (option_analysis['pcr_oi'] / 2 * 100))) if option_analysis else 50

        # ── Max Pain bar (relative to support/resistance range)
        if option_analysis:
            rng     = resistance - support if resistance != support else 1
            mp_pct  = min(100, max(0, (option_analysis['max_pain'] - support) / rng * 100))
            # Call/Put OI bars relative to each other
            total_oi     = option_analysis['total_ce_oi'] + option_analysis['total_pe_oi']
            ce_oi_pct    = min(100, max(0, option_analysis['total_ce_oi'] / total_oi * 100)) if total_oi > 0 else 50
            pe_oi_pct    = 100 - ce_oi_pct
        else:
            mp_pct = ce_oi_pct = pe_oi_pct = 50

        self.html_data = {
            'timestamp':      ist_now.strftime('%d-%b-%Y %H:%M IST'),
            'current_price':  current,
            'expiry':         option_analysis['expiry'] if option_analysis else 'N/A',
            'atm_strike':     atm_strike,
            'bias':           bias,
            'bias_icon':      bias_icon,
            'bias_class':     bias_class,
            'confidence':     confidence,
            'bullish_score':  bullish_score,
            'bearish_score':  bearish_score,

            'rsi':            rsi,
            'rsi_pct':        rsi_pct,
            'rsi_status':     rsi_status,
            'rsi_badge':      rsi_badge,
            'rsi_icon':       rsi_icon,

            'sma_20':         technical['sma_20'],
            'sma_20_above':   current > technical['sma_20'],
            'sma_20_pct':     sma_bar(technical['sma_20']),

            'sma_50':         technical['sma_50'],
            'sma_50_above':   current > technical['sma_50'],
            'sma_50_pct':     sma_bar(technical['sma_50']),

            'sma_200':        technical['sma_200'],
            'sma_200_above':  current > technical['sma_200'],
            'sma_200_pct':    sma_bar(technical['sma_200']),

            'macd':           technical['macd'],
            'macd_signal':    technical['signal'],
            'macd_bullish':   macd_bullish,
            'macd_pct':       macd_pct,

            'pcr':            option_analysis['pcr_oi'] if option_analysis else 0,
            'pcr_pct':        pcr_pct,
            'pcr_status':     pcr_status,
            'pcr_badge':      pcr_badge,
            'pcr_icon':       pcr_icon,

            'max_pain':       option_analysis['max_pain']           if option_analysis else 0,
            'max_pain_pct':   mp_pct,
            'max_ce_oi':      max_ce_strike,
            'max_pe_oi':      max_pe_strike,
            'ce_oi_pct':      ce_oi_pct,
            'pe_oi_pct':      pe_oi_pct,

            'total_ce_oi_change': option_analysis['total_ce_oi_change'] if option_analysis else 0,
            'total_pe_oi_change': option_analysis['total_pe_oi_change'] if option_analysis else 0,
            'net_oi_change':      option_analysis['net_oi_change']       if option_analysis else 0,
            'oi_direction':       option_analysis['oi_direction']        if option_analysis else 'N/A',
            'oi_signal':          option_analysis['oi_signal']           if option_analysis else 'N/A',
            'oi_icon':            option_analysis['oi_icon']             if option_analysis else '🟡',
            'oi_class':           option_analysis['oi_class']            if option_analysis else 'neutral',

            'support':            support,
            'resistance':         resistance,
            'strong_support':     support    - 100,
            'strong_resistance':  resistance + 100,

            'strategy_type':  bias,
            'entry_low':      entry_low,
            'entry_high':     entry_high,
            'target_1':       target_1,
            'target_2':       target_2,
            'stop_loss':      stop_loss,
            'risk_points':    int(risk_points),
            'reward_points':  int(reward_points),
            'risk_reward_ratio': risk_reward_ratio,

            'option_strategies':               option_strategies,
            'recommended_technical_strategy':  self.select_best_technical_strategy(bias, option_strategies),
            'recommended_oi_strategy':         self.select_best_oi_strategy(
                option_analysis['oi_direction'] if option_analysis else 'Neutral', atm_strike
            ) if option_analysis else None,

            'top_ce_strikes':  option_analysis['top_ce_strikes'] if option_analysis else [],
            'top_pe_strikes':  option_analysis['top_pe_strikes'] if option_analysis else [],
            'has_option_data': option_analysis is not None,
        }

    # ─────────────────────────────────────────────
    #  HTML GENERATION
    # ─────────────────────────────────────────────
    def _bar_color_class(self, badge):
        """Return CSS bar class based on badge type."""
        return {'bullish':'bar-teal','bearish':'bar-red','neutral':'bar-gold'}.get(badge,'bar-teal')

    def _stat_card(self, icon, label, value, badge_text, badge_class, bar_pct, bar_type, sub_text=""):
        """
        Render one Glassmorphism Stat Card + Progress Bar tile.
        bar_type: 'bar-teal' | 'bar-red' | 'bar-gold' | 'bar-grn'
        """
        tag_map = {
            'bullish': ('tag-bull', '#00e5ff'),
            'bearish': ('tag-bear', '#ff5252'),
            'neutral': ('tag-neu',  '#ffb74d'),
        }
        tag_cls, _  = tag_map.get(badge_class, tag_map['neutral'])
        hi_cls      = 'g-hi' if badge_class == 'bullish' else ('g-red' if badge_class == 'bearish' else '')
        sub_html    = f'<div class="sub">{sub_text}</div>' if sub_text else ''
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

    def generate_html_email(self):
        d = self.html_data

        # ── bar color helpers
        sma20_bar  = 'bar-teal' if d['sma_20_above']  else 'bar-red'
        sma50_bar  = 'bar-teal' if d['sma_50_above']  else 'bar-red'
        sma200_bar = 'bar-teal' if d['sma_200_above'] else 'bar-red'
        macd_bar   = 'bar-teal' if d['macd_bullish']  else 'bar-red'
        pcr_bar    = self._bar_color_class(d['pcr_badge'])

        sma20_badge  = 'bullish' if d['sma_20_above']  else 'bearish'
        sma50_badge  = 'bullish' if d['sma_50_above']  else 'bearish'
        sma200_badge = 'bullish' if d['sma_200_above'] else 'bearish'
        macd_badge   = 'bullish' if d['macd_bullish']  else 'bearish'
        sma20_lbl    = 'Above'   if d['sma_20_above']  else 'Below'
        sma50_lbl    = 'Above'   if d['sma_50_above']  else 'Below'
        sma200_lbl   = 'Above'   if d['sma_200_above'] else 'Below'
        macd_lbl     = 'Bullish' if d['macd_bullish']  else 'Bearish'
        sma20_ico    = '✅'      if d['sma_20_above']  else '❌'
        sma50_ico    = '✅'      if d['sma_50_above']  else '❌'
        sma200_ico   = '✅'      if d['sma_200_above'] else '❌'
        macd_ico     = '🟢'      if d['macd_bullish']  else '🔴'

        # ── build technical indicator cards
        tech_cards = (
            self._stat_card(d['rsi_icon'], 'RSI (14)',  f"{d['rsi']:.1f}",
                            d['rsi_status'], d['rsi_badge'], d['rsi_pct'], 'bar-gold', '14-period momentum') +
            self._stat_card(sma20_ico,  'SMA 20',  f"₹{d['sma_20']:,.0f}",
                            sma20_lbl,  sma20_badge,  d['sma_20_pct'],  sma20_bar,  '20-day average') +
            self._stat_card(sma50_ico,  'SMA 50',  f"₹{d['sma_50']:,.0f}",
                            sma50_lbl,  sma50_badge,  d['sma_50_pct'],  sma50_bar,  '50-day average') +
            self._stat_card(sma200_ico, 'SMA 200', f"₹{d['sma_200']:,.0f}",
                            sma200_lbl, sma200_badge, d['sma_200_pct'], sma200_bar, '200-day average') +
            self._stat_card(macd_ico,   'MACD',    f"{d['macd']:.2f}",
                            macd_lbl,   macd_badge,   d['macd_pct'],    macd_bar,   f"Signal: {d['macd_signal']:.2f}")
        )

        # ── build option chain cards
        if d['has_option_data']:
            ce_badge = 'bearish'; pe_badge = 'bullish'
            oc_cards = (
                self._stat_card(d['pcr_icon'], 'PCR Ratio (OI)', f"{d['pcr']:.3f}",
                                d['pcr_status'], d['pcr_badge'], d['pcr_pct'], pcr_bar, 'Put/Call OI ratio') +
                self._stat_card('🎯', 'Max Pain', f"₹{d['max_pain']:,}",
                                'Expiry Magnet', 'neutral', d['max_pain_pct'], 'bar-gold', 'Price gravity level') +
                self._stat_card('🔴', 'Max Call OI', f"₹{d['max_ce_oi']:,}",
                                'Resistance', ce_badge, d['ce_oi_pct'], 'bar-red', 'CE wall') +
                self._stat_card('🟢', 'Max Put OI', f"₹{d['max_pe_oi']:,}",
                                'Support', pe_badge, d['pe_oi_pct'], 'bar-teal', 'PE floor')
            )
        else:
            oc_cards = '<div style="color:#80deea;padding:20px;">Option chain data unavailable</div>'

        # ── key levels
        _ss  = d['strong_support']
        _sr  = d['strong_resistance']
        _rng = _sr - _ss if _sr != _ss else 1

        def _pct_real(val):
            return round(max(3, min(97, (val - _ss) / _rng * 100)), 2)

        _pct_cp      = _pct_real(d['current_price'])
        _pts_to_res  = int(d['resistance']    - d['current_price'])
        _pts_to_sup  = int(d['current_price'] - d['support'])

        _mp_node = ""
        if d['has_option_data']:
            _mp_node = f"""
              <div class="rl-node-b" style="left:43%;">
                <div class="rl-dot" style="background:#ffb74d;box-shadow:0 0 8px #ffb74d;margin:0 auto 5px;"></div>
                <div class="rl-lbl" style="color:#ffb74d;">Max Pain</div>
                <div class="rl-val" style="color:#ffb74d;">₹{d['max_pain']:,}</div>
              </div>"""

        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nifty 50 Daily Report</title>
    <link href="https://fonts.googleapis.com/css2?family=Oxanium:wght@400;600;700;800&family=Rajdhani:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        /* ── RESET & BASE ── */
        *{{margin:0;padding:0;box-sizing:border-box;}}
        body{{
            font-family:'Rajdhani',sans-serif;
            background:linear-gradient(135deg,#0f2027 0%,#203a43 50%,#2c5364 100%);
            min-height:100vh; padding:20px; color:#b0bec5;
        }}
        .container{{
            max-width:1200px; margin:0 auto;
            background:rgba(15,32,39,0.85);
            backdrop-filter:blur(20px);
            border-radius:20px; overflow:hidden;
            box-shadow:0 20px 60px rgba(0,0,0,0.5);
            border:1px solid rgba(79,195,247,0.18);
        }}

        /* ── HEADER ── */
        .header{{
            background:linear-gradient(135deg,#0f2027,#203a43);
            padding:40px 30px; text-align:center;
            border-bottom:2px solid rgba(79,195,247,0.3);
            position:relative; overflow:hidden;
        }}
        .header::before{{
            content:''; position:absolute; inset:0;
            background:radial-gradient(circle at 50% 50%,rgba(79,195,247,0.08) 0%,transparent 70%);
            pointer-events:none;
        }}
        .header h1{{
            font-family:'Oxanium',sans-serif;
            font-size:30px; font-weight:800; color:#4fc3f7;
            text-shadow:0 0 30px rgba(79,195,247,0.5);
            letter-spacing:2px; position:relative; z-index:1;
        }}
        .header p{{color:#80deea;font-size:13px;margin-top:8px;position:relative;z-index:1;}}

        /* ── SECTIONS ── */
        .section{{padding:28px 26px;border-bottom:1px solid rgba(79,195,247,0.08);}}
        .section:last-child{{border-bottom:none;}}
        .section-title{{
            font-family:'Oxanium',sans-serif;
            font-size:13px; font-weight:700; letter-spacing:2.5px; color:#4fc3f7;
            text-transform:uppercase; display:flex; align-items:center; gap:10px;
            margin-bottom:20px; padding-bottom:12px;
            border-bottom:1px solid rgba(79,195,247,0.18);
        }}
        .section-title span{{font-size:18px;}}

        /* ── GLASS CARD BASE ── */
        .g{{
            background:rgba(255,255,255,0.04);
            backdrop-filter:blur(20px);
            -webkit-backdrop-filter:blur(20px);
            border:1px solid rgba(79,195,247,0.18);
            border-radius:16px;
            position:relative; overflow:hidden;
            transition:all 0.35s cubic-bezier(0.4,0,0.2,1);
        }}
        /* top shimmer line */
        .g::before{{
            content:''; position:absolute; top:0; left:0; right:0; height:1px;
            background:linear-gradient(90deg,transparent,rgba(255,255,255,0.25),transparent);
            z-index:1;
        }}
        /* sweep shimmer on hover */
        .g::after{{
            content:''; position:absolute; top:-60%; left:-30%; width:50%; height:200%;
            background:linear-gradient(105deg,transparent,rgba(255,255,255,0.04),transparent);
            transform:skewX(-15deg); transition:left 0.6s ease; z-index:0;
        }}
        .g:hover::after{{left:130%;}}
        .g:hover{{
            background:rgba(79,195,247,0.09);
            border-color:rgba(79,195,247,0.45);
            box-shadow:0 12px 40px rgba(0,0,0,0.35),inset 0 1px 0 rgba(255,255,255,0.1);
            transform:translateY(-4px);
        }}
        .g-hi{{background:rgba(79,195,247,0.09);border-color:rgba(79,195,247,0.35);}}
        .g-red{{background:rgba(244,67,54,0.06);border-color:rgba(244,67,54,0.25);}}
        .g-red:hover{{background:rgba(244,67,54,0.1);border-color:rgba(244,67,54,0.45);}}

        /* ── STAT CARD + BAR (Layout 4) ── */
        .card-grid{{display:grid;gap:14px;}}
        .grid-5{{grid-template-columns:repeat(5,1fr);}}
        .grid-4{{grid-template-columns:repeat(4,1fr);}}

        .g .card-top-row{{
            display:flex; align-items:center; gap:10px;
            margin-bottom:10px; position:relative; z-index:2;
        }}
        .card-ico{{font-size:22px;line-height:1;}}
        .lbl{{
            font-size:9px; letter-spacing:2.5px; color:rgba(128,222,234,0.65);
            text-transform:uppercase; font-weight:600; line-height:1.3;
        }}
        .val{{
            font-family:'Oxanium',sans-serif; font-size:24px; font-weight:700;
            color:#fff; display:block; margin-bottom:10px; position:relative; z-index:2;
            padding:0 16px;
        }}

        /* progress bar */
        .bar-wrap{{
            height:5px; background:rgba(0,0,0,0.35);
            border-radius:3px; margin:0 16px 12px; overflow:hidden;
            position:relative; z-index:2;
        }}
        .bar-fill{{height:100%;border-radius:3px;transition:width 1.2s cubic-bezier(0.4,0,0.2,1);}}
        .bar-teal{{background:linear-gradient(90deg,#00bcd4,#4fc3f7);box-shadow:0 0 8px rgba(79,195,247,0.6);}}
        .bar-red {{background:linear-gradient(90deg,#f44336,#ff5722);box-shadow:0 0 8px rgba(244,67,54,0.5);}}
        .bar-gold{{background:linear-gradient(90deg,#ffb74d,#ffd54f);box-shadow:0 0 8px rgba(255,183,77,0.5);}}
        .bar-grn {{background:linear-gradient(90deg,#00e676,#00bcd4);box-shadow:0 0 8px rgba(0,230,118,0.5);}}

        /* card footer: sub-text + badge */
        .card-foot{{
            display:flex; justify-content:space-between; align-items:center;
            padding:0 16px 14px; position:relative; z-index:2;
        }}
        .sub{{font-size:10px;color:#455a64;font-family:'JetBrains Mono',monospace;}}

        /* badge pills */
        .tag{{
            display:inline-flex; align-items:center;
            padding:3px 11px; border-radius:20px; font-size:11px; font-weight:700;
            letter-spacing:0.5px; font-family:'Rajdhani',sans-serif;
        }}
        .tag-neu {{background:rgba(255,183,77,0.15); color:#ffb74d; border:1px solid rgba(255,183,77,0.35);}}
        .tag-bull{{background:rgba(0,229,255,0.12);  color:#00e5ff; border:1px solid rgba(0,229,255,0.35);}}
        .tag-bear{{background:rgba(255,82,82,0.12);  color:#ff5252; border:1px solid rgba(255,82,82,0.35);}}

        /* ── DIRECTION BOX ── */
        .direction-box{{
            padding:28px; border-radius:14px; text-align:center; margin:20px 0;
            border:2px solid #4fc3f7;
            background:rgba(79,195,247,0.06);
            backdrop-filter:blur(10px);
        }}
        .direction-box.bullish {{background:linear-gradient(135deg,#00bcd4,#26c6da);border-color:#00bcd4;box-shadow:0 0 30px rgba(0,188,212,0.35);}}
        .direction-box.bearish {{background:linear-gradient(135deg,#d32f2f,#f44336);border-color:#f44336;box-shadow:0 0 30px rgba(244,67,54,0.35);}}
        .direction-box.sideways{{background:linear-gradient(135deg,#ffa726,#ffb74d);border-color:#ffb74d;box-shadow:0 0 30px rgba(255,183,77,0.35);}}
        .direction-box.neutral {{background:rgba(79,195,247,0.08);border-color:#4fc3f7;}}
        .direction-title{{font-family:'Oxanium',sans-serif;font-size:28px;font-weight:800;margin-bottom:8px;color:#fff;}}
        .direction-box.bullish .direction-title,
        .direction-box.bearish .direction-title,
        .direction-box.sideways .direction-title{{color:#000;}}
        .direction-subtitle{{font-size:13px;opacity:0.9;color:#e0f7fa;font-weight:600;}}
        .direction-box.bullish .direction-subtitle,
        .direction-box.bearish .direction-subtitle,
        .direction-box.sideways .direction-subtitle{{color:#000;}}

        /* ── LOGIC BOX ── */
        .logic-box{{
            background:rgba(79,195,247,0.07);
            backdrop-filter:blur(8px);
            padding:16px 18px; border-radius:10px; margin-top:18px;
            border-left:4px solid #4fc3f7;
        }}
        .logic-box p{{font-size:13px;line-height:1.9;color:#80deea;}}
        .logic-box strong{{color:#4fc3f7;}}

        /* ── OI CHANGE CARDS ── */
        .oi-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-top:18px;}}

        /* ── KEY LEVELS ── */
        .rl-node-a{{position:absolute;bottom:0;transform:translateX(-50%);text-align:center;}}
        .rl-node-b{{position:absolute;top:0;transform:translateX(-50%);text-align:center;}}
        .rl-dot{{width:12px;height:12px;border-radius:50%;border:2px solid rgba(10,20,35,0.9);}}
        .rl-lbl{{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:0.6px;line-height:1.4;white-space:nowrap;color:#b0bec5;}}
        .rl-val{{font-size:13px;font-weight:700;color:#fff;white-space:nowrap;margin-top:2px;}}

        /* ── STRATEGY CARDS ── */
        .strat-card{{
            background:rgba(255,255,255,0.03);
            backdrop-filter:blur(16px);
            padding:24px; border-radius:14px; margin-bottom:18px;
            border:1.5px solid rgba(79,195,247,0.2);
            box-shadow:0 8px 20px rgba(0,0,0,0.25);
        }}
        .strat-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:14px;margin-bottom:14px;}}
        .strat-cell .cell-lbl{{font-size:9px;letter-spacing:2px;color:#80deea;text-transform:uppercase;margin-bottom:5px;}}
        .strat-cell .cell-val{{font-size:17px;font-weight:700;color:#fff;}}
        .setup-box{{background:rgba(15,32,39,0.6);padding:14px;border-radius:8px;margin-bottom:12px;}}
        .setup-box .setup-lbl{{font-size:11px;color:#4fc3f7;font-weight:700;margin-bottom:6px;}}
        .setup-box .setup-val{{font-size:14px;font-weight:600;color:#fff;}}
        .why-text{{font-size:13px;color:#80deea;}}
        .why-text strong{{color:#4fc3f7;}}
        .profit-loss-row{{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:14px;}}
        .pl-box{{padding:12px;border-radius:8px;}}
        .pl-box .pl-lbl{{font-size:9px;letter-spacing:2px;color:#80deea;text-transform:uppercase;margin-bottom:5px;}}
        .pl-box .pl-val{{font-size:14px;font-weight:700;}}
        .pl-profit{{background:rgba(0,188,212,0.1);border-left:3px solid #00bcd4;}}
        .pl-profit .pl-val{{color:#00bcd4;}}
        .pl-loss{{background:rgba(244,67,54,0.1);border-left:3px solid #f44336;}}
        .pl-loss .pl-val{{color:#f44336;}}

        /* ── FIRE ROW — KEY TRADING LEVELS ── */
        .fire-row{{
            background:rgba(12,6,0,0.75);
            backdrop-filter:blur(14px);
            -webkit-backdrop-filter:blur(14px);
            border:1px solid rgba(255,140,0,0.25);
            border-left:4px solid #ff8c00;
            border-radius:10px;
            margin-top:18px;
            padding:18px 22px;
            display:grid;
            grid-template-columns:1.4fr 1.6fr 1.6fr 1.8fr;
            gap:0;
            align-items:center;
            box-shadow:0 0 28px rgba(255,140,0,0.08), inset 0 1px 0 rgba(255,140,0,0.08);
            transition:box-shadow 0.3s ease;
        }}
        .fire-row:hover{{
            box-shadow:0 0 40px rgba(255,140,0,0.15), inset 0 1px 0 rgba(255,140,0,0.12);
        }}
        .fire-col{{
            padding:4px 18px;
            border-right:1px solid rgba(255,140,0,0.12);
        }}
        .fire-col:first-child{{padding-left:6px;}}
        .fire-col:last-child{{border-right:none;}}
        .fire-heading{{
            display:flex; align-items:center; gap:8px;
            font-family:'Oxanium',sans-serif;
            font-size:11px; font-weight:800;
            color:#ff8c00; letter-spacing:2.5px;
            text-transform:uppercase; line-height:1.4;
        }}
        .fire-col-label{{
            font-size:9px; letter-spacing:2px; color:rgba(255,140,0,0.5);
            text-transform:uppercase; font-weight:700;
            margin-bottom:7px; font-family:'Rajdhani',sans-serif;
        }}
        .fire-col-value{{
            font-family:'Oxanium',sans-serif;
            font-size:20px; font-weight:800;
            color:#ff8c00; letter-spacing:0.5px;
            line-height:1.2;
        }}
        .fire-col-value.stop-text{{
            font-size:13px; font-weight:700; color:#ff8c00;
            line-height:1.5; opacity:0.85;
        }}
        .fire-col-value.stop-price{{
            color:#f44336; font-size:20px;
        }}
        .fire-rr{{
            margin-top:6px;
            font-size:10px; color:rgba(255,140,0,0.45);
            font-family:'JetBrains Mono',monospace; letter-spacing:1px;
        }}

        /* ── STRIKES TABLE ── */
        .strikes-table{{width:100%;border-collapse:collapse;margin-top:18px;border-radius:10px;overflow:hidden;}}
        .strikes-table th{{
            background:linear-gradient(135deg,#4fc3f7,#26c6da);
            color:#000;padding:14px;text-align:left;font-weight:700;font-size:12px;text-transform:uppercase;
        }}
        .strikes-table td{{padding:14px;border-bottom:1px solid rgba(79,195,247,0.08);color:#b0bec5;font-size:13px;}}
        .strikes-table tr:hover{{background:rgba(79,195,247,0.06);}}
        .strikes-table tbody tr:last-child td{{border-bottom:none;}}

        /* ── MARKET SNAPSHOT CARDS ── */
        .snap-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;}}
        .snap-card{{padding:18px 16px;}}
        .snap-card .card-top-row{{margin-bottom:8px;}}
        .snap-card .val{{font-size:26px;padding:0;margin-bottom:0;}}

        /* ── DISCLAIMER / FOOTER ── */
        .disclaimer{{
            background:rgba(255,183,77,0.1);
            backdrop-filter:blur(8px);
            padding:22px; border-radius:12px;
            border-left:4px solid #ffb74d;
            font-size:13px; color:#ffb74d; line-height:1.8;
        }}
        .footer{{text-align:center;padding:24px;color:#546e7a;font-size:12px;background:rgba(10,20,28,0.4);}}

        /* ── RESPONSIVE ── */
        @media(max-width:900px){{
            .grid-5{{grid-template-columns:repeat(2,1fr);}}
            .grid-4{{grid-template-columns:repeat(2,1fr);}}
            .snap-grid{{grid-template-columns:1fr;}}
            .oi-grid{{grid-template-columns:1fr;}}
        }}
        @media(max-width:480px){{
            .grid-5,.grid-4{{grid-template-columns:1fr;}}
        }}
    </style>
</head>
<body>
<div class="container">

    <!-- ── HEADER ── -->
    <div class="header">
        <h1>📊 NIFTY 50 DAILY REPORT</h1>
        <p>Generated: {d['timestamp']}</p>
    </div>

    <!-- ── MARKET SNAPSHOT ── -->
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
                <span class="val" style="font-size:20px">{d['expiry']}</span>
            </div>
        </div>
    </div>

    <!-- ── MARKET DIRECTION ── -->
    <div class="section">
        <div class="section-title"><span>🧭</span> MARKET DIRECTION (Algorithmic)</div>
        <div class="direction-box {d['bias_class']}">
            <div class="direction-title">{d['bias_icon']} {d['bias']}</div>
            <div class="direction-subtitle">Confidence: {d['confidence']} &nbsp;|&nbsp; Bullish: {d['bullish_score']} vs Bearish: {d['bearish_score']}</div>
        </div>
        <div class="logic-box">
            <p>
                <strong>📊 Scoring Logic:</strong><br>
                • <strong>BULLISH</strong>: Diff ≥ +3 · Price above SMAs, oversold RSI, +MACD, PCR &gt; 1.2<br>
                • <strong>BEARISH</strong>: Diff ≤ −3 · Price below SMAs, overbought RSI, −MACD, PCR &lt; 0.7<br>
                • <strong>SIDEWAYS</strong>: Diff −2 to +2 · Mixed signals, consolidation<br>
                • <strong>Confidence</strong>: HIGH when gap ≥ 4 | OI scope: ATM ±10 strikes only
            </p>
        </div>
    </div>

    <!-- ── TECHNICAL INDICATORS (Stat Card + Bar) ── -->
    <div class="section">
        <div class="section-title"><span>🔍</span> TECHNICAL INDICATORS</div>
        <div class="card-grid grid-5">
            {tech_cards}
        </div>
    </div>
"""

        # ── OPTION CHAIN SECTION
        if d['has_option_data']:
            html += f"""
    <div class="section">
        <div class="section-title">
            <span>🎯</span> OPTION CHAIN ANALYSIS
            <span style="font-size:11px;color:#80deea;font-weight:400;letter-spacing:1px;">(ATM ±10 Strikes Only)</span>
        </div>
        <div class="card-grid grid-4">
            {oc_cards}
        </div>
    </div>

    <div class="section">
        <div class="section-title">
            <span>📊</span> CHANGE IN OPEN INTEREST
            <span style="font-size:11px;color:#80deea;font-weight:400;letter-spacing:1px;">(Today's Direction · ATM ±10 Only)</span>
        </div>
        <div class="direction-box {d['oi_class']}" style="margin:0 0 18px;">
            <div class="direction-title" style="font-size:24px;">{d['oi_icon']} {d['oi_direction']}</div>
            <div class="direction-subtitle">{d['oi_signal']}</div>
        </div>
        <div class="oi-grid">
"""
            # Call OI change card
            ce_chg_badge  = 'bearish' if d['total_ce_oi_change'] > 0 else 'bullish'
            ce_chg_lbl    = 'Bearish Signal' if d['total_ce_oi_change'] > 0 else 'Bullish Signal'
            ce_chg_ico    = '🔴' if d['total_ce_oi_change'] > 0 else '🟢'
            ce_chg_bar    = 'bar-red' if d['total_ce_oi_change'] > 0 else 'bar-teal'
            ce_chg_pct    = min(100, abs(d['total_ce_oi_change']) / 50000 * 100) if d['total_ce_oi_change'] != 0 else 5

            pe_chg_badge  = 'bullish' if d['total_pe_oi_change'] > 0 else 'bearish'
            pe_chg_lbl    = 'Bullish Signal' if d['total_pe_oi_change'] > 0 else 'Bearish Signal'
            pe_chg_ico    = '🟢' if d['total_pe_oi_change'] > 0 else '🔴'
            pe_chg_bar    = 'bar-teal' if d['total_pe_oi_change'] > 0 else 'bar-red'
            pe_chg_pct    = min(100, abs(d['total_pe_oi_change']) / 50000 * 100) if d['total_pe_oi_change'] != 0 else 5

            net_badge     = 'bullish' if d['net_oi_change'] > 0 else ('bearish' if d['net_oi_change'] < 0 else 'neutral')
            net_lbl       = 'Bullish Net' if d['net_oi_change'] > 0 else ('Bearish Net' if d['net_oi_change'] < 0 else 'Balanced')
            net_bar       = 'bar-teal' if d['net_oi_change'] > 0 else ('bar-red' if d['net_oi_change'] < 0 else 'bar-gold')
            net_pct       = min(100, abs(d['net_oi_change']) / 50000 * 100) if d['net_oi_change'] != 0 else 5

            html += (
                self._stat_card(ce_chg_ico, 'CALL OI CHANGE', f"{d['total_ce_oi_change']:+,}",
                                ce_chg_lbl, ce_chg_badge, ce_chg_pct, ce_chg_bar, 'CE open interest Δ') +
                self._stat_card(pe_chg_ico, 'PUT OI CHANGE',  f"{d['total_pe_oi_change']:+,}",
                                pe_chg_lbl, pe_chg_badge, pe_chg_pct, pe_chg_bar, 'PE open interest Δ') +
                self._stat_card('⚖️', 'NET OI CHANGE', f"{d['net_oi_change']:+,}",
                                net_lbl, net_badge, net_pct, net_bar, 'PE Δ − CE Δ')
            )

            html += f"""
        </div>
        <div class="logic-box">
            <p>
                <strong>📖 How to Read:</strong><br>
                • <strong>Call OI +</strong> = Writers selling calls (Bearish) &nbsp;|&nbsp; <strong>Call OI −</strong> = Unwinding (Bullish)<br>
                • <strong>Put OI +</strong>  = Writers selling puts (Bullish) &nbsp;|&nbsp; <strong>Put OI −</strong> = Unwinding (Bearish)<br>
                • <strong>Net OI</strong> = Put Δ − Call Δ &nbsp;(Positive = Bullish, Negative = Bearish)
            </p>
        </div>
    </div>
"""

        # ── KEY LEVELS
        html += f"""
    <div class="section">
        <div class="section-title"><span>📊</span> KEY LEVELS</div>
        <div style="display:flex;justify-content:space-between;margin-bottom:8px;">
            <span style="font-size:11px;color:#26c6da;font-weight:700;letter-spacing:1px;">◄ SUPPORT ZONE</span>
            <span style="font-size:11px;color:#f44336;font-weight:700;letter-spacing:1px;">RESISTANCE ZONE ►</span>
        </div>
        <!-- ROW A -->
        <div style="position:relative;height:62px;">
            <div class="rl-node-a" style="left:3%;">
                <div class="rl-lbl" style="color:#26c6da;">Strong<br>Support</div>
                <div class="rl-val" style="color:#26c6da;">₹{d['strong_support']:,.0f}</div>
                <div class="rl-dot" style="background:#26c6da;margin:6px auto 0;"></div>
            </div>
            <div class="rl-node-a" style="left:22%;">
                <div class="rl-lbl" style="color:#00bcd4;">Support</div>
                <div class="rl-val" style="color:#00bcd4;">₹{d['support']:,.0f}</div>
                <div class="rl-dot" style="background:#00bcd4;box-shadow:0 0 8px #00bcd4;margin:6px auto 0;"></div>
            </div>
            <div style="position:absolute;left:{_pct_cp}%;transform:translateX(-50%);
                        bottom:4px;background:#4fc3f7;color:#000;font-size:11px;font-weight:700;
                        padding:4px 13px;border-radius:6px;white-space:nowrap;z-index:10;
                        box-shadow:0 0 16px rgba(79,195,247,0.7);">
                ▼ NOW &nbsp;₹{d['current_price']:,.0f}
            </div>
            <div class="rl-node-a" style="left:75%;">
                <div class="rl-lbl" style="color:#ff7043;">Resistance</div>
                <div class="rl-val" style="color:#ff7043;">₹{d['resistance']:,.0f}</div>
                <div class="rl-dot" style="background:#ff7043;box-shadow:0 0 8px #ff7043;margin:6px auto 0;"></div>
            </div>
            <div class="rl-node-a" style="left:95%;">
                <div class="rl-lbl" style="color:#f44336;">Strong<br>Resistance</div>
                <div class="rl-val" style="color:#f44336;">₹{d['strong_resistance']:,.0f}</div>
                <div class="rl-dot" style="background:#f44336;margin:6px auto 0;"></div>
            </div>
        </div>
        <!-- GRADIENT TRACK -->
        <div style="position:relative;height:8px;border-radius:4px;
                    background:linear-gradient(90deg,#26c6da 0%,#00bcd4 20%,#4fc3f7 40%,#ffb74d 58%,#ff7043 76%,#f44336 100%);
                    box-shadow:0 2px 14px rgba(0,0,0,0.5);">
            <div style="position:absolute;left:{_pct_cp}%;top:50%;transform:translate(-50%,-50%);
                        width:4px;height:22px;background:#fff;border-radius:2px;
                        box-shadow:0 0 16px rgba(255,255,255,1);z-index:10;"></div>
        </div>
        <!-- ROW B -->
        <div style="position:relative;height:58px;">
            {_mp_node}
        </div>
        <!-- Distance bar -->
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:4px;">
            <div style="background:rgba(244,67,54,0.08);border:1px solid rgba(244,67,54,0.25);
                        border-radius:8px;padding:10px 16px;display:flex;justify-content:space-between;align-items:center;">
                <span style="font-size:12px;color:#b0bec5;">📍 Distance to Resistance</span>
                <span style="font-size:15px;font-weight:700;color:#f44336;">+{_pts_to_res:,} pts</span>
            </div>
            <div style="background:rgba(0,188,212,0.08);border:1px solid rgba(0,188,212,0.25);
                        border-radius:8px;padding:10px 16px;display:flex;justify-content:space-between;align-items:center;">
                <span style="font-size:12px;color:#b0bec5;">📍 Distance to Support</span>
                <span style="font-size:15px;font-weight:700;color:#00bcd4;">−{_pts_to_sup:,} pts</span>
            </div>
        </div>
    </div>
"""

        html += self._generate_recommendations_html(d)

        # ── TOP STRIKES TABLE
        if d['has_option_data'] and (d['top_ce_strikes'] or d['top_pe_strikes']):
            html += """
    <div class="section">
        <div class="section-title"><span>📋</span> TOP 5 STRIKES BY OPEN INTEREST
            <span style="font-size:11px;color:#80deea;font-weight:400;letter-spacing:1px;">(ATM ±10 Only)</span>
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;">
            <div>
                <h3 style="color:#00bcd4;margin-bottom:14px;font-size:15px;font-family:'Oxanium',sans-serif;">📞 CALL OPTIONS (CE)</h3>
                <table class="strikes-table">
                    <thead><tr><th>#</th><th>Strike</th><th>OI</th><th>LTP</th></tr></thead><tbody>
"""
            for i, s in enumerate(d['top_ce_strikes'], 1):
                html += f"<tr><td><strong>{i}</strong></td><td><strong>₹{int(s['Strike']):,}</strong></td><td>{int(s['CE_OI']):,}</td><td style='color:#00bcd4;font-weight:700;font-family:Oxanium,sans-serif;'>₹{s['CE_LTP']:.2f}</td></tr>\n"
            html += """</tbody></table></div>
            <div>
                <h3 style="color:#f44336;margin-bottom:14px;font-size:15px;font-family:'Oxanium',sans-serif;">📉 PUT OPTIONS (PE)</h3>
                <table class="strikes-table">
                    <thead><tr><th>#</th><th>Strike</th><th>OI</th><th>LTP</th></tr></thead><tbody>
"""
            for i, s in enumerate(d['top_pe_strikes'], 1):
                html += f"<tr><td><strong>{i}</strong></td><td><strong>₹{int(s['Strike']):,}</strong></td><td>{int(s['PE_OI']):,}</td><td style='color:#f44336;font-weight:700;font-family:Oxanium,sans-serif;'>₹{s['PE_LTP']:.2f}</td></tr>\n"
            html += """</tbody></table></div></div></div>
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
    <div class="footer">
        <p>Automated Nifty 50 Option Chain + Technical Analysis Report</p>
        <p style="margin-top:6px;">© 2026 · Glassmorphism UI · Deep Ocean Theme · For Educational Purposes Only</p>
    </div>
</div>
</body>
</html>
"""
        return html

    # ─────────────────────────────────────────────
    #  DUAL RECOMMENDATIONS
    # ─────────────────────────────────────────────
    def _generate_recommendations_html(self, d):
        html = """
    <div class="section">
        <div class="section-title"><span>💡</span> TRADING RECOMMENDATIONS (Dual Strategy)</div>
        <p style="color:#80deea;font-size:13px;margin-bottom:20px;line-height:1.7;">
            Two independent strategy recommendations based on <strong>Technical Analysis</strong> and <strong>OI Momentum</strong>.
        </p>
"""
        ts     = d['recommended_technical_strategy']
        ts_cls = 'positive' if 'Bull' in ts['name'] else ('negative' if 'Bear' in ts['name'] else 'neutral')
        ts_bdr = '#00bcd4' if ts_cls == 'positive' else ('#f44336' if ts_cls == 'negative' else '#ffb74d')
        tag_cls = 'tag-bull' if ts_cls == 'positive' else ('tag-bear' if ts_cls == 'negative' else 'tag-neu')

        html += f"""
        <div class="strat-card" style="border-color:{ts_bdr};">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:18px;flex-wrap:wrap;gap:10px;">
                <h3 style="color:#4fc3f7;font-family:'Oxanium',sans-serif;font-size:17px;margin:0;">1️⃣ TECHNICAL ANALYSIS STRATEGY</h3>
                <span style="background:rgba(79,195,247,0.15);color:#4fc3f7;padding:5px 14px;border-radius:20px;font-size:11px;font-weight:700;letter-spacing:1px;">Positional · 1–5 Days</span>
            </div>
            <div class="strat-grid">
                <div class="strat-cell"><div class="cell-lbl">Strategy</div><div class="cell-val">{ts['name']}</div></div>
                <div class="strat-cell"><div class="cell-lbl">Market Bias</div><span class="tag {tag_cls}">{ts['market_bias']}</span></div>
                <div class="strat-cell"><div class="cell-lbl">Type</div><div class="cell-val">{ts['type']}</div></div>
                <div class="strat-cell"><div class="cell-lbl">Risk</div><div class="cell-val" style="color:#ffb74d;">{ts['risk']}</div></div>
            </div>
            <div class="setup-box">
                <div class="setup-lbl">📋 SETUP</div>
                <div class="setup-val">{ts['description']}</div>
            </div>
            <div class="why-text"><strong>💡 Why?</strong> {ts['best_for']}</div>
            <div class="profit-loss-row">
                <div class="pl-box pl-profit"><div class="pl-lbl">MAX PROFIT</div><div class="pl-val">{ts['max_profit']}</div></div>
                <div class="pl-box pl-loss"><div class="pl-lbl">MAX LOSS</div><div class="pl-val">{ts['max_loss']}</div></div>
            </div>
        </div>
"""

        if d['recommended_oi_strategy']:
            oi     = d['recommended_oi_strategy']
            oi_cls = 'positive' if oi['market_bias'] == 'Bullish' else ('negative' if oi['market_bias'] == 'Bearish' else 'neutral')
            oi_bdr = '#00bcd4' if oi_cls == 'positive' else ('#f44336' if oi_cls == 'negative' else '#ffb74d')
            oi_tag = 'tag-bull' if oi_cls == 'positive' else ('tag-bear' if oi_cls == 'negative' else 'tag-neu')

            html += f"""
        <div class="strat-card" style="border-color:{oi_bdr};">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:18px;flex-wrap:wrap;gap:10px;">
                <h3 style="color:#4fc3f7;font-family:'Oxanium',sans-serif;font-size:17px;margin:0;">2️⃣ OI MOMENTUM STRATEGY</h3>
                <span style="background:rgba(255,183,77,0.15);color:#ffb74d;padding:5px 14px;border-radius:20px;font-size:11px;font-weight:700;letter-spacing:1px;">{oi.get('time_horizon','Intraday')}</span>
            </div>
            <div style="background:rgba(79,195,247,0.07);padding:12px;border-radius:8px;margin-bottom:14px;border-left:3px solid #4fc3f7;">
                <div style="color:#4fc3f7;font-size:11px;font-weight:700;letter-spacing:1px;margin-bottom:5px;">📊 OI SIGNAL</div>
                <div style="color:#fff;font-size:13px;">{oi.get('signal','Market signal detected')}</div>
            </div>
            <div class="strat-grid">
                <div class="strat-cell"><div class="cell-lbl">Strategy</div><div class="cell-val">{oi['name']}</div></div>
                <div class="strat-cell"><div class="cell-lbl">Market Bias</div><span class="tag {oi_tag}">{oi['market_bias']}</span></div>
                <div class="strat-cell"><div class="cell-lbl">Type</div><div class="cell-val">{oi['type']}</div></div>
                <div class="strat-cell"><div class="cell-lbl">Risk</div><div class="cell-val" style="color:#ffb74d;">{oi['risk']}</div></div>
            </div>
            <div class="setup-box">
                <div class="setup-lbl" style="color:#ffb74d;">📋 SETUP</div>
                <div class="setup-val">{oi['description']}</div>
            </div>
            <div class="why-text"><strong style="color:#ffb74d;">💡 Why?</strong> {oi['best_for']}</div>
            <div class="profit-loss-row">
                <div class="pl-box pl-profit"><div class="pl-lbl">MAX PROFIT</div><div class="pl-val">{oi['max_profit']}</div></div>
                <div class="pl-box pl-loss"><div class="pl-lbl">MAX LOSS</div><div class="pl-val">{oi['max_loss']}</div></div>
            </div>
        </div>
"""

        # ── build stop-loss column content
        if d['stop_loss']:
            sl_html = f"""
                <div class="fire-col-label">STOP LOSS</div>
                <div class="fire-col-value stop-price">₹{d['stop_loss']:,.0f}</div>
                <div class="fire-rr">Risk {d['risk_points']} pts &nbsp;·&nbsp; R:R 1:{d['risk_reward_ratio']}</div>"""
        else:
            sl_html = f"""
                <div class="fire-col-label">STOP LOSS</div>
                <div class="fire-col-value stop-text">Use option premium<br>as max loss</div>"""

        html += f"""
        <!-- ── FIRE ROW — KEY TRADING LEVELS ── -->
        <div class="fire-row">
            <!-- col 1: heading -->
            <div class="fire-col">
                <div class="fire-heading">📍 KEY<br>LEVELS</div>
            </div>
            <!-- col 2: entry zone -->
            <div class="fire-col">
                <div class="fire-col-label">ENTRY ZONE</div>
                <div class="fire-col-value">₹{d['entry_low']:,.0f}–₹{d['entry_high']:,.0f}</div>
            </div>
            <!-- col 3: targets -->
            <div class="fire-col">
                <div class="fire-col-label">TARGET 1 / 2</div>
                <div class="fire-col-value">₹{d['target_1']:,.0f} &nbsp;/&nbsp; ₹{d['target_2']:,.0f}</div>
            </div>
            <!-- col 4: stop loss -->
            <div class="fire-col">
                {sl_html}
            </div>
        </div>
    </div>
"""
        return html

    # ─────────────────────────────────────────────
    #  SAVE & EMAIL
    # ─────────────────────────────────────────────
    def save_html_to_file(self, filename='index.html'):
        try:
            print(f"\n📄 Saving HTML to {filename}...")
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self.generate_html_email())
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
            }
            with open('latest_report.json', 'w') as f:
                json.dump(metadata, f, indent=2)
            print("   ✅ Saved latest_report.json")
            return True
        except Exception as e:
            print(f"\n❌ Save failed: {e}")
            return False

    def send_html_email_report(self):
        gmail_user     = os.getenv('GMAIL_USER')
        gmail_password = os.getenv('GMAIL_APP_PASSWORD')
        recipient1     = os.getenv('RECIPIENT_EMAIL_1')
        recipient2     = os.getenv('RECIPIENT_EMAIL_2')
        if not all([gmail_user, gmail_password, recipient1, recipient2]):
            print("\n⚠️  Email credentials not set. Skipping.")
            return False
        try:
            ist_now = datetime.now(pytz.timezone('Asia/Kolkata'))
            msg = MIMEMultipart('alternative')
            msg['From']    = gmail_user
            msg['To']      = f"{recipient1}, {recipient2}"
            msg['Subject'] = f"📊 Nifty 50 OI & Technical Report — {ist_now.strftime('%d-%b-%Y %H:%M IST')}"
            msg.attach(MIMEText(self.generate_html_email(), 'html'))
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(gmail_user, gmail_password)
                server.send_message(msg)
            print("   ✅ Email sent!")
            return True
        except Exception as e:
            print(f"\n❌ Email failed: {e}")
            return False

    # ─────────────────────────────────────────────
    #  MAIN
    # ─────────────────────────────────────────────
    def generate_full_report(self):
        ist_now = datetime.now(pytz.timezone('Asia/Kolkata'))
        print("=" * 70)
        print("NIFTY 50 DAILY REPORT — GLASSMORPHISM UI · STAT CARD + BAR LAYOUT")
        print(f"Generated: {ist_now.strftime('%d-%b-%Y %H:%M IST')}")
        print("=" * 70)

        oc_data         = self.fetch_nse_option_chain_silent()
        option_analysis = self.analyze_option_chain_data(oc_data) if oc_data else None

        if option_analysis:
            print(f"✅ Option data | Expiry: {option_analysis['expiry']} | Spot: {option_analysis['underlying_value']}")
        else:
            print("⚠️  No option data — technical-only mode")

        print("\nFetching technical data...")
        technical = self.get_technical_data()
        self.generate_analysis_data(technical, option_analysis)
        return option_analysis


def main():
    try:
        print("\n🚀 Starting Nifty 50 Analysis...\n")
        analyzer = NiftyHTMLAnalyzer()
        analyzer.generate_full_report()
        print("\n" + "=" * 70)
        save_ok = analyzer.save_html_to_file('index.html')
        if save_ok:
            analyzer.send_html_email_report()
        else:
            print("\n⚠️  Skipping email due to save failure")
        print("\n✅ Done! Open index.html in your browser.\n")
    except Exception as e:
        print(f"\n❌ Critical Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
