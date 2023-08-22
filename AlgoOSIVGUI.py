import streamlit as st
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats

hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


st.header("Options IV Ranking Algorithm")
ticker = st.text_input("Enter ticker:",value="QQQ")
stock = yf.Ticker(ticker)
st.write("Available expiry dates are:\n", stock.options)

exp = st.selectbox("Enter expiry date (YYY-MM-DD):",options=stock.options)

option_chain = stock.option_chain(exp)
lastc = option_chain.calls.sort_values(by='lastTradeDate', ascending=False)

mincolc = lastc[["contractSymbol", "lastTradeDate", "strike", "lastPrice", "volume",'openInterest',"impliedVolatility"]]
optiontype=["All","Calls","Puts"]
ct = st.radio("Select contract type to display:",options=optiontype)
nr_contracts=st.number_input("Select quantity of contract to display, starting from most recent:",value=5,step=1)
if ct=="All" or ct=="Calls":
    
    st.write("Latest ",nr_contracts," call options are:\n", mincolc.head(nr_contracts))
    sel_c=mincolc.head(nr_contracts)
    
    st.write("Top Implied Volatilites for calls on this ticker and strike for contracts selected are:\n",
            sel_c[['contractSymbol', 'lastTradeDate', 'strike', 'lastPrice','volume', 'openInterest',"impliedVolatility"]].sort_values(by="impliedVolatility",ascending=False))
    
lastp = option_chain.puts.sort_values(by='lastTradeDate', ascending=False)

mincolp = lastp[["contractSymbol", "lastTradeDate", "strike", "lastPrice", "volume",'openInterest',"impliedVolatility"]]
if ct=="All" or ct=="Puts":
    
    st.write("Latest ",nr_contracts," put options are:\n", mincolp.head(nr_contracts))
    sel_p=mincolp.head(nr_contracts)
    st.write("Top Implied Volatilites for puts on this ticker and strike for contracts selected are:\n",
            sel_p[['contractSymbol', 'lastTradeDate', 'strike', 'lastPrice','volume', 'openInterest',"impliedVolatility"]].sort_values(by="impliedVolatility",ascending=False))

select = st.checkbox("Plot optimal strikes")
print(select)
if select:
    #st.write("Depending on your strategy and based on outputs above, enter implied volatiliy to see +/-1 σ optimal strike prices in %: ")
    iv_input = st.number_input("Enter implied volatiliy percentage [%] to see +/-1 $σ$ optimal strike prices: ",value=15,step=1)
    url1="https://financialmodelingprep.com/api/v3/quote-short/" #AAPL?apikey=e1f7367c932b9ff3949e05adf400970c"
    url2="?apikey=e1f7367c932b9ff3949e05adf400970c"
    url3=url1+ticker+url2
    pr=pd.read_json(url3)
    price=round(pr.iloc[0,1],2)
    
    #price = stock.info["ask"]
    x_axis = np.arange(price - (0.1 * price), price + (0.1 * price), 0.1)
    plt.plot(x_axis, stats.norm.pdf(x_axis, price, iv_input))
    plt.axvline(x=price + iv_input, color='b',
                label='optimal upper strike for short calls:' + str(round(price + iv_input, 2)))
    plt.axvline(x=price - iv_input, color='r',
                label='optimal lower strike for short puts:' + str(round(price - iv_input, 2)))
    plt.legend(loc='upper left', fontsize="7")
    extraticks = [price - iv_input, price + iv_input]
    st.pyplot(plt)

st.image("https://github.com/YWCo/logo/blob/main/YellowWolf.jpg?raw=true")
