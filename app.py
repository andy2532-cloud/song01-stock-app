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
    "🇹🇼 台灣股市": ['00673R.TW', '00941.TW','2330.TW', '2454.TW', '0050.TW', '2317.TW', '2303.TW'],
    "🇨🇳 中國股市": ['600519.SS', '000001.SZ', '601318.SS'],
    "🇺🇸 美國股市": ['AAPL', 'NVDA', 'TSLA', 'MSFT', 'GOOGL']
}

def get_stock_info(tickers):
    if not tickers:
        return pd.DataFrame()
    
    df_list = []
    # 強制抓取今天的 1 分鐘級別資料 (這是免費數據中最快的方式)
    # group_by='ticker' 方便我們拆分多檔股票
    try:
        data = yf.download(tickers, period="1d", interval="1m", progress=False, group_by='ticker')
        
        for ticker in tickers:
            try:
                # 取得該股票的最新一筆資料
                if len(tickers) > 1:
                    ticker_data = data[ticker].dropna()
                else:
                    ticker_data = data.dropna()
                
                if not ticker_data.empty:
                    last_row = ticker_data.iloc[-1]
                    current_price = last_row['Close']
                    # 昨收價需要另外抓取以計算漲跌
                    stock_obj = yf.Ticker(ticker)
                    prev_close = stock_obj.info.get('previousClose', current_price)
                    
                    change = current_price - prev_close
                    change_pct = (change / prev_close) * 100
                    
                    df_list.append({
                        "股票代號": ticker,
                        "當前價格": round(float(current_price), 2),
                        "漲跌": round(float(change), 2),
                        "漲跌幅(%)": round(float(change_pct), 2)
                    })
                else:
                    df_list.append({"股票代號": ticker, "當前價格": "讀取中", "漲跌": 0, "漲跌幅(%)": 0})
            except:
                df_list.append({"股票代號": ticker, "當前價格": "錯誤", "漲跌": 0, "漲跌幅(%)": 0})
    except:
        return pd.DataFrame(columns=["股票代號", "當前價格", "漲跌", "漲跌幅(%)"])
    
    return pd.DataFrame(df_list)

# 2. 建立 Excel 分頁
tabs = st.tabs(list(market_data.keys()))

for i, (market_name, tickers) in enumerate(market_data.items()):
    with tabs[i]:
        st.write(f"**{market_name} 即時行情**")
        
        df = get_stock_info(tickers)
        
        if not df.empty:
            def color_change(val):
                try:
                    val = float(val)
                    if val > 0: return 'color: #ff4b4b;' # 紅色
                    elif val < 0: return 'color: #008000;' # 綠色
                except:
                    return ''
                return ''

            st.dataframe(
                df.style.map(color_change, subset=['漲跌', '漲跌幅(%)'])
                .format("{:.2f}", subset=['當前價格', '漲跌', '漲跌幅(%)']), # 這一行控制小數點
                use_container_width=True,
                height=300
            )

# 3. 處理台北時間
taipei_tz = pytz.timezone('Asia/Taipei')
now_taipei = datetime.now(taipei_tz).strftime('%Y-%m-%d %H:%M:%S')

st.caption(f"最後更新時間 (台北): {now_taipei}")
st.caption("註：台股與陸股數據由 Yahoo 提供，通常有 15 分鐘延遲。")

if st.button('🔄 點擊刷新價格'):
    st.rerun()
