
import streamlit as st
import pandas as pd
import yfinance as yf
import datetime, math
import wallstreet as ws
import numpy as np
import time, sys
import opstrat as op
import warnings
warnings.filterwarnings("ignore")
from optionprice import Option

st.set_page_config(page_title="Protective Put Algorithm",
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

st.markdown("<h1 style='text-align: center; color: black;'>Protective Put Algorithm</h1>", unsafe_allow_html=True)
@st.cache_data
def calculate_strike_params_call(_p, symbol, spot, start_dummy, stop_dummy, exp,strike_params_table_empty,max_pain):
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
            put_BSM_price=Option(european=True,
                    kind='put',
                    s0=spot,
                    k=p.strikes[n],
                    t= count_working_days(datetime.date.today().strftime("%Y-%m-%d"), str(exp)),
                    sigma=annual_volatility,
                    r=0.05,
                    dv=0).getPrice()

            bsm_on_strike=round(put_BSM_price,2)
            dummy_strike_par=[dummy_strike_number,p.volume,p.open_interest,p.implied_volatility(),bsm_on_strike,max_pain,p.delta(),p.gamma(),p.vega(),p.theta(),p.rho()]
            this_strike_params=pd.DataFrame([dummy_strike_par],columns=cols)
            strike_params_table=pd.concat([strike_params_table,this_strike_params])
            n+=1
    strike_params_table.reset_index(drop=True, inplace=True)
    
    return strike_params_table


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

def options_chain(tk, expiry):
    options = pd.DataFrame()
    opt = tk.option_chain(expiry.strip())
    opt = pd.concat([opt.calls, opt.puts], ignore_index=True)
    opt['expirationDate'] = expiry
    options = pd.concat([options, opt], ignore_index=True)
    options['expirationDate'] = pd.to_datetime(options['expirationDate']) + datetime.timedelta(days=1)
    options['dte'] = (options['expirationDate'] - datetime.datetime.today()).dt.days / 365
    options['CALL'] = options['contractSymbol'].str[4:].apply(lambda x: "C" in x)
    options[['bid', 'ask', 'strike']] = options[['bid', 'ask', 'strike']].apply(pd.to_numeric)
    options = options.drop(columns=['contractSize', 'currency', 'change', 'percentChange', 'lastTradeDate', 'lastPrice', 'contractSymbol', 'bid', 'ask', 'impliedVolatility', 'inTheMoney', 'dte'])
    return options
def total_loss_on_strike(chain, expiry_price):
    callChain = chain.loc[chain['CALL'] == True]
    callChain = callChain.dropna()
    in_money_calls = callChain[callChain['strike'] < expiry_price][["openInterest", "strike"]]
    in_money_calls["CLoss"] = (expiry_price - in_money_calls['strike']) * in_money_calls["openInterest"]
    putChain = chain.loc[chain['CALL'] == False]
    putChain = putChain.dropna()
    in_money_puts = putChain[putChain['strike'] > expiry_price][["openInterest", "strike"]]
    in_money_puts["PLoss"] = (in_money_puts['strike'] - expiry_price) * in_money_puts["openInterest"]
    total_loss = in_money_calls["CLoss"].sum() + in_money_puts["PLoss"].sum()
    return total_loss


def call_loss_on_strike(chain, expiry_price):
    callChain = chain.loc[chain['CALL'] == True]
    callChain = callChain.dropna()
    in_money_calls = callChain[callChain['strike'] < expiry_price][["openInterest", "strike"]]
    in_money_calls["CLoss"] = (expiry_price - in_money_calls['strike']) * in_money_calls["openInterest"]
    call_loss = in_money_calls["CLoss"].sum()
    return call_loss


def put_loss_on_strike(chain, expiry_price):
    putChain = chain.loc[chain['CALL'] == False]
    putChain = putChain.dropna()
    in_money_puts = putChain[putChain['strike'] > expiry_price][["openInterest", "strike"]]
    in_money_puts["PLoss"] = (in_money_puts['strike'] - expiry_price) * in_money_puts["openInterest"]
    put_loss = in_money_puts["PLoss"].sum()
    return put_loss
purpose=["1-Buy to Open protective Puts",
"2-Check position"]
#"3-Model new or existing position"]
#"4-Speculative trade"]

expiration_types = [
    "1-Specific date",
    "2-Before a specific date",
    "3-After a specific date",
    "4-Between two dates"
]


strike_types = [
"1-ITM (In The Money)",
"2-ATM (At The Money)",
"3-OTM (Out of The Money)",
"4-Specific Strike",
"5-Strike Higher Than",
"6-Strike Lower Than"
]

st.set_option('deprecation.showPyplotGlobalUse', False)
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
# Todays date and extract day, month, and year as integers
today = datetime.date.today()
day = today.day
month = today.month+1
year = today.year

import math
atm_put=ws.Put(symbol, day, month, year, strike=spot)
atm_put_iv_annual=round(atm_put.implied_volatility()*100,2)
atm_put_iv=atm_put.implied_volatility()*math.sqrt(30)/math.sqrt(365)
st.write("The expected move based on the IV is a low price of",round(spot*(1-atm_put_iv),2),"and high price of",round(spot*(1+atm_put_iv),2),"over the next 30 days.")

#st.info("https://images.contentstack.io/v3/assets/blt40263f25ec36953f/blt8069825dc4234378/638783b9ed757210a08975f3/Implied_volatility_example-nl.png?format=pjpg&auto=webp&quality=50&width=1000&disable=upscale")

st.divider()
st.subheader("Select strategy")
purpose_select=st.radio("Select Purpose",options=purpose,label_visibility="hidden")

cols=["Strike","Vol","OI","IV","BSM","MP","Delta","Gamma","Vega","Theta","Rho"]
strike_params_table_empty = pd.DataFrame( columns=list(cols))
st.divider()
st.subheader("Expiration inputs")
contract_expirations=st.selectbox("Filter by expiration timeframes:",options=expiration_types,index=0)
if contract_expirations==expiration_types[0]:
    exp=st.selectbox("Select expiration date",options=exps,index=3)
#before specific date
elif contract_expirations==expiration_types[1]:
    today_date = datetime.date.today()
    
    one_month_in_future = today_date + datetime.timedelta(days=30)
    future_date=st.date_input("Select furthest date",value=one_month_in_future)
    
    #future_date=datetime(future_date.year, future_date.month,future_date.day)
    #future_date = datetime.datetime.strptime(future_date, '%Y-%m-%d')
    # Filter dates greater than the future date
    dates_smaller_than_future = [date for date in exps if date < str(future_date)]
    exp=st.selectbox("Select expriy",options=dates_smaller_than_future,index=len(dates_smaller_than_future)-1)
#after specific date
elif contract_expirations==expiration_types[2]:
    today_date = datetime.date.today()
    three_months_in_future = today_date + datetime.timedelta(weeks=12)
    future_date=st.date_input("Select closest date",value=three_months_in_future)
    
    #future_date = datetime.datetime.strptime(str(future_date), '%Y-%m-%d')
    # Filter dates greater than the future date
    dates_greater_than_future = [date for date in exps if date > str(future_date)]
    exp=st.selectbox("Select expriy",options=dates_greater_than_future,index=0)
else:
# Convert the range of dates to compare against to datetime objects
    start_date=st.date_input("Select expirations range start")
    end_date=st.date_input("Select expirations range end")
    
    # Filter dates between start_date and end_date
    dates_between_range = [date for date in exps if str(start_date) <= date <= str(end_date)]
    exp=st.selectbox("Select expriy",options=dates_between_range,index=0)


#st.write(type(exp))
exp_dtime = datetime.datetime.strptime(exp, "%Y-%m-%d")
d, m, y = exp_dtime.day, exp_dtime.month, exp_dtime.year
p = ws.Put(symbol, d, m, y)
#st.write(type(c.strike))

chain = options_chain(tk, str(exp))
strikes = chain.get(['strike']).values.tolist()
losses = [total_loss_on_strike(chain, strike[0]) for strike in strikes]
closses = [call_loss_on_strike(chain, strike[0]) for strike in strikes]
plosses = [put_loss_on_strike(chain, strike[0]) for strike in strikes]
flat_strikes = [item for sublist in strikes for item in sublist]
point = losses.index(min(losses))
max_pain = flat_strikes[point]





if st.button("Get parameters table for each strike price"):
    start_dummy=int(len(p.strikes)/2-5)
    stop_dummy=int(len(p.strikes)/2+5)
    n=start_dummy
    dfr_put=calculate_strike_params_call(p, symbol, spot, start_dummy, stop_dummy, str(exp),strike_params_table_empty,max_pain)
    st.dataframe(dfr_put)


    

st.divider()
st.subheader("Strike inputs")
contract_params=st.selectbox("Filter strikes by Moneyness criteria:",options=strike_types,index=2)
#ITM
if contract_params==strike_types[0]:
    itm_values = [value for value in p.strikes if value > spot]
    strike = st.selectbox("Select strike (USD): ",options=itm_values,index=int(len(itm_values)/2))
#ATM
elif contract_params==strike_types[1]:
    #greater_values = [value for value in c.strikes if value < spot]
    arr = np.asarray(p.strikes)
    i = (np.abs(arr - spot)).argmin()
    st.write("Closest strike to ATM is:",p.strikes[i])
    strike=p.strikes[i]
    #strike = st.selectbox("Enter strike (USD): ",options=greater_values,index=int(len(c.strikes)*0.5))
#OTM
elif contract_params==strike_types[2]:
    otm_values = [value for value in p.strikes if value < spot]
    strike = st.selectbox("Select strike (USD): ",options=otm_values,index=int(len((otm_values))/2))
#Spec Strike
elif contract_params==strike_types[3]:
    strike= st.selectbox("Select strike (USD): ",options=list(p.strikes),index=int(len(p.strikes)*0.5))
#Strike higher than
elif contract_params==strike_types[4]:
    barrier_strike=st.number_input("Enter minimum strike value: ",min_value=int(p.strikes[0]))
    greater_than = [value for value in p.strikes if value > barrier_strike]
    strike = st.selectbox("Select strike (USD): ",options=greater_than)
#Strike lower than
elif contract_params==strike_types[5]:
    barrier_strike=st.number_input("Enter maximum strike value: ")
    greater_values = [value for value in p.strikes if value < barrier_strike]
    strike = st.selectbox("Select strike (USD): ",options=greater_values,index=int(len(p.strikes)*0.5))


st.divider()
if purpose_select==purpose[0]:
    build_pos=st.radio("Build long put position for held underlying asset combination?",options=["Yes","no"],index=0) 
    if build_pos=="Yes":
        nr_shares=st.number_input("Enter amount of equity held in quantity (Shares)/units (ETF):",min_value=0,step=5,value=100)
        #nr_contracts_buy=int(nr_shares/100)
        st.sidebar.subheader("Protective Put builder")
        st.sidebar.divider()
        st.sidebar.write("Spot price:",spot,"USD")
        st.sidebar.write("Quantity (Shares)/Units (ETF) held:",nr_shares)
        st.sidebar.write("Market value",nr_shares*spot,"USD")
        st.sidebar.divider()
        st.sidebar.write("Expiry selected:",exp)
        st.sidebar.write("Strike selected:",strike)
        year_option_ticker=str(exp)[2:4]
        month_option_ticker=str(exp)[-5:-3]
        date_option_ticker=str(exp)[-2:]
        full_ticker=symbol+year_option_ticker+month_option_ticker+date_option_ticker+"P"+"00"+str(strike)+"000"
        st.sidebar.write("OCC Option ticker:",full_ticker)
        api_call=("https://api.polygon.io/v2/last/trade/O:"+full_ticker+"?apiKey=gZ8y5mYiZQ07XxeIemZbSBpeaErIwTyl")
        api_live_data=pd.read_json(api_call)
        live_price=api_live_data.loc["p","results"]
        st.sidebar.write("Option last price (USD):", round(live_price,2))
        
        #rates_senti=st.radio("Will interest rates probably go up or down during trade (if unsure select 'Up'): ",options=["Up","Down"],index=0)
        rates_senti="Up"
        
        
        
        if st.button('Score'):
            p.set_strike(strike)
            put_vol=p.volume
            put_oi=p.open_interest
            put_iv=p.implied_volatility()
            put_delta=int(p.delta()*100)
            put_gamma=p.gamma()
            put_theta=p.theta()
            put_vega=p.vega()
            put_rho=p.rho()
            #st.write("Option Volume:", put_vol)
            #st.write("Option OI:", put_oi)
            #st.write("IV:", round(put_iv, 4))
            #st.write("Delta:", round(put_delta, 4))
            #st.write("Gamma:", round(put_gamma, 4))
            #st.write("Theta:", np.round(put_theta, 4))
            #st.write("Vega:", round(put_vega, 4))
            #st.write("Rho:", round(put_rho, 4))
            if put_oi==0:
                st.write("No contract OI found, assigned value of 1. Please re-run during market hours.")
                put_oi=1

            progress_text = "Running algorithm. Please wait."
            my_bar = st.progress(0, text=progress_text)

            for percent_complete in range(100):
                time.sleep(0.05)
                my_bar.progress(percent_complete + 1, text=progress_text+" "+str(percent_complete)+"%")
            my_bar.empty()
            #scoring volume puts:
            tk = yf.Ticker(symbol)
            option_chain=tk.option_chain(str(exp))
            puts_df = option_chain.puts
            puts_df=puts_df[[ "contractSymbol","strike","volume"]]
            puts_df.sort_values(by="volume",ascending=False,inplace=True)
            #top10
            puts_df_top10volume=puts_df.head(10)
            #st.dataframe(puts_df_top10volume)
            scoring_bands = [(puts_df_top10volume.volume.iloc[-1]), (puts_df_top10volume.volume.iloc[-2]), 
                                (puts_df_top10volume.volume.iloc[-3]), (puts_df_top10volume.volume.iloc[-4]), 
                                (puts_df_top10volume.volume.iloc[-5]), (puts_df_top10volume.volume.iloc[-6]),
                                (puts_df_top10volume.volume.iloc[-7]), (puts_df_top10volume.volume.iloc[-8]),
                                (puts_df_top10volume.volume.iloc[-9]), (puts_df_top10volume.volume.iloc[0])
                                ]
            scores = [-10,-8,-6,-4,-2,2,4,6,8,10]
            #initialize variable
            vol_score_put = None
            # Value to compare
            value_to_compare = put_vol
            for i, value in enumerate(scoring_bands):
                if value == value_to_compare:
                    vol_score_put = scores[i]
                    break

            # If no range matched, assign a default score
            if vol_score_put is None:
                vol_score_put = -10

            #st.write("Score:", vol_score_put)

            
            
            #2-score OI:
            scoring_bands_oi = [(0.1,0.2),
                                (0.2,0.3),
                                (0.3,0.4),
                                (0.4,0.5),
                                (0.5,0.6),
                                (0.6,0.7),
                                (0.7,0.8),
                                (0.8,0.9),
                                (0.9,1)
                                ]
            scores_oi = [-8,-6,-4,-2,0,2,4,6,8]
            # Value to compare
            value_to_compare = put_vol/put_oi
            # Initialize the score variable
            oi_score_put = None
            array_score_bands=np.array(scoring_bands_oi)
            # Compare the value with the scoring bands
            if value_to_compare < scoring_bands_oi[0][0]:
                oi_score_put = 10
            elif value_to_compare > scoring_bands_oi[-1][-1]:
                oi_score_put = -10
            else:
                for i, (lower,upper) in enumerate(array_score_bands):
                    if lower <= value_to_compare < upper:
                        oi_score_put = scores[i]
                        break

            

            #st.write("oi score:", oi_score_put)




            #3-scoring IV:
            iv_score_put=0
            if put_iv>0.3:
                iv_score_put=10
            else: iv_score_put=-10
            #st.write("iv score:", iv_score_put)
            

            #4-score BSM:
            # Define the scoring bands and corresponding scores
            scoring_bands_bsm = [(-0.05,-0.04),
                            (-0.04,-0.03),
                            (-0.03,-0.02),
                            (-0.02,-0.01),
                            (-0.01,0.01),
                            (0.01,0.02),
                            (0.02,0.03),
                            (0.03,0.04),
                            (0.04,0.05)]
            scores = [-8,-6,-4,-2,0,2,4,6,8]
            today = datetime.date.today()
            # Format the date as YYYY-MM-DD
            formatted_date_today = today.strftime("%Y-%m-%d")
            # Calculate the date 5 years ago
            # Download the historical stock data
            stock_data = yf.download(symbol, start="2018-01-01", end=formatted_date_today)

            # Calculate the daily returns
            stock_data['Daily_Return'] = stock_data['Adj Close'].pct_change()

            # Calculate the annual volatility
            annual_volatility = stock_data['Daily_Return'].std() * (252 ** 0.5)  # 252 trading days in a year
            put_BSM_price=Option(european=True,
                    kind='put',
                    s0=spot,
                    k=strike,
                    t= count_working_days(datetime.date.today().strftime("%Y-%m-%d"), str(exp)),
                    sigma=annual_volatility,
                    r=0.05,
                    dv=0).getPrice()
            # Value to compare
            value_to_compare = 1-(live_price/round(put_BSM_price,2))
            
            # Initialize the score variable
            bsm_score_put = None
            array_score_bands=np.array(scoring_bands_bsm)
            # Compare the value with the scoring bands
            if value_to_compare < scoring_bands_bsm[0][0]:
                bsm_score_put = -10
            elif value_to_compare > scoring_bands_bsm[-1][-1]:
                bsm_score_put = 10
            else:
                for i, (lower,upper) in enumerate(array_score_bands):
                    if lower <= value_to_compare < upper:
                        bsm_score_put = scores[i]
                        break
            #st.write("bsm score:", bsm_score_put)





            #4-score Max Pain for puts:
            scoring_bands_mp = [(-0.05,-0.04),
                                (-0.04,-0.03),
                                (-0.03,-0.02),
                                (-0.02,-0.01),
                                (-0.01,0.01),
                                (0.01,0.02),
                                (0.02,0.03),
                                (0.03,0.04),
                                (0.04,0.05)]
            scores = [-8,-6,-4,-2,0,2,4,6,8]

            # Value to compare
            value_to_compare = 1-(max_pain/spot)
            
            # Initialize the score variable
            mp_score_put = None
            array_score_bands=np.array(scoring_bands_mp)
            # Compare the value with the scoring bands
            if value_to_compare < scoring_bands_mp[0][0]:
                mp_score_put = -10
            elif value_to_compare > scoring_bands_mp[-1][-1]:
                mp_score_put = 10
            else:
                for i, (lower,upper) in enumerate(array_score_bands):
                    if lower <= value_to_compare < upper:
                        mp_score_put = scores[i]
                        break
            #st.write("mp score:", mp_score_put)           

            #Score Delta puts:
            scoring_bands_delta = [(-100, -90),
                        (-90, -80),
                        (-80, -70),
                        (-70, -60),
                        (-60, -50),
                        (-50, -40),
                        (-40, -30),
                        (-30, -20),
                        (-20, -10),
                        (-10, 0)
                        ]
            scores = [10,8,6,4,2,0,-2,-4,-6,-8]     
            value_to_compare = put_delta
            # Initialize the score variable
            delta_score_put = None
            array_score_bands=np.array(scoring_bands_delta)
            # Compare the value with the scoring bands
            if value_to_compare==0:
                delta_score_put=-10
            elif value_to_compare==-100:
                delta_score_put=10
            
            else:
                for i, (lower, upper) in enumerate(array_score_bands):
                    if lower <= value_to_compare < upper:
                        delta_score_put = scores[i]
                        break
            
            #st.write("delta score:", delta_score_put) 

            #Score Gamma puts:
            scoring_bands_gamma = [(0,0.005),
                                (0.005,0.010),
                                (0.010,0.015),
                                (0.015,0.020),
                                (0.020,0.025),
                                (0.025,0.030),
                                (0.030,0.035),
                                (0.035,0.040)
                                ]
            scores = [-10,-7.5,-5,-2.5,0,2.5,5,7.5]

            # Value to compare
            value_to_compare = put_gamma
            #st.write(value_to_compare)
            # Initialize the score variable
            gamma_score_put = None
            array_score_bands=np.array(scoring_bands_gamma)
            # Compare the value with the scoring bands
            if value_to_compare > scoring_bands_gamma[-1][-1]:
                gamma_score_put = 10
            else:
                for i, (lower,upper) in enumerate(array_score_bands):
                    if lower <= value_to_compare < upper:
                        gamma_score_put = scores[i]
                        break
            #st.write("gamma score:", gamma_score_put)  

            #Score Vega puts:
            scoring_bands_vega = [(0,0.05),
                                (0.05,0.1),
                                (0.1,0.15),
                                (0.15,0.2),
                                (0.2,0.25),
                                (0.3,0.35),
                                (0.35,0.40),
                                (0.45,0.5),
                                ]
            scores = [-10,-8,-6,-4,-2,0,2,4,6,8]     
            value_to_compare = put_vega
            # Initialize the score variable
            vega_score_put = None
            array_score_bands=np.array(scoring_bands_vega)
            # Compare the value with the scoring bands
            if value_to_compare > scoring_bands_vega[-1][-1]:
                gamma_score_put = 10
            else:
                for i, (lower,upper) in enumerate(array_score_bands):
                    if lower <= value_to_compare < upper:
                        vega_score_put = scores[i]
                        break
            #st.write("vega score:", vega_score_put) 

            #Score Theta puts:
            scoring_bands_theta = [(-0.04,-0.035),
                                (-0.035,-0.030),
                                (-0.030,-0.025),
                                (-0.025,-0.020),
                                (-0.020,-0.015),
                                (-0.015,-0.010),
                                (-0.010,-0.005),
                                (-0.005,0)
                                
                                ]
            scores = [-7.5,-5,-2.5,0,2.5,5,7.5,10]
            value_to_compare = -put_theta
            # Initialize the score variable
            theta_score_put = None
            array_score_bands=np.array(scoring_bands_theta)
            # Compare the value with the scoring bands
            if value_to_compare < scoring_bands_theta[0][0]:
                theta_score_put = -10
            else:
                for i, (lower,upper) in enumerate(array_score_bands):
                    if lower <= value_to_compare < upper:
                        theta_score_put = scores[i]
                        break
            #st.write("theta score:", theta_score_put) 

            #Score Rho puts:
            if rates_senti=="Up":
                
                scoring_bands_rho = [(-float("inf"),-0.04),
                        (-0.04, -0.03),
                        (-0.03, -0.02),
                        (-0.02, -0.01),
                        (-0.01,0)
                    ]
                scores = [-10,-5,0,5,10]
                value_to_compare = put_rho
                array_score_bands=np.array(scoring_bands_rho)
                # Initialize the score variable
                rho_score_put = None
                for i, (lower,upper) in enumerate(array_score_bands):
                    if lower <= value_to_compare <= upper:
                        rho_score_put = scores[i]
                        break
            else:
        
                scoring_bands_rho = [( -float("inf"),-0.04),
                        (-0.04, -0.03),
                        (-0.03, -0.02),
                        (-0.02, -0.01),
                        (-0.01, 0)
                    ]
                scores = [10,5,0,-5,-10]
                value_to_compare = put_rho
                array_score_bands=np.array(scoring_bands_rho)
                # Initialize the score variable
                rho_score_put = None
                for i, (lower,upper) in enumerate(array_score_bands):
                    if lower <= value_to_compare < upper:
                        rho_score_put = scores[i]
                        break
            #st.write("rho score:", rho_score_put)

            parameters_score_dict={ "Volume":[put_vol,vol_score_put],"OI":[put_oi,oi_score_put],"IV":[round(put_iv, 4),iv_score_put],"BSM":[round(put_BSM_price,2),bsm_score_put],"Max Pain":[max_pain,mp_score_put],"Delta":[round(put_delta,4),delta_score_put],"Gamma":[round(put_gamma, 4),gamma_score_put],"Vega":[round(put_vega, 4),vega_score_put],"Theta":[np.round(-put_theta, 4),theta_score_put],"Rho":[round(put_rho, 4),rho_score_put]}
            df_param_score_weights=pd.DataFrame(parameters_score_dict)
            rows_params=["Data","Score","Weights"]
            weights=[0.1,0.1,0.15,0.1,0.1,0.13,0.09,0.05,0.15,0.03]
            
            df_param_score_weights.loc[len(df_param_score_weights)]=weights
            df_param_score_weights.index=rows_params
            st.dataframe(df_param_score_weights.loc[["Data","Score"]])
            sum_score=df_param_score_weights.loc["Score"].dot(df_param_score_weights.loc["Weights"])
            st.write("Total Score is:",round(sum_score,2))
        if st.radio("Is the last price your entry price?",options=["Yes","No"],index=0) == "No":
            last_price=st.number_input("Enter put contract ask price",min_value=0.00,value=1.00,step=0.05)
        else:
            last_price=live_price
        max_contracts_buy=int(nr_shares/100)
        #if contracts to buy=0 shares<100 then shares remainder=shares
        if max_contracts_buy==0:
            remainder_shares=nr_shares
        else: remainder_shares=round(nr_shares%100,2)
        st.write("Possibility to buy up to",max_contracts_buy,"put contract/s. The quantity of uncovered shares/units after protective puts are bought is",remainder_shares,", and a USD value exposure of ",round(remainder_shares*spot,2))
        nr_contracts_buy=st.number_input("Enter amount of protective contracts to buy",min_value=0,max_value=max_contracts_buy,value=max_contracts_buy,step=1)
        st.write("Premium amount required is",round(nr_contracts_buy*last_price*100,2),"USD.")
        #st.write("Based on the price and paramteres selected it is possible to buy up to : USD",last_price*nr_contracts*100,"in premium.")
        st.sidebar.write("Buy to open quantity of contracts:",nr_contracts_buy)
        st.sidebar.write("Premium invested:",round(last_price*nr_contracts_buy*100,2))

        st.divider()
        st.subheader("P&L potential and targets")
        st.write("Max profit potential is +infinite.")
        perc_profit=st.number_input("What is the % profit target?",min_value=0,step=1,value=10)
        perc_profit=perc_profit/100
        st.write("Max loss potential, including any uncovered positions if applicable, is",round((spot-strike)*nr_shares+nr_contracts_buy*100*last_price+remainder_shares*(spot),2))
        perc_risk=st.number_input("What is the % risk target?",min_value=0,step=1,value=5)
        perc_risk=perc_risk/100

        st.divider()
        st.subheader("Results based on inputs")
        if  nr_contracts_buy==0:
            st.write("No contracts to buy. To see other scenarios change inputs.")
        else:
            st.write("The take profit exit price is: ",round(spot*(1+perc_profit)+last_price,2))
            st.write("The profit amount would be: ",round((spot*(perc_profit)+last_price)*nr_shares-last_price*100*nr_contracts_buy,2),"USD including premium paid.")
            st.write("The stop loss price is: ",round(spot*(1-perc_risk)+last_price,2))
            st.write("The loss amount would be: ",round((spot*(perc_risk)+last_price)*nr_shares-last_price*100*nr_contracts_buy,2),"USD including premium paid.")

        
        if st.button("Plot Protective Put payoff diagram"):
            st.write("Breakeven",round(strike+last_price,2))
            #st.set_option('deprecation.showPyplotGlobalUse', False)
            plot_prot_put=op.single_plotter( 
            op_type='c',
            spot=spot,
            spot_range = 10,#atm_call_iv_annual
            strike=strike ,
            tr_type= 'b',
            op_pr= last_price,
            save= False)
            st.pyplot(plot_prot_put)
            
    else: 
        st.write("Thank you for using the YWC Algorithm.")
if purpose_select==purpose[1]:
   
    nr_shares=st.number_input("Enter amount of equity held in quantity (Shares)/units (ETF):",min_value=0,step=5,value=100)
    #nr_contracts=int(nr_shares/100)
    st.sidebar.subheader("Protective Put position check")
    st.sidebar.divider()
    st.sidebar.write("Spot price:",spot,"USD")
    st.sidebar.write("Quantity (Shares)/Units (ETF) held:",nr_shares)
    st.sidebar.write("Market value",nr_shares*spot,"USD")
    st.sidebar.divider()
    st.sidebar.write("Expiry selected:",exp)
    st.sidebar.write("Strike selected:",strike)
    year_option_ticker=str(exp)[2:4]
    month_option_ticker=str(exp)[-5:-3]
    date_option_ticker=str(exp)[-2:]
    full_ticker=symbol+year_option_ticker+month_option_ticker+date_option_ticker+"P"+"00"+str(strike)+"000"
    st.sidebar.write("OCC Option ticker:",full_ticker)
    api_call=("https://api.polygon.io/v2/last/trade/O:"+full_ticker+"?apiKey=gZ8y5mYiZQ07XxeIemZbSBpeaErIwTyl")
    api_live_data=pd.read_json(api_call)
    live_price=api_live_data.loc["p","results"]
    st.sidebar.write("Option last price (USD):", round(live_price,2))
    
    #rates_senti=st.radio("Will interest rates probably go up or down during trade (if unsure select 'Up'): ",options=["Up","Down"],index=0)
    rates_senti="Up"
    
    
    
    
    if st.button('Score'):
        p.set_strike(strike)
        put_vol=p.volume
        put_oi=p.open_interest
        put_iv=p.implied_volatility()
        put_delta=int(p.delta()*100)
        put_gamma=p.gamma()
        put_theta=p.theta()
        put_vega=p.vega()
        put_rho=p.rho()
        #st.write("Option Volume:", put_vol)
        #st.write("Option OI:", put_oi)
        #st.write("IV:", round(put_iv, 4))
        #st.write("Delta:", round(put_delta, 4))
        #st.write("Gamma:", round(put_gamma, 4))
        #st.write("Theta:", np.round(put_theta, 4))
        #st.write("Vega:", round(put_vega, 4))
        #st.write("Rho:", round(put_rho, 4))
        if put_oi==0:
            st.write("No contract OI found, assigned value of 1. Please re-run during market hours.")
            put_oi=1

        progress_text = "Running algorithm. Please wait."
        my_bar = st.progress(0, text=progress_text)

        for percent_complete in range(100):
            time.sleep(0.05)
            my_bar.progress(percent_complete + 1, text=progress_text+" "+str(percent_complete)+"%")
        my_bar.empty()
        #scoring volume puts:
        tk = yf.Ticker(symbol)
        option_chain=tk.option_chain(str(exp))
        puts_df = option_chain.puts
        puts_df=puts_df[[ "contractSymbol","strike","volume"]]
        puts_df.sort_values(by="volume",ascending=False,inplace=True)
        #top10
        puts_df_top10volume=puts_df.head(10)
        #st.dataframe(puts_df_top10volume)
        scoring_bands = [(puts_df_top10volume.volume.iloc[-1]), (puts_df_top10volume.volume.iloc[-2]), 
                            (puts_df_top10volume.volume.iloc[-3]), (puts_df_top10volume.volume.iloc[-4]), 
                            (puts_df_top10volume.volume.iloc[-5]), (puts_df_top10volume.volume.iloc[-6]),
                            (puts_df_top10volume.volume.iloc[-7]), (puts_df_top10volume.volume.iloc[-8]),
                            (puts_df_top10volume.volume.iloc[-9]), (puts_df_top10volume.volume.iloc[0])
                            ]
        scores = [-10,-8,-6,-4,-2,2,4,6,8,10]
        #initialize variable
        vol_score_put = None
        # Value to compare
        value_to_compare = put_vol
        for i, value in enumerate(scoring_bands):
            if value == value_to_compare:
                vol_score_put = scores[i]
                break

        # If no range matched, assign a default score
        if vol_score_put is None:
            vol_score_put = -10

        #st.write("Score:", vol_score_put)

        
        
        #2-score OI:
        scoring_bands_oi = [(0.1,0.2),
                            (0.2,0.3),
                            (0.3,0.4),
                            (0.4,0.5),
                            (0.5,0.6),
                            (0.6,0.7),
                            (0.7,0.8),
                            (0.8,0.9),
                            (0.9,1)
                            ]
        scores_oi = [-8,-6,-4,-2,0,2,4,6,8]
        # Value to compare
        value_to_compare = put_vol/put_oi
        # Initialize the score variable
        oi_score_put = None
        array_score_bands=np.array(scoring_bands_oi)
        # Compare the value with the scoring bands
        if value_to_compare < scoring_bands_oi[0][0]:
            oi_score_put = 10
        elif value_to_compare > scoring_bands_oi[-1][-1]:
            oi_score_put = -10
        else:
            for i, (lower,upper) in enumerate(array_score_bands):
                if lower <= value_to_compare < upper:
                    oi_score_put = scores[i]
                    break

        

        #st.write("oi score:", oi_score_put)




        #3-scoring IV:
        iv_score_put=0
        if put_iv>0.3:
            iv_score_put=10
        else: iv_score_put=-10
        #st.write("iv score:", iv_score_put)
        

        #4-score BSM:
        # Define the scoring bands and corresponding scores
        scoring_bands_bsm = [(-0.05,-0.04),
                            (-0.04,-0.03),
                            (-0.03,-0.02),
                            (-0.02,-0.01),
                            (-0.01,0.01),
                            (0.01,0.02),
                            (0.02,0.03),
                            (0.03,0.04),
                            (0.04,0.05)]
        scores = [-8,-6,-4,-2,0,2,4,6,8]
        today = datetime.date.today()
        # Format the date as YYYY-MM-DD
        formatted_date_today = today.strftime("%Y-%m-%d")
        # Calculate the date 5 years ago
        # Download the historical stock data
        stock_data = yf.download(symbol, start="2018-01-01", end=formatted_date_today)

        # Calculate the daily returns
        stock_data['Daily_Return'] = stock_data['Adj Close'].pct_change()

        # Calculate the annual volatility
        annual_volatility = stock_data['Daily_Return'].std() * (252 ** 0.5)  # 252 trading days in a year
        put_BSM_price=Option(european=True,
                kind='put',
                s0=spot,
                k=strike,
                t= count_working_days(datetime.date.today().strftime("%Y-%m-%d"), str(exp)),
                sigma=annual_volatility,
                r=0.05,
                dv=0).getPrice()
        # Value to compare
        value_to_compare = 1-(live_price/round(put_BSM_price,2))
        
        # Initialize the score variable
        bsm_score_put = None
        array_score_bands=np.array(scoring_bands_bsm)
        # Compare the value with the scoring bands
        if value_to_compare < scoring_bands_bsm[0][0]:
            bsm_score_put = -10
        elif value_to_compare > scoring_bands_bsm[-1][-1]:
            bsm_score_put = 10
        else:
            for i, (lower,upper) in enumerate(array_score_bands):
                if lower <= value_to_compare < upper:
                    bsm_score_put = scores[i]
                    break
        #st.write("bsm score:", bsm_score_put)





        #4-score Max Pain for puts:
        scoring_bands_mp = [(-0.05,-0.04),
                            (-0.04,-0.03),
                            (-0.03,-0.02),
                            (-0.02,-0.01),
                            (-0.01,0.01),
                            (0.01,0.02),
                            (0.02,0.03),
                            (0.03,0.04),
                            (0.04,0.05)]
        scores = [-8,-6,-4,-2,0,2,4,6,8]

        # Value to compare
        value_to_compare = 1-(max_pain/spot)
        
        # Initialize the score variable
        mp_score_put = None
        array_score_bands=np.array(scoring_bands_mp)
        # Compare the value with the scoring bands
        if value_to_compare < scoring_bands_mp[0][0]:
            mp_score_put = -10
        elif value_to_compare > scoring_bands_mp[-1][-1]:
            mp_score_put = 10
        else:
            for i, (lower,upper) in enumerate(array_score_bands):
                if lower <= value_to_compare < upper:
                    mp_score_put = scores[i]
                    break
        #st.write("mp score:", mp_score_put)           

        #Score Delta puts:
        scoring_bands_delta = [(-100, -90),
                    (-90, -80),
                    (-80, -70),
                    (-70, -60),
                    (-60, -50),
                    (-50, -40),
                    (-40, -30),
                    (-30, -20),
                    (-20, -10),
                    (-10, 0)
                    ]
        scores = [10,8,6,4,2,0,-2,-4,-6,-8]     
        value_to_compare = put_delta
        # Initialize the score variable
        delta_score_put = None
        array_score_bands=np.array(scoring_bands_delta)
        # Compare the value with the scoring bands
        if value_to_compare==0:
            delta_score_put=-10
        elif value_to_compare==-100:
            delta_score_put=10
        
        else:
            for i, (lower, upper) in enumerate(array_score_bands):
                if lower <= value_to_compare < upper:
                    delta_score_put = scores[i]
                    break
        
        #st.write("delta score:", delta_score_put) 

        #Score Gamma puts:
        scoring_bands_gamma = [(0,0.005),
                            (0.005,0.010),
                            (0.010,0.015),
                            (0.015,0.020),
                            (0.020,0.025),
                            (0.025,0.030),
                            (0.030,0.035),
                            (0.035,0.040)
                            ]
        scores = [-10,-7.5,-5,-2.5,0,2.5,5,7.5]

        # Value to compare
        value_to_compare = put_gamma
        #st.write(value_to_compare)
        # Initialize the score variable
        gamma_score_put = None
        array_score_bands=np.array(scoring_bands_gamma)
        # Compare the value with the scoring bands
        if value_to_compare > scoring_bands_gamma[-1][-1]:
            gamma_score_put = 10
        else:
            for i, (lower,upper) in enumerate(array_score_bands):
                if lower <= value_to_compare < upper:
                    gamma_score_put = scores[i]
                    break
        #st.write("gamma score:", gamma_score_put)  

        #Score Vega puts:
        scoring_bands_vega = [(0,0.05),
                            (0.05,0.1),
                            (0.1,0.15),
                            (0.15,0.2),
                            (0.2,0.25),
                            (0.3,0.35),
                            (0.35,0.40),
                            (0.45,0.5),
                            ]
        scores = [-10,-8,-6,-4,-2,0,2,4,6,8]     
        value_to_compare = put_vega
        # Initialize the score variable
        vega_score_put = None
        array_score_bands=np.array(scoring_bands_vega)
        # Compare the value with the scoring bands
        if value_to_compare > scoring_bands_vega[-1][-1]:
            gamma_score_put = 10
        else:
            for i, (lower,upper) in enumerate(array_score_bands):
                if lower <= value_to_compare < upper:
                    vega_score_put = scores[i]
                    break
        #st.write("vega score:", vega_score_put) 

        #Score Theta puts:
        scoring_bands_theta = [(-0.04,-0.035),
                            (-0.035,-0.030),
                            (-0.030,-0.025),
                            (-0.025,-0.020),
                            (-0.020,-0.015),
                            (-0.015,-0.010),
                            (-0.010,-0.005),
                            (-0.005,0)
                            
                            ]
        scores = [-7.5,-5,-2.5,0,2.5,5,7.5,10]
        value_to_compare = -put_theta
        # Initialize the score variable
        theta_score_put = None
        array_score_bands=np.array(scoring_bands_theta)
        # Compare the value with the scoring bands
        if value_to_compare < scoring_bands_theta[0][0]:
            theta_score_put = -10
        else:
            for i, (lower,upper) in enumerate(array_score_bands):
                if lower <= value_to_compare < upper:
                    theta_score_put = scores[i]
                    break
        #st.write("theta score:", theta_score_put) 

        #Score Rho puts:
        if rates_senti=="Up":
            
            scoring_bands_rho = [(-float("inf"),-0.04),
                    (-0.04, -0.03),
                    (-0.03, -0.02),
                    (-0.02, -0.01),
                    (-0.01,0)
                ]
            scores = [-10,-5,0,5,10]
            value_to_compare = put_rho
            array_score_bands=np.array(scoring_bands_rho)
            # Initialize the score variable
            rho_score_put = None
            for i, (lower,upper) in enumerate(array_score_bands):
                if lower <= value_to_compare <= upper:
                    rho_score_put = scores[i]
                    break
        else:
    
            scoring_bands_rho = [( -float("inf"),-0.04),
                    (-0.04, -0.03),
                    (-0.03, -0.02),
                    (-0.02, -0.01),
                    (-0.01, 0)
                ]
            scores = [10,5,0,-5,-10]
            value_to_compare = put_rho
            array_score_bands=np.array(scoring_bands_rho)
            # Initialize the score variable
            rho_score_put = None
            for i, (lower,upper) in enumerate(array_score_bands):
                if lower <= value_to_compare < upper:
                    rho_score_put = scores[i]
                    break
        #st.write("rho score:", rho_score_put)

        parameters_score_dict={ "Volume":[put_vol,vol_score_put],"OI":[put_oi,oi_score_put],"IV":[round(put_iv, 4),iv_score_put],"BSM":[round(put_BSM_price,2),bsm_score_put],"Max Pain":[max_pain,mp_score_put],"Delta":[round(put_delta,4),delta_score_put],"Gamma":[round(put_gamma, 4),gamma_score_put],"Vega":[round(put_vega, 4),vega_score_put],"Theta":[np.round(-put_theta, 4),theta_score_put],"Rho":[round(put_rho, 4),rho_score_put]}
        df_param_score_weights=pd.DataFrame(parameters_score_dict)
        rows_params=["Data","Score","Weights"]
        weights=[0.1,0.1,0.15,0.1,0.1,0.13,0.09,0.05,0.15,0.03]
        
        df_param_score_weights.loc[len(df_param_score_weights)]=weights
        df_param_score_weights.index=rows_params
        st.dataframe(df_param_score_weights.loc[["Data","Score"]])
        sum_score=df_param_score_weights.loc["Score"].dot(df_param_score_weights.loc["Weights"])
        st.write("Total Score is:",round(sum_score,2))
    if st.radio("Is the last price your entry price?",options=["Yes","No"],index=1) == "No":
        entry_price=st.number_input("Enter put contract paid price",min_value=0.00,value=1.00,step=0.05)
    else:
        entry_price=live_price
    #max_contracts_buy=int(premium_investment/(last_price*100))
    #st.write("Possibility to buy up to",max_contracts_buy,"contract/s. The remainder cash position after the premium paid is",round(premium_investment%(last_price*max_contracts_buy*100),2),"USD.")
    nr_contracts_buy=st.number_input("Enter amount of contracts bought",min_value=0,value=1,step=1)
    if nr_contracts_buy==0:
        remainder_shares=nr_shares
    else: remainder_shares=round(nr_shares%100,2)
    #st.write("Based on the price and paramteres selected it is possible to buy up to : USD",last_price*nr_contracts*100,"in premium.")
    st.sidebar.write("Buy to open quantity of contracts:",nr_contracts_buy)
    st.sidebar.write("Premium required:",round(entry_price*nr_contracts_buy*100,2))
    #st.sidebar.write("Cash avilable after premium paid:",round(premium_investment%(last_price*nr_contracts_buy*100),2))
    
    st.divider()
    st.subheader("P&L potential and targets")
    st.write("Max profit potential is +infinite.")
    perc_profit=st.number_input("What is the % profit target?",min_value=0,step=1,value=10)
    perc_profit=perc_profit/100
    st.write("Max loss potential, including any uncovered positions if applicable, is",(spot-strike-entry_price)*nr_contracts_buy*100+remainder_shares*(spot))
    perc_risk=st.number_input("What is the % risk target?",min_value=0,step=1,value=5)
    perc_risk=perc_risk/100

    st.divider()
    st.subheader("Results based on inputs")
    if  nr_contracts_buy==0:
        st.write("No contracts bought. To see other scenarios change inputs.")
    else:
        st.write("The take profit exit price is: ",round(spot*(1+perc_profit)+entry_price,2))
        st.write("The profit amount would be: ",round((spot*(perc_profit)+entry_price)*nr_shares-entry_price*100*nr_contracts_buy,2),"USD including premium paid.")
        st.write("The stop loss price is: ",round(spot*(1-perc_risk)+entry_price,2))
        st.write("The loss amount would be: ",round((spot*(perc_risk)+entry_price)*nr_shares-entry_price*100*nr_contracts_buy,2),"USD including premium paid.")


    if st.button("Plot Protective Put payoff diagram"):
        st.write("Breakeven",round(strike+entry_price,2))
        #st.set_option('deprecation.showPyplotGlobalUse', False)
        plot_long_call=op.single_plotter( 
        op_type='c',
        spot=spot,
        spot_range = 10,#atm_call_iv_annual,
        strike=strike ,
        tr_type= 'b',
        op_pr= entry_price,
        save= False)

        st.pyplot(plot_long_call)

    
   



col1, col2, col3 = st.columns(3)

with col1:
    st.write("")
with col2:
    st.image("https://github.com/YWCo/logo/blob/main/YellowWolf.jpg?raw=true")
with col3:
    st.write("")
