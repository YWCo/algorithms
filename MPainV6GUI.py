import streamlit as st
import pandas as pd
import yfinance as yf
import datetime
import matplotlib.pyplot as plt
import numpy as np
from datetime import date
import wallstreet as ws
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

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


def greeks(symbol, expiry, optiontype):
    if optiontype == "call":
        exp = datetime.datetime.strptime(expiry, "%Y-%m-%d").date()
        d, m, y = exp.day, exp.month, exp.year
        st.write("symbol:", symbol)
        st.write("expiry (YYYY-MM-DD):", expiry)
        c = ws.Call(symbol, d, m, y)
        st.write("strikes (USD):", c.strikes)
        strike = st.number_input("Enter strike (USD): ",value=c.strikes[0])
        c.set_strike(strike)
        st.write("Option Type:", c.Option_type)
        st.write("Option price (USD):", c.price)
        st.write("Underlying price (USD):", c.underlying.price)
        st.write("Delta:", round(c.delta(), 4))
        st.write("Gamma:", round(c.gamma(), 4))
        st.write("Vega:", round(c.vega(), 4))
        st.write("Rho:", round(c.rho(), 4))
        st.write("Implied Vol.:", round(c.implied_volatility(), 4))
    else:
        exp = datetime.datetime.strptime(expiry, "%Y-%m-%d").date()
        d, m, y = exp.day, exp.month, exp.year
        st.write("symbol:", symbol)
        st.write("expiry (YYYY-MM-DD):", expiry)
        p = ws.Put(symbol, d, m, y)
        st.write("strikes (USD):", p.strikes)
        strike = st.number_input("Enter strike (USD): ",value=p.strikes[0])
        p.set_strike(strike)
        st.write("Option Type:", p.Option_type)
        st.write("Option price (USD):", p.price)
        st.write("Underlying price (USD):", p.underlying.price)
        st.write("Delta:", round(p.delta(), 4))
        st.write("Gamma:", round(p.gamma(), 4))
        st.write("Vega:", round(p.vega(), 4))
        st.write("Rho:", round(p.rho(), 4))
        st.write("Implied Vol.:", round(p.implied_volatility(), 4))


#def main():
st.header("Max Pain Algorithm")
st.subheader("Max Pain Analysis",help="Max pain calculation is the sum of all dollar values of outstanding puts and call options for each in-the-money strike price.")
symbol = st.text_input("Enter the Symbol:",value="QQQ")
#if st.button("Enter Ticker"):
tk = yf.Ticker(symbol)
pr_api=("https://financialmodelingprep.com/api/v3/quote-short/"+symbol+"?apikey=e1f7367c932b9ff3949e05adf400970c")
x=pd.read_json(pr_api)
spot = round(x.iloc[0,1],2)
deno = "USD"
st.write('\nThe spot price is:', spot, deno)
exps = tk.options
st.write("\nExpiry dates:",exps)
    #for i in exps:
    #    st.write(f"{i}")

expiry = st.text_input("Enter the Expiry date (YYYY-MM-DD):",value=exps[0])
if st.button("Max Pain"):
    tk = yf.Ticker(symbol)
    chain = options_chain(tk, expiry)
    strikes = chain.get(['strike']).values.tolist()
    losses = [total_loss_on_strike(chain, strike[0]) for strike in strikes]
    closses = [call_loss_on_strike(chain, strike[0]) for strike in strikes]
    plosses = [put_loss_on_strike(chain, strike[0]) for strike in strikes]
    flat_strikes = [item for sublist in strikes for item in sublist]
    point = losses.index(min(losses))
    lossmp = min(losses)
    max_pain = flat_strikes[point]
    st.write(f"\nMaximum Pain: **{max_pain}**")
    today = str(date.today())
    dayscount = np.busday_count(today, expiry)
    perct = (max_pain - spot) / spot * 100
    if perct >= 0:
        st.write("\nThe Spot price:", spot, "USD is", round((spot / max_pain) * 100, 2),
                "% of the Max Pain. The spot price needs to increase by", round(perct, 2),
                "% in the next", dayscount, "trading days to reach it.")
    else:
        st.write("\nThe Max Pain is", round((max_pain / spot) * 100, 2), "% of the spot price:", spot,
                "USD. The spot price needs to decrease by", round(perct, 2),
                "% in the next", dayscount, "trading days to reach it.")
    callChain = chain.loc[chain['CALL'] == True]
    putChain = chain.loc[chain['CALL'] == False]
    pcr = putChain["volume"].sum() / callChain["volume"].sum()
    st.write("\nPut to call ratio:", round(pcr, 2))
    cch = callChain.sort_values(by='openInterest', ascending=False)
    pch = putChain.sort_values(by='openInterest', ascending=False)
    i = 0
    j = 0
    st.write("\nThe 5 near resistances for selected expiration date based on max descending Open Interest on calls are: ")
    while i < 5:
        st.write(i + 1, ") Strike:", cch['strike'].iloc[i], "; OI:", cch['openInterest'].iloc[i])
        i += 1
    st.write("\nThe 5 near supports for selected expiration date based on max descending Open Interest on puts are: ")
    while j < 5:
        st.write(j + 1, ") Strike", pch['strike'].iloc[j], "; OI:", pch['openInterest'].iloc[i])
        j += 1
    total = {}
    for i in range(len(flat_strikes)):
        if flat_strikes[i] not in total:
            total[flat_strikes[i]] = losses[i]
        else:
            total[flat_strikes[i]] += losses[i]
    totalc = {}
    for i in range(len(flat_strikes)):
        if flat_strikes[i] not in totalc:
            totalc[flat_strikes[i]] = closses[i]
        else:
            totalc[flat_strikes[i]] += closses[i]
    totalp = {}
    for i in range(len(flat_strikes)):
        if flat_strikes[i] not in totalp:
            totalp[flat_strikes[i]] = plosses[i]
        else:
            totalp[flat_strikes[i]] += plosses[i]
    plt.figure(figsize=(20, 5))
    plt.bar(totalc.keys(), totalc.values(), width=1.5, color="black")
    plt.bar(totalp.keys(), totalp.values(), bottom=list(totalc.values()), width=1.5, color="red")
    plt.bar(max_pain, total[max_pain], width=1.5, color="dodgerblue")
    plt.xticks(rotation=45, ha="center")
    instruments = ["Calls", "Puts", "Max Pain"]
    plt.legend(instruments, loc=2)
    plt.xlabel('Strike Price')
    plt.title(f"{symbol.upper()} Max Pain with expiry (YYYY-MM-DD) " + expiry)
    st.pyplot(plt,use_container_width=True)
    #gr_sel = st.selectbox("Print the Greeks?", ("No", "Yes"))
    #if gr_sel == "Yes":
#grdis = st.text_input("Display Greeks? Enter Yes/No",value="No")
st.subheader("Greeks Analysis",help="sensitivities of options")
optiontype = st.radio("Enter the type of Option, Call or Put",options=["Call","Put"])
if optiontype == "Call":
    exp = datetime.datetime.strptime(expiry, "%Y-%m-%d").date()
    d, m, y = exp.day, exp.month, exp.year
    st.write("symbol:", symbol)
    st.write("expiry (YYYY-MM-DD):", expiry)
    c = ws.Call(symbol, d, m, y)
    st.write("strikes (USD):", c.strikes)
    strike = st.number_input("Enter strike (USD): ",value=c.strikes[0])
else:
    exp = datetime.datetime.strptime(expiry, "%Y-%m-%d").date()
    d, m, y = exp.day, exp.month, exp.year
    st.write("symbol:", symbol)
    st.write("expiry (YYYY-MM-DD):", expiry)
    p = ws.Put(symbol, d, m, y)
    st.write("strikes (USD):", p.strikes)
    strike = st.number_input("Enter strike (USD): ",value=p.strikes[0])

if st.button("Display Greeks"):
    #optiontype = st.radio("Enter the type of Option, Call or Put",options=["Call","Put"])
    if optiontype == "Call":
        #exp = datetime.datetime.strptime(expiry, "%Y-%m-%d").date()
        #d, m, y = exp.day, exp.month, exp.year
        #st.write("symbol:", symbol)
        #st.write("expiry (YYYY-MM-DD):", expiry)
        #c = ws.Call(symbol, d, m, y)
        #st.write("strikes (USD):", c.strikes)
        #strike = st.number_input("Enter strike (USD): ")#,value=c.strikes[0])
        c.set_strike(strike)
        st.write("Option Type:", c.Option_type)
        st.write("Option price (USD):", c.price)
        st.write("Underlying price (USD):", c.underlying.price)
        st.write("Delta:", round(c.delta(), 4))
        st.write("Gamma:", round(c.gamma(), 4))
        st.write("Theta:", np.round(c.theta(), 4)) 
        st.write("Vega:", round(c.vega(), 4))
        st.write("Rho:", round(c.rho(), 4))
        st.write("Implied Vol.:", round(c.implied_volatility(), 4))
    else:
        #exp = datetime.datetime.strptime(expiry, "%Y-%m-%d").date()
        #d, m, y = exp.day, exp.month, exp.year
        #st.write("symbol:", symbol)
        #st.write("expiry (YYYY-MM-DD):", expiry)
        #p = ws.Put(symbol, d, m, y)
        #st.write("strikes (USD):", p.strikes)
        #strike = st.number_input("Enter strike (USD): ",value=p.strikes[0])
        p.set_strike(strike)
        st.write("Option Type:", p.Option_type)
        st.write("Option price (USD):", p.price)
        st.write("Underlying price (USD):", p.underlying.price)
        st.write("Delta:", round(p.delta(), 4))
        st.write("Gamma:", round(p.gamma(), 4))
        st.write("Theta:", np.round(p.theta(), 4))
        st.write("Vega:", round(p.vega(), 4))
        st.write("Rho:", round(p.rho(), 4))
        st.write("Implied Vol.:", round(p.implied_volatility(), 4))
    #optiontype = st.text_input("Enter the type of Option, Call or Put", value="Call")
    #if optiontype=="call":
    #greeks(symbol, expiry, "call")
    #greeks(symbol, expiry, "put")
#if __name__ == "__main__":
#main()
st.image("https://github.com/YWCo/logo/blob/main/YellowWolf.jpg?raw=true")
