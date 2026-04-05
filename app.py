import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
from datetime import datetime

# Настройка страницы - теперь название вкладки "actives"
st.set_page_config(page_title="actives", layout="wide")

# Кастомный темный дизайн
st.markdown("""
    <style>
    .main { background-color: #0E1117; color: white; }
    [data-testid="stMetricValue"] { color: #00FFA3 !important; font-size: 2rem; }
    .stButton>button { width: 100%; border-radius: 10px; border: 1px solid #00FFA3; background: none; color: white; }
    .stDataFrame { border: 1px solid #30363D; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# Функция получения цен с Мосбиржи
def get_moex_price(ticker):
    try:
        url = f"https://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities/{ticker}.json?iss.meta=off&iss.only=marketdata&marketdata.columns=LAST"
        r = requests.get(url, timeout=5).json()
        price = r['marketdata']['data'][0][0]
        if price: return price
        
        url_bond = f"https://iss.moex.com/iss/engines/stock/markets/bonds/boards/TQCB/securities/{ticker}.json?iss.meta=off&iss.only=marketdata&marketdata.columns=LAST"
        r_bond = requests.get(url_bond, timeout=5).json()
        return r_bond['marketdata']['data'][0][0]
    except:
        return None

# --- ЗАГОЛОВОК ---
st.title("📈 actives | Terminal")
st.sidebar.header("Настройки")
user_mode = st.sidebar.toggle("Active Mode", value=True)

# --- ХРАНИЛИЩЕ ДАННЫХ ---
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = [
        {"ticker": "YDEX", "amount": 5},
        {"ticker": "SBER", "amount": 100}
    ]

# --- ИНТЕРФЕЙС ДОБАВЛЕНИЯ ---
with st.expander("➕ Добавить актив"):
    new_ticker = st.text_input("Тикер (напр. YDEX, LKOH)").upper()
    new_amount = st.number_input("Количество", min_value=0.1, step=1.0)
    if st.button("Добавить в actives"):
        st.session_state.portfolio.append({"ticker": new_ticker, "amount": new_amount})
        st.rerun()

# --- РАСЧЕТЫ ---
data = []
total_balance = 0

for item in st.session_state.portfolio:
    price = get_moex_price(item['ticker'])
    if price is None: price = 0
    value = price * item['amount']
    total_balance += value
    data.append({
        "Тикер": item['ticker'],
        "Цена (₽)": price,
        "Кол-во": item['amount'],
        "Всего (₽)": round(value, 2)
    })

df = pd.DataFrame(data)

# --- ВИЗУАЛ ---
col1, col2 = st.columns([1, 2])

with col1:
    st.metric("Total Balance", f"{total_sum if 'total_sum' in locals() else total_balance:,.2f} ₽")
    if not df.empty and total_balance > 0:
        fig = go.Figure(data=[go.Pie(labels=df['Тикер'], values=df['Всего (₽)'], hole=.6, 
                                     marker=dict(colors=['#00FFA3', '#007BFF', '#FF0055', '#FFCC00']))])
        fig.update_layout(showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                          margin=dict(t=0, b=0, l=0, r=0), font=dict(color="white"))
        st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Portfolio Structure")
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    if user_mode:
        st.info("🔥 Active Mode: Фокус на IT и волатильность.")
    else:
        st.success("🛡️ Passive Mode: Фокус на облигации и дивиденды.")

st.caption(f"actives v1.0 | {datetime.now().strftime('%H:%M:%S')}")
