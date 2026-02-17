"""
NIFTY 50 COMPLETE ANALYSIS - DEEP OCEAN THEME - ENHANCED CARD LAYOUT
FIXES:
  1. Expiry: TUESDAY weekly - always picks NEXT Tuesday (never today)
     e.g. If today is Tue 17-Feb → expiry = Tue 24-Feb
  2. Auto-fallback: if NSE returns empty, fetches real expiry list
  3. SIDEWAYS targets: T1=Resistance, T2=Support (distinct values)
  4. Stop loss fallback text for neutral strategies
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
        self.yf_symbol = "^NSEI"
        self.nse_symbol = "NIFTY"
        self.report_lines = []
        self.html_data = {}

    def log(self, message):
        print(message)
        self.report_lines.append(message)

    # ==================== NSE SESSION HELPER ====================

    def _make_nse_session(self):
        """Create a fresh NSE session with cookies"""
        headers = {
            "authority": "www.nseindia.com",
            "accept": "application/json, text/plain, */*",
            "user-agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
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

    # ==================== EXPIRY DETECTION ====================

    def get_upcoming_expiry_tuesday(self):
        """
        Always returns the NEXT Tuesday date (never today).
        Uses Python's date + calendar — no manual weekday math errors.

        Examples:
          Today = Tue 17-Feb  →  returns 24-Feb  (next Tuesday)
          Today = Wed 18-Feb  →  returns 24-Feb
          Today = Mon 23-Feb  →  returns 24-Feb
          Today = Tue 24-Feb  →  returns 03-Mar  (next Tuesday again)
        """
        ist_tz    = pytz.timezone('Asia/Kolkata')
        today_ist = datetime.now(ist_tz).date()

        weekday = today_ist.weekday()   # Mon=0, Tue=1, ..., Sun=6

        if weekday == 1:
            # Today IS Tuesday → always jump to next Tuesday (7 days ahead)
            days_ahead = 7
        else:
            # How many days until next Tuesday?
            days_ahead = (1 - weekday) % 7
            if days_ahead == 0:
                days_ahead = 7

        next_tuesday = today_ist + timedelta(days=days_ahead)
        expiry_str   = next_tuesday.strftime('%d-%b-%Y')

        print(f"  📅 Today (IST): {today_ist.strftime('%A %d-%b-%Y')} | Expiry: {expiry_str}")
        return expiry_str

    def fetch_available_expiries(self, session, headers):
        """Ask NSE for available expiry dates and return the nearest one"""
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

    # ==================== NSE OPTION CHAIN FETCH ====================

    def fetch_nse_option_chain_silent(self):
        """Fetch option chain — tries calculated Tuesday, falls back to NSE list"""
        session, headers = self._make_nse_session()

        selected_expiry = self.get_upcoming_expiry_tuesday()
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
        """Fetch option chain for a specific expiry. Returns dict or None."""
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
                    time.sleep(2)
                    continue

                json_data = resp.json()
                data      = json_data.get('records', {}).get('data', [])

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

                df         = pd.DataFrame(rows).sort_values('Strike').reset_index(drop=True)
                underlying = json_data.get('records', {}).get('underlyingValue', 0)
                print(f"    ✅ {len(df)} strikes | Underlying: {underlying}")

                return {'expiry': expiry, 'df': df, 'raw_data': data, 'underlying': underlying}

            except Exception as e:
                print(f"    ❌ Attempt {attempt} error: {e}")
                time.sleep(2)
        return None

    # ==================== OPTION CHAIN ANALYSIS ====================

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

        if total_ce_oi_change > 0 and total_pe_oi_change < 0:
            oi_direction, oi_signal, oi_icon, oi_class = "Strong Bearish", "Call Build-up + Put Unwinding", "🔴", "bearish"
        elif total_ce_oi_change < 0 and total_pe_oi_change > 0:
            oi_direction, oi_signal, oi_icon, oi_class = "Strong Bullish", "Put Build-up + Call Unwinding", "🟢", "bullish"
        elif total_ce_oi_change > 0 and total_pe_oi_change > 0:
            if total_pe_oi_change > total_ce_oi_change * 1.5:
                oi_direction, oi_signal, oi_icon, oi_class = "Bullish", "Put Build-up Dominant", "🟢", "bullish"
            elif total_ce_oi_change > total_pe_oi_change * 1.5:
                oi_direction, oi_signal, oi_icon, oi_class = "Bearish", "Call Build-up Dominant", "🔴", "bearish"
            else:
                oi_direction, oi_signal, oi_icon, oi_class = "Neutral (High Volatility)", "Both Calls & Puts Building", "🟡", "neutral"
        elif total_ce_oi_change < 0 and total_pe_oi_change < 0:
            oi_direction, oi_signal, oi_icon, oi_class = "Neutral (Unwinding)", "Both Calls & Puts Unwinding", "🟡", "neutral"
        else:
            if net_oi_change > 0:
                oi_direction, oi_signal, oi_icon, oi_class = "Moderately Bullish", "Net Put Accumulation", "🟢", "bullish"
            elif net_oi_change < 0:
                oi_direction, oi_signal, oi_icon, oi_class = "Moderately Bearish", "Net Call Accumulation", "🔴", "bearish"
            else:
                oi_direction, oi_signal, oi_icon, oi_class = "Neutral", "Balanced OI Changes", "🟡", "neutral"

        max_ce_oi_row  = df.loc[df['CE_OI'].idxmax()]
        max_pe_oi_row  = df.loc[df['PE_OI'].idxmax()]
        df['pain']     = abs(df['CE_OI'] - df['PE_OI'])
        max_pain_row   = df.loc[df['pain'].idxmin()]
        df['Total_OI'] = df['CE_OI'] + df['PE_OI']

        top_ce_strikes = df.nlargest(5, 'CE_OI')[['Strike', 'CE_OI', 'CE_LTP']].to_dict('records')
        top_pe_strikes = df.nlargest(5, 'PE_OI')[['Strike', 'PE_OI', 'PE_LTP']].to_dict('records')

        return {
            'expiry':             oc_data['expiry'],
            'underlying_value':   oc_data['underlying'],
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

    # ==================== TECHNICAL ANALYSIS ====================

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
            print(f"✓ Technical done | Price: {technical['current_price']:.2f} | RSI: {technical['rsi']:.1f}")
            return technical

        except Exception as e:
            print(f"Technical analysis error: {e}")
            return None

    # ==================== STOP LOSS ====================

    def calculate_smart_stop_loss(self, current_price, support, resistance, bias):
        if bias == "BULLISH":
            return round(max(support - 30, current_price - 150), 0)
        elif bias == "BEARISH":
            return round(min(resistance + 30, current_price + 150), 0)
        return None

    # ==================== STRATEGY SELECTORS ====================

    def select_best_technical_strategy(self, bias, option_strategies):
        name_map = {"BULLISH": "Bull Call Spread", "BEARISH": "Bear Put Spread", "SIDEWAYS": "Iron Condor"}
        target   = name_map.get(bias, "")
        for s in option_strategies:
            if s['name'] == target:
                return s
        return option_strategies[0]

    def select_best_oi_strategy(self, oi_direction, atm_strike):
        if "Strong Bullish" in oi_direction or oi_direction == "Bullish":
            return {'name': 'Long Call', 'market_bias': 'Bullish', 'type': 'Debit', 'risk': 'High',
                    'max_profit': 'Unlimited', 'max_loss': 'Premium Paid',
                    'description': f'Buy {atm_strike} CE', 'best_for': 'Put build-up indicates bullish momentum',
                    'signal': '🟢 Institutional buying interest detected', 'time_horizon': 'Intraday to 1-2 days'}
        elif "Strong Bearish" in oi_direction or oi_direction == "Bearish":
            return {'name': 'Long Put', 'market_bias': 'Bearish', 'type': 'Debit', 'risk': 'High',
                    'max_profit': 'Huge (to ₹0)', 'max_loss': 'Premium Paid',
                    'description': f'Buy {atm_strike} PE', 'best_for': 'Call build-up indicates bearish momentum',
                    'signal': '🔴 Institutional selling interest detected', 'time_horizon': 'Intraday to 1-2 days'}
        elif "High Volatility" in oi_direction:
            return {'name': 'Long Straddle', 'market_bias': 'Volatile', 'type': 'Debit', 'risk': 'High',
                    'max_profit': 'Unlimited', 'max_loss': 'Premium Paid',
                    'description': f'Buy {atm_strike} CE + {atm_strike} PE',
                    'best_for': 'Both Calls & Puts building',
                    'signal': '🟡 Big move expected, direction uncertain', 'time_horizon': 'Intraday'}
        elif "Unwinding" in oi_direction:
            return {'name': 'Iron Butterfly', 'market_bias': 'Neutral', 'type': 'Credit', 'risk': 'Low',
                    'max_profit': 'Premium Received', 'max_loss': 'Capped',
                    'description': f'Sell {atm_strike} CE + PE, Buy {atm_strike+100} CE + {atm_strike-100} PE',
                    'best_for': 'Unwinding suggests reduced volatility',
                    'signal': '🟡 Position squaring, range-bound expected', 'time_horizon': 'Intraday'}
        else:
            return {'name': 'Vertical Spread', 'market_bias': 'Moderate', 'type': 'Debit', 'risk': 'Moderate',
                    'max_profit': 'Capped', 'max_loss': 'Limited',
                    'description': f'Vertical spread near {atm_strike}',
                    'best_for': 'Balanced OI changes',
                    'signal': '🟡 Moderate directional move expected', 'time_horizon': '1-2 days'}

    # ==================== MAIN ANALYSIS ====================

    def generate_analysis_data(self, technical, option_analysis):
        if not technical:
            self.log("⚠️  Technical data unavailable")
            return

        current    = technical['current_price']
        support    = technical['support']
        resistance = technical['resistance']
        ist_now    = datetime.now(pytz.timezone('Asia/Kolkata'))

        bullish_score = 0
        bearish_score = 0

        for sma in ['sma_20', 'sma_50', 'sma_200']:
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
        print(f"  📊 Score → Bullish: {bullish_score} | Bearish: {bearish_score} | Diff: {score_diff}")

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
        else:
            max_ce_strike = int(current/50)*50 + 200
            max_pe_strike = int(current/50)*50 - 200

        atm_strike = int(current/50)*50

        if bias == "BULLISH":
            mid        = (support + resistance) / 2
            entry_low  = current - 100 if current > mid else current - 50
            entry_high = current - 50  if current > mid else current
            target_1   = resistance
            target_2   = max_ce_strike
            stop_loss  = self.calculate_smart_stop_loss(current, support, resistance, "BULLISH")
            option_strategies = [
                {'name': 'Long Call',        'market_bias': 'Bullish', 'type': 'Debit',  'risk': 'High',
                 'max_profit': 'Unlimited',  'max_loss': 'Premium Paid',
                 'description': f'Buy {atm_strike} CE', 'best_for': 'Strong upward momentum expected'},
                {'name': 'Bull Call Spread',  'market_bias': 'Bullish', 'type': 'Debit',  'risk': 'Moderate',
                 'max_profit': 'Capped',     'max_loss': 'Premium Paid',
                 'description': f'Buy {atm_strike} CE, Sell {atm_strike+200} CE', 'best_for': 'Moderate upside with limited risk'},
                {'name': 'Bull Put Spread',   'market_bias': 'Bullish', 'type': 'Credit', 'risk': 'Moderate',
                 'max_profit': 'Premium Received', 'max_loss': 'Capped',
                 'description': f'Sell {atm_strike-100} PE, Buy {atm_strike-200} PE', 'best_for': 'Expect market to stay above support'},
            ]

        elif bias == "BEARISH":
            mid        = (support + resistance) / 2
            entry_low  = current
            entry_high = current + 100 if current < mid else current + 50
            target_1   = support
            target_2   = max_pe_strike
            stop_loss  = self.calculate_smart_stop_loss(current, support, resistance, "BEARISH")
            option_strategies = [
                {'name': 'Long Put',          'market_bias': 'Bearish', 'type': 'Debit',  'risk': 'High',
                 'max_profit': 'Huge (to ₹0)', 'max_loss': 'Premium Paid',
                 'description': f'Buy {atm_strike} PE', 'best_for': 'Strong downward momentum expected'},
                {'name': 'Bear Put Spread',   'market_bias': 'Bearish', 'type': 'Debit',  'risk': 'Moderate',
                 'max_profit': 'Capped',      'max_loss': 'Premium Paid',
                 'description': f'Buy {atm_strike} PE, Sell {atm_strike-200} PE', 'best_for': 'Moderate downside with limited risk'},
                {'name': 'Bear Call Spread',  'market_bias': 'Bearish', 'type': 'Credit', 'risk': 'Moderate',
                 'max_profit': 'Premium Received', 'max_loss': 'Capped',
                 'description': f'Sell {atm_strike+100} CE, Buy {atm_strike+200} CE', 'best_for': 'Expect market to stay below resistance'},
            ]

        else:  # SIDEWAYS
            entry_low  = support
            entry_high = resistance
            target_1   = resistance
            target_2   = support
            stop_loss  = None
            option_strategies = [
                {'name': 'Iron Condor',    'market_bias': 'Neutral',  'type': 'Credit', 'risk': 'Low',
                 'max_profit': 'Premium Received', 'max_loss': 'Capped',
                 'description': f'Sell {atm_strike+100} CE + Buy {atm_strike+200} CE, Sell {atm_strike-100} PE + Buy {atm_strike-200} PE',
                 'best_for': 'Expect low volatility, range-bound market'},
                {'name': 'Iron Butterfly', 'market_bias': 'Neutral',  'type': 'Credit', 'risk': 'Low',
                 'max_profit': 'Premium Received', 'max_loss': 'Capped',
                 'description': f'Sell {atm_strike} CE + Sell {atm_strike} PE, Buy {atm_strike+100} CE + Buy {atm_strike-100} PE',
                 'best_for': 'Expect price to remain near ATM strike'},
                {'name': 'Short Straddle', 'market_bias': 'Neutral',  'type': 'Credit', 'risk': 'Very High',
                 'max_profit': 'Premium Received', 'max_loss': 'Unlimited',
                 'description': f'Sell {atm_strike} CE + Sell {atm_strike} PE',
                 'best_for': 'ONLY for experienced traders!'},
                {'name': 'Long Strangle',  'market_bias': 'Volatile', 'type': 'Debit',  'risk': 'High',
                 'max_profit': 'Unlimited', 'max_loss': 'Premium Paid',
                 'description': f'Buy {atm_strike+100} CE + Buy {atm_strike-100} PE',
                 'best_for': 'Expect big move but unsure of direction'},
            ]

        if stop_loss and bias != "SIDEWAYS":
            risk_points       = abs(current - stop_loss)
            reward_points     = abs(target_1 - current)
            risk_reward_ratio = round(reward_points / risk_points, 2) if risk_points > 0 else 0
        else:
            risk_points = reward_points = risk_reward_ratio = 0

        self.html_data = {
            'timestamp':      ist_now.strftime('%d-%b-%Y %H:%M IST'),
            'current_price':  current,
            'expiry':         option_analysis['expiry'] if option_analysis else 'N/A',
            'bias':           bias,
            'bias_icon':      bias_icon,
            'bias_class':     bias_class,
            'confidence':     confidence,
            'bullish_score':  bullish_score,
            'bearish_score':  bearish_score,
            'rsi':            rsi,
            'rsi_status':     rsi_status,
            'rsi_badge':      rsi_badge,
            'rsi_icon':       rsi_icon,
            'sma_20':         technical['sma_20'],
            'sma_20_above':   current > technical['sma_20'],
            'sma_50':         technical['sma_50'],
            'sma_50_above':   current > technical['sma_50'],
            'sma_200':        technical['sma_200'],
            'sma_200_above':  current > technical['sma_200'],
            'macd':           technical['macd'],
            'macd_signal':    technical['signal'],
            'macd_bullish':   macd_bullish,
            'pcr':            option_analysis['pcr_oi'] if option_analysis else 0,
            'pcr_status':     pcr_status,
            'pcr_badge':      pcr_badge,
            'pcr_icon':       pcr_icon,
            'max_pain':       option_analysis['max_pain']           if option_analysis else 0,
            'max_ce_oi':      max_ce_strike,
            'max_pe_oi':      max_pe_strike,
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
            'strategy_type':      bias,
            'entry_low':          entry_low,
            'entry_high':         entry_high,
            'target_1':           target_1,
            'target_2':           target_2,
            'stop_loss':          stop_loss,
            'risk_points':        int(risk_points),
            'reward_points':      int(reward_points),
            'risk_reward_ratio':  risk_reward_ratio,
            'option_strategies':  option_strategies,
            'recommended_technical_strategy': self.select_best_technical_strategy(bias, option_strategies),
            'recommended_oi_strategy': self.select_best_oi_strategy(
                option_analysis['oi_direction'] if option_analysis else 'Neutral', atm_strike
            ) if option_analysis else None,
            'top_ce_strikes':  option_analysis['top_ce_strikes'] if option_analysis else [],
            'top_pe_strikes':  option_analysis['top_pe_strikes'] if option_analysis else [],
            'has_option_data': option_analysis is not None,
        }

    # ==================== HTML GENERATION ====================

    def generate_html_email(self):
        data = self.html_data

        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nifty 50 Daily Report</title>
    <style>
        *{{margin:0;padding:0;box-sizing:border-box;}}
        body{{font-family:'Segoe UI',Tahoma,Geneva,Verdana,sans-serif;
              background:linear-gradient(135deg,#0f2027 0%,#203a43 50%,#2c5364 100%);
              min-height:100vh;padding:20px;color:#b0bec5;}}
        .container{{max-width:1200px;margin:0 auto;background:rgba(15,32,39,0.95);
                    border-radius:16px;overflow:hidden;box-shadow:0 20px 60px rgba(0,0,0,0.5);
                    border:1px solid rgba(79,195,247,0.2);}}
        .header{{background:linear-gradient(135deg,#0f2027,#203a43);padding:40px 30px;
                 text-align:center;border-bottom:3px solid #4fc3f7;position:relative;overflow:hidden;}}
        .header::before{{content:'';position:absolute;top:0;left:0;right:0;bottom:0;
                         background:radial-gradient(circle at 50% 50%,rgba(79,195,247,0.1) 0%,transparent 70%);
                         pointer-events:none;}}
        .header h1{{font-size:32px;font-weight:700;color:#4fc3f7;margin-bottom:10px;
                    text-shadow:0 0 20px rgba(79,195,247,0.5);position:relative;z-index:1;}}
        .header p{{color:#80deea;font-size:14px;opacity:0.9;position:relative;z-index:1;}}
        .section{{padding:25px;border-bottom:1px solid rgba(79,195,247,0.1);}}
        .section:last-child{{border-bottom:none;}}
        .section-title{{font-size:18px;font-weight:600;margin-bottom:20px;color:#4fc3f7;
                         display:flex;align-items:center;gap:10px;
                         padding-bottom:10px;border-bottom:2px solid rgba(79,195,247,0.3);}}
        .section-title span{{font-size:22px;}}
        .card-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin-top:20px;}}
        .card{{background:linear-gradient(135deg,rgba(15,32,39,0.8),rgba(32,58,67,0.6));
               border-radius:12px;padding:14px;border:1.5px solid rgba(79,195,247,0.25);
               transition:all 0.3s cubic-bezier(0.4,0,0.2,1);position:relative;overflow:hidden;}}
        .card::before{{content:'';position:absolute;top:0;left:0;width:100%;height:4px;
                       background:linear-gradient(90deg,#4fc3f7,#26c6da);
                       transform:scaleX(0);transform-origin:left;transition:transform 0.3s ease;}}
        .card:hover{{transform:translateY(-4px);box-shadow:0 12px 30px rgba(79,195,247,0.25);border-color:#4fc3f7;}}
        .card:hover::before{{transform:scaleX(1);}}
        .card-icon{{font-size:24px;margin-bottom:8px;display:block;}}
        .card-label{{font-size:10px;color:#80deea;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;font-weight:600;}}
        .card-value{{font-size:22px;font-weight:700;color:#fff;margin-bottom:6px;text-shadow:0 2px 4px rgba(0,0,0,0.3);}}
        .card-change{{font-size:14px;font-weight:600;display:inline-flex;align-items:center;gap:4px;padding:4px 10px;border-radius:6px;}}
        .card-change.positive{{color:#00bcd4;background:rgba(0,188,212,0.15);}}
        .card-change.negative{{color:#f44336;background:rgba(244,67,54,0.15);}}
        .card-change.neutral{{color:#ffb74d;background:rgba(255,183,77,0.15);}}
        .card.bullish{{border-left:4px solid #00bcd4;}}
        .card.bearish{{border-left:4px solid #f44336;}}
        .card.neutral{{border-left:4px solid #ffb74d;}}
        .card.highlight{{background:linear-gradient(135deg,rgba(79,195,247,0.15),rgba(79,195,247,0.05));border:2px solid #4fc3f7;}}
        .direction-box{{padding:30px;border-radius:14px;text-align:center;margin:20px 0;
                        border:2px solid #4fc3f7;background:linear-gradient(135deg,#0f2027,#2c5364);}}
        .direction-box.bullish{{background:linear-gradient(135deg,#00bcd4,#26c6da);border-color:#00bcd4;box-shadow:0 0 30px rgba(0,188,212,0.4);}}
        .direction-box.bearish{{background:linear-gradient(135deg,#d32f2f,#f44336);border-color:#f44336;box-shadow:0 0 30px rgba(244,67,54,0.4);}}
        .direction-box.sideways{{background:linear-gradient(135deg,#ffa726,#ffb74d);border-color:#ffb74d;box-shadow:0 0 30px rgba(255,183,77,0.4);}}
        .direction-title{{font-size:30px;font-weight:700;margin-bottom:10px;color:#000;}}
        .direction-subtitle{{font-size:14px;opacity:0.95;color:#000;font-weight:600;}}
        .logic-box{{background:rgba(79,195,247,0.1);padding:18px;border-radius:10px;margin-top:20px;border-left:4px solid #4fc3f7;}}
        .logic-box p{{font-size:13px;line-height:1.8;color:#80deea;margin:0;}}
        .logic-box strong{{color:#4fc3f7;}}
        .levels-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px;margin-top:20px;}}
        .level-card{{background:rgba(15,32,39,0.6);border-radius:10px;padding:14px;
                     display:flex;justify-content:space-between;align-items:center;border:1.5px solid;transition:all 0.3s ease;}}
        .level-card:hover{{transform:translateX(6px);}}
        .level-card.resistance{{border-color:rgba(244,67,54,0.5);border-left:4px solid #f44336;background:linear-gradient(90deg,rgba(244,67,54,0.1),rgba(244,67,54,0.05));}}
        .level-card.support{{border-color:rgba(0,188,212,0.5);border-left:4px solid #00bcd4;background:linear-gradient(90deg,rgba(0,188,212,0.1),rgba(0,188,212,0.05));}}
        .level-card.current{{border-color:#4fc3f7;border-left:4px solid #4fc3f7;background:linear-gradient(90deg,rgba(79,195,247,0.2),rgba(79,195,247,0.1));}}
        .level-name{{font-weight:600;font-size:12px;color:#b0bec5;}}
        .level-value{{font-weight:700;font-size:16px;color:#fff;}}
        .risk-box{{background:rgba(255,183,77,0.12);padding:18px;border-radius:10px;margin-top:15px;
                   border-left:4px solid #ffb74d;display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px;}}
        .risk-item{{display:flex;justify-content:space-between;align-items:center;}}
        .risk-label{{font-size:13px;color:#ffb74d;font-weight:600;}}
        .risk-value{{font-size:16px;color:#ffb74d;font-weight:700;}}
        .strikes-table{{width:100%;border-collapse:collapse;margin-top:20px;border-radius:10px;overflow:hidden;}}
        .strikes-table th{{background:linear-gradient(135deg,#4fc3f7,#26c6da);color:#000;padding:16px;
                           text-align:left;font-weight:700;font-size:13px;text-transform:uppercase;}}
        .strikes-table td{{padding:16px;border-bottom:1px solid rgba(79,195,247,0.1);color:#b0bec5;font-size:14px;}}
        .strikes-table tr:hover{{background:rgba(79,195,247,0.08);}}
        .strikes-table tbody tr:last-child td{{border-bottom:none;}}
        .disclaimer{{background:rgba(255,183,77,0.15);padding:25px;border-radius:12px;
                     border-left:4px solid #ffb74d;font-size:13px;color:#ffb74d;line-height:1.8;}}
        .footer{{text-align:center;padding:25px;color:#607d8b;font-size:12px;background:rgba(15,32,39,0.5);}}
        @media(max-width:768px){{
            .card-grid{{grid-template-columns:repeat(2,1fr);}}
            .levels-grid{{grid-template-columns:1fr;}}
            .header h1{{font-size:24px;}}
            .direction-title{{font-size:22px;}}
            body{{padding:10px;}}
        }}
        @media(max-width:480px){{.card-grid{{grid-template-columns:1fr;}}}}
    </style>
</head>
<body>
<div class="container">

    <div class="header">
        <h1>📊 NIFTY 50 DAILY REPORT</h1>
        <p>Generated: {data['timestamp']}</p>
    </div>

    <div class="section">
        <div class="section-title"><span>📈</span> MARKET SNAPSHOT</div>
        <div class="card-grid">
            <div class="card highlight">
                <span class="card-icon">💹</span>
                <div class="card-label">NIFTY 50</div>
                <div class="card-value">₹{data['current_price']:,.2f}</div>
            </div>
            <div class="card">
                <span class="card-icon">📅</span>
                <div class="card-label">EXPIRY DATE</div>
                <div class="card-value" style="font-size:20px;">{data['expiry']}</div>
            </div>
        </div>
    </div>

    <div class="section">
        <div class="section-title"><span>🎯</span> MARKET DIRECTION (Algorithmic Analysis)</div>
        <div class="direction-box {data['bias_class']}">
            <div class="direction-title">{data['bias_icon']} {data['bias']}</div>
            <div class="direction-subtitle">Confidence: {data['confidence']} | Bullish: {data['bullish_score']} vs Bearish: {data['bearish_score']}</div>
        </div>
        <div class="logic-box">
            <p>
                <strong>📊 Direction Logic:</strong><br>
                • <strong>BULLISH</strong>: Score diff ≥ +3 (Price above SMAs, RSI oversold, positive MACD, high PCR)<br>
                • <strong>BEARISH</strong>: Score diff ≤ -3 (Price below SMAs, RSI overbought, negative MACD, low PCR)<br>
                • <strong>SIDEWAYS</strong>: Score diff between -2 and +2 (Mixed signals, consolidation phase)<br>
                • <strong>Confidence</strong>: HIGH when gap ≥ 4, MEDIUM otherwise
            </p>
        </div>
    </div>

    <div class="section">
        <div class="section-title"><span>🔍</span> TECHNICAL INDICATORS</div>
        <div class="card-grid">
            <div class="card {data['rsi_badge']}">
                <span class="card-icon">{data['rsi_icon']}</span>
                <div class="card-label">RSI (14)</div>
                <div class="card-value">{data['rsi']:.1f}</div>
                <span class="card-change {data['rsi_badge']}">{data['rsi_status']}</span>
            </div>
            <div class="card {'bullish' if data['sma_20_above'] else 'bearish'}">
                <span class="card-icon">{'✅' if data['sma_20_above'] else '❌'}</span>
                <div class="card-label">SMA 20</div>
                <div class="card-value">₹{data['sma_20']:,.0f}</div>
                <span class="card-change {'positive' if data['sma_20_above'] else 'negative'}">{'Above' if data['sma_20_above'] else 'Below'}</span>
            </div>
            <div class="card {'bullish' if data['sma_50_above'] else 'bearish'}">
                <span class="card-icon">{'✅' if data['sma_50_above'] else '❌'}</span>
                <div class="card-label">SMA 50</div>
                <div class="card-value">₹{data['sma_50']:,.0f}</div>
                <span class="card-change {'positive' if data['sma_50_above'] else 'negative'}">{'Above' if data['sma_50_above'] else 'Below'}</span>
            </div>
            <div class="card {'bullish' if data['sma_200_above'] else 'bearish'}">
                <span class="card-icon">{'✅' if data['sma_200_above'] else '❌'}</span>
                <div class="card-label">SMA 200</div>
                <div class="card-value">₹{data['sma_200']:,.0f}</div>
                <span class="card-change {'positive' if data['sma_200_above'] else 'negative'}">{'Above' if data['sma_200_above'] else 'Below'}</span>
            </div>
            <div class="card {'bullish' if data['macd_bullish'] else 'bearish'}">
                <span class="card-icon">{'🟢' if data['macd_bullish'] else '🔴'}</span>
                <div class="card-label">MACD</div>
                <div class="card-value">{data['macd']:.2f}</div>
                <span class="card-change {'positive' if data['macd_bullish'] else 'negative'}">{'Bullish' if data['macd_bullish'] else 'Bearish'}</span>
            </div>
        </div>
    </div>
"""

        if data['has_option_data']:
            html += f"""
    <div class="section">
        <div class="section-title"><span>🎯</span> OPTION CHAIN ANALYSIS</div>
        <div class="card-grid">
            <div class="card {data['pcr_badge']}">
                <span class="card-icon">{data['pcr_icon']}</span>
                <div class="card-label">PCR RATIO (OI)</div>
                <div class="card-value">{data['pcr']:.3f}</div>
                <span class="card-change {data['pcr_badge']}">{data['pcr_status']}</span>
            </div>
            <div class="card neutral">
                <span class="card-icon">🎯</span>
                <div class="card-label">MAX PAIN</div>
                <div class="card-value">₹{data['max_pain']:,}</div>
            </div>
            <div class="card bearish">
                <span class="card-icon">🔴</span>
                <div class="card-label">MAX CALL OI</div>
                <div class="card-value">₹{data['max_ce_oi']:,}</div>
                <span class="card-change negative">Resistance</span>
            </div>
            <div class="card bullish">
                <span class="card-icon">🟢</span>
                <div class="card-label">MAX PUT OI</div>
                <div class="card-value">₹{data['max_pe_oi']:,}</div>
                <span class="card-change positive">Support</span>
            </div>
        </div>
    </div>

    <div class="section">
        <div class="section-title"><span>📊</span> CHANGE IN OPEN INTEREST (Today's Direction)</div>
        <div class="direction-box {data['oi_class']}" style="margin:15px 0;">
            <div class="direction-title" style="font-size:26px;">{data['oi_icon']} {data['oi_direction']}</div>
            <div class="direction-subtitle" style="font-size:13px;">{data['oi_signal']}</div>
        </div>
        <div class="card-grid" style="margin-top:20px;">
            <div class="card {'bearish' if data['total_ce_oi_change'] > 0 else 'bullish'}">
                <span class="card-icon">{'🔴' if data['total_ce_oi_change'] > 0 else '🟢'}</span>
                <div class="card-label">CALL OI CHANGE</div>
                <div class="card-value">{data['total_ce_oi_change']:+,}</div>
                <span class="card-change {'negative' if data['total_ce_oi_change'] > 0 else 'positive'}">
                    {'Bearish Signal' if data['total_ce_oi_change'] > 0 else 'Bullish Signal'}
                </span>
            </div>
            <div class="card {'bullish' if data['total_pe_oi_change'] > 0 else 'bearish'}">
                <span class="card-icon">{'🟢' if data['total_pe_oi_change'] > 0 else '🔴'}</span>
                <div class="card-label">PUT OI CHANGE</div>
                <div class="card-value">{data['total_pe_oi_change']:+,}</div>
                <span class="card-change {'positive' if data['total_pe_oi_change'] > 0 else 'negative'}">
                    {'Bullish Signal' if data['total_pe_oi_change'] > 0 else 'Bearish Signal'}
                </span>
            </div>
            <div class="card highlight">
                <span class="card-icon">⚖️</span>
                <div class="card-label">NET OI CHANGE</div>
                <div class="card-value">{data['net_oi_change']:+,}</div>
                <span class="card-change {'positive' if data['net_oi_change'] > 0 else 'negative' if data['net_oi_change'] < 0 else 'neutral'}">
                    {'Bullish Net' if data['net_oi_change'] > 0 else 'Bearish Net' if data['net_oi_change'] < 0 else 'Balanced'}
                </span>
            </div>
        </div>
        <div class="logic-box">
            <p>
                <strong>📖 How to Read:</strong><br>
                • <strong>Call OI Increase (+)</strong> = Writers selling calls (Bearish) | <strong>Decrease (-)</strong> = Unwinding (Bullish)<br>
                • <strong>Put OI Increase (+)</strong> = Writers selling puts (Bullish) | <strong>Decrease (-)</strong> = Unwinding (Bearish)<br>
                • <strong>Net OI</strong> = Put Change - Call Change (Positive = Bullish, Negative = Bearish)
            </p>
        </div>
    </div>
"""

        html += f"""
    <div class="section">
        <div class="section-title"><span>📊</span> KEY LEVELS</div>
        <div class="levels-grid">
            <div class="level-card resistance">
                <span class="level-name">🔴 Strong Resistance</span>
                <strong class="level-value">₹{data['strong_resistance']:,.0f}</strong>
            </div>
            <div class="level-card resistance">
                <span class="level-name">🟠 Resistance</span>
                <strong class="level-value">₹{data['resistance']:,.0f}</strong>
            </div>
            <div class="level-card current">
                <span class="level-name">⚪ Current Price</span>
                <strong class="level-value">₹{data['current_price']:,.0f}</strong>
            </div>
"""
        if data['has_option_data']:
            html += f"""
            <div class="level-card support">
                <span class="level-name">🟡 Max Pain</span>
                <strong class="level-value">₹{data['max_pain']:,}</strong>
            </div>
"""
        html += f"""
            <div class="level-card support">
                <span class="level-name">🟢 Support</span>
                <strong class="level-value">₹{data['support']:,.0f}</strong>
            </div>
            <div class="level-card support">
                <span class="level-name">🟢 Strong Support</span>
                <strong class="level-value">₹{data['strong_support']:,.0f}</strong>
            </div>
        </div>
    </div>
"""
        html += self.generate_dual_recommendations_html(data)

        if data['has_option_data'] and (data['top_ce_strikes'] or data['top_pe_strikes']):
            html += """
    <div class="section">
        <div class="section-title"><span>📋</span> TOP 5 STRIKES (by Open Interest)</div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;">
            <div>
                <h3 style="color:#00bcd4;margin-bottom:15px;font-size:16px;">📞 CALL OPTIONS (CE)</h3>
                <table class="strikes-table">
                    <thead><tr><th>#</th><th>Strike</th><th>OI</th><th>LTP</th></tr></thead><tbody>
"""
            for i, s in enumerate(data['top_ce_strikes'], 1):
                html += f"<tr><td><strong>{i}</strong></td><td><strong>₹{int(s['Strike']):,}</strong></td><td>{int(s['CE_OI']):,}</td><td style='color:#00bcd4;font-weight:700;'>₹{s['CE_LTP']:.2f}</td></tr>\n"
            html += """</tbody></table></div>
            <div>
                <h3 style="color:#f44336;margin-bottom:15px;font-size:16px;">📉 PUT OPTIONS (PE)</h3>
                <table class="strikes-table">
                    <thead><tr><th>#</th><th>Strike</th><th>OI</th><th>LTP</th></tr></thead><tbody>
"""
            for i, s in enumerate(data['top_pe_strikes'], 1):
                html += f"<tr><td><strong>{i}</strong></td><td><strong>₹{int(s['Strike']):,}</strong></td><td>{int(s['PE_OI']):,}</td><td style='color:#f44336;font-weight:700;'>₹{s['PE_LTP']:.2f}</td></tr>\n"
            html += """</tbody></table></div></div></div>
"""

        html += """
    <div class="section">
        <div class="disclaimer">
            <strong>⚠️ DISCLAIMER</strong><br><br>
            This is for EDUCATIONAL purposes only - NOT financial advice.<br>
            Always use stop losses and consult a SEBI registered advisor.<br>
            Past performance does not guarantee future results.
        </div>
    </div>
    <div class="footer">
        <p>Automated Nifty 50 Option Chain Analysis Report</p>
        <p>© 2026 - For Educational Purposes Only</p>
    </div>
</div></body></html>
"""
        return html

    # ==================== DUAL RECOMMENDATIONS ====================

    def generate_dual_recommendations_html(self, data):
        html = """
    <div class="section">
        <div class="section-title"><span>💡</span> TRADING RECOMMENDATIONS (Dual Strategy Approach)</div>
        <p style="color:#80deea;font-size:13px;margin-bottom:20px;line-height:1.7;">
            We provide <strong>TWO independent strategy recommendations</strong> based on different analysis methods:
        </p>
"""
        ts       = data['recommended_technical_strategy']
        ts_class  = 'positive' if 'Bull' in ts['name'] else 'negative' if 'Bear' in ts['name'] else 'neutral'
        ts_border = '#00bcd4' if ts_class == 'positive' else '#f44336' if ts_class == 'negative' else '#ffb74d'

        html += f"""
        <div style="background:linear-gradient(135deg,rgba(15,32,39,0.8),rgba(32,58,67,0.6));padding:25px;border-radius:14px;margin-bottom:20px;border:2px solid {ts_border};box-shadow:0 8px 20px rgba(0,0,0,0.3);">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:18px;flex-wrap:wrap;gap:10px;">
                <h3 style="color:#4fc3f7;font-size:18px;margin:0;">1️⃣ TECHNICAL ANALYSIS STRATEGY</h3>
                <span style="background:rgba(79,195,247,0.2);color:#4fc3f7;padding:6px 14px;border-radius:8px;font-size:12px;font-weight:600;">Positional • 1-5 Days</span>
            </div>
            <div style="background:rgba(79,195,247,0.08);padding:20px;border-radius:10px;border-left:4px solid {ts_border};">
                <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:15px;margin-bottom:15px;">
                    <div><div style="color:#80deea;font-size:11px;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px;">Strategy</div><div style="color:#fff;font-size:18px;font-weight:700;">{ts['name']}</div></div>
                    <div><div style="color:#80deea;font-size:11px;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px;">Market Bias</div><span class="card-change {ts_class}" style="display:inline-block;">{ts['market_bias']}</span></div>
                    <div><div style="color:#80deea;font-size:11px;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px;">Type</div><div style="color:#fff;font-size:16px;font-weight:600;">{ts['type']}</div></div>
                    <div><div style="color:#80deea;font-size:11px;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px;">Risk Profile</div><div style="color:#ffb74d;font-size:16px;font-weight:600;">{ts['risk']}</div></div>
                </div>
                <div style="background:rgba(15,32,39,0.6);padding:15px;border-radius:8px;margin-bottom:12px;">
                    <div style="color:#4fc3f7;font-size:12px;font-weight:600;margin-bottom:8px;">📋 SETUP</div>
                    <div style="color:#fff;font-size:15px;font-weight:500;">{ts['description']}</div>
                </div>
                <div style="color:#80deea;font-size:13px;"><strong style="color:#4fc3f7;">💡 Why?</strong> {ts['best_for']}</div>
            </div>
            <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:10px;margin-top:15px;">
                <div style="background:rgba(0,188,212,0.1);padding:12px;border-radius:8px;border-left:3px solid #00bcd4;"><div style="color:#80deea;font-size:10px;margin-bottom:4px;">MAX PROFIT</div><div style="color:#00bcd4;font-size:14px;font-weight:700;">{ts['max_profit']}</div></div>
                <div style="background:rgba(244,67,54,0.1);padding:12px;border-radius:8px;border-left:3px solid #f44336;"><div style="color:#80deea;font-size:10px;margin-bottom:4px;">MAX LOSS</div><div style="color:#f44336;font-size:14px;font-weight:700;">{ts['max_loss']}</div></div>
            </div>
        </div>
"""

        if data['recommended_oi_strategy']:
            oi       = data['recommended_oi_strategy']
            oi_class  = 'positive' if oi['market_bias'] == 'Bullish' else 'negative' if oi['market_bias'] == 'Bearish' else 'neutral'
            oi_border = '#00bcd4' if oi_class == 'positive' else '#f44336' if oi_class == 'negative' else '#ffb74d'

            html += f"""
        <div style="background:linear-gradient(135deg,rgba(15,32,39,0.8),rgba(32,58,67,0.6));padding:25px;border-radius:14px;margin-bottom:20px;border:2px solid {oi_border};box-shadow:0 8px 20px rgba(0,0,0,0.3);">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:18px;flex-wrap:wrap;gap:10px;">
                <h3 style="color:#4fc3f7;font-size:18px;margin:0;">2️⃣ OPEN INTEREST MOMENTUM STRATEGY</h3>
                <span style="background:rgba(255,183,77,0.2);color:#ffb74d;padding:6px 14px;border-radius:8px;font-size:12px;font-weight:600;">{oi.get('time_horizon','Intraday')}</span>
            </div>
            <div style="background:rgba(255,183,77,0.08);padding:20px;border-radius:10px;border-left:4px solid {oi_border};">
                <div style="background:rgba(79,195,247,0.1);padding:12px;border-radius:8px;margin-bottom:15px;">
                    <div style="color:#4fc3f7;font-size:12px;font-weight:600;margin-bottom:6px;">📊 OI SIGNAL</div>
                    <div style="color:#fff;font-size:14px;">{oi.get('signal','Market signal detected')}</div>
                </div>
                <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:15px;margin-bottom:15px;">
                    <div><div style="color:#80deea;font-size:11px;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px;">Strategy</div><div style="color:#fff;font-size:18px;font-weight:700;">{oi['name']}</div></div>
                    <div><div style="color:#80deea;font-size:11px;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px;">Market Bias</div><span class="card-change {oi_class}" style="display:inline-block;">{oi['market_bias']}</span></div>
                    <div><div style="color:#80deea;font-size:11px;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px;">Type</div><div style="color:#fff;font-size:16px;font-weight:600;">{oi['type']}</div></div>
                    <div><div style="color:#80deea;font-size:11px;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px;">Risk Profile</div><div style="color:#ffb74d;font-size:16px;font-weight:600;">{oi['risk']}</div></div>
                </div>
                <div style="background:rgba(15,32,39,0.6);padding:15px;border-radius:8px;margin-bottom:12px;">
                    <div style="color:#ffb74d;font-size:12px;font-weight:600;margin-bottom:8px;">📋 SETUP</div>
                    <div style="color:#fff;font-size:15px;font-weight:500;">{oi['description']}</div>
                </div>
                <div style="color:#80deea;font-size:13px;"><strong style="color:#ffb74d;">💡 Why?</strong> {oi['best_for']}</div>
            </div>
            <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:10px;margin-top:15px;">
                <div style="background:rgba(0,188,212,0.1);padding:12px;border-radius:8px;border-left:3px solid #00bcd4;"><div style="color:#80deea;font-size:10px;margin-bottom:4px;">MAX PROFIT</div><div style="color:#00bcd4;font-size:14px;font-weight:700;">{oi['max_profit']}</div></div>
                <div style="background:rgba(244,67,54,0.1);padding:12px;border-radius:8px;border-left:3px solid #f44336;"><div style="color:#80deea;font-size:10px;margin-bottom:4px;">MAX LOSS</div><div style="color:#f44336;font-size:14px;font-weight:700;">{oi['max_loss']}</div></div>
            </div>
        </div>
"""

        html += f"""
        <div class="risk-box" style="margin-top:20px;">
            <div style="grid-column:1/-1;margin-bottom:12px;"><h4 style="color:#ffb74d;font-size:15px;margin:0;">📍 KEY TRADING LEVELS</h4></div>
            <div class="risk-item"><span class="risk-label">ENTRY ZONE</span><span class="risk-value">₹{data['entry_low']:,.0f} – ₹{data['entry_high']:,.0f}</span></div>
            <div class="risk-item"><span class="risk-label">TARGET 1</span><span class="risk-value">₹{data['target_1']:,.0f}</span></div>
            <div class="risk-item"><span class="risk-label">TARGET 2</span><span class="risk-value">₹{data['target_2']:,.0f}</span></div>
"""
        if data['stop_loss']:
            html += f"""
            <div class="risk-item"><span class="risk-label">STOP LOSS</span><span class="risk-value" style="color:#f44336;">₹{data['stop_loss']:,.0f}</span></div>
            <div class="risk-item"><span class="risk-label">RISK</span><span class="risk-value">{data['risk_points']} pts</span></div>
            <div class="risk-item"><span class="risk-label">REWARD</span><span class="risk-value">{data['reward_points']} pts</span></div>
            <div class="risk-item"><span class="risk-label">R:R RATIO</span><span class="risk-value">1:{data['risk_reward_ratio']}</span></div>
"""
        else:
            html += """
            <div class="risk-item" style="grid-column:1/-1;"><span class="risk-label">STOP LOSS</span><span class="risk-value" style="color:#ffb74d;">Use option premium as max loss (credit strategy)</span></div>
"""
        html += """
        </div>
    </div>
"""
        return html

    # ==================== FILE SAVING ====================

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

    # ==================== EMAIL ====================

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
            msg['Subject'] = f"📊 Nifty 50 OI & Technical Report - {ist_now.strftime('%d-%b-%Y %H:%M IST')}"
            msg.attach(MIMEText(self.generate_html_email(), 'html'))
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(gmail_user, gmail_password)
                server.send_message(msg)
            print("   ✅ Email sent!")
            return True
        except Exception as e:
            print(f"\n❌ Email failed: {e}")
            return False

    # ==================== MAIN ====================

    def generate_full_report(self):
        ist_now = datetime.now(pytz.timezone('Asia/Kolkata'))
        print("=" * 75)
        print("NIFTY 50 DAILY REPORT — TUESDAY EXPIRY")
        print(f"Generated: {ist_now.strftime('%d-%b-%Y %H:%M IST')}")
        print("=" * 75)

        oc_data         = self.fetch_nse_option_chain_silent()
        option_analysis = self.analyze_option_chain_data(oc_data) if oc_data else None

        if option_analysis:
            print(f"✅ Option data ready | Expiry: {option_analysis['expiry']} | Underlying: {option_analysis['underlying_value']}")
        else:
            print("⚠️  No option data — running in technical-only mode")

        print("\nFetching technical data...")
        technical = self.get_technical_data()
        self.generate_analysis_data(technical, option_analysis)
        return option_analysis


def main():
    try:
        print("\n🚀 Starting Nifty 50 Analysis (Tuesday expiry + auto-fallback)...\n")
        analyzer = NiftyHTMLAnalyzer()
        analyzer.generate_full_report()

        print("\n" + "=" * 80)
        save_success = analyzer.save_html_to_file('index.html')
        if save_success:
            analyzer.send_html_email_report()
        else:
            print("\n⚠️  Skipping email due to save failure")

        print("\n✅ Done!\n")

    except Exception as e:
        print(f"\n❌ Critical Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
