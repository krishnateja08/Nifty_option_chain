"""
NIFTY 50 COMPLETE ANALYSIS - DEEP OCEAN THEME - ENHANCED CARD LAYOUT
- Professional Deep Ocean Blue Theme
- Card-based grid layout for indicators (like stock tickers)
- Fixed: Tight stop losses (50-150 points max)
- Fixed: Email send duplication prevention
- Improved: Better risk management
- NEW: Beautiful card grids for all sections
"""

from curl_cffi import requests
import pandas as pd
import time
from datetime import datetime, timedelta
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
        """Log message to console only"""
        print(message)
        self.report_lines.append(message)
    
    # ==================== NSE OPTION CHAIN LOGIC ====================
    
    def get_upcoming_expiry_tuesday(self):
        """Calculates the date of the current or next Tuesday - FIXED WITH IST"""
        ist_tz = pytz.timezone('Asia/Kolkata')
        now = datetime.now(ist_tz)
        
        current_weekday = now.weekday()
        
        if current_weekday == 1:
            if now.hour < 15 or (now.hour == 15 and now.minute < 30):
                expiry_date = now
            else:
                expiry_date = now + timedelta(days=7)
        elif current_weekday == 0:
            expiry_date = now + timedelta(days=1)
        else:
            days_ahead = (8 - current_weekday) % 7
            expiry_date = now + timedelta(days=days_ahead)
        
        return expiry_date.strftime('%d-%b-%Y')
    
    def fetch_nse_option_chain_silent(self):
        """Fetch NSE option chain silently"""
        symbol = self.nse_symbol
        selected_expiry = self.get_upcoming_expiry_tuesday()
        
        api_url = f"https://www.nseindia.com/api/option-chain-v3?type=Indices&symbol={symbol}&expiry={selected_expiry}"
        base_url = "https://www.nseindia.com/"
        
        headers = {
            "authority": "www.nseindia.com",
            "accept": "application/json, text/plain, */*",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "referer": "https://www.nseindia.com/option-chain",
            "accept-language": "en-US,en;q=0.9",
        }

        session = requests.Session()

        try:
            print(f"Fetching option chain for {selected_expiry}...")
            session.get(base_url, headers=headers, impersonate="chrome", timeout=15)
            time.sleep(1)
            response = session.get(api_url, headers=headers, impersonate="chrome", timeout=30)
            
            if response.status_code == 200:
                json_data = response.json()
                data = json_data.get('records', {}).get('data', [])
                
                if not data:
                    print(f"Warning: No data for {selected_expiry}")
                    return None

                rows = []
                for item in data:
                    strike = item.get('strikePrice')
                    ce = item.get('CE', {})
                    pe = item.get('PE', {})
                    
                    rows.append({
                        'Expiry': selected_expiry,
                        'Strike': strike,
                        'CE_LTP': ce.get('lastPrice', 0),
                        'CE_OI': ce.get('openInterest', 0),
                        'CE_Vol': ce.get('totalTradedVolume', 0),
                        'PE_LTP': pe.get('lastPrice', 0),
                        'PE_OI': pe.get('openInterest', 0),
                        'PE_Vol': pe.get('totalTradedVolume', 0)
                    })

                df = pd.DataFrame(rows).sort_values('Strike')
                print(f"✓ Option chain fetched: {len(df)} strikes")
                
                return {
                    'expiry': selected_expiry,
                    'df': df,
                    'raw_data': data,
                    'underlying': json_data.get('records', {}).get('underlyingValue', 0)
                }
            else:
                print(f"NSE Error: {response.status_code}")
                return None

        except Exception as e:
            print(f"NSE Fetch Error: {e}")
            return None
    
    def analyze_option_chain_data(self, oc_data):
        """Analyze the option chain data"""
        if not oc_data:
            return None
        
        df = oc_data['df']
        
        total_ce_oi = df['CE_OI'].sum()
        total_pe_oi = df['PE_OI'].sum()
        total_ce_vol = df['CE_Vol'].sum()
        total_pe_vol = df['PE_Vol'].sum()
        
        pcr_oi = total_pe_oi / total_ce_oi if total_ce_oi > 0 else 0
        pcr_vol = total_pe_vol / total_ce_vol if total_ce_vol > 0 else 0
        
        # ========== CHANGE IN OI ANALYSIS ==========
        # Extract Change in OI from API data
        ce_oi_change_list = []
        pe_oi_change_list = []
        
        for item in oc_data['raw_data']:
            ce = item.get('CE', {})
            pe = item.get('PE', {})
            
            ce_chng = ce.get('changeinOpenInterest', 0)
            pe_chng = pe.get('changeinOpenInterest', 0)
            
            if ce_chng != 0:
                ce_oi_change_list.append(ce_chng)
            if pe_chng != 0:
                pe_oi_change_list.append(pe_chng)
        
        total_ce_oi_change = sum(ce_oi_change_list)
        total_pe_oi_change = sum(pe_oi_change_list)
        net_oi_change = total_pe_oi_change - total_ce_oi_change
        
        # Determine market direction based on OI changes
        if total_ce_oi_change > 0 and total_pe_oi_change < 0:
            oi_direction = "Strong Bearish"
            oi_signal = "Call Build-up + Put Unwinding"
            oi_icon = "🔴"
            oi_class = "bearish"
        elif total_ce_oi_change < 0 and total_pe_oi_change > 0:
            oi_direction = "Strong Bullish"
            oi_signal = "Put Build-up + Call Unwinding"
            oi_icon = "🟢"
            oi_class = "bullish"
        elif total_ce_oi_change > 0 and total_pe_oi_change > 0:
            if total_pe_oi_change > total_ce_oi_change * 1.5:
                oi_direction = "Bullish"
                oi_signal = "Put Build-up Dominant"
                oi_icon = "🟢"
                oi_class = "bullish"
            elif total_ce_oi_change > total_pe_oi_change * 1.5:
                oi_direction = "Bearish"
                oi_signal = "Call Build-up Dominant"
                oi_icon = "🔴"
                oi_class = "bearish"
            else:
                oi_direction = "Neutral (High Volatility)"
                oi_signal = "Both Calls & Puts Building"
                oi_icon = "🟡"
                oi_class = "neutral"
        elif total_ce_oi_change < 0 and total_pe_oi_change < 0:
            oi_direction = "Neutral (Unwinding)"
            oi_signal = "Both Calls & Puts Unwinding"
            oi_icon = "🟡"
            oi_class = "neutral"
        else:
            if net_oi_change > 0:
                oi_direction = "Moderately Bullish"
                oi_signal = "Net Put Accumulation"
                oi_icon = "🟢"
                oi_class = "bullish"
            elif net_oi_change < 0:
                oi_direction = "Moderately Bearish"
                oi_signal = "Net Call Accumulation"
                oi_icon = "🔴"
                oi_class = "bearish"
            else:
                oi_direction = "Neutral"
                oi_signal = "Balanced OI Changes"
                oi_icon = "🟡"
                oi_class = "neutral"
        
        max_ce_oi_row = df.loc[df['CE_OI'].idxmax()]
        max_pe_oi_row = df.loc[df['PE_OI'].idxmax()]
        
        df['pain'] = abs(df['CE_OI'] - df['PE_OI'])
        max_pain_row = df.loc[df['pain'].idxmin()]
        
        df['Total_OI'] = df['CE_OI'] + df['PE_OI']
        
        # Get top 5 Call strikes by CE OI
        top_ce_strikes = df.nlargest(5, 'CE_OI')[['Strike', 'CE_OI', 'CE_LTP']].to_dict('records')
        
        # Get top 5 Put strikes by PE OI
        top_pe_strikes = df.nlargest(5, 'PE_OI')[['Strike', 'PE_OI', 'PE_LTP']].to_dict('records')
        
        analysis = {
            'expiry': oc_data['expiry'],
            'underlying_value': oc_data['underlying'],
            'pcr_oi': round(pcr_oi, 3),
            'pcr_volume': round(pcr_vol, 3),
            'total_ce_oi': int(total_ce_oi),
            'total_pe_oi': int(total_pe_oi),
            'max_ce_oi_strike': int(max_ce_oi_row['Strike']),
            'max_ce_oi_value': int(max_ce_oi_row['CE_OI']),
            'max_pe_oi_strike': int(max_pe_oi_row['Strike']),
            'max_pe_oi_value': int(max_pe_oi_row['PE_OI']),
            'max_pain': int(max_pain_row['Strike']),
            'top_ce_strikes': top_ce_strikes,
            'top_pe_strikes': top_pe_strikes,
            # OI Change Analysis
            'total_ce_oi_change': int(total_ce_oi_change),
            'total_pe_oi_change': int(total_pe_oi_change),
            'net_oi_change': int(net_oi_change),
            'oi_direction': oi_direction,
            'oi_signal': oi_signal,
            'oi_icon': oi_icon,
            'oi_class': oi_class,
            'df': df
        }
        
        return analysis
    
    # ==================== TECHNICAL ANALYSIS ====================
    
    def get_technical_data(self):
        """Get technical analysis data"""
        try:
            print("Calculating technical indicators...")
            nifty = yf.Ticker(self.yf_symbol)
            df = nifty.history(period="1y")
            
            if df.empty:
                print("Warning: Failed to fetch historical data")
                return None
            
            df['SMA_20'] = df['Close'].rolling(window=20).mean()
            df['SMA_50'] = df['Close'].rolling(window=50).mean()
            df['SMA_200'] = df['Close'].rolling(window=200).mean()
            
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))
            
            df['EMA_12'] = df['Close'].ewm(span=12, adjust=False).mean()
            df['EMA_26'] = df['Close'].ewm(span=26, adjust=False).mean()
            df['MACD'] = df['EMA_12'] - df['EMA_26']
            df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
            
            latest = df.iloc[-1]
            recent = df.tail(60)
            
            technical = {
                'current_price': latest['Close'],
                'sma_20': latest['SMA_20'],
                'sma_50': latest['SMA_50'],
                'sma_200': latest['SMA_200'],
                'rsi': latest['RSI'],
                'macd': latest['MACD'],
                'signal': latest['Signal'],
                'resistance': recent['High'].quantile(0.90),
                'support': recent['Low'].quantile(0.10),
            }
            
            print(f"✓ Technical analysis complete")
            
            return technical
            
        except Exception as e:
            print(f"Technical analysis error: {e}")
            return None
    
    # ==================== IMPROVED STOP LOSS LOGIC ====================
    
    def calculate_smart_stop_loss(self, current_price, support, resistance, bias):
        """
        Calculate tight stop loss based on proper risk management
        
        Rules:
        - For BULLISH: Stop loss just below immediate support (30-50 points)
        - For BEARISH: Stop loss just above immediate resistance (30-50 points)
        - Maximum risk: 150 points for Nifty
        """
        
        if bias == "BULLISH":
            stop_loss = support - 30
            max_allowed_stop = current_price - 150
            if stop_loss < max_allowed_stop:
                stop_loss = max_allowed_stop
            
        elif bias == "BEARISH":
            stop_loss = resistance + 30
            max_allowed_stop = current_price + 150
            if stop_loss > max_allowed_stop:
                stop_loss = max_allowed_stop
                
        else:  # SIDEWAYS - Iron Condor
            stop_loss = None
        
        return round(stop_loss, 0) if stop_loss else None
    
    # ==================== ANALYSIS & DATA COLLECTION ====================
    
    def generate_analysis_data(self, technical, option_analysis):
        """Generate analysis with IMPROVED stop loss logic"""
        
        if not technical:
            self.log("⚠️  Technical data unavailable")
            return
        
        current = technical['current_price']
        support = technical['support']
        resistance = technical['resistance']
        
        ist_tz = pytz.timezone('Asia/Kolkata')
        ist_now = datetime.now(ist_tz)
        
        # Calculate scores
        bullish_score = 0
        bearish_score = 0
        
        if current > technical['sma_20']:
            bullish_score += 1
        else:
            bearish_score += 1
            
        if current > technical['sma_50']:
            bullish_score += 1
        else:
            bearish_score += 1
            
        if current > technical['sma_200']:
            bullish_score += 1
        else:
            bearish_score += 1
        
        rsi = technical['rsi']
        if rsi > 70:
            bearish_score += 1
        elif rsi < 30:
            bullish_score += 2
        
        if technical['macd'] > technical['signal']:
            bullish_score += 1
        else:
            bearish_score += 1
        
        if option_analysis:
            pcr = option_analysis['pcr_oi']
            max_pain = option_analysis['max_pain']
            
            if pcr > 1.2:
                bullish_score += 2
            elif pcr < 0.7:
                bearish_score += 2
            
            if current > max_pain + 100:
                bearish_score += 1
            elif current < max_pain - 100:
                bullish_score += 1
        
        # Determine bias
        score_diff = bullish_score - bearish_score
        
        if bullish_score > bearish_score + 2:
            bias = "BULLISH"
            bias_icon = "📈"
            confidence = "HIGH" if score_diff >= 4 else "MEDIUM"
            bias_class = "bullish"
        elif bearish_score > bullish_score + 2:
            bias = "BEARISH"
            bias_icon = "📉"
            confidence = "HIGH" if abs(score_diff) >= 4 else "MEDIUM"
            bias_class = "bearish"
        else:
            bias = "SIDEWAYS"
            bias_icon = "↔️"
            confidence = "MEDIUM"
            bias_class = "sideways"
        
        # RSI status
        if rsi > 70:
            rsi_status = "Overbought"
            rsi_badge = "bearish"
            rsi_icon = "🔴"
        elif rsi < 30:
            rsi_status = "Oversold"
            rsi_badge = "bullish"
            rsi_icon = "🟢"
        else:
            rsi_status = "Neutral"
            rsi_badge = "neutral"
            rsi_icon = "🟡"
        
        macd_bullish = technical['macd'] > technical['signal']
        
        if option_analysis:
            pcr = option_analysis['pcr_oi']
            if pcr > 1.2:
                pcr_status = "Bullish"
                pcr_badge = "bullish"
                pcr_icon = "🟢"
            elif pcr < 0.7:
                pcr_status = "Bearish"
                pcr_badge = "bearish"
                pcr_icon = "🔴"
            else:
                pcr_status = "Neutral"
                pcr_badge = "neutral"
                pcr_icon = "🟡"
        
        # Trading recommendations
        if option_analysis:
            max_ce_strike = option_analysis['max_ce_oi_strike']
            max_pe_strike = option_analysis['max_pe_oi_strike']
        else:
            max_ce_strike = int(current/50)*50 + 200
            max_pe_strike = int(current/50)*50 - 200
        
        if bias == "BULLISH":
            entry_high = current
            entry_low = current - 50
            
            if current > (support + resistance) / 2:
                entry_low = current - 100
                entry_high = current - 50
            
            target_1 = resistance
            target_2 = max_ce_strike
            stop_loss = self.calculate_smart_stop_loss(current, support, resistance, "BULLISH")
            option_play = f"Buy {int(current/50)*50 + 50} CE"
            
        elif bias == "BEARISH":
            entry_low = current
            entry_high = current + 50
            
            if current < (support + resistance) / 2:
                entry_low = current + 50
                entry_high = current + 100
            
            target_1 = support
            target_2 = max_pe_strike
            stop_loss = self.calculate_smart_stop_loss(current, support, resistance, "BEARISH")
            option_play = f"Buy {int(current/50)*50 - 50} PE"
            
        else:  # SIDEWAYS
            entry_low = support
            entry_high = resistance
            target_1 = (support + resistance) / 2
            target_2 = target_1
            stop_loss = None
            option_play = "Iron Condor (see strategy)"
        
        # Calculate risk-reward ratio
        if stop_loss and bias != "SIDEWAYS":
            risk_points = abs(current - stop_loss)
            reward_points = abs(target_1 - current)
            risk_reward_ratio = round(reward_points / risk_points, 2) if risk_points > 0 else 0
        else:
            risk_points = 0
            reward_points = 0
            risk_reward_ratio = 0
        
        # Store all data for HTML generation
        self.html_data = {
            'timestamp': ist_now.strftime('%d-%b-%Y %H:%M IST'),
            'current_price': current,
            'expiry': option_analysis['expiry'] if option_analysis else 'N/A',
            'bias': bias,
            'bias_icon': bias_icon,
            'bias_class': bias_class,
            'confidence': confidence,
            'bullish_score': bullish_score,
            'bearish_score': bearish_score,
            'rsi': rsi,
            'rsi_status': rsi_status,
            'rsi_badge': rsi_badge,
            'rsi_icon': rsi_icon,
            'sma_20': technical['sma_20'],
            'sma_20_above': current > technical['sma_20'],
            'sma_50': technical['sma_50'],
            'sma_50_above': current > technical['sma_50'],
            'sma_200': technical['sma_200'],
            'sma_200_above': current > technical['sma_200'],
            'macd': technical['macd'],
            'macd_signal': technical['signal'],
            'macd_bullish': macd_bullish,
            'pcr': option_analysis['pcr_oi'] if option_analysis else 0,
            'pcr_status': pcr_status if option_analysis else 'N/A',
            'pcr_badge': pcr_badge if option_analysis else 'neutral',
            'pcr_icon': pcr_icon if option_analysis else '🟡',
            'max_pain': option_analysis['max_pain'] if option_analysis else 0,
            'max_ce_oi': max_ce_strike,
            'max_pe_oi': max_pe_strike,
            # OI Change data
            'total_ce_oi_change': option_analysis['total_ce_oi_change'] if option_analysis else 0,
            'total_pe_oi_change': option_analysis['total_pe_oi_change'] if option_analysis else 0,
            'net_oi_change': option_analysis['net_oi_change'] if option_analysis else 0,
            'oi_direction': option_analysis['oi_direction'] if option_analysis else 'N/A',
            'oi_signal': option_analysis['oi_signal'] if option_analysis else 'N/A',
            'oi_icon': option_analysis['oi_icon'] if option_analysis else '🟡',
            'oi_class': option_analysis['oi_class'] if option_analysis else 'neutral',
            'support': support,
            'resistance': resistance,
            'strong_support': support - 100,
            'strong_resistance': resistance + 100,
            'strategy_type': bias,
            'entry_low': entry_low,
            'entry_high': entry_high,
            'target_1': target_1,
            'target_2': target_2,
            'stop_loss': stop_loss,
            'risk_points': int(risk_points),
            'reward_points': int(reward_points),
            'risk_reward_ratio': risk_reward_ratio,
            'option_play': option_play,
            'top_ce_strikes': option_analysis['top_ce_strikes'] if option_analysis else [],
            'top_pe_strikes': option_analysis['top_pe_strikes'] if option_analysis else [],
            'has_option_data': option_analysis is not None
        }
        
        # Special handling for Iron Condor
        if bias == "SIDEWAYS":
            sell_ce = int(resistance/50)*50
            sell_pe = int(support/50)*50
            self.html_data['iron_condor'] = {
                'sell_ce': sell_ce,
                'sell_pe': sell_pe,
                'buy_ce': sell_ce + 50,
                'buy_pe': sell_pe - 50,
                'profit_low': support,
                'profit_high': resistance
            }
    
    # ==================== HTML GENERATION - ENHANCED CARD LAYOUT ====================
    
    def generate_html_email(self):
        """Generate beautiful HTML with Enhanced Card Grid Layout"""
        
        data = self.html_data
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nifty 50 Daily Report - Enhanced Cards</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
            min-height: 100vh;
            padding: 20px;
            color: #b0bec5;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: rgba(15, 32, 39, 0.95);
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
            border: 1px solid rgba(79, 195, 247, 0.2);
        }}
        
        .header {{
            background: linear-gradient(135deg, #0f2027 0%, #203a43 100%);
            padding: 40px 30px;
            text-align: center;
            border-bottom: 3px solid #4fc3f7;
            position: relative;
            overflow: hidden;
        }}
        
        .header::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: radial-gradient(circle at 50% 50%, rgba(79, 195, 247, 0.1) 0%, transparent 70%);
            pointer-events: none;
        }}
        
        .header h1 {{
            font-size: 32px;
            font-weight: 700;
            color: #4fc3f7;
            margin-bottom: 10px;
            text-shadow: 0 0 20px rgba(79, 195, 247, 0.5);
            position: relative;
            z-index: 1;
        }}
        
        .header p {{
            color: #80deea;
            font-size: 14px;
            opacity: 0.9;
            position: relative;
            z-index: 1;
        }}
        
        .section {{
            padding: 30px;
            border-bottom: 1px solid rgba(79, 195, 247, 0.1);
        }}
        
        .section:last-child {{
            border-bottom: none;
        }}
        
        .section-title {{
            font-size: 20px;
            font-weight: 600;
            margin-bottom: 25px;
            color: #4fc3f7;
            display: flex;
            align-items: center;
            gap: 12px;
            padding-bottom: 12px;
            border-bottom: 2px solid rgba(79, 195, 247, 0.3);
        }}
        
        .section-title span {{
            font-size: 24px;
        }}
        
        /* ========== CARD GRID LAYOUT (STOCK TICKER STYLE) ========== */
        
        .card-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }}
        
        .card {{
            background: linear-gradient(135deg, rgba(15, 32, 39, 0.8) 0%, rgba(32, 58, 67, 0.6) 100%);
            border-radius: 14px;
            padding: 16px;
            border: 1.5px solid rgba(79, 195, 247, 0.25);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }}
        
        .card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 4px;
            background: linear-gradient(90deg, #4fc3f7, #26c6da);
            transform: scaleX(0);
            transform-origin: left;
            transition: transform 0.3s ease;
        }}
        
        .card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 12px 30px rgba(79, 195, 247, 0.25);
            border-color: #4fc3f7;
        }}
        
        .card:hover::before {{
            transform: scaleX(1);
        }}
        
        .card-icon {{
            font-size: 28px;
            margin-bottom: 10px;
            display: block;
        }}
        
        .card-label {{
            font-size: 11px;
            color: #80deea;
            text-transform: uppercase;
            letter-spacing: 1.2px;
            margin-bottom: 10px;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 6px;
        }}
        
        .card-value {{
            font-size: 26px;
            font-weight: 700;
            color: #ffffff;
            margin-bottom: 8px;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
        }}
        
        .card-change {{
            font-size: 14px;
            font-weight: 600;
            display: inline-flex;
            align-items: center;
            gap: 4px;
            padding: 4px 10px;
            border-radius: 6px;
        }}
        
        .card-change.positive {{
            color: #00bcd4;
            background: rgba(0, 188, 212, 0.15);
        }}
        
        .card-change.negative {{
            color: #f44336;
            background: rgba(244, 67, 54, 0.15);
        }}
        
        .card-change.neutral {{
            color: #ffb74d;
            background: rgba(255, 183, 77, 0.15);
        }}
        
        /* Special styling for different card types */
        .card.bullish {{
            border-left: 4px solid #00bcd4;
        }}
        
        .card.bearish {{
            border-left: 4px solid #f44336;
        }}
        
        .card.neutral {{
            border-left: 4px solid #ffb74d;
        }}
        
        .card.highlight {{
            background: linear-gradient(135deg, rgba(79, 195, 247, 0.15) 0%, rgba(79, 195, 247, 0.05) 100%);
            border: 2px solid #4fc3f7;
        }}
        
        /* ========== DIRECTION BOX ========== */
        
        .direction-box {{
            background: linear-gradient(135deg, #0f2027 0%, #2c5364 100%);
            padding: 30px;
            border-radius: 14px;
            text-align: center;
            margin: 20px 0;
            border: 2px solid #4fc3f7;
            box-shadow: 0 0 30px rgba(79, 195, 247, 0.3);
        }}
        
        .direction-box.bullish {{
            background: linear-gradient(135deg, #00bcd4 0%, #26c6da 100%);
            border-color: #00bcd4;
            box-shadow: 0 0 30px rgba(0, 188, 212, 0.4);
        }}
        
        .direction-box.bearish {{
            background: linear-gradient(135deg, #d32f2f 0%, #f44336 100%);
            border-color: #f44336;
            box-shadow: 0 0 30px rgba(244, 67, 54, 0.4);
        }}
        
        .direction-box.sideways {{
            background: linear-gradient(135deg, #ffa726 0%, #ffb74d 100%);
            border-color: #ffb74d;
            box-shadow: 0 0 30px rgba(255, 183, 77, 0.4);
        }}
        
        .direction-title {{
            font-size: 30px;
            font-weight: 700;
            margin-bottom: 10px;
            color: #000;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        }}
        
        .direction-subtitle {{
            font-size: 14px;
            opacity: 0.95;
            color: #000;
            font-weight: 600;
        }}
        
        /* ========== KEY LEVELS CARDS ========== */
        
        .levels-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }}
        
        .level-card {{
            background: rgba(15, 32, 39, 0.6);
            border-radius: 12px;
            padding: 18px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border: 1.5px solid;
            transition: all 0.3s ease;
        }}
        
        .level-card:hover {{
            transform: translateX(6px);
            box-shadow: -8px 0 20px rgba(79, 195, 247, 0.2);
        }}
        
        .level-card.resistance {{
            border-color: rgba(244, 67, 54, 0.5);
            border-left: 4px solid #f44336;
            background: linear-gradient(90deg, rgba(244, 67, 54, 0.1) 0%, rgba(244, 67, 54, 0.05) 100%);
        }}
        
        .level-card.support {{
            border-color: rgba(0, 188, 212, 0.5);
            border-left: 4px solid #00bcd4;
            background: linear-gradient(90deg, rgba(0, 188, 212, 0.1) 0%, rgba(0, 188, 212, 0.05) 100%);
        }}
        
        .level-card.current {{
            border-color: #4fc3f7;
            border-left: 4px solid #4fc3f7;
            background: linear-gradient(90deg, rgba(79, 195, 247, 0.2) 0%, rgba(79, 195, 247, 0.1) 100%);
            box-shadow: 0 0 20px rgba(79, 195, 247, 0.3);
        }}
        
        .level-name {{
            font-weight: 600;
            font-size: 14px;
            color: #b0bec5;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .level-value {{
            font-weight: 700;
            font-size: 18px;
            color: #ffffff;
        }}
        
        /* ========== RECOMMENDATION BOX ========== */
        
        .recommendation-box {{
            background: linear-gradient(135deg, rgba(79, 195, 247, 0.1) 0%, rgba(79, 195, 247, 0.05) 100%);
            padding: 25px;
            border-radius: 14px;
            border: 2px solid #4fc3f7;
            margin: 20px 0;
        }}
        
        .rec-title {{
            font-size: 22px;
            font-weight: 700;
            color: #4fc3f7;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .rec-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }}
        
        .rec-card {{
            background: rgba(15, 32, 39, 0.6);
            border-radius: 10px;
            padding: 16px;
            border-left: 3px solid #4fc3f7;
        }}
        
        .rec-label {{
            color: #80deea;
            font-weight: 600;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.8px;
            margin-bottom: 8px;
        }}
        
        .rec-value {{
            color: #ffffff;
            font-weight: 700;
            font-size: 18px;
        }}
        
        .rec-value.stop-loss {{
            color: #f44336;
            font-size: 20px;
        }}
        
        .risk-box {{
            background: rgba(255, 183, 77, 0.12);
            padding: 18px;
            border-radius: 10px;
            margin-top: 15px;
            border-left: 4px solid #ffb74d;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 12px;
        }}
        
        .risk-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .risk-label {{
            font-size: 13px;
            color: #ffb74d;
            font-weight: 600;
        }}
        
        .risk-value {{
            font-size: 16px;
            color: #ffb74d;
            font-weight: 700;
        }}
        
        /* ========== STRIKES TABLE ========== */
        
        .strikes-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            overflow: hidden;
            border-radius: 10px;
        }}
        
        .strikes-table th {{
            background: linear-gradient(135deg, #4fc3f7 0%, #26c6da 100%);
            color: #000;
            padding: 16px;
            text-align: left;
            font-weight: 700;
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .strikes-table td {{
            padding: 16px;
            border-bottom: 1px solid rgba(79, 195, 247, 0.1);
            color: #b0bec5;
            font-size: 14px;
            font-weight: 500;
        }}
        
        .strikes-table tr:hover {{
            background: rgba(79, 195, 247, 0.08);
        }}
        
        .strikes-table tbody tr:last-child td {{
            border-bottom: none;
        }}
        
        /* ========== DISCLAIMER ========== */
        
        .disclaimer {{
            background: rgba(255, 183, 77, 0.15);
            padding: 25px;
            border-radius: 12px;
            border-left: 4px solid #ffb74d;
            font-size: 13px;
            color: #ffb74d;
            line-height: 1.8;
        }}
        
        .footer {{
            text-align: center;
            padding: 25px;
            color: #607d8b;
            font-size: 12px;
            background: rgba(15, 32, 39, 0.5);
        }}
        
        /* ========== RESPONSIVE ========== */
        
        @media only screen and (max-width: 768px) {{
            .card-grid {{
                grid-template-columns: repeat(2, 1fr);
                gap: 12px;
            }}
            
            .levels-grid {{
                grid-template-columns: 1fr;
            }}
            
            .rec-grid {{
                grid-template-columns: 1fr;
            }}
            
            /* Stack strike tables on mobile */
            .section > div[style*="grid-template-columns: 1fr 1fr"] {{
                grid-template-columns: 1fr !important;
            }}
            
            .header h1 {{
                font-size: 24px;
            }}
            
            .direction-title {{
                font-size: 22px;
            }}
            
            body {{
                padding: 10px;
            }}
        }}
        
        @media only screen and (max-width: 480px) {{
            .card-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- HEADER -->
        <div class="header">
            <h1>📊 NIFTY 50 DAILY REPORT</h1>
            <p>Generated: {data['timestamp']}</p>
        </div>

        <!-- MARKET SNAPSHOT -->
        <div class="section">
            <div class="section-title">
                <span>📈</span> MARKET SNAPSHOT
            </div>
            <div class="card-grid">
                <div class="card highlight">
                    <span class="card-icon">💹</span>
                    <div class="card-label">NIFTY 50</div>
                    <div class="card-value">₹{data['current_price']:,.2f}</div>
                </div>
                <div class="card">
                    <span class="card-icon">📅</span>
                    <div class="card-label">EXPIRY DATE</div>
                    <div class="card-value" style="font-size: 20px;">{data['expiry']}</div>
                </div>
            </div>
        </div>

        <!-- MARKET DIRECTION -->
        <div class="section">
            <div class="direction-box {data['bias_class']}">
                <div class="direction-title">{data['bias_icon']} {data['bias']}</div>
                <div class="direction-subtitle">Confidence: {data['confidence']} | Bullish: {data['bullish_score']} vs Bearish: {data['bearish_score']}</div>
            </div>
        </div>

        <!-- TECHNICAL INDICATORS - CARD GRID -->
        <div class="section">
            <div class="section-title">
                <span>🔍</span> TECHNICAL INDICATORS
            </div>
            <div class="card-grid">
                <!-- RSI Card -->
                <div class="card {data['rsi_badge']}">
                    <span class="card-icon">{data['rsi_icon']}</span>
                    <div class="card-label">RSI (14)</div>
                    <div class="card-value">{data['rsi']:.1f}</div>
                    <span class="card-change {data['rsi_badge']}">{data['rsi_status']}</span>
                </div>
                
                <!-- SMA 20 Card -->
                <div class="card {'bullish' if data['sma_20_above'] else 'bearish'}">
                    <span class="card-icon">{'✅' if data['sma_20_above'] else '❌'}</span>
                    <div class="card-label">SMA 20</div>
                    <div class="card-value">₹{data['sma_20']:,.0f}</div>
                    <span class="card-change {'positive' if data['sma_20_above'] else 'negative'}">
                        {'Above' if data['sma_20_above'] else 'Below'}
                    </span>
                </div>
                
                <!-- SMA 50 Card -->
                <div class="card {'bullish' if data['sma_50_above'] else 'bearish'}">
                    <span class="card-icon">{'✅' if data['sma_50_above'] else '❌'}</span>
                    <div class="card-label">SMA 50</div>
                    <div class="card-value">₹{data['sma_50']:,.0f}</div>
                    <span class="card-change {'positive' if data['sma_50_above'] else 'negative'}">
                        {'Above' if data['sma_50_above'] else 'Below'}
                    </span>
                </div>
                
                <!-- SMA 200 Card -->
                <div class="card {'bullish' if data['sma_200_above'] else 'bearish'}">
                    <span class="card-icon">{'✅' if data['sma_200_above'] else '❌'}</span>
                    <div class="card-label">SMA 200</div>
                    <div class="card-value">₹{data['sma_200']:,.0f}</div>
                    <span class="card-change {'positive' if data['sma_200_above'] else 'negative'}">
                        {'Above' if data['sma_200_above'] else 'Below'}
                    </span>
                </div>
                
                <!-- MACD Card -->
                <div class="card {'bullish' if data['macd_bullish'] else 'bearish'}">
                    <span class="card-icon">{'🟢' if data['macd_bullish'] else '🔴'}</span>
                    <div class="card-label">MACD</div>
                    <div class="card-value">{data['macd']:.2f}</div>
                    <span class="card-change {'positive' if data['macd_bullish'] else 'negative'}">
                        {'Bullish' if data['macd_bullish'] else 'Bearish'}
                    </span>
                </div>
            </div>
        </div>
"""

        # OPTION CHAIN ANALYSIS - CARD GRID
        if data['has_option_data']:
            html += f"""
        <div class="section">
            <div class="section-title">
                <span>🎯</span> OPTION CHAIN ANALYSIS
            </div>
            <div class="card-grid">
                <!-- PCR Ratio Card -->
                <div class="card {data['pcr_badge']}">
                    <span class="card-icon">{data['pcr_icon']}</span>
                    <div class="card-label">PCR RATIO (OI)</div>
                    <div class="card-value">{data['pcr']:.3f}</div>
                    <span class="card-change {data['pcr_badge']}">{data['pcr_status']}</span>
                </div>
                
                <!-- Max Pain Card -->
                <div class="card neutral">
                    <span class="card-icon">🎯</span>
                    <div class="card-label">MAX PAIN</div>
                    <div class="card-value">₹{data['max_pain']:,}</div>
                </div>
                
                <!-- Max Call OI Card -->
                <div class="card bearish">
                    <span class="card-icon">🔴</span>
                    <div class="card-label">MAX CALL OI</div>
                    <div class="card-value">₹{data['max_ce_oi']:,}</div>
                    <span class="card-change negative">Resistance</span>
                </div>
                
                <!-- Max Put OI Card -->
                <div class="card bullish">
                    <span class="card-icon">🟢</span>
                    <div class="card-label">MAX PUT OI</div>
                    <div class="card-value">₹{data['max_pe_oi']:,}</div>
                    <span class="card-change positive">Support</span>
                </div>
            </div>
        </div>
"""

        # OI CHANGE ANALYSIS - NEW SECTION
        if data['has_option_data']:
            html += f"""
        <div class="section">
            <div class="section-title">
                <span>📊</span> CHANGE IN OPEN INTEREST (Today's Market Direction)
            </div>
            
            <!-- OI Direction Box -->
            <div class="direction-box {data['oi_class']}" style="margin: 15px 0;">
                <div class="direction-title" style="font-size: 26px;">{data['oi_icon']} {data['oi_direction']}</div>
                <div class="direction-subtitle" style="font-size: 13px;">{data['oi_signal']}</div>
            </div>
            
            <!-- OI Change Cards -->
            <div class="card-grid" style="margin-top: 20px;">
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
            
            <!-- OI Change Explanation -->
            <div style="background: rgba(79, 195, 247, 0.1); padding: 18px; border-radius: 10px; margin-top: 20px; border-left: 4px solid #4fc3f7;">
                <p style="font-size: 13px; line-height: 1.8; color: #80deea;">
                    <strong style="color: #4fc3f7;">📖 How to Read:</strong><br>
                    • <strong>Call OI Increase (+)</strong> = Writers selling calls (Bearish) | <strong>Decrease (-)</strong> = Unwinding (Bullish)<br>
                    • <strong>Put OI Increase (+)</strong> = Writers selling puts (Bullish) | <strong>Decrease (-)</strong> = Unwinding (Bearish)<br>
                    • <strong>Net OI</strong> = Put Change - Call Change (Positive = Bullish, Negative = Bearish)
                </p>
            </div>
        </div>
"""

        # KEY LEVELS - CARD GRID
        html += f"""
        <div class="section">
            <div class="section-title">
                <span>📊</span> KEY LEVELS
            </div>
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

        <!-- TRADING RECOMMENDATION -->
        <div class="section">
            <div class="section-title">
                <span>💡</span> TRADING RECOMMENDATION
            </div>
            
            <div class="recommendation-box">
"""
        
        if data['strategy_type'] == "BULLISH":
            html += f"""
                <div class="rec-title">{data['bias_icon']} LONG / BUY Strategy</div>
                
                <div class="rec-grid">
                    <div class="rec-card">
                        <div class="rec-label">Entry Zone</div>
                        <div class="rec-value">₹{data['entry_low']:,.0f} - ₹{data['entry_high']:,.0f}</div>
                    </div>
                    <div class="rec-card">
                        <div class="rec-label">Target 1</div>
                        <div class="rec-value">₹{data['target_1']:,.0f}</div>
                    </div>
                    <div class="rec-card">
                        <div class="rec-label">Target 2</div>
                        <div class="rec-value">₹{data['target_2']:,}</div>
                    </div>
                    <div class="rec-card">
                        <div class="rec-label">Stop Loss</div>
                        <div class="rec-value stop-loss">₹{data['stop_loss']:,.0f}</div>
                    </div>
                    <div class="rec-card">
                        <div class="rec-label">Option Play</div>
                        <div class="rec-value" style="font-size: 16px;">{data['option_play']}</div>
                    </div>
                </div>
                
                <div class="risk-box">
                    <div class="risk-item">
                        <span class="risk-label">RISK</span>
                        <span class="risk-value">{data['risk_points']} pts</span>
                    </div>
                    <div class="risk-item">
                        <span class="risk-label">REWARD</span>
                        <span class="risk-value">{data['reward_points']} pts</span>
                    </div>
                    <div class="risk-item">
                        <span class="risk-label">R:R RATIO</span>
                        <span class="risk-value">1:{data['risk_reward_ratio']}</span>
                    </div>
                </div>
"""
        elif data['strategy_type'] == "BEARISH":
            html += f"""
                <div class="rec-title">{data['bias_icon']} SHORT / SELL Strategy</div>
                
                <div class="rec-grid">
                    <div class="rec-card">
                        <div class="rec-label">Entry Zone</div>
                        <div class="rec-value">₹{data['entry_low']:,.0f} - ₹{data['entry_high']:,.0f}</div>
                    </div>
                    <div class="rec-card">
                        <div class="rec-label">Target 1</div>
                        <div class="rec-value">₹{data['target_1']:,.0f}</div>
                    </div>
                    <div class="rec-card">
                        <div class="rec-label">Target 2</div>
                        <div class="rec-value">₹{data['target_2']:,}</div>
                    </div>
                    <div class="rec-card">
                        <div class="rec-label">Stop Loss</div>
                        <div class="rec-value stop-loss">₹{data['stop_loss']:,.0f}</div>
                    </div>
                    <div class="rec-card">
                        <div class="rec-label">Option Play</div>
                        <div class="rec-value" style="font-size: 16px;">{data['option_play']}</div>
                    </div>
                </div>
                
                <div class="risk-box">
                    <div class="risk-item">
                        <span class="risk-label">RISK</span>
                        <span class="risk-value">{data['risk_points']} pts</span>
                    </div>
                    <div class="risk-item">
                        <span class="risk-label">REWARD</span>
                        <span class="risk-value">{data['reward_points']} pts</span>
                    </div>
                    <div class="risk-item">
                        <span class="risk-label">R:R RATIO</span>
                        <span class="risk-value">1:{data['risk_reward_ratio']}</span>
                    </div>
                </div>
"""
        else:  # SIDEWAYS
            ic = data['iron_condor']
            html += f"""
                <div class="rec-title">{data['bias_icon']} IRON CONDOR (Range Trading)</div>
                
                <div class="rec-grid">
                    <div class="rec-card">
                        <div class="rec-label">Sell Options</div>
                        <div class="rec-value" style="font-size: 15px;">{ic['sell_ce']} CE + {ic['sell_pe']} PE</div>
                    </div>
                    <div class="rec-card">
                        <div class="rec-label">Buy Options</div>
                        <div class="rec-value" style="font-size: 15px;">{ic['buy_ce']} CE + {ic['buy_pe']} PE</div>
                    </div>
                    <div class="rec-card">
                        <div class="rec-label">Profit Zone</div>
                        <div class="rec-value">₹{ic['profit_low']:,.0f} - ₹{ic['profit_high']:,.0f}</div>
                    </div>
                </div>
"""
        
        html += """
            </div>
        </div>
"""

        # TOP STRIKES TABLE - SPLIT CALLS AND PUTS
        if data['has_option_data'] and (data['top_ce_strikes'] or data['top_pe_strikes']):
            html += """
        <div class="section">
            <div class="section-title">
                <span>📋</span> TOP 5 STRIKES (by Open Interest)
            </div>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                <!-- CALL OPTIONS (LEFT) -->
                <div>
                    <h3 style="color: #00bcd4; margin-bottom: 15px; font-size: 16px; display: flex; align-items: center; gap: 8px;">
                        <span>📞</span> CALL OPTIONS (CE)
                    </h3>
                    <table class="strikes-table">
                        <thead>
                            <tr>
                                <th>#</th>
                                <th>Strike</th>
                                <th>OI</th>
                                <th>LTP</th>
                            </tr>
                        </thead>
                        <tbody>
"""
            for i, strike in enumerate(data['top_ce_strikes'], 1):
                html += f"""
                            <tr>
                                <td><strong>{i}</strong></td>
                                <td><strong>₹{int(strike['Strike']):,}</strong></td>
                                <td>{int(strike['CE_OI']):,}</td>
                                <td style="color: #00bcd4; font-weight: 700;">₹{strike['CE_LTP']:.2f}</td>
                            </tr>
"""
            html += """
                        </tbody>
                    </table>
                </div>
                
                <!-- PUT OPTIONS (RIGHT) -->
                <div>
                    <h3 style="color: #f44336; margin-bottom: 15px; font-size: 16px; display: flex; align-items: center; gap: 8px;">
                        <span>📉</span> PUT OPTIONS (PE)
                    </h3>
                    <table class="strikes-table">
                        <thead>
                            <tr>
                                <th>#</th>
                                <th>Strike</th>
                                <th>OI</th>
                                <th>LTP</th>
                            </tr>
                        </thead>
                        <tbody>
"""
            for i, strike in enumerate(data['top_pe_strikes'], 1):
                html += f"""
                            <tr>
                                <td><strong>{i}</strong></td>
                                <td><strong>₹{int(strike['Strike']):,}</strong></td>
                                <td>{int(strike['PE_OI']):,}</td>
                                <td style="color: #f44336; font-weight: 700;">₹{strike['PE_LTP']:.2f}</td>
                            </tr>
"""
            html += """
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
"""

        # DISCLAIMER & FOOTER
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
    </div>
</body>
</html>
"""
        
        return html
    
    # ==================== FILE SAVING ====================
    
    def save_html_to_file(self, filename='index.html'):
        """Save HTML report to file for GitHub Pages"""
        try:
            print(f"\n📄 Saving HTML report to {filename}...")
            
            html_content = self.generate_html_email()
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"   ✅ HTML report saved to {filename}")
            
            metadata = {
                'timestamp': self.html_data['timestamp'],
                'current_price': float(self.html_data['current_price']),
                'bias': self.html_data['bias'],
                'confidence': self.html_data['confidence'],
                'rsi': float(self.html_data['rsi']),
                'pcr': float(self.html_data['pcr']) if self.html_data['has_option_data'] else None,
                'stop_loss': float(self.html_data['stop_loss']) if self.html_data['stop_loss'] else None,
                'risk_reward_ratio': self.html_data.get('risk_reward_ratio', 0)
            }
            
            with open('latest_report.json', 'w') as f:
                json.dump(metadata, f, indent=2)
            
            print(f"   ✅ Metadata saved to latest_report.json")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Failed to save HTML: {e}")
            return False
    
    # ==================== MAIN REPORT ====================
    
    def generate_full_report(self):
        """Generate complete analysis report"""
        ist_tz = pytz.timezone('Asia/Kolkata')
        ist_now = datetime.now(ist_tz)
        
        print("=" * 75)
        print("NIFTY 50 DAILY REPORT - ENHANCED CARD LAYOUT")
        print(f"Generated: {ist_now.strftime('%d-%b-%Y %H:%M IST')}")
        print("=" * 75)
        print()
        
        oc_data = self.fetch_nse_option_chain_silent()
        option_analysis = self.analyze_option_chain_data(oc_data) if oc_data else None
        
        print("Fetching technical data...")
        technical = self.get_technical_data()
        
        self.generate_analysis_data(technical, option_analysis)
        
        return option_analysis
    
    # ==================== EMAIL FUNCTIONALITY ====================
    
    def send_html_email_report(self):
        """Send HTML email report - with error handling to prevent duplicates"""
        
        gmail_user = os.getenv('GMAIL_USER')
        gmail_password = os.getenv('GMAIL_APP_PASSWORD')
        recipient1 = os.getenv('RECIPIENT_EMAIL_1')
        recipient2 = os.getenv('RECIPIENT_EMAIL_2')
        
        if not all([gmail_user, gmail_password, recipient1, recipient2]):
            print("\n⚠️  Email credentials not found in environment variables!")
            print("   Skipping email send...")
            return False
        
        try:
            ist_tz = pytz.timezone('Asia/Kolkata')
            ist_now = datetime.now(ist_tz)
            
            print(f"\n📧 Preparing HTML email report...")
            
            html_content = self.generate_html_email()
            
            msg = MIMEMultipart('alternative')
            msg['From'] = gmail_user
            msg['To'] = f"{recipient1}, {recipient2}"
            msg['Subject'] = f"📊 Nifty 50 Report - {ist_now.strftime('%d-%b-%Y %H:%M IST')}"
            
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            print(f"   📤 Sending email to {recipient1} and {recipient2}...")
            
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(gmail_user, gmail_password)
                server.send_message(msg)
            
            print(f"   ✅ Email sent successfully!")
            return True
            
        except Exception as e:
            print(f"\n❌ Failed to send email: {e}")
            return False


def main():
    """Main execution - FIXED to prevent duplicate emails"""
    try:
        print("\n🚀 Starting Nifty 50 HTML Analysis (Enhanced Card Layout)...\n")
        
        analyzer = NiftyHTMLAnalyzer()
        option_analysis = analyzer.generate_full_report()
        
        # Save HTML report
        print("\n" + "="*80)
        print("💾 SAVING HTML REPORT FOR GITHUB PAGES")
        print("="*80)
        save_success = analyzer.save_html_to_file('index.html')
        
        # Send email ONLY if save was successful
        if save_success:
            print("\n" + "="*80)
            print("📧 SENDING EMAIL REPORT")
            print("="*80)
            analyzer.send_html_email_report()
        else:
            print("\n⚠️  Skipping email send due to save failure")
        
        print("\n✅ Analysis complete!\n")
        
    except Exception as e:
        print(f"\n❌ Critical Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
