"""
NIFTY 50 COMPLETE ANALYSIS - DEEP OCEAN THEME
- Professional Deep Ocean Blue Theme
- Fixed: Tight stop losses (50-150 points max)
- Fixed: Email send duplication prevention
- Improved: Better risk management
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
        
        max_ce_oi_row = df.loc[df['CE_OI'].idxmax()]
        max_pe_oi_row = df.loc[df['PE_OI'].idxmax()]
        
        df['pain'] = abs(df['CE_OI'] - df['PE_OI'])
        max_pain_row = df.loc[df['pain'].idxmin()]
        
        df['Total_OI'] = df['CE_OI'] + df['PE_OI']
        top_strikes = df.nlargest(5, 'Total_OI')[['Strike', 'CE_OI', 'PE_OI', 'Total_OI']]
        
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
            'top_strikes': top_strikes.to_dict('records'),
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
            'macd_bullish': macd_bullish,
            'pcr': option_analysis['pcr_oi'] if option_analysis else 0,
            'pcr_status': pcr_status if option_analysis else 'N/A',
            'pcr_badge': pcr_badge if option_analysis else 'neutral',
            'pcr_icon': pcr_icon if option_analysis else '🟡',
            'max_pain': option_analysis['max_pain'] if option_analysis else 0,
            'max_ce_oi': max_ce_strike,
            'max_pe_oi': max_pe_strike,
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
            'top_strikes': option_analysis['top_strikes'] if option_analysis else [],
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
    
    # ==================== HTML GENERATION - DEEP OCEAN THEME ====================
    
    def generate_html_email(self):
        """Generate beautiful HTML with Deep Ocean Theme"""
        
        data = self.html_data
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nifty 50 Daily Report - Deep Ocean</title>
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
            max-width: 900px;
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
            margin-bottom: 20px;
            color: #4fc3f7;
            display: flex;
            align-items: center;
            gap: 12px;
            padding-bottom: 10px;
            border-bottom: 2px solid rgba(79, 195, 247, 0.3);
        }}
        
        .section-title span {{
            font-size: 24px;
        }}
        
        .metric-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        
        .metric-box {{
            background: linear-gradient(135deg, rgba(79, 195, 247, 0.1) 0%, rgba(79, 195, 247, 0.05) 100%);
            padding: 20px;
            border-radius: 12px;
            border-left: 4px solid #4fc3f7;
            transition: all 0.3s ease;
        }}
        
        .metric-box:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(79, 195, 247, 0.2);
        }}
        
        .metric-label {{
            font-size: 11px;
            color: #80deea;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 8px;
            font-weight: 600;
        }}
        
        .metric-value {{
            font-size: 24px;
            font-weight: 700;
            color: #ffffff;
        }}
        
        .direction-box {{
            background: linear-gradient(135deg, #0f2027 0%, #2c5364 100%);
            padding: 30px;
            border-radius: 12px;
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
            font-size: 28px;
            font-weight: 700;
            margin-bottom: 10px;
            color: #000;
        }}
        
        .direction-subtitle {{
            font-size: 14px;
            opacity: 0.9;
            color: #000;
        }}
        
        .indicator-row {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 16px 0;
            border-bottom: 1px solid rgba(79, 195, 247, 0.1);
        }}
        
        .indicator-row:last-child {{
            border-bottom: none;
        }}
        
        .indicator-name {{
            font-weight: 600;
            color: #b0bec5;
            font-size: 15px;
        }}
        
        .indicator-value {{
            font-weight: 700;
            color: #ffffff;
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 15px;
        }}
        
        .badge {{
            display: inline-block;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
        }}
        
        .badge.bullish {{
            background: rgba(0, 188, 212, 0.2);
            color: #00bcd4;
            border: 1px solid #00bcd4;
        }}
        
        .badge.bearish {{
            background: rgba(244, 67, 54, 0.2);
            color: #f44336;
            border: 1px solid #f44336;
        }}
        
        .badge.neutral {{
            background: rgba(255, 183, 77, 0.2);
            color: #ffb74d;
            border: 1px solid #ffb74d;
        }}
        
        .levels-container {{
            margin: 20px 0;
        }}
        
        .level-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 14px 20px;
            margin: 10px 0;
            border-radius: 8px;
            font-weight: 600;
            transition: all 0.3s ease;
        }}
        
        .level-item:hover {{
            transform: translateX(5px);
        }}
        
        .level-item.resistance {{
            background: rgba(244, 67, 54, 0.1);
            border-left: 4px solid #f44336;
        }}
        
        .level-item.current {{
            background: rgba(79, 195, 247, 0.2);
            border-left: 4px solid #4fc3f7;
            font-size: 16px;
            box-shadow: 0 0 20px rgba(79, 195, 247, 0.3);
        }}
        
        .level-item.support {{
            background: rgba(0, 188, 212, 0.1);
            border-left: 4px solid #00bcd4;
        }}
        
        .recommendation-box {{
            background: linear-gradient(135deg, rgba(79, 195, 247, 0.1) 0%, rgba(79, 195, 247, 0.05) 100%);
            padding: 25px;
            border-radius: 12px;
            border: 2px solid #4fc3f7;
            margin: 20px 0;
        }}
        
        .rec-title {{
            font-size: 20px;
            font-weight: 700;
            color: #4fc3f7;
            margin-bottom: 20px;
        }}
        
        .rec-detail {{
            display: flex;
            justify-content: space-between;
            padding: 12px 0;
            border-bottom: 1px dashed rgba(79, 195, 247, 0.2);
        }}
        
        .rec-detail:last-child {{
            border-bottom: none;
        }}
        
        .rec-label {{
            color: #80deea;
            font-weight: 600;
            font-size: 14px;
        }}
        
        .rec-value {{
            color: #ffffff;
            font-weight: 700;
            font-size: 15px;
        }}
        
        .rec-value.stop-loss {{
            color: #f44336;
            font-size: 16px;
        }}
        
        .risk-box {{
            background: rgba(255, 183, 77, 0.15);
            padding: 15px;
            border-radius: 8px;
            margin-top: 15px;
            border-left: 4px solid #ffb74d;
        }}
        
        .risk-detail {{
            display: flex;
            justify-content: space-between;
            padding: 6px 0;
            font-size: 14px;
            color: #ffb74d;
        }}
        
        .strikes-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        
        .strikes-table th {{
            background: linear-gradient(135deg, #4fc3f7 0%, #26c6da 100%);
            color: #000;
            padding: 14px;
            text-align: left;
            font-weight: 700;
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .strikes-table td {{
            padding: 14px;
            border-bottom: 1px solid rgba(79, 195, 247, 0.1);
            color: #b0bec5;
            font-size: 14px;
        }}
        
        .strikes-table tr:hover {{
            background: rgba(79, 195, 247, 0.05);
        }}
        
        .disclaimer {{
            background: rgba(255, 183, 77, 0.15);
            padding: 25px;
            border-radius: 10px;
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
        
        @media only screen and (max-width: 600px) {{
            .metric-grid {{
                grid-template-columns: 1fr;
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
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 NIFTY 50 DAILY REPORT</h1>
            <p>Generated: {data['timestamp']}</p>
        </div>

        <div class="section">
            <div class="section-title">
                <span>📈</span> MARKET SNAPSHOT
            </div>
            <div class="metric-grid">
                <div class="metric-box">
                    <div class="metric-label">Nifty 50</div>
                    <div class="metric-value">₹{data['current_price']:,.2f}</div>
                </div>
                <div class="metric-box">
                    <div class="metric-label">Expiry Date</div>
                    <div class="metric-value">{data['expiry']}</div>
                </div>
            </div>
        </div>

        <div class="section">
            <div class="direction-box {data['bias_class']}">
                <div class="direction-title">{data['bias_icon']} MARKET DIRECTION: {data['bias']}</div>
                <div class="direction-subtitle">Confidence: {data['confidence']} | Score: {data['bullish_score']} Bullish vs {data['bearish_score']} Bearish</div>
            </div>
        </div>

        <div class="section">
            <div class="section-title">
                <span>🔍</span> TECHNICAL INDICATORS
            </div>
            
            <div class="indicator-row">
                <span class="indicator-name">RSI (14)</span>
                <span class="indicator-value">
                    {data['rsi']:.1f}
                    <span class="badge {data['rsi_badge']}">{data['rsi_icon']} {data['rsi_status']}</span>
                </span>
            </div>
            
            <div class="indicator-row">
                <span class="indicator-name">SMA 20</span>
                <span class="indicator-value">
                    ₹{data['sma_20']:,.0f}
                    <span class="badge {'bullish' if data['sma_20_above'] else 'bearish'}">{'✅ Above' if data['sma_20_above'] else '❌ Below'}</span>
                </span>
            </div>
            
            <div class="indicator-row">
                <span class="indicator-name">SMA 50</span>
                <span class="indicator-value">
                    ₹{data['sma_50']:,.0f}
                    <span class="badge {'bullish' if data['sma_50_above'] else 'bearish'}">{'✅ Above' if data['sma_50_above'] else '❌ Below'}</span>
                </span>
            </div>
            
            <div class="indicator-row">
                <span class="indicator-name">SMA 200</span>
                <span class="indicator-value">
                    ₹{data['sma_200']:,.0f}
                    <span class="badge {'bullish' if data['sma_200_above'] else 'bearish'}">{'✅ Above' if data['sma_200_above'] else '❌ Below'}</span>
                </span>
            </div>
            
            <div class="indicator-row">
                <span class="indicator-name">MACD</span>
                <span class="indicator-value">
                    <span class="badge {'bullish' if data['macd_bullish'] else 'bearish'}">{'✅ Bullish' if data['macd_bullish'] else '❌ Bearish'}</span>
                </span>
            </div>
        </div>
"""

        if data['has_option_data']:
            html += f"""
        <div class="section">
            <div class="section-title">
                <span>🎯</span> OPTION CHAIN ANALYSIS
            </div>
            
            <div class="indicator-row">
                <span class="indicator-name">PCR Ratio (OI)</span>
                <span class="indicator-value">
                    {data['pcr']:.3f}
                    <span class="badge {data['pcr_badge']}">{data['pcr_icon']} {data['pcr_status']}</span>
                </span>
            </div>
            
            <div class="indicator-row">
                <span class="indicator-name">Max Pain</span>
                <span class="indicator-value">{data['max_pain']:,}</span>
            </div>
            
            <div class="indicator-row">
                <span class="indicator-name">Max Call OI (Resistance)</span>
                <span class="indicator-value">{data['max_ce_oi']:,}</span>
            </div>
            
            <div class="indicator-row">
                <span class="indicator-name">Max Put OI (Support)</span>
                <span class="indicator-value">{data['max_pe_oi']:,}</span>
            </div>
        </div>
"""

        html += f"""
        <div class="section">
            <div class="section-title">
                <span>📊</span> KEY LEVELS
            </div>
            
            <div class="levels-container">
                <div class="level-item resistance">
                    <span>🔴 Strong Resistance</span>
                    <strong>₹{data['strong_resistance']:,.0f}</strong>
                </div>
                <div class="level-item resistance">
                    <span>🟠 Resistance</span>
                    <strong>₹{data['resistance']:,.0f}</strong>
                </div>
                <div class="level-item current">
                    <span>⚪ Current Price</span>
                    <strong>₹{data['current_price']:,.0f}</strong>
                </div>
"""
        
        if data['has_option_data']:
            html += f"""
                <div class="level-item support">
                    <span>🟡 Max Pain</span>
                    <strong>₹{data['max_pain']:,}</strong>
                </div>
"""
        
        html += f"""
                <div class="level-item support">
                    <span>🟢 Support</span>
                    <strong>₹{data['support']:,.0f}</strong>
                </div>
                <div class="level-item support">
                    <span>🟢 Strong Support</span>
                    <strong>₹{data['strong_support']:,.0f}</strong>
                </div>
            </div>
        </div>

        <div class="section">
            <div class="section-title">
                <span>💡</span> TRADING RECOMMENDATION
            </div>
            
            <div class="recommendation-box">
"""
        
        if data['strategy_type'] == "BULLISH":
            html += f"""
                <div class="rec-title">{data['bias_icon']} LONG / BUY Strategy</div>
                
                <div class="rec-detail">
                    <span class="rec-label">Entry Zone</span>
                    <span class="rec-value">₹{data['entry_low']:,.0f} - ₹{data['entry_high']:,.0f}</span>
                </div>
                
                <div class="rec-detail">
                    <span class="rec-label">Target 1</span>
                    <span class="rec-value">₹{data['target_1']:,.0f}</span>
                </div>
                
                <div class="rec-detail">
                    <span class="rec-label">Target 2</span>
                    <span class="rec-value">₹{data['target_2']:,}</span>
                </div>
                
                <div class="rec-detail">
                    <span class="rec-label">Stop Loss</span>
                    <span class="rec-value stop-loss">₹{data['stop_loss']:,.0f}</span>
                </div>
                
                <div class="rec-detail">
                    <span class="rec-label">Option Play</span>
                    <span class="rec-value">{data['option_play']}</span>
                </div>
                
                <div class="risk-box">
                    <div class="risk-detail">
                        <span><strong>Risk:</strong> {data['risk_points']} points</span>
                        <span><strong>Reward:</strong> {data['reward_points']} points</span>
                    </div>
                    <div class="risk-detail">
                        <span><strong>Risk:Reward Ratio:</strong> 1:{data['risk_reward_ratio']}</span>
                    </div>
                </div>
"""
        elif data['strategy_type'] == "BEARISH":
            html += f"""
                <div class="rec-title">{data['bias_icon']} SHORT / SELL Strategy</div>
                
                <div class="rec-detail">
                    <span class="rec-label">Entry Zone</span>
                    <span class="rec-value">₹{data['entry_low']:,.0f} - ₹{data['entry_high']:,.0f}</span>
                </div>
                
                <div class="rec-detail">
                    <span class="rec-label">Target 1</span>
                    <span class="rec-value">₹{data['target_1']:,.0f}</span>
                </div>
                
                <div class="rec-detail">
                    <span class="rec-label">Target 2</span>
                    <span class="rec-value">₹{data['target_2']:,}</span>
                </div>
                
                <div class="rec-detail">
                    <span class="rec-label">Stop Loss</span>
                    <span class="rec-value stop-loss">₹{data['stop_loss']:,.0f}</span>
                </div>
                
                <div class="rec-detail">
                    <span class="rec-label">Option Play</span>
                    <span class="rec-value">{data['option_play']}</span>
                </div>
                
                <div class="risk-box">
                    <div class="risk-detail">
                        <span><strong>Risk:</strong> {data['risk_points']} points</span>
                        <span><strong>Reward:</strong> {data['reward_points']} points</span>
                    </div>
                    <div class="risk-detail">
                        <span><strong>Risk:Reward Ratio:</strong> 1:{data['risk_reward_ratio']}</span>
                    </div>
                </div>
"""
        else:
            ic = data['iron_condor']
            html += f"""
                <div class="rec-title">{data['bias_icon']} IRON CONDOR (Range Trading)</div>
                
                <div class="rec-detail">
                    <span class="rec-label">Sell Options</span>
                    <span class="rec-value">{ic['sell_ce']} CE + {ic['sell_pe']} PE</span>
                </div>
                
                <div class="rec-detail">
                    <span class="rec-label">Buy Options</span>
                    <span class="rec-value">{ic['buy_ce']} CE + {ic['buy_pe']} PE</span>
                </div>
                
                <div class="rec-detail">
                    <span class="rec-label">Profit Zone</span>
                    <span class="rec-value">₹{ic['profit_low']:,.0f} - ₹{ic['profit_high']:,.0f}</span>
                </div>
"""
        
        html += """
            </div>
        </div>
"""

        if data['has_option_data'] and data['top_strikes']:
            html += """
        <div class="section">
            <div class="section-title">
                <span>📋</span> TOP 5 STRIKES (by Open Interest)
            </div>
            
            <table class="strikes-table">
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Strike</th>
                        <th>CE OI</th>
                        <th>PE OI</th>
                        <th>Total OI</th>
                    </tr>
                </thead>
                <tbody>
"""
            for i, strike in enumerate(data['top_strikes'], 1):
                html += f"""
                    <tr>
                        <td>{i}</td>
                        <td>₹{int(strike['Strike']):,}</td>
                        <td>{int(strike['CE_OI']):,}</td>
                        <td>{int(strike['PE_OI']):,}</td>
                        <td><strong>{int(strike['Total_OI']):,}</strong></td>
                    </tr>
"""
            html += """
                </tbody>
            </table>
        </div>
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
        print("NIFTY 50 DAILY REPORT - DEEP OCEAN THEME")
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
        print("\n🚀 Starting Nifty 50 HTML Analysis (Deep Ocean Theme)...\n")
        
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
