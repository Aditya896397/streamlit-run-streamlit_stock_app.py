import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objs as go
from datetime import date, timedelta

st.set_page_config(layout="wide", page_title="Stock Visualizer")

st.title("Stock Price Visualizer")

# Sidebar controls
ticker = st.sidebar.text_input("Ticker", value="AAPL").upper()
end_date = st.sidebar.date_input("End date", value=date.today())
start_date = st.sidebar.date_input("Start date", value=end_date - timedelta(days=365))
show_sma = st.sidebar.checkbox("Show SMA (20 & 50)", value=True)
show_volume = st.sidebar.checkbox("Show Volume", value=True)

if st.sidebar.button("Fetch"):
    try:
        data = yf.download(ticker, start=start_date, end=end_date + timedelta(days=1))  # inclusive
        if data.empty:
            st.error("No data. Check ticker or date range.")
        else:
            st.success(f"Fetched {len(data)} rows for {ticker}")
            st.dataframe(data.tail(5))

            # Candlestick
            fig = go.Figure()
            fig.add_trace(go.Candlestick(x=data.index,
                                         open=data['Open'], high=data['High'],
                                         low=data['Low'], close=data['Close'],
                                         name='candlestick'))
            if show_sma:
                fig.add_trace(go.Scatter(x=data.index, y=data['Close'].rolling(20).mean(),
                                         mode='lines', name='SMA20'))
                fig.add_trace(go.Scatter(x=data.index, y=data['Close'].rolling(50).mean(),
                                         mode='lines', name='SMA50'))
            fig.update_layout(xaxis_rangeslider_visible=False, height=600,
                              title=f"{ticker} Price")
            st.plotly_chart(fig, use_container_width=True)

            # Volume bar chart
            if show_volume:
                vol_fig = go.Figure([go.Bar(x=data.index, y=data['Volume'], name='Volume')])
                vol_fig.update_layout(height=200, title='Volume')
                st.plotly_chart(vol_fig, use_container_width=True)

            csv = data.to_csv().encode('utf-8')
            st.download_button("Download CSV", data=csv, file_name=f"{ticker}_history.csv", mime='text/csv')
    except Exception as e:
        st.error(f"Error: {e}")
