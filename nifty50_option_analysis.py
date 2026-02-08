"""
NIFTY 50 COMPLETE ANALYSIS - GitHub Automated Version with HTML Email
Technical Analysis + Live NSE Option Chain + Beautiful HTML Email Reports

This script:
1. Fetches live NSE option chain data
2. Performs technical analysis
3. Generates trading recommendations
4. Sends BEAUTIFUL HTML emails to specified recipients

Environment Variables Required (GitHub Secrets):
- GMAIL_USER: Your Gmail address
- GMAIL_APP_PASSWORD: Gmail App Password (not regular password)
- RECIPIENT_EMAIL_1: First recipient email
- RECIPIENT_EMAIL_2: Second recipient email
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
warnings.filterwarnings('ignore')


class NiftyHTMLAnalyzer:
    def __init__(self):
        self.yf_symbol = "^NSEI"
        self.nse_symbol = "NIFTY"
        self.report_lines = []  # Store report lines for console
        self.html_data = {}  # Store data for HTML generation
        
    def log(self, message):
        """Log message to console only"""
        print(message)
        self.report_lines.append(message)
    
    # ==================== NSE OPTION CHAIN LOGIC ====================
    
    def get_upcoming_expiry_tuesday(self):
        """Calculates the date of the current or next Tuesday"""
        now = datetime.now()
        days_ahead = (1 - now.weekday() + 7) % 7
        
        if days_ahead == 0 and now.hour >= 15 and now.minute >= 30:
            days_ahead = 7
            
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
    
    # ==================== ANALYSIS & DATA COLLECTION ====================
    
    def generate_analysis_data(self, technical, option_analysis):
        """Generate analysis and collect data for HTML"""
        
        if not technical:
            self.log("⚠️  Technical data unavailable")
            return
        
        current = technical['current_price']
        
        # Calculate scores (NO CHANGES TO LOGIC)
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
        
        # MACD status
        macd_bullish = technical['macd'] > technical['signal']
        
        # PCR status
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
        support = technical['support']
        resistance = technical['resistance']
        
        if option_analysis:
            max_ce_strike = option_analysis['max_ce_oi_strike']
            max_pe_strike = option_analysis['max_pe_oi_strike']
        else:
            max_ce_strike = int(current/50)*50 + 200
            max_pe_strike = int(current/50)*50 - 200
        
        # Store all data for HTML generation
        self.html_data = {
            'timestamp': datetime.now().strftime('%d-%b-%Y %H:%M IST'),
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
            'entry_low': support if bias == "BULLISH" else current,
            'entry_high': current if bias == "BULLISH" else resistance,
            'target_1': resistance if bias == "BULLISH" else support,
            'target_2': max_ce_strike if bias == "BULLISH" else max_pe_strike,
            'stop_loss': support - 100 if bias == "BULLISH" else resistance + 100,
            'option_play': f"Buy {int(current/50)*50 + 50} CE" if bias == "BULLISH" else f"Buy {int(current/50)*50 - 50} PE",
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
    
    # ==================== HTML GENERATION ====================
    
    def generate_html_email(self):
        """Generate beautiful HTML email"""
        
        data = self.html_data
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nifty 50 Daily Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f5f5f5;
            margin: 0;
            padding: 20px;
            color: #333;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            background-color: #ffffff;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 28px;
            font-weight: 600;
        }}
        .header p {{
            margin: 10px 0 0 0;
            font-size: 14px;
            opacity: 0.9;
        }}
        .section {{
            padding: 25px 30px;
            border-bottom: 1px solid #eee;
        }}
        .section:last-child {{
            border-bottom: none;
        }}
        .section-title {{
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 15px;
            color: #2c3e50;
            display: flex;
            align-items: center;
        }}
        .section-title span {{
            margin-right: 10px;
            font-size: 22px;
        }}
        .metric-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
            margin-top: 15px;
        }}
        .metric-box {{
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }}
        .metric-label {{
            font-size: 12px;
            color: #6c757d;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 5px;
        }}
        .metric-value {{
            font-size: 20px;
            font-weight: 600;
            color: #2c3e50;
        }}
        .direction-box {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            margin: 15px 0;
        }}
        .direction-box.bullish {{
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        }}
        .direction-box.bearish {{
            background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        }}
        .direction-box.sideways {{
            background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        }}
        .direction-title {{
            font-size: 24px;
            font-weight: 700;
            margin-bottom: 10px;
        }}
        .direction-subtitle {{
            font-size: 14px;
            opacity: 0.9;
        }}
        .indicator-row {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 0;
            border-bottom: 1px solid #eee;
        }}
        .indicator-row:last-child {{
            border-bottom: none;
        }}
        .indicator-name {{
            font-weight: 500;
            color: #495057;
        }}
        .indicator-value {{
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
        }}
        .badge.bullish {{
            background-color: #d4edda;
            color: #155724;
        }}
        .badge.bearish {{
            background-color: #f8d7da;
            color: #721c24;
        }}
        .badge.neutral {{
            background-color: #fff3cd;
            color: #856404;
        }}
        .levels-container {{
            position: relative;
            padding: 20px 0;
        }}
        .level-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 15px;
            margin: 8px 0;
            border-radius: 6px;
            font-weight: 500;
        }}
        .level-item.resistance {{
            background-color: #ffe5e5;
            border-left: 4px solid #dc3545;
        }}
        .level-item.current {{
            background-color: #e3f2fd;
            border-left: 4px solid #2196f3;
            font-weight: 700;
        }}
        .level-item.support {{
            background-color: #e8f5e9;
            border-left: 4px solid #28a745;
        }}
        .recommendation-box {{
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            border: 2px solid #667eea;
            margin: 15px 0;
        }}
        .rec-title {{
            font-size: 18px;
            font-weight: 600;
            color: #667eea;
            margin-bottom: 15px;
        }}
        .rec-detail {{
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px dashed #dee2e6;
        }}
        .rec-detail:last-child {{
            border-bottom: none;
        }}
        .rec-label {{
            color: #6c757d;
            font-weight: 500;
        }}
        .rec-value {{
            color: #2c3e50;
            font-weight: 600;
        }}
        .strikes-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}
        .strikes-table th {{
            background-color: #667eea;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
            font-size: 14px;
        }}
        .strikes-table td {{
            padding: 12px;
            border-bottom: 1px solid #eee;
        }}
        .strikes-table tr:hover {{
            background-color: #f8f9fa;
        }}
        .disclaimer {{
            background-color: #fff3cd;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #ffc107;
            font-size: 13px;
            color: #856404;
            line-height: 1.6;
        }}
        .footer {{
            text-align: center;
            padding: 20px;
            color: #6c757d;
            font-size: 12px;
        }}
        @media only screen and (max-width: 600px) {{
            .metric-grid {{
                grid-template-columns: 1fr;
            }}
            .container {{
                border-radius: 0;
            }}
            body {{
                padding: 0;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>📊 NIFTY 50 DAILY REPORT</h1>
            <p>Generated: {data['timestamp']}</p>
        </div>

        <!-- Market Snapshot -->
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

        <!-- Market Direction -->
        <div class="section">
            <div class="direction-box {data['bias_class']}">
                <div class="direction-title">{data['bias_icon']} MARKET DIRECTION: {data['bias']}</div>
                <div class="direction-subtitle">Confidence: {data['confidence']} | Score: {data['bullish_score']} Bullish vs {data['bearish_score']} Bearish</div>
            </div>
        </div>

        <!-- Technical Indicators -->
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

        # Option Chain section (only if data available)
        if data['has_option_data']:
            html += f"""
        <!-- Option Chain Analysis -->
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

        # Key Levels
        html += f"""
        <!-- Key Levels -->
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

        <!-- Trading Recommendation -->
        <div class="section">
            <div class="section-title">
                <span>💡</span> TRADING RECOMMENDATION
            </div>
            
            <div class="recommendation-box">
"""
        
        # Trading recommendation based on strategy
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
                    <span class="rec-value">₹{data['stop_loss']:,.0f}</span>
                </div>
                
                <div class="rec-detail">
                    <span class="rec-label">Option Play</span>
                    <span class="rec-value">{data['option_play']}</span>
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
                    <span class="rec-value">₹{data['stop_loss']:,.0f}</span>
                </div>
                
                <div class="rec-detail">
                    <span class="rec-label">Option Play</span>
                    <span class="rec-value">{data['option_play']}</span>
                </div>
"""
        else:  # SIDEWAYS
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

        # Top Strikes section (only if data available)
        if data['has_option_data'] and data['top_strikes']:
            html += """
        <!-- Top Strikes -->
        <div class="section">
            <div class="section-title">
                <span>📋</span> TOP 5 STRIKES (by Open Interest)
            </div>
            
            <table class="strikes-table">
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Strike</th>
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
                        <td>{int(strike['Total_OI']):,}</td>
                    </tr>
"""
            html += """
                </tbody>
            </table>
        </div>
"""

        # Disclaimer and Footer
        html += """
        <!-- Disclaimer -->
        <div class="section">
            <div class="disclaimer">
                <strong>⚠️ DISCLAIMER</strong><br><br>
                This is for EDUCATIONAL purposes only - NOT financial advice.<br>
                Always use stop losses and consult a SEBI registered advisor.
            </div>
        </div>

        <!-- Footer -->
        <div class="footer">
            <p>Automated Nifty 50 Analysis Report</p>
            <p>© 2026 - For Educational Purposes Only</p>
        </div>
    </div>
</body>
</html>
"""
        
        return html
    
    # ==================== MAIN REPORT ====================
    
    def generate_full_report(self):
        """Generate complete analysis report"""
        print("=" * 75)
        print("NIFTY 50 DAILY REPORT")
        print(f"Generated: {datetime.now().strftime('%d-%b-%Y %H:%M IST')}")
        print("=" * 75)
        print()
        
        # Fetch Option Chain (silent mode)
        oc_data = self.fetch_nse_option_chain_silent()
        option_analysis = self.analyze_option_chain_data(oc_data) if oc_data else None
        
        # Get Technical Data
        print("Fetching technical data...")
        technical = self.get_technical_data()
        
        # Generate Analysis Data (NO LOGIC CHANGES)
        self.generate_analysis_data(technical, option_analysis)
        
        return option_analysis
    
    # ==================== EMAIL FUNCTIONALITY ====================
    
    def send_html_email_report(self):
        """Send HTML email report"""
        
        # Get email credentials from environment variables
        gmail_user = os.getenv('GMAIL_USER')
        gmail_password = os.getenv('GMAIL_APP_PASSWORD')
        recipient1 = os.getenv('RECIPIENT_EMAIL_1')
        recipient2 = os.getenv('RECIPIENT_EMAIL_2')
        
        if not all([gmail_user, gmail_password, recipient1, recipient2]):
            print("\n❌ Email credentials not found in environment variables!")
            print("Required: GMAIL_USER, GMAIL_APP_PASSWORD, RECIPIENT_EMAIL_1, RECIPIENT_EMAIL_2")
            return False
        
        try:
            print(f"\n📧 Preparing HTML email report...")
            
            # Generate HTML
            html_content = self.generate_html_email()
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = gmail_user
            msg['To'] = f"{recipient1}, {recipient2}"
            msg['Subject'] = f"📊 Nifty 50 Analysis Report - {datetime.now().strftime('%d-%b-%Y %H:%M')}"
            
            # Attach HTML
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Send email
            print(f"   📤 Sending HTML email to {recipient1} and {recipient2}...")
            
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(gmail_user, gmail_password)
                server.send_message(msg)
            
            print(f"   ✅ HTML email sent successfully!")
            return True
            
        except Exception as e:
            print(f"\n❌ Failed to send email: {e}")
            print("\nTroubleshooting:")
            print("1. Make sure you're using Gmail App Password, not regular password")
            print("2. Enable 2-factor authentication in Gmail")
            print("3. Generate App Password: https://myaccount.google.com/apppasswords")
            print("4. Check environment variables are set correctly")
            return False


def main():
    """Main execution"""
    try:
        print("\n🚀 Starting Nifty 50 HTML Analysis...\n")
        
        analyzer = NiftyHTMLAnalyzer()
        option_analysis = analyzer.generate_full_report()
        
        # Send HTML email report
        print("\n" + "="*80)
        print("📧 HTML EMAIL REPORT")
        print("="*80)
        analyzer.send_html_email_report()
        
        print("\n✅ Analysis complete!\n")
        
    except Exception as e:
        print(f"\n❌ Critical Error: {e}")
        import traceback
        traceback.print_exc()
        print("\nTroubleshooting:")
        print("1. Install: pip install curl_cffi pandas yfinance")
        print("2. Check internet connection")
        print("3. Verify environment variables are set")
        print("4. Run during market hours for best results")


if __name__ == "__main__":
    main()
