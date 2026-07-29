import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz

# 設定網頁標題
st.set_page_config(page_title="全球股票監控", layout="wide")

# 1. 調整標題大小
st.markdown("#### 📊 全球股市即時監控 (Excel 模式)")

# 自訂你的股票清單
market_data = {
    "🇹🇼 台灣股市": ['00673R.TW', '00941.TW', '2330.TW', '2454.TW', '0050.TW', '2317.TW' ],
    "🇨🇳 中國股市": ['600519.SS', '000001.SZ', '601318.SS'],
    "🇺🇸 美國股市": ['AAPL', 'NVDA', 'TSLA', 'MSFT', 'GOOGL']
}

def get_stock_info(tickers):
    if not tickers:
        return pd.DataFrame()
    
    df_list = []
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            info = stock.fast_info
            current_price = info['last_price']
            prev_close = info['previous_close']
            change = current_price - prev_close
            change_pct = (change / prev_close) * 100
            
            df_list.append({
                "股票代號": ticker,
                "當前價格": current_price,
                "漲跌": change,
                "漲跌幅(%)": change_pct
            })
        except:
            df_list.append({"股票代號": ticker, "當前價格": None, "漲跌": None, "漲跌幅(%)": None})
    
    return pd.DataFrame(df_list)

# 2. 建立 Excel 分頁
tabs = st.tabs(list(market_data.keys()))

for i, (market_name, tickers) in enumerate(market_data.items()):
    with tabs[i]:
        st.write(f"**{market_name} 即時行情**")
        
        df = get_stock_info(tickers)
        
        if not df.empty:
            def color_change(val):
                if val is None: return ''
                if val > 0: return 'color: #ff4b4b;' # 紅色
                elif val < 0: return 'color: #008000;' # 綠色
                return ''

            # --- 修正重點：強制設定顯示格式為小數點後兩位 ---
            st.dataframe(
                df.style.map(color_change, subset=['漲跌', '漲跌幅(%)'])
                .format({
                    "當前價格": "{:.2f}",
                    "漲跌": "{:.2f}",
                    "漲跌幅(%)": "{:.2f}"
                }),
                use_container_width=True,
                height=300
            )

# 3. 處理台北時間
taipei_tz = pytz.timezone('Asia/Taipei')
now_taipei = datetime.now(taipei_tz).strftime('%Y-%m-%d %H:%M:%S')

st.caption(f"最後更新時間 (台北): {now_taipei}")

if st.button('🔄 點擊刷新價格'):
    st.rerun()
