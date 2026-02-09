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
        self.report_lines = []  
        self.html_data = {}  
        
    def log(self, message):
        print(message)
        self.report_lines.append(message)
    
    def get_upcoming_expiry_tuesday(self):
        now = datetime.now()
        days_ahead = (1 - now.weekday() + 7) % 7
        if days_ahead == 0 and now.hour >= 15 and now.minute >= 30:
            days_ahead = 7
        expiry_date = now + timedelta(days=days_ahead)
        return expiry_date.strftime('%d-%b-%Y')
    
    def fetch_nse_option_chain_silent(self):
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
                    return None
                rows = []
                for item in data:
                    strike = item.get('strikePrice')
                    ce = item.get('CE', {})
                    pe = item.get('PE', {})
                    rows.append({
                        'Expiry': selected_expiry, 'Strike': strike,
                        'CE_LTP': ce.get('lastPrice', 0), 'CE_OI': ce.get('openInterest', 0),
                        'CE_Vol': ce.get('totalTradedVolume', 0), 'PE_LTP': pe.get('lastPrice', 0),
                        'PE_OI': pe.get('openInterest', 0), 'PE_Vol': pe.get('totalTradedVolume', 0)
                    })
                df = pd.DataFrame(rows).sort_values('Strike')
                return {'expiry': selected_expiry, 'df': df, 'raw_data': data, 'underlying': json_data.get('records', {}).get('underlyingValue', 0)}
            return None
        except Exception as e:
            print(f"NSE Fetch Error: {e}")
            return None
    
    def analyze_option_chain_data(self, oc_data):
        if not oc_data: return None
        df = oc_data['df']
        total_ce_oi, total_pe_oi = df['CE_OI'].sum(), df['PE_OI'].sum()
        total_ce_vol, total_pe_vol = df['CE_Vol'].sum(), df['PE_Vol'].sum()
        pcr_oi = total_pe_oi / total_ce_oi if total_ce_oi > 0 else 0
        pcr_vol = total_pe_vol / total_ce_vol if total_ce_vol > 0 else 0
        max_ce_oi_row = df.loc[df['CE_OI'].idxmax()]
        max_pe_oi_row = df.loc[df['PE_OI'].idxmax()]
        df['pain'] = abs(df['CE_OI'] - df['PE_OI'])
        max_pain_row = df.loc[df['pain'].idxmin()]
        df['Total_OI'] = df['CE_OI'] + df['PE_OI']
        top_strikes = df.nlargest(5, 'Total_OI')[['Strike', 'CE_OI', 'PE_OI', 'Total_OI']]
        return {
            'expiry': oc_data['expiry'], 'underlying_value': oc_data['underlying'],
            'pcr_oi': round(pcr_oi, 3), 'pcr_volume': round(pcr_vol, 3),
            'total_ce_oi': int(total_ce_oi), 'total_pe_oi': int(total_pe_oi),
            'max_ce_oi_strike': int(max_ce_oi_row['Strike']), 'max_ce_oi_value': int(max_ce_oi_row['CE_OI']),
            'max_pe_oi_strike': int(max_pe_oi_row['Strike']), 'max_pe_oi_value': int(max_pe_oi_row['PE_OI']),
            'max_pain': int(max_pain_row['Strike']), 'top_strikes': top_strikes.to_dict('records'), 'df': df
        }
    
    def get_technical_data(self):
        try:
            nifty = yf.Ticker(self.yf_symbol)
            df = nifty.history(period="1y")
            if df.empty: return None
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
            return {
                'current_price': latest['Close'], 'sma_20': latest['SMA_20'], 'sma_50': latest['SMA_50'],
                'sma_200': latest['SMA_200'], 'rsi': latest['RSI'], 'macd': latest['MACD'],
                'signal': latest['Signal'], 'resistance': recent['High'].quantile(0.90), 'support': recent['Low'].quantile(0.10),
            }
        except Exception as e:
            print(f"Technical analysis error: {e}")
            return None
    
    def generate_analysis_data(self, technical, option_analysis):
        if not technical: return
        current = technical['current_price']
        bullish_score, bearish_score = 0, 0
        if current > technical['sma_20']: bullish_score += 1
        else: bearish_score += 1
        if current > technical['sma_50']: bullish_score += 1
        else: bearish_score += 1
        if current > technical['sma_200']: bullish_score += 1
        else: bearish_score += 1
        
        rsi = technical['rsi']
        if rsi > 70: bearish_score += 1
        elif rsi < 30: bullish_score += 2
        
        if technical['macd'] > technical['signal']: bullish_score += 1
        else: bearish_score += 1
        
        if option_analysis:
            pcr = option_analysis['pcr_oi']
            if pcr > 1.2: bullish_score += 2
            elif pcr < 0.7: bearish_score += 2
        
        score_diff = bullish_score - bearish_score
        if bullish_score > bearish_score + 2:
            bias, bias_icon, bias_class = "BULLISH", "📈", "bullish"
            confidence = "HIGH" if score_diff >= 4 else "MEDIUM"
        elif bearish_score > bullish_score + 2:
            bias, bias_icon, bias_class = "BEARISH", "📉", "bearish"
            confidence = "HIGH" if abs(score_diff) >= 4 else "MEDIUM"
        else:
            bias, bias_icon, bias_class, confidence = "SIDEWAYS", "↔️", "sideways", "MEDIUM"

        # Constructing the dictionary for HTML
        self.html_data = {
            'timestamp': datetime.now().strftime('%d-%b-%Y %H:%M IST'),
            'current_price': current, 'expiry': option_analysis['expiry'] if option_analysis else 'N/A',
            'bias': bias, 'bias_icon': bias_icon, 'bias_class': bias_class, 'confidence': confidence,
            'bullish_score': bullish_score, 'bearish_score': bearish_score,
            'rsi': rsi, 'rsi_status': "Overbought" if rsi > 70 else ("Oversold" if rsi < 30 else "Neutral"),
            'rsi_badge': "bearish" if rsi > 70 else ("bullish" if rsi < 30 else "neutral"),
            'rsi_icon': "🔴" if rsi > 70 else ("🟢" if rsi < 30 else "🟡"),
            'sma_20': technical['sma_20'], 'sma_20_above': current > technical['sma_20'],
            'sma_50': technical['sma_50'], 'sma_50_above': current > technical['sma_50'],
            'sma_200': technical['sma_200'], 'sma_200_above': current > technical['sma_200'],
            'macd_bullish': technical['macd'] > technical['signal'],
            'pcr': option_analysis['pcr_oi'] if option_analysis else 0,
            'pcr_status': "Bullish" if (option_analysis and option_analysis['pcr_oi'] > 1.2) else "Neutral",
            'pcr_badge': "bullish" if (option_analysis and option_analysis['pcr_oi'] > 1.2) else "neutral",
            'pcr_icon': "🟢" if (option_analysis and option_analysis['pcr_oi'] > 1.2) else "🟡",
            'max_pain': option_analysis['max_pain'] if option_analysis else 0,
            'max_ce_oi': option_analysis['max_ce_oi_strike'] if option_analysis else 0,
            'max_pe_oi': option_analysis['max_pe_oi_strike'] if option_analysis else 0,
            'support': technical['support'], 'resistance': technical['resistance'],
            'strong_support': technical['support'] - 100, 'strong_resistance': technical['resistance'] + 100,
            'strategy_type': bias, 'has_option_data': option_analysis is not None,
            'top_strikes': option_analysis['top_strikes'] if option_analysis else [],
            'target_1': technical['resistance'] if bias == "BULLISH" else technical['support'],
            'target_2': (option_analysis['max_ce_oi_strike'] if option_analysis else current+200) if bias == "BULLISH" else (option_analysis['max_pe_oi_strike'] if option_analysis else current-200),
            'stop_loss': technical['support'] - 100 if bias == "BULLISH" else technical['resistance'] + 100,
            'entry_low': technical['support'] if bias == "BULLISH" else current,
            'entry_high': current if bias == "BULLISH" else technical['resistance'],
            'option_play': f"Buy {int(current/50)*50 + 50} CE" if bias == "BULLISH" else f"Buy {int(current/50)*50 - 50} PE"
        }
        if bias == "SIDEWAYS":
            self.html_data['iron_condor'] = {'sell_ce': int(technical['resistance']/50)*50, 'sell_pe': int(technical['support']/50)*50, 
                                           'buy_ce': int(technical['resistance']/50)*50 + 50, 'buy_pe': int(technical['support']/50)*50 - 50,
                                           'profit_low': technical['support'], 'profit_high': technical['resistance']}

    def generate_html_email(self):
        data = self.html_data
        
        # CONSTRUCTION OF GITHUB RUN LINK
        run_id = os.getenv("GITHUB_RUN_ID")
        repo = os.getenv("GITHUB_REPO")
        github_link = f"https://github.com/{repo}/actions/runs/{run_id}" if run_id and repo else "#"

        html = f"""
        <html>
        <head>
            <style>
                .container {{ font-family: sans-serif; max-width: 600px; margin: auto; border: 1px solid #ddd; border-radius: 8px; overflow: hidden; }}
                .header {{ background: #4a148c; color: white; padding: 20px; text-align: center; }}
                .section {{ padding: 20px; border-bottom: 1px solid #eee; }}
                .bullish {{ color: green; font-weight: bold; }}
                .bearish {{ color: red; font-weight: bold; }}
                .btn {{ background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header"><h1>Nifty 50 Analysis</h1><p>{data['timestamp']}</p></div>
                <div class="section">
                    <h2>Market Bias: <span class="{data['bias_class']}">{data['bias_icon']} {data['bias']}</span></h2>
                    <p>Confidence: {data['confidence']}</p>
                    <p>Current Price: <b>₹{data['current_price']:,.2f}</b></p>
                </div>
                <div class="section">
                    <h3>Actionable Strategy</h3>
                    <p><b>{data['option_play']}</b></p>
                    <p>Target 1: {data['target_1']:,.0f} | Stop Loss: {data['stop_loss']:,.0f}</p>
                </div>
                <div class="section" style="text-align: center; background: #f9f9f9;">
                    <p>View full logs and download Excel reports here:</p>
                    <a href="{github_link}" class="btn">View on GitHub Actions</a>
                </div>
            </div>
        </body>
        </html>
        """
        return html

def send_email(html_content):
    sender = os.getenv("GMAIL_USER")
    password = os.getenv("GMAIL_APP_PASSWORD")
    recipients = [os.getenv("RECIPIENT_EMAIL_1"), os.getenv("RECIPIENT_EMAIL_2")]
    
    msg = MIMEMultipart()
    msg['Subject'] = f"Nifty 50 Hourly Report - {datetime.now().strftime('%H:%M')}"
    msg['From'] = sender
    msg['To'] = ", ".join(filter(None, recipients))
    msg.attach(MIMEText(html_content, 'html'))
    
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender, password)
            server.sendmail(sender, recipients, msg.as_string())
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

if __name__ == "__main__":
    analyzer = NiftyHTMLAnalyzer()
    tech = analyzer.get_technical_data()
    oc_raw = analyzer.fetch_nse_option_chain_silent()
    oc_ana = analyzer.analyze_option_chain_data(oc_raw)
    
    analyzer.generate_analysis_data(tech, oc_ana)
    html_report = analyzer.generate_html_email()
    
    send_email(html_report)
