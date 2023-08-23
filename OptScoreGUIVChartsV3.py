import streamlit as st
import pandas as pd
import plotly.express as px
import yfinance as yf
import datetime, math
import wallstreet as ws
import numpy as np
import time, sys
import warnings
warnings.filterwarnings("ignore")
from optionprice import Option

st.set_page_config(page_title="Option Exposure Algorithm",
                   page_icon="https://github.com/YWCo/logo/blob/main/YW_Firma_Mail.png?raw=true",
                   layout="wide",
                    )

hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: black;'>Option Exposure Algorithm</h1>", unsafe_allow_html=True)

def count_working_days(start_date, end_date):
    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
    
    # Calculate the number of working days
    working_days = 0
    current_date = start_date
    while current_date <= end_date:
        if current_date.weekday() < 5:  # 0 to 4 represent Monday to Friday
            working_days += 1
        current_date += datetime.timedelta(days=1)
    
    return working_days









@st.cache_data
def calculate_strike_params_call(_c, symbol, spot, start_dummy, stop_dummy, expiry,strike_params_table_empty,optiontype):
    #cols = ['Strike', 'Volume', 'Open_Interest', 'Implied_Volatility', 'BSM_Price', 'Max_Pain', 'Delta', 'Gamma', 'Vega', 'Theta', 'Rho']
    #strike_params_table = pd.DataFrame(columns=cols)
    strike_params_table=strike_params_table_empty
    n = start_dummy
    for s in c.strikes[start_dummy:stop_dummy]:
            #for each strike
            #1)STRIKE
            dummy_strike_number=c.strikes[n]
            #2)set strike
            c.set_strike(c.strikes[n])
            #2)VOLUME
            #c.volume
            #3)OI
            #c.open_interest
            #4)IV
            #c.implied_volatility
            #5)BSM
            today = datetime.date.today()
            # Format the date as YYYY-MM-DD
            formatted_date_today = today.strftime("%Y-%m-%d")
            # Calculate the date 5 years ago
            #five_years_ago = today - timedelta(days=5*365)  # Approximate for simplicity
            # Format the date as YYYY-MM-DD
            #formatted_date_fiveago = five_years_ago.strftime("%Y-%m-%d")
            # Download the historical stock data
            stock_data = yf.download(symbol, start="2018-01-01", end=formatted_date_today)

            # Calculate the daily returns
            stock_data['Daily_Return'] = stock_data['Adj Close'].pct_change()

            # Calculate the annual volatility
            annual_volatility = stock_data['Daily_Return'].std() * (252 ** 0.5)  # 252 trading days in a year
            call_BSM_price=Option(european=False,
                    kind='call',
                    s0=spot,
                    k=c.strikes[n],
                    t= count_working_days(datetime.date.today().strftime("%Y-%m-%d"), expiry),
                    sigma=annual_volatility,
                    r=0.05,
                    dv=0).getPrice()

            bsm_on_strike=round(call_BSM_price,2)
            dummy_strike_par=[optiontype,dummy_strike_number,c.volume,c.open_interest,c.implied_volatility(),bsm_on_strike,c.delta(),c.gamma(),c.vega(),c.theta(),c.rho()]
            this_strike_params=pd.DataFrame([dummy_strike_par],columns=cols)
            strike_params_table=pd.concat([strike_params_table,this_strike_params])
            n+=1
    strike_params_table.reset_index(drop=True, inplace=True)
    
    return strike_params_table

@st.cache_data
def calculate_strike_params_put(_p, symbol, spot, start_dummy, stop_dummy, expiry,strike_params_table_empty,optiontype):
    #cols = ['Strike', 'Volume', 'Open_Interest', 'Implied_Volatility', 'BSM_Price', 'Max_Pain', 'Delta', 'Gamma', 'Vega', 'Theta', 'Rho']
    #strike_params_table = pd.DataFrame(columns=cols)
    strike_params_table=strike_params_table_empty
    n = start_dummy
    for s in p.strikes[start_dummy:stop_dummy]:
            #for each strike
            #1)STRIKE
            dummy_strike_number=p.strikes[n]
            #2)set strike
            p.set_strike(p.strikes[n])
            #2)VOLUME
            #p.volume
            #3)OI
            #p.open_interest
            #4)IV
            #p.implied_volatility
            #5)BSM
            today = datetime.date.today()
            # Format the date as YYYY-MM-DD
            formatted_date_today = today.strftime("%Y-%m-%d")
            # Calculate the date 5 years ago
            #five_years_ago = today - timedelta(days=5*365)  # Approximate for simplicity
            # Format the date as YYYY-MM-DD
            #formatted_date_fiveago = five_years_ago.strftime("%Y-%m-%d")
            # Download the historical stock data
            stock_data = yf.download(symbol, start="2018-01-01", end=formatted_date_today)

            # Calculate the daily returns
            stock_data['Daily_Return'] = stock_data['Adj Close'].pct_change()

            # Calculate the annual volatility
            annual_volatility = stock_data['Daily_Return'].std() * (252 ** 0.5)  # 252 trading days in a year
            call_BSM_price=Option(european=True,
                    kind='put',
                    s0=spot,
                    k=p.strikes[n],
                    t= count_working_days(datetime.date.today().strftime("%Y-%m-%d"), expiry),
                    sigma=annual_volatility,
                    r=0.05,
                    dv=0).getPrice()

            bsm_on_strike=round(call_BSM_price,2)
            dummy_strike_par=[optiontype,dummy_strike_number,p.volume,p.open_interest,p.implied_volatility(),bsm_on_strike,p.delta(),p.gamma(),p.vega(),p.theta(),p.rho()]
            this_strike_params=pd.DataFrame([dummy_strike_par],columns=cols)
            strike_params_table=pd.concat([strike_params_table,this_strike_params])
            n+=1
    strike_params_table.reset_index(drop=True, inplace=True)
    
    return strike_params_table




#Insert Ticker: (Manual) 
symbol = st.text_input("Enter the Symbol:",value="QQQ")
#calculate max pain for calls and puts (irrespective). Inputs: ticker, expiry date. Output: Max Pain
tk = yf.Ticker(symbol)
pr_api=("https://financialmodelingprep.com/api/v3/quote-short/"+symbol+"?apikey=e1f7367c932b9ff3949e05adf400970c")
x=pd.read_json(pr_api)
spot = round(x.iloc[0,1],2)
deno = "USD"
st.write('\nThe spot price is:', spot, deno)
exps = tk.options
exps_known=st.radio("Expiry date known:",options=["Yes","No"],index=0)
if exps_known=="No":
    st.write("\nExpiry dates:",exps)
        #for i in exps:
        #    st.write(f"{i}")
expiry = st.selectbox("Select the Expiry date (YYYY-MM-DD):",options=exps,index=5)

#calculate Greeks for calls or puts. Inherited: ticker, expiry date. Inputs:C/P,strike. Output: Greeks, Vol, OI, BSM
optiontype_sele = st.radio("Select the type of exposure preferred:",options=["Call","Put","Call and Put","Net"],index=2)

cols=["Option Type","Strike","Vol","OI","IV","BSM","Delta","Gamma","Vega","Theta","Rho"]
strike_params_table_empty = pd.DataFrame( columns=list(cols))
exposure_type = st.selectbox("Select exposure parameter to chart: ",cols[4:],index=4)
#if st.button("Run"):
#strike_known=st.radio("Strike price known:",options=["Yes","No"],index=0)
year_option_ticker=expiry[2:4]
month_option_ticker=expiry[-5:-3]
date_option_ticker=expiry[-2:]
#rates_senti=st.radio("Will interest rates probably go up or down during trade (if unsure select 'Up'): ",options=["Up","Down"],index=0)

#if strike not known display strikes and paramters

#rates_senti=st.radio("Will interest rates probably go up or down during your position exposure: ",options=["Up","Down"],index=0)
#cols=["Option Type","Strike","Vol","OI","IV","BSM","Delta","Gamma","Vega","Theta","Rho"]
#strike_params_table_empty = pd.DataFrame( columns=list(cols))
if optiontype_sele == "Call":
    optiontype="Call"
    exp = datetime.datetime.strptime(expiry, "%Y-%m-%d").date()
    d, m, y = exp.day, exp.month, exp.year
    
    c = ws.Call(symbol, d, m, y)
    #st.write("strikes (USD):", c.strikes)
    n=0
    #start_dummy=int(len(c.strikes)/2-10)
    #stop_dummy=int(len(c.strikes)/2+10)
    start_dummy=int(len(c.strikes)*0.3)
    stop_dummy=int(len(c.strikes)*0.7)
    n=start_dummy
    
    dfr_call=calculate_strike_params_call(c, symbol, spot, start_dummy, stop_dummy, expiry,strike_params_table_empty,optiontype)
        

    #exposure_type = st.selectbox("Select exposure parameter to chart: ",cols[2:],index=4)
    #c.set_strike(strike)
    #st.write("expiry (YYYY-MM-DD):", expiry)
    #st.write("strike price (USD):",strike)
    #full_ticker=symbol+year_option_ticker+month_option_ticker+date_option_ticker+"C"+"00"+str(strike)+"000"
    #st.write("OCC Option ticker:",full_ticker)

    #st.write("Option BSM price (USD):",round(call_BSM_price,2)) #c.price)
    #api_call=("https://api.polygon.io/v2/last/trade/O:"+full_ticker+"?apiKey=gZ8y5mYiZQ07XxeIemZbSBpeaErIwTyl")
    #api_live_data=pd.read_json(api_call)
    #live_price=api_live_data.loc["p","results"]
    #st.write("Option live price (USD):", live_price)

    
    barchart=px.bar(dfr_call,x="Strike",y=exposure_type,width=1350,range_x=[c.strikes[int(len(c.strikes)*0.2)],c.strikes[int(len(c.strikes)*0.8)]],title=exposure_type+" "+"Exposure"+" "+"Calls")
    barchart.update_traces(marker_color = 'green').update_layout(xaxis=dict(showgrid=False),title_x=0.5,
              yaxis=dict(showgrid=False))
    barchart.add_vline(x=spot,line_width=2, line_dash="dash",annotation_text="last price "+str(spot), annotation_position="top")

    st.plotly_chart(barchart)
    #st.checkbox("Display table with parameters:",value=False)
    if st.checkbox("Display table with parameters:",value=False):
            st.dataframe(dfr_call,use_container_width=True)

   

elif optiontype_sele=="Put":
    optiontype="Put"
    exp = datetime.datetime.strptime(expiry, "%Y-%m-%d").date()
    d, m, y = exp.day, exp.month, exp.year

    p = ws.Put(symbol, d, m, y)
    #st.write("strikes (USD):", c.strikes)
    n=0
    start_dummy=int(len(p.strikes)*0.3)
    stop_dummy=int(len(p.strikes)*0.7)
    n=start_dummy
    
    dfr_put=calculate_strike_params_put(p, symbol, spot, start_dummy, stop_dummy, expiry,strike_params_table_empty,optiontype)

    barchart=px.bar(dfr_put,x="Strike",y=exposure_type,width=1350,range_x=[p.strikes[int(len(p.strikes)*0.2)],p.strikes[int(len(p.strikes)*0.8)]],title=exposure_type+" "+"Exposure"+" "+"Puts")
    barchart.update_traces(marker_color = 'red').update_layout(xaxis=dict(showgrid=False),title_x=0.5,
              yaxis=dict(showgrid=False))
    barchart.add_vline(x=spot,line_width=2, line_dash="dash",annotation_text="last price "+str(spot), annotation_position="top")

    st.plotly_chart(barchart)
    #st.checkbox("Display table with parameters:",value=False)
    if st.checkbox("Display table with parameters:",value=False):
            st.dataframe(dfr_put,use_container_width=True)

   
else: 
    #if optiontype_sele=="Call and Put":
    exp = datetime.datetime.strptime(expiry, "%Y-%m-%d").date()
    d, m, y = exp.day, exp.month, exp.year
    optiontype="Call"
    c = ws.Call(symbol, d, m, y)
    #st.write("strikes (USD):", c.strikes)
    n=0
    #start_dummy=int(len(c.strikes)/2-10)
    #stop_dummy=int(len(c.strikes)/2+10)
    start_dummy=int(len(c.strikes)*0.3)
    stop_dummy=int(len(c.strikes)*0.7)
    n=start_dummy
    
    dfr_call=calculate_strike_params_call(c, symbol, spot, start_dummy, stop_dummy, expiry,strike_params_table_empty,optiontype)
    optiontype="Put"
    p = ws.Put(symbol, d, m, y)

    dfr_put=calculate_strike_params_put(p, symbol, spot, start_dummy, stop_dummy, expiry,strike_params_table_empty,optiontype)
    dfr_call_put=pd.concat([dfr_call,dfr_put],ignore_index=True)
    dfr_call_put["Vol"]=np.where(dfr_call_put["Option Type"]=="Put",dfr_call_put["Vol"]*-1,dfr_call_put["Vol"])
    dfr_call_put["OI"]=np.where(dfr_call_put["Option Type"]=="Put",dfr_call_put["OI"]*-1,dfr_call_put["OI"])
    dfr_call_put["IV"]=np.where(dfr_call_put["Option Type"]=="Put",dfr_call_put["IV"]*-1,dfr_call_put["IV"])
    dfr_call_put["BSM"]=np.where(dfr_call_put["Option Type"]=="Put",dfr_call_put["BSM"]*-1,dfr_call_put["BSM"])
    #dfr_call_put["Delta"]=np.where(dfr_call_put["Option Type"]=="Put",dfr_call_put["Delta"]*-1,dfr_call_put["Delta"])
    dfr_call_put["Gamma"]=np.where(dfr_call_put["Option Type"]=="Put",dfr_call_put["Gamma"]*-1,dfr_call_put["Gamma"])
    dfr_call_put["Vega"]=np.where(dfr_call_put["Option Type"]=="Put",dfr_call_put["Vega"]*-1,dfr_call_put["Vega"])
    dfr_call_put["Theta"]=np.where(dfr_call_put["Option Type"]=="Put",dfr_call_put["Theta"]*-1,dfr_call_put["Theta"])
    #dfr_call_put["Rho"]=np.where(dfr_call_put["Option Type"]=="Put",dfr_call_put["Rho"]*-1,dfr_call_put["Rho"])
    #[dfr_call_put["Option Type"]=="Put",dfr_call_put.loc["Vol","OI","IV","BSM","Delta","Gamma","Vega","Theta","Rho"]*-1]
    if optiontype_sele=="Call and Put":
        dfr_call_put["Color"] = np.where(dfr_call_put["Option Type"]=="Call", 'green', 'red')
        barchart=px.bar(dfr_call_put,x="Strike",y=exposure_type,width=1350,range_x=[p.strikes[int(len(p.strikes)*0.2)],c.strikes[int(len(c.strikes)*0.8)]],title=exposure_type+" "+"Exposure"+" "+"Calls and Puts")
        barchart.update_traces(marker_color = dfr_call_put['Color']).update_layout(xaxis=dict(showgrid=False),title_x=0.5, yaxis=dict(showgrid=False))
        barchart.add_vline(x=spot,line_width=2, line_dash="dash",annotation_text="last price "+str(spot), annotation_position="top")

        st.plotly_chart(barchart)
        if st.checkbox("Display table with parameters:",value=False):
            st.dataframe(dfr_call_put,use_container_width=True)

    
        
    else:
        dfr_net=dfr_call_put.groupby(dfr_call_put["Strike"],as_index=False).aggregate("sum")
        barchart=px.bar(dfr_net,x="Strike",y=exposure_type,width=1350,range_x=[p.strikes[int(len(p.strikes)*0.2)],c.strikes[int(len(c.strikes)*0.8)]],title=exposure_type+" "+"Exposure"+ " "+"Net")
        barchart.update_traces(marker_color = "blue").update_layout(xaxis=dict(showgrid=False),title_x=0.5, yaxis=dict(showgrid=False))
        barchart.add_vline(x=spot,line_width=2, line_dash="dash",annotation_text="last price "+str(spot), annotation_position="top")

        st.plotly_chart(barchart)
        if st.checkbox("Display table with parameters:",value=False):
            st.dataframe(dfr_net,use_container_width=True)
     


col1, col2, col3 = st.columns(3)

with col1:
    st.write("")
with col2:
    st.image("https://github.com/YWCo/logo/blob/main/YellowWolf.jpg?raw=true")
with col3:
    st.write("")
