import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Set the title and sidebar
st.title('Stock Price App')
st.sidebar.header('User Input')

# Create a sidebar for user input
ticker_symbol = st.sidebar.text_input('Enter Stock Ticker Symbol:', 'AAPL')
start_date = st.sidebar.date_input('Select Start Date:', pd.to_datetime('2003-01-01'))
end_date = st.sidebar.date_input('Select End Date:', pd.to_datetime('2023-01-01'))

# Download stock data using yfinance
@st.cache
def load_data(ticker_symbol, start_date, end_date):
    data = yf.download(ticker_symbol, start=start_date, end=end_date)
    return data

data = load_data(ticker_symbol, start_date, end_date)

# Display the stock data
st.subheader('Stock Data')
st.write(data)

# Calculate moving averages
data['MA9'] = data['Close'].rolling(window=9).mean()
data['MA20'] = data['Close'].rolling(window=20).mean()
data['MA50'] = data['Close'].rolling(window=50).mean()

# Calculate Bollinger Bands
data['Upper'] = data['Close'] + 2 * data['Close'].rolling(window=20).std()
data['Lower'] = data['Close'] - 2 * data['Close'].rolling(window=20).std()

# Calculate RSI without using talib
def calculate_rsi(data, window=14):
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

data['RSI'] = calculate_rsi(data)

# Calculate CCI without using talib
def calculate_cci(data, window=20):
    typical_price = (data['High'] + data['Low'] + data['Close']) / 3
    mean_deviation = typical_price - typical_price.rolling(window=window).mean()
    cci = typical_price / (0.015 * mean_deviation)
    return cci

data['CCI'] = calculate_cci(data)

# Calculate 21-day volatility
data['Volatility'] = data['Close'].rolling(window=21).std()

# Create candlestick chart
fig = go.Figure(data=[go.Candlestick(x=data.index,
                open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close'])])

# Add moving averages to the chart
fig.add_trace(go.Scatter(x=data.index, y=data['MA9'], mode='lines', name='MA9'))
fig.add_trace(go.Scatter(x=data.index, y=data['MA20'], mode='lines', name='MA20'))
fig.add_trace(go.Scatter(x=data.index, y=data['MA50'], mode='lines', name='MA50'))

# Add Bollinger Bands to the chart
fig.add_trace(go.Scatter(x=data.index, y=data['Upper'], line=dict(color='red'), name='Upper Bollinger Band'))
fig.add_trace(go.Scatter(x=data.index, y=data['Lower'], line=dict(color='blue'), name='Lower Bollinger Band'))

# Create RSI chart
rsi_fig = px.line(data, x=data.index, y=data['RSI'], labels={'x':'Date', 'y':'RSI'}, title='Relative Strength Index (RSI)')

# Create CCI chart
cci_fig = px.line(data, x=data.index, y=data['CCI'], labels={'x':'Date', 'y':'CCI'}, title='Commodity Channel Index (CCI)')

# Create volatility chart
volatility_fig = px.line(data, x=data.index, y=data['Volatility'], labels={'x':'Date', 'y':'Volatility'}, title='Volatility (21-day)')

# Display the charts
st.subheader('Candlestick Chart with Moving Averages and Bollinger Bands')
st.plotly_chart(fig, use_container_width=True)

st.subheader('RSI Chart')
st.plotly_chart(rsi_fig, use_container_width=True)

st.subheader('CCI Chart')
st.plotly_chart(cci_fig, use_container_width=True)

st.subheader('Volatility (21-day) Chart')
st.plotly_chart(volatility_fig, use_container_width=True)
