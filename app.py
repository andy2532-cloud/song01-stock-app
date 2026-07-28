import streamlit as st
import yfinance as yf
import pandas as pd

# 設定網頁標題與排版
st.set_page_config(page_title="我的全球股票監控", layout="wide")
st.title("📊 全球股市即時監控 (Excel 模式)")

# 1. 定義你想追蹤的股票清單 (你可以隨時叫 AI 幫你改這裡)
stocks_tw = ['2330.TW', '2454.TW', '0050.TW']  # 台灣
stocks_cn = ['600519.SS', '000001.SZ', '601318.SS']  # 中國 (滬深)
stocks_us = ['AAPL', 'NVDA', 'TSLA', 'MSFT']  # 美國

# 定義抓取資料的函式
def get_data(tickers):
    if not tickers: return pd.DataFrame()
    data = yf.download(tickers, period="1d", interval="1m") # 抓取今天最新的數據
    # 整理成乾淨的表格格式
    current_prices = data['Close'].iloc[-1]
    df = pd.DataFrame(current_prices).reset_index()
    df.columns = ['股票代號', '當前價格']
    return df

# 2. 建立像 Excel 的「工作表」分頁
tab1, tab2, tab3 = st.tabs(["🇹🇼 台灣股市", "🇨🇳 中國股市", "🇺🇸 美國股市"])

with tab1:
    st.subheader("台灣市場股票")
    df_tw = get_data(stocks_tw)
    st.dataframe(df_tw, use_container_width=True) # 顯示成 Excel 表格

with tab2:
    st.subheader("中國市場股票")
    df_cn = get_data(stocks_cn)
    st.dataframe(df_cn, use_container_width=True)

with tab3:
    st.subheader("美國市場股票")
    df_us = get_data(stocks_us)
    st.dataframe(df_us, use_container_width=True)

st.write("最後更新時間:", pd.Timestamp.now())
if st.button('手動刷新價格'):
    st.rerun()
