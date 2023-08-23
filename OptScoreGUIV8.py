import streamlit as st
import pandas as pd
import yfinance as yf
import datetime, math
import wallstreet as ws
import numpy as np
import time, sys
import warnings
warnings.filterwarnings("ignore")
from optionprice import Option

st.set_page_config(page_title="Option Scoring Algorithm",
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

st.markdown("<h1 style='text-align: center; color: black;'>Option Scoring Algorithm</h1>", unsafe_allow_html=True)

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
option_type="Call"

@st.cache_data
def calculate_strike_params_call(_c, symbol, spot, start_dummy, stop_dummy, expiry,strike_params_table_empty,max_pain):
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
            dummy_strike_par=[dummy_strike_number,c.volume,c.open_interest,c.implied_volatility(),bsm_on_strike,max_pain,c.delta(),c.gamma(),c.vega(),c.theta(),c.rho()]
            this_strike_params=pd.DataFrame([dummy_strike_par],columns=cols)
            strike_params_table=pd.concat([strike_params_table,this_strike_params])
            n+=1
    strike_params_table.reset_index(drop=True, inplace=True)
    
    return strike_params_table

@st.cache_data
def calculate_strike_params_put(_p, symbol, spot, start_dummy, stop_dummy, expiry,strike_params_table_empty,max_pain):
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
            dummy_strike_par=[dummy_strike_number,p.volume,p.open_interest,p.implied_volatility(),bsm_on_strike,max_pain,p.delta(),p.gamma(),p.vega(),p.theta(),p.rho()]
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
chain = options_chain(tk, expiry)
strikes = chain.get(['strike']).values.tolist()
losses = [total_loss_on_strike(chain, strike[0]) for strike in strikes]
closses = [call_loss_on_strike(chain, strike[0]) for strike in strikes]
plosses = [put_loss_on_strike(chain, strike[0]) for strike in strikes]
flat_strikes = [item for sublist in strikes for item in sublist]
point = losses.index(min(losses))
max_pain = flat_strikes[point]
#st.write(f"\nMaximum Pain: **{max_pain}**")
#calculate Greeks for calls or puts. Inherited: ticker, expiry date. Inputs:C/P,strike. Output: Greeks, Vol, OI, BSM
optiontype = st.radio("Enter the type of Option, Call or Put",options=["Call","Put"])
strike_known=st.radio("Strike price known:",options=["Yes","No"],index=0)
year_option_ticker=expiry[2:4]
month_option_ticker=expiry[-5:-3]
date_option_ticker=expiry[-2:]
rates_senti=st.radio("Will interest rates probably go up or down during trade (if unsure select 'Up'): ",options=["Up","Down"],index=0)
if strike_known=="Yes":
    if optiontype == "Call":
        exp = datetime.datetime.strptime(expiry, "%Y-%m-%d").date()
        d, m, y = exp.day, exp.month, exp.year
        #st.write("symbol:", symbol)
        #st.write("expiry (YYYY-MM-DD):", expiry)
        c = ws.Call(symbol, d, m, y)
        strike = st.selectbox("Enter strike (USD): ",options=list(c.strikes),index=int(len(c.strikes)*0.3))
        st.write("symbol:", symbol)
        st.write("Underlying price (USD):", c.underlying.price)
        st.write("Option Type:", c.Option_type)
        c.set_strike(strike)
        st.write("expiry (YYYY-MM-DD):", expiry)
        st.write("strike price (USD):",strike)
        full_ticker=symbol+year_option_ticker+month_option_ticker+date_option_ticker+"C"+"00"+str(strike)+"000"
        st.write("OCC Option ticker:",full_ticker)
        #BSM
        #get todays date
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
                k=strike,
                t= count_working_days(datetime.date.today().strftime("%Y-%m-%d"), expiry),
                sigma=annual_volatility,
                r=0.05,
                dv=0).getPrice()

        st.write("Option BSM price (USD):",round(call_BSM_price,2)) #c.price)
        api_call=("https://api.polygon.io/v2/last/trade/O:"+full_ticker+"?apiKey=gZ8y5mYiZQ07XxeIemZbSBpeaErIwTyl")
        api_live_data=pd.read_json(api_call)
        live_price=api_live_data.loc["p","results"]
        st.write("Option live price (USD):", live_price)
        if st.button('Score'):
            #c.set_strike(strike)
            #st.write("Option Type:", c.Option_type)
            #st.write("Option price (USD):", c.price)
            #st.write("Underlying price (USD):", c.underlying.price)

            call_vol=c.volume
            call_oi=c.open_interest
            call_iv=c.implied_volatility()
            call_delta=int(c.delta()*100)
            call_gamma=c.gamma()
            call_theta=c.theta()
            call_vega=c.vega()
            call_rho=c.rho()
            
            if call_oi==0:
                st.write("No contract OI found, assigned value of 1. Please re-run during market hours.")
                call_oi=1

            progress_text = "Running algorithm. Please wait."
            my_bar = st.progress(0, text=progress_text)

            for percent_complete in range(100):
                time.sleep(0.05)
                my_bar.progress(percent_complete + 1, text=progress_text+" "+str(percent_complete)+"%")
            my_bar.empty()
            
            #st.write("Option Volume:",call_vol)
            #st.write("Option OI:", call_oi)
            #st.write("IV:", round(call_iv, 4))
            #st.write("Delta:", round(call_delta, 4))
            #st.write("Gamma:", round(call_gamma, 4))
            #st.write("Theta:", np.round(call_theta, 4)) 
            #st.write("Vega:", round(call_vega, 4))
            #st.write("Rho:", round(call_rho, 4))

            #1-scoring volume calls:
            
            tk = yf.Ticker(symbol)
            option_chain=tk.option_chain(expiry)
            calls_df_all = option_chain.calls
            calls_df=calls_df_all[[ "contractSymbol","strike","volume"]]
            calls_df.sort_values(by="volume",ascending=False,inplace=True)
            #top10
            calls_df_top10volume=calls_df.head(10)
            #st.dataframe(calls_df_top10volume)
            scoring_bands = [(calls_df_top10volume.volume.iloc[-1]), (calls_df_top10volume.volume.iloc[-2]), 
                              (calls_df_top10volume.volume.iloc[-3]), (calls_df_top10volume.volume.iloc[-4]), 
                              (calls_df_top10volume.volume.iloc[-5]), (calls_df_top10volume.volume.iloc[-6]),
                              (calls_df_top10volume.volume.iloc[-7]), (calls_df_top10volume.volume.iloc[-8]),
                              (calls_df_top10volume.volume.iloc[-9]), (calls_df_top10volume.volume.iloc[0])
                              ]
            scores = [-10,-8,-6,-4,-2,2,4,6,8,10]
            #initialize variable
            vol_score_call = None
            # Value to compare
            value_to_compare = call_vol
            for i, value in enumerate(scoring_bands):
                if value == value_to_compare:
                    vol_score_call = scores[i]
                    break

            # If no range matched, assign a default score
            if vol_score_call is None:
                vol_score_call = -10

            #st.write("vol score:", vol_score_call)
            
            
            
            
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
            scores_oi = [8,6,4,2,0,-2,-4,-6,-8]
            # Value to compare
            value_to_compare = call_vol/call_oi
            # Initialize the score variable
            oi_score_call = None
            array_score_bands=np.array(scoring_bands_oi)
            # Compare the value with the scoring bands
            if value_to_compare <= scoring_bands_oi[0][0]:
                oi_score_call = 10
            elif value_to_compare >= scoring_bands_oi[-1][-1]:
                oi_score_call = -10
            else:
                for i, (lower,upper) in enumerate(array_score_bands):
                    if lower <= value_to_compare < upper:
                        oi_score_call = scores[i]
                        break

           

            #st.write("oi score:", oi_score_call)




            #3-scoring IV:
            iv_score_call=0
            if call_iv>0.3:
                iv_score_call=10
            else: iv_score_call=-10
            #st.write("iv score:", iv_score_call)
            

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

            # Value to compare
            value_to_compare = 1-(live_price/round(call_BSM_price,2))
            
            # Initialize the score variable
            bsm_score_call = None
            array_score_bands=np.array(scoring_bands_bsm)
            # Compare the value with the scoring bands
            if value_to_compare < scoring_bands_bsm[0][0]:
                bsm_score_call = -10
            elif value_to_compare > scoring_bands_bsm[-1][-1]:
                bsm_score_call = 10
            else:
                for i, (lower,upper) in enumerate(array_score_bands):
                    if lower <= value_to_compare < upper:
                        bsm_score_call = scores[i]
                        break
            #st.write("bsm score:", bsm_score_call)





            #4-score Max Pain for Calls:
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
            mp_score_call = None
            array_score_bands=np.array(scoring_bands_mp)
            # Compare the value with the scoring bands
            if value_to_compare < scoring_bands_mp[0][0]:
                mp_score_call = -10
            elif value_to_compare > scoring_bands_mp[-1][-1]:
                mp_score_call = 10
            else:
                for i, (lower,upper) in enumerate(array_score_bands):
                    if lower <= value_to_compare < upper:
                        mp_score_call = scores[i]
                        break
            #st.write("mp score:", mp_score_call)           

            #Score Delta calls:
            scoring_bands_delta = [(0,10),
                             (10,20),
                             (20,30),
                             (30,40),
                             (40,50),
                             (50,60),
                             (60,70),
                             (70,80),
                             (80,90),
                             (90,100)
                             ]
            scores = [-10,-8,-6,-4,-2,0,2,4,6,8]     
            value_to_compare = call_delta
            # Initialize the score variable
            delta_score_call = None
            array_score_bands=np.array(scoring_bands_delta)
            # Compare the value with the scoring bands

            #if value_to_compare==0:
             #       delta_score_call=-10
            if value_to_compare==100:
                    delta_score_call=10
            
            else:
                for i, (lower,upper) in enumerate(array_score_bands):
                    if lower <= value_to_compare < upper:
                        delta_score_call = scores[i]
                        break
            #st.write("delta score:", delta_score_call) 

            #Score Gamma calls:
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
            value_to_compare = call_gamma
            
            # Initialize the score variable
            gamma_score_call = None
            array_score_bands=np.array(scoring_bands_gamma)
            # Compare the value with the scoring bands
            if value_to_compare > scoring_bands_gamma[-1][-1]:
                gamma_score_call = 10
            else:
                for i, (lower,upper) in enumerate(array_score_bands):
                    if lower <= value_to_compare < upper:
                        gamma_score_call = scores[i]
                        break
            #st.write("gamma score:", gamma_score_call)  

            #Score Vega calls:
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
            value_to_compare = call_vega
            # Initialize the score variable
            vega_score_call = None
            array_score_bands=np.array(scoring_bands_vega)
            # Compare the value with the scoring bands
            if value_to_compare > scoring_bands_vega[-1][-1]:
                gamma_score_call = 10
            else:
                for i, (lower,upper) in enumerate(array_score_bands):
                    if lower <= value_to_compare < upper:
                        vega_score_call = scores[i]
                        break
            #st.write("vega score:", vega_score_call) 

            #Score Theta calls:
            scoring_bands_theta = [(-0.04,-0.035),
                             (-0.035,-0.03),
                             (-0.030,-0.025),
                             (-0.025,-0.020),
                             (-0.020,-0.015),
                             (-0.015,-0.010),
                             (-0.010,-0.005),
                             (-0.005,0)
                             
                             ]
            scores = [-7.5,-5,-2.5,0,2.5,5,7.5,10]
            value_to_compare = -call_theta
            # Initialize the score variable
            theta_score_call = None
            array_score_bands=np.array(scoring_bands_theta)
            # Compare the value with the scoring bands
            if value_to_compare < scoring_bands_theta[0][0]:
                theta_score_call = -10
            else:
                for i, (lower,upper) in enumerate(array_score_bands):
                    if lower <= value_to_compare < upper:
                        theta_score_call = scores[i]
                        break
            #st.write("theta score:", theta_score_call) 

            #Score Rho calls:
            if rates_senti=="Up":
                
                scoring_bands_rho = [(0,0.01),
                                       (0.01,0.02),
                                       (0.02,0.03),
                                       (0.03,0.04),
                                       (0.04,float("inf"))
                                       ]
                scores = [-10,-5,0,5,10]
                value_to_compare = call_rho
                array_score_bands=np.array(scoring_bands_rho)
                # Initialize the score variable
                rho_score_call = None
                for i, (lower,upper) in enumerate(array_score_bands):
                    if lower <= value_to_compare < upper:
                        rho_score_call = scores[i]
                        break
            else:
                scoring_bands_rho = [(0,0.01),
                                       (0.01,0.02),
                                       (0.02,0.03),
                                       (0.03,0.04),
                                       (0.04,float("inf"))
                                       ]
                scores = [10,5,0,-5,-10]
                value_to_compare = call_rho
                array_score_bands=np.array(scoring_bands_rho)
                # Initialize the score variable
                rho_score_call = None
                for i, (lower,upper) in enumerate(array_score_bands):
                    if lower <= value_to_compare < upper:
                        rho_score_call = scores[i]
                        break
            #st.write("rho score:", rho_score_call)
            
            parameters_score_dict={ "Volume":[call_vol,vol_score_call],"OI":[call_oi,oi_score_call],"IV":[round(call_iv, 4),iv_score_call],"BSM":[round(call_BSM_price,2),bsm_score_call],"Max Pain":[max_pain,mp_score_call],"Delta":[round(call_delta, 4),delta_score_call],"Gamma":[round(call_gamma, 4),gamma_score_call],"Vega":[round(call_vega, 4),vega_score_call],"Theta":[np.round(-call_theta, 4),theta_score_call],"Rho":[round(call_rho, 4),rho_score_call]}
            df_param_score_weights=pd.DataFrame(parameters_score_dict)
            rows_params=["Data","Score","Weights"]
            weights=[0.1,0.1,0.15,0.1,0.1,0.13,0.09,0.05,0.15,0.03]
            
            df_param_score_weights.loc[len(df_param_score_weights)]=weights
            df_param_score_weights.index=rows_params
            st.dataframe(df_param_score_weights["Data","Score"])
            sum_score=df_param_score_weights.loc["Score"].dot(df_param_score_weights.loc["Weights"])
            st.write("Total Score is:",round(sum_score,2))

    #option=put
    else:
        exp = datetime.datetime.strptime(expiry, "%Y-%m-%d").date()
        d, m, y = exp.day, exp.month, exp.year
        #st.write("symbol:", symbol)
        #st.write("expiry (YYYY-MM-DD):", expiry)
        p = ws.Put(symbol, d, m, y)
        strike = st.selectbox("Enter strike (USD): ",options=list(p.strikes),index=int(len(p.strikes)*0.6))
        
        st.write("symbol:", symbol)
        st.write("Underlying price (USD):", p.underlying.price)
        st.write("Option Type:", p.Option_type)
        p.set_strike(strike)
        st.write("expiry (YYYY-MM-DD):", expiry)
        st.write("strike price (USD):",strike)
        full_ticker=symbol+year_option_ticker+month_option_ticker+date_option_ticker+"P"+"00"+str(strike)+"000"
        st.write("OCC Option ticker:",full_ticker)
        #BSM
        #get todays date
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
                k=strike,
                t= count_working_days(datetime.date.today().strftime("%Y-%m-%d"), expiry),
                sigma=annual_volatility,
                r=0.05,
                dv=0).getPrice()

        st.write("Option BSM price (USD):", round(put_BSM_price,2))
        api_call=("https://api.polygon.io/v2/last/trade/O:"+full_ticker+"?apiKey=gZ8y5mYiZQ07XxeIemZbSBpeaErIwTyl")
        api_live_data=pd.read_json(api_call)
        live_price=api_live_data.loc["p","results"]
        st.write("Option live price (USD):", live_price)
        if st.button('Score'):
            #p.set_strike(strike)
            #st.write("Option Type:", p.Option_type)
            #st.write("Option theoretical BSM price (USD):", p.price)
            #st.write("Underlying price (USD):", p.underlying.price)  
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
            option_chain=tk.option_chain(expiry)
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

            # Value to compare
            value_to_compare = 1-(live_price/round(put_BSM_price,2))
            #st.write(value_to_compare)
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
            value_to_compare = put_theta
            # Initialize the score variable
            theta_score_put = None
            array_score_bands=np.array(scoring_bands_theta)
            # Compare the value with the scoring bands
            if value_to_compare == scoring_bands_theta[-1][-1]:
                theta_score_put = 10
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
            st.dataframe(df_param_score_weights["Data","Score"])
            sum_score=df_param_score_weights.loc["Score"].dot(df_param_score_weights.loc["Weights"])
            st.write("Total Score is:",round(sum_score,2))

#if strike not known display strikes and paramters
else:
    #rates_senti=st.radio("Will interest rates probably go up or down during your position exposure: ",options=["Up","Down"],index=0)
    cols=["Strike","Vol","OI","IV","BSM","MP","Delta","Gamma","Vega","Theta","Rho"]
    strike_params_table_empty = pd.DataFrame( columns=list(cols))
    if optiontype == "Call":
        exp = datetime.datetime.strptime(expiry, "%Y-%m-%d").date()
        d, m, y = exp.day, exp.month, exp.year
        st.write("symbol:", symbol)
        st.write("expiry (YYYY-MM-DD):", expiry)
        c = ws.Call(symbol, d, m, y)
        #st.write("strikes (USD):", c.strikes)
        n=0
        start_dummy=int(len(c.strikes)/2-5)
        stop_dummy=int(len(c.strikes)/2+5)
        n=start_dummy
        
        dfr_call=calculate_strike_params_call(c, symbol, spot, start_dummy, stop_dummy, expiry,strike_params_table_empty,max_pain)
        st.dataframe(dfr_call) 

        strike = st.selectbox("Enter strike (USD): ",list(c.strikes[start_dummy:stop_dummy]),index=0)
        type(strike)
        c.set_strike(strike)
        st.write("expiry (YYYY-MM-DD):", expiry)
        st.write("strike price (USD):",strike)
        full_ticker=symbol+year_option_ticker+month_option_ticker+date_option_ticker+"C"+"00"+str(strike)+"000"
        st.write("OCC Option ticker:",full_ticker)
        #BSM
        #get todays date
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
                k=strike,
                t= count_working_days(datetime.date.today().strftime("%Y-%m-%d"), expiry),
                sigma=annual_volatility,
                r=0.05,
                dv=0).getPrice()

        st.write("Option BSM price (USD):",round(call_BSM_price,2)) #c.price)
        api_call=("https://api.polygon.io/v2/last/trade/O:"+full_ticker+"?apiKey=gZ8y5mYiZQ07XxeIemZbSBpeaErIwTyl")
        api_live_data=pd.read_json(api_call)
        live_price=api_live_data.loc["p","results"]
        st.write("Option live price (USD):", live_price)
        if st.button('Score'):
            #c.set_strike(strike)
            #st.write("Option Type:", c.Option_type)
            #st.write("Option price (USD):", c.price)
            #st.write("Underlying price (USD):", c.underlying.price)
            call_vol=c.volume
            call_oi=c.open_interest
            call_iv=c.implied_volatility()
            call_delta=int(c.delta()*100)
            call_gamma=c.gamma()
            call_theta=c.theta()
            call_vega=c.vega()
            call_rho=c.rho()
            if call_oi==0:
                st.write("No contract OI found, assigned value of 1. Please re-run during market hours.")
                call_oi=1

            progress_text = "Running algorithm. Please wait."
            my_bar = st.progress(0, text=progress_text)

            for percent_complete in range(100):
                time.sleep(0.1)
                my_bar.progress(percent_complete + 1, text=progress_text+" "+str(percent_complete)+"%")
            my_bar.empty()

            #st.write("Option Volume:",call_vol)
            #st.write("Option OI:", call_oi)
            #st.write("IV:", round(call_iv, 4))
            #st.write("Delta:", round(call_delta, 4))
            #st.write("Gamma:", round(call_gamma, 4))
            #st.write("Theta:", np.round(call_theta, 4)) 
            #st.write("Vega:", round(call_vega, 4))
            #st.write("Rho:", round(call_rho, 4))

            #1-scoring volume calls:
            
            tk = yf.Ticker(symbol)
            option_chain=tk.option_chain(expiry)
            calls_df_all = option_chain.calls
            calls_df=calls_df_all[[ "contractSymbol","strike","volume"]]
            calls_df.sort_values(by="volume",ascending=False,inplace=True)
            #top10
            calls_df_top10volume=calls_df.head(10)
            #st.dataframe(calls_df_top10volume)
            scoring_bands = [(calls_df_top10volume.volume.iloc[-1]), (calls_df_top10volume.volume.iloc[-2]), 
                              (calls_df_top10volume.volume.iloc[-3]), (calls_df_top10volume.volume.iloc[-4]), 
                              (calls_df_top10volume.volume.iloc[-5]), (calls_df_top10volume.volume.iloc[-6]),
                              (calls_df_top10volume.volume.iloc[-7]), (calls_df_top10volume.volume.iloc[-8]),
                              (calls_df_top10volume.volume.iloc[-9]), (calls_df_top10volume.volume.iloc[0])
                              ]
            scores = [-10,-8,-6,-4,-2,2,4,6,8,10]
            #initialize variable
            vol_score_call = None
            # Value to compare
            value_to_compare = call_vol
            for i, value in enumerate(scoring_bands):
                if value == value_to_compare:
                    vol_score_call = scores[i]
                    break

            # If no range matched, assign a default score
            if vol_score_call is None:
                vol_score_call = -10
            
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
            scores_oi = [8,6,4,2,0,-2,-4,-6,-8]
            # Value to compare
            value_to_compare = call_vol/call_oi
            # Initialize the score variable
            oi_score_call = None
            array_score_bands=np.array(scoring_bands_oi)
            # Compare the value with the scoring bands
            if value_to_compare < scoring_bands_oi[0][0]:
                oi_score_call = 10
            elif value_to_compare > scoring_bands_oi[-1][-1]:
                oi_score_call = -10
            else:
                for i, (lower,upper) in enumerate(array_score_bands):
                    if lower <= value_to_compare < upper:
                        oi_score_call = scores[i]
                        break

            #3-scoring IV:
            iv_score_call=0
            if call_iv>0.3:
                iv_score_call=10
            else: iv_score_call=-10
            #st.write("iv score:", iv_score_call)
            

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

            # Value to compare
            value_to_compare = 1-(live_price/round(call_BSM_price,2))
            
            # Initialize the score variable
            bsm_score_call = None
            array_score_bands=np.array(scoring_bands_bsm)
            # Compare the value with the scoring bands
            if value_to_compare < scoring_bands_bsm[0][0]:
                bsm_score_call = -10
            elif value_to_compare > scoring_bands_bsm[-1][-1]:
                bsm_score_call = 10
            else:
                for i, (lower,upper) in enumerate(array_score_bands):
                    if lower <= value_to_compare < upper:
                        bsm_score_call = scores[i]
                        break
            
            #4-score Max Pain for Calls:
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
            #st.write(value_to_compare)
            # Initialize the score variable
            mp_score_call = None
            array_score_bands=np.array(scoring_bands_mp)
            # Compare the value with the scoring bands
            if value_to_compare < scoring_bands_mp[0][0]:
                mp_score_call = -10
            elif value_to_compare > scoring_bands_mp[-1][-1]:
                mp_score_call = 10
            else:
                for i, (lower,upper) in enumerate(array_score_bands):
                    if lower <= value_to_compare < upper:
                        mp_score_call = scores[i]
                        break
            #st.write("mp score:", mp_score_call)           

            #Score Delta calls:
            scoring_bands_delta = [(0,10),
                             (10,20),
                             (20,30),
                             (30,40),
                             (40,50),
                             (60,70),
                             (70,80),
                             (80,90),
                             (90,100)
                             ]
            scores = [-8,-6,-4,-2,0,2,4,6,8]     
            value_to_compare = call_delta
            # Initialize the score variable
            delta_score_call = None
            array_score_bands=np.array(scoring_bands_delta)
            # Compare the value with the scoring bands
            if value_to_compare==0:
                    delta_score_call=-10
            elif value_to_compare==100:
                    delta_score_call=10
            
            else:
                for i, (lower,upper) in enumerate(array_score_bands):
                    if lower <= value_to_compare < upper:
                        delta_score_call = scores[i]
                        break
            #st.write("delta score:", delta_score_call) 

            #Score Gamma calls:
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
            value_to_compare = call_gamma
            #st.write(value_to_compare)
            # Initialize the score variable
            gamma_score_call = None
            array_score_bands=np.array(scoring_bands_gamma)
            # Compare the value with the scoring bands
            if value_to_compare > scoring_bands_gamma[-1][-1]:
                gamma_score_call = 10
            else:
                for i, (lower,upper) in enumerate(array_score_bands):
                    if lower <= value_to_compare < upper:
                        gamma_score_call = scores[i]
                        break
            #st.write("gamma score:", gamma_score_call)  

            #Score Vega calls:
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
            value_to_compare = call_vega
            # Initialize the score variable
            vega_score_call = None
            array_score_bands=np.array(scoring_bands_vega)
            # Compare the value with the scoring bands
            if value_to_compare > scoring_bands_vega[-1][-1]:
                gamma_score_call = 10
            else:
                for i, (lower,upper) in enumerate(array_score_bands):
                    if lower <= value_to_compare < upper:
                        vega_score_call = scores[i]
                        break
            #st.write("vega score:", vega_score_call) 

            #Score Theta calls:
            scoring_bands_theta = [(-0.04,-0.035),
                             (-0.035,-0.03),
                             (-0.030,-0.025),
                             (-0.025,-0.020),
                             (-0.020,-0.015),
                             (-0.015,-0.010),
                             (-0.010,-0.005),
                             (-0.005,0)
                             
                             ]
            scores = [-7.5,-5,-2.5,0,2.5,5,7.5,10]
            value_to_compare = call_theta
            # Initialize the score variable
            theta_score_call = None
            array_score_bands=np.array(scoring_bands_theta)
            # Compare the value with the scoring bands
            if value_to_compare < scoring_bands_theta[0][0]:
                theta_score_call = -10
            else:
                for i, (lower,upper) in enumerate(array_score_bands):
                    if lower <= value_to_compare < upper:
                        theta_score_call = scores[i]
                        break
            #st.write("theta score:", theta_score_call) 

            #Score Rho calls:
            if rates_senti=="Up":
                
                scoring_bands_rho = [(0,0.01),
                                       (0.01,0.02),
                                       (0.02,0.03),
                                       (0.03,0.04),
                                       (0.04,float("inf"))
                                       ]
                scores = [-10,-5,0,5,10]
                value_to_compare = call_rho
                array_score_bands=np.array(scoring_bands_rho)
                # Initialize the score variable
                rho_score_call = None
                for i, (lower,upper) in enumerate(array_score_bands):
                    if lower <= value_to_compare < upper:
                        rho_score_call = scores[i]
                        break
            else:
                scoring_bands_rho = [(0,0.01),
                                       (0.01,0.02),
                                       (0.02,0.03),
                                       (0.03,0.04),
                                       (0.04,float("inf"))
                                       ]
                scores = [10,5,0,-5,-10]
                value_to_compare = call_rho
                array_score_bands=np.array(scoring_bands_rho)
                # Initialize the score variable
                rho_score_call = None
                for i, (lower,upper) in enumerate(array_score_bands):
                    if lower <= value_to_compare < upper:
                        rho_score_call = scores[i]
                        break
            #st.write("rho score:", rho_score_call)
            
            parameters_score_dict={ "Volume":[call_vol,vol_score_call],"OI":[call_oi,oi_score_call],"IV":[round(call_iv, 4),iv_score_call],"BSM":[round(call_BSM_price,2),bsm_score_call],"Max Pain":[max_pain,mp_score_call],"Delta":[round(call_delta, 4),delta_score_call],"Gamma":[round(call_gamma, 4),gamma_score_call],"Vega":[round(call_vega, 4),vega_score_call],"Theta":[np.round(call_theta, 4),theta_score_call],"Rho":[round(call_rho, 4),rho_score_call]}
            df_param_score_weights=pd.DataFrame(parameters_score_dict)
            rows_params=["Data","Score","Weights"]
            weights=[0.1,0.1,0.15,0.1,0.1,0.13,0.09,0.05,0.15,0.03]
            
            df_param_score_weights.loc[len(df_param_score_weights)]=weights
            df_param_score_weights.index=rows_params
            st.dataframe(df_param_score_weights["Data","Score"])
            sum_score=df_param_score_weights.loc["Score"].dot(df_param_score_weights.loc["Weights"])
            st.write("Total Score is:",round(sum_score,2))
         # selectbox with nnumbers

        

    else:
        exp = datetime.datetime.strptime(expiry, "%Y-%m-%d").date()
        d, m, y = exp.day, exp.month, exp.year
        st.write("symbol:", symbol)
        st.write("expiry (YYYY-MM-DD):", expiry)
        p = ws.Put(symbol, d, m, y)
        #st.write("strikes (USD):", c.strikes)
        n=0
        start_dummy=int(len(p.strikes)/2-5)
        stop_dummy=int(len(p.strikes)/2+5)
        n=start_dummy
     
        dfr_put=calculate_strike_params_put(p, symbol, spot, start_dummy, stop_dummy, expiry,strike_params_table_empty,max_pain)

        st.dataframe(dfr_put)

        strike = st.selectbox("Enter strike (USD): ",list(p.strikes[start_dummy:stop_dummy]),index=0)
        type(strike)
        p.set_strike(strike)
        st.write("expiry (YYYY-MM-DD):", expiry)
        st.write("strike price (USD):",strike)
        full_ticker=symbol+year_option_ticker+month_option_ticker+date_option_ticker+"P"+"00"+str(strike)+"000"
        st.write("OCC Option ticker:",full_ticker)
        #BSM
        #get todays date
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
                k=strike,
                t= count_working_days(datetime.date.today().strftime("%Y-%m-%d"), expiry),
                sigma=annual_volatility,
                r=0.05,
                dv=0).getPrice()

        st.write("Option BSM price (USD):",round(put_BSM_price,2)) #c.price)
        api_call=("https://api.polygon.io/v2/last/trade/O:"+full_ticker+"?apiKey=gZ8y5mYiZQ07XxeIemZbSBpeaErIwTyl")
        api_live_data=pd.read_json(api_call)
        live_price=api_live_data.loc["p","results"]
        st.write("Option live price (USD):", live_price)
        if st.button('Score'):
            #c.set_strike(strike)
            #st.write("Option Type:", c.Option_type)
            #st.write("Option price (USD):", c.price)
            #st.write("Underlying price (USD):", c.underlying.price)
            put_vol=p.volume
            put_oi=p.open_interest
            put_iv=p.implied_volatility()
            put_delta=int(p.delta()*100)
            put_gamma=p.gamma()
            put_theta=p.theta()
            put_vega=p.vega()
            put_rho=p.rho()
            if put_oi==0:
                st.write("No contract OI found, assigned value of 1. Please re-run during market hours.")
                put_oi=1

            progress_text = "Running algorithm. Please wait."
            my_bar = st.progress(0, text=progress_text)

            for percent_complete in range(100):
                time.sleep(0.1)
                my_bar.progress(percent_complete + 1, text=progress_text+" "+str(percent_complete)+"%")
            my_bar.empty()

            #st.write("Option Volume:",put_vol)
            #st.write("Option OI:", put_oi)
            #st.write("IV:", round(put_iv, 4))
            #st.write("Delta:", round(put_delta, 4))
            #st.write("Gamma:", round(put_gamma, 4))
            #st.write("Theta:", np.round(put_theta, 4)) 
            #st.write("Vega:", round(put_vega, 4))
            #st.write("Rho:", round(put_rho, 4))

            #1-scoring volume puts:
            
            tk = yf.Ticker(symbol)
            option_chain=tk.option_chain(expiry)
            puts_df_all = option_chain.puts
            puts_df=puts_df_all[[ "contractSymbol","strike","volume"]]
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

            #st.write("vol score:", vol_score_put)
            
            
            
            
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
            scores_oi = [8,6,4,2,0,-2,-4,-6,-8]
            # Value to compare
            value_to_compare = put_vol/put_oi
            # Initialize the score variable
            oi_score_put = None
            array_score_bands=np.array(scoring_bands_oi)
            # Compare the value with the scoring bands
            if value_to_compare < scoring_bands_oi[0][0]:
                oi_score_put = 10
            elif value_to_compare >= scoring_bands_oi[-1][-1]:
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

            # Value to compare
            value_to_compare = 1-(live_price/round(put_BSM_price,2))
            #st.write(value_to_compare)
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
            #st.write(value_to_compare)
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
                       (-20, -10)
                             ]
            scores = [8,6,4,2,0,-2,-4,-6,-8]     
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
                for i, (lower,upper) in enumerate(array_score_bands):
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
                             (-0.035,-0.03),
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
                
                scoring_bands_rho = [( -float("inf"),-0.04),
                     (-0.04, -0.03),
                     (-0.03, -0.02),
                     (-0.02, -0.01),
                     (-0.01,0)
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
            else:
                
                scoring_bands_rho = [( -float("inf"),-0.04),
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
                    if lower <= value_to_compare < upper:
                        rho_score_put = scores[i]
                        break
            #st.write("rho score:", rho_score_put)
            
            parameters_score_dict={ "Volume":[put_vol,vol_score_put],"OI":[put_oi,oi_score_put],"IV":[round(put_iv, 4),iv_score_put],"BSM":[round(put_BSM_price,2),bsm_score_put],"Max Pain":[max_pain,mp_score_put],"Delta":[round(put_delta, 4),delta_score_put],"Gamma":[round(put_gamma, 4),gamma_score_put],"Vega":[round(put_vega, 4),vega_score_put],"Theta":[np.round(-put_theta, 4),theta_score_put],"Rho":[round(put_rho, 4),rho_score_put]}
            df_param_score_weights=pd.DataFrame(parameters_score_dict)
            rows_params=["Data","Score","Weights"]
            weights=[0.1,0.1,0.15,0.1,0.1,0.13,0.09,0.05,0.15,0.03]
            
            df_param_score_weights.loc[len(df_param_score_weights)]=weights
            df_param_score_weights.index=rows_params
            st.dataframe(df_param_score_weights.loc[["Data","Score"]])
            sum_score=df_param_score_weights.loc["Score"].dot(df_param_score_weights.loc["Weights"])
            st.write("Total Score is:",round(sum_score,2))
col1, col2, col3 = st.columns(3)

with col1:
    st.write("")
with col2:
    st.image("https://github.com/YWCo/logo/blob/main/YellowWolf.jpg?raw=true")
with col3:
    st.write("")
