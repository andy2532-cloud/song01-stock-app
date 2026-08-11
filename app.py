import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz

# 設定網頁標題
st.set_page_config(page_title="全球股票監控", layout="wide")

# 1. 調整標題大小
st.markdown("#### 📊 全球股市即時監控 (Excel 模式)")

# 2. 自訂你的股票清單與中文名稱 (在這邊修改代號與名稱)
market_configs = {
    "🇹🇼 台灣股市": {
        '2330.TW': '台積電',
        '00673R.TW': '原油反',
        '00941.TW': '中信半導體',
        '6618.TE': '永虹',
        '2405.TW': '輔信'
    },
    "🇨🇳 中國股市": {
        '600519.SS': '貴州茅台',
        '000001.SZ': '平安銀行',
        '601318.SS': '中國平安'
    },
    "🇺🇸 美國股市": {
        'AAPL': '蘋果',
        'NVDA': '輝達',
        'TSLA': '特斯拉',
        'MSFT': '微軟',
        'GOOGL': 'Google'
    }
}

def get_stock_info(stock_dict):
    if not stock_dict:
        return pd.DataFrame()
    
    tickers = list(stock_dict.keys())
    df_list = []
    
    try:
        # 抓取資料
        data = yf.download(tickers, period="1d", interval="1m", progress=False, group_by='ticker')
        
        for ticker, name in stock_dict.items():
            try:
                if len(tickers) > 1:
                    ticker_data = data[ticker].dropna()
                else:
                    ticker_data = data.dropna()
                
                if not ticker_data.empty:
                    last_row = ticker_data.iloc[-1]
                    current_price = last_row['Close']
                    
                    # 抓取昨收價
                    stock_obj = yf.Ticker(ticker)
                    prev_close = stock_obj.info.get('previousClose', current_price)
                    
                    change = current_price - prev_close
                    change_pct = (change / prev_close) * 100
                    
                    df_list.append({
                        "名稱": name,
                        "股票代號": ticker,
                        "當前價格": float(current_price),
                        "漲跌": float(change),
                        "漲跌幅(%)": float(change_pct)
                    })
                else:
                    df_list.append({"名稱": name, "股票代號": ticker, "當前價格": None, "漲跌": None, "漲跌幅(%)": None})
            except:
                df_list.append({"名稱": name, "股票代號": ticker, "當前價格": None, "漲跌": None, "漲跌幅(%)": None})
    except:
        return pd.DataFrame()
    
    return pd.DataFrame(df_list)

# 3. 建立 Excel 分頁
tabs = st.tabs(list(market_configs.keys()))

for i, (market_name, stock_dict) in enumerate(market_configs.items()):
    with tabs[i]:
        st.write(f"**{market_name} 即時行情**")
        
        df = get_stock_info(stock_dict)
        
        if not df.empty:
            def color_change(val):
                try:
                    if val > 0: return 'color: #ff4b4b;' # 紅
                    elif val < 0: return 'color: #008000;' # 綠
                except: pass
                return ''

            # 顯示表格，並格式化小數點為 2 位
            st.dataframe(
                df.style.map(color_change, subset=['漲跌', '漲跌幅(%)'])
                .format("{:.2f}", subset=['當前價格', '漲跌', '漲跌幅(%)'], na_rep="-"),
                use_container_width=True,
                height=300
            )

# 4. 處理台北時間
taipei_tz = pytz.timezone('Asia/Taipei')
now_taipei = datetime.now(taipei_tz).strftime('%Y-%m-%d %H:%M:%S')

st.caption(f"最後更新時間 (台北): {now_taipei}")
st.caption("註：台股與陸股數據由 Yahoo 提供，延遲約 15 分鐘。")

if st.button('🔄 點擊刷新價格'):
    st.rerun()
