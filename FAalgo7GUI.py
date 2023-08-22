import streamlit as st
import fundamentalanalysis as fa
import pandas as pd
import matplotlib.pyplot as plt
from financetoolkit import Toolkit
#import cufflinks as cf
import plotly.express as px
import datetime

st.set_page_config(page_title="Fundamental Analysis Algo",
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





st.header("Fundamental Analysis Algorithm")
api_key = 'e1f7367c932b9ff3949e05adf400970c'  

col1, col2= st.columns(2)
with col1:
    ticker_one = st.text_input("Enter the ticker symbol (e.g., 'MSFT'): ",value="MSFT")
    instru=[]
    instru.append(ticker_one)
    #st.write(instru[0])

    date=str(st.date_input("Enter start date for analysis:",datetime.date(2020, 1, 1)))
    companies=Toolkit(instru, api_key, start_date=date)
    

    #companies=Toolkit(["AAPL", "MSFT", "GOOGL", "AMZN"], api_key, start_date="2018-01-01")

with col2:
    st.image("https://financialmodelingprep.com/image-stock/"+ticker_one+".png",width=210)
 

col12, col22= st.columns(2)
with col12:
   st.subheader("Quote")
   st.dataframe(fa.quote(ticker_one, api_key),height=350)
#chart
with col22:
    st.subheader("Chart")
    #st.checkbox("Add benchmarks to the graph:")
    fig=px.line(companies.get_historical_data()["Adj Close"])
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(showgrid=False, zeroline=False)
    st.plotly_chart(fig, use_container_width=False)



# Display available fundamental data options
fund = [
    "Profile",
    "Quote",
    "Balance Sheet",
    "Income Statement",
    "Cash Flow Statement",
    "Profitability Ratios", 
    "Efficiency Ratios",
    "Solvency Ratios",
    "Liquidity Ratios",
    "Valuation Ratios",
    "Du Pont Analysis",
    "Financial Statement Growth",
    "Stock Data",
    "Dividends",
    "Ratings",
    "DCF Valuation",
    "Enterprise Value",
    "Bankruptcy Scores"
]


fax = st.sidebar.multiselect("Select fundamental data to visualize:", fund,default=["Profitability Ratios", 
    "Efficiency Ratios",
    "Solvency Ratios",
    "Liquidity Ratios",
    "Valuation Ratios"])
time_frame=st.sidebar.selectbox("Select timeframe:", ["quarter","annual"],index=1)

test = time_frame=="quarter"
companies=Toolkit(instru, api_key, start_date=date,quarterly=test)


for i in range(len(fax)): 
    if fax[i] in ["Stock Data", "Dividends"]:

        if fax[i] == "Stock Data":
                out = fa.stock_data(ticker_one,period="1d",start=date)
        if fax[i] == "Dividends":
                out = fa.stock_dividend(ticker_one,api_key,begin=date)
        st.write(out)

            # Display the plot using Streamlit
        fig, ax = plt.subplots(figsize=(10, 6))
        out.plot(ax=ax)
        st.pyplot(fig)

    elif fax[i] == "Altman Z Score":
        year = st.text_input("For what year do you want to estimate the Altman Z Score (YYYY): ")

        if year:
            key_metrics = fa.key_metrics(ticker_one, api_key, period="annual")
            balance_sheet = fa.balance_sheet_statement(ticker_one, api_key, period="annual")
            income_statement = fa.income_statement(ticker_one, api_key, period="annual")
            enterprise_value = fa.enterprise(ticker_one, api_key,period="annual")

            wc = key_metrics.at['workingCapital', year]
            ta = balance_sheet.at['totalAssets', year]
            tl = balance_sheet.at['totalLiabilities', year]
            re = balance_sheet.at['retainedEarnings', year]
            ebitda = income_statement.at['ebitda', year]
            depamo = income_statement.at['depreciationAndAmortization', year]
            rev = income_statement.at['revenue', year]
            mcap = key_metrics.at['marketCap', year]

            a = wc / ta
            b = re / ta
            c = (ebitda - depamo) / ta
            d = mcap / tl
            e = rev / ta

            altz = 1.2 * a + 1.4 * b + 3.3 * c + 0.6 * d + 1.0 * e

            st.write("The Altman Z Score is: ", round(altz, 2))
            st.write("A score below 1.8 means it's likely the company is headed for bankruptcy, while companies with scores above 3 are not likely to go bankrupt. Investors can use Altman Z-scores to determine whether they should buy or sell a stock if they're concerned about the company's underlying financial strength. Investors may consider purchasing a stock if its Altman Z-Score value is closer to 3 and selling or shorting a stock if the value is closer to 1.8")

    else:
        #if time_frame=="quarter":
        limit=6
        #else:limit=6
        #limit=6
        if fax[i] == "Profile":
            st.subheader("Profile")
            out_one = fa.profile(ticker_one, api_key)
        if fax[i] == "Quote":
            st.subheader("Quote")
            out_one = fa.quote(ticker_one, api_key)
        if fax[i] == "Balance Sheet":
            st.subheader("Balance Sheet")
            out_one = fa.balance_sheet_statement(ticker_one, api_key, period=time_frame,limit=limit)
        if fax[i] == "Income Statement":
            st.subheader("Balance Sheet")
            out_one = fa.income_statement(ticker_one, api_key, period=time_frame,limit=limit)
        if fax[i] == "Cash Flow Statement":
            st.subheader("Cash Flow Statement")
            out_one = fa.cash_flow_statement(ticker_one, api_key, period=time_frame,limit=limit)
        if fax[i] == "Key Metrics":
            st.subheader("Key Metrics")
            out_one = fa.key_metrics(ticker_one, api_key, period=time_frame,limit=limit)
        if fax[i] == "Financial Statement Growth":
            st.subheader("Financial Statement Growth")
            out_one = fa.financial_statement_growth(ticker_one, api_key, period=time_frame,limit=limit)
        if fax[i] == "Ratings":
            st.subheader("Ratings")
            out_one = fa.rating(ticker_one, api_key)
        if fax[i] == "DCF Valuation":
            st.subheader("DCF Valuation")
            methodology="""
            Methodology for DCF is:

            Market Cap = Weighted Average Shares Outstanding Diluted * Stock Price

            Enterprise Value NB = Market Cap + Long Term Debt + Short Term Debt

            Equity Value = Enterprise Value NB - Net Debt

            DCF = Equity Value / Weigted Average Shares Outstanding Diluted

            Stock Beta = Monthly price change of stock relative to the monthly price change of the S&P500 (COV(Rs,RM) / VAR(Rm))
            """
            st.text(methodology)
            out_one = fa.discounted_cash_flow(ticker_one, api_key, period=time_frame,limit=limit)
        if fax[i] == "Enterprise Value":
            st.subheader("Enterprise Value")
            out_one = fa.enterprise(ticker_one, api_key,period=time_frame,limit=limit)
        if fax[i] == "Profitability Ratios":
            st.subheader("Profitability Ratios")
            out_one = companies.ratios.collect_profitability_ratios()
        if fax[i] == "Efficiency Ratios":
            st.subheader("Efficiency Ratios")
            out_one = companies.ratios.collect_efficiency_ratios()    
        if fax[i] == "Solvency Ratios":
            st.subheader("Solvency Ratios")
            out_one =  companies.ratios.collect_solvency_ratios()       
        if fax[i] == "Liquidity Ratios":
            st.subheader("Liquidity Ratios")
            out_one =  companies.ratios.collect_liquidity_ratios()   
        if fax[i] == "Valuation Ratios":
            st.subheader("Valuation Ratios")
            out_one =  companies.ratios.collect_valuation_ratios()  
        if fax[i] == "Du Pont Analysis":
            st.subheader("Du Pont Analysis")
            out_one = companies.models.get_dupont_analysis() 
        if fax[i] == "Bankruptcy Scores":
            st.subheader("Bankruptcy Scores")
            url = ("https://financialmodelingprep.com/api/v4/score?symbol="+ticker_one+"&apikey=e1f7367c932b9ff3949e05adf400970c")
            df = pd.read_json(url)
            out_one=df[["symbol","altmanZScore","piotroskiScore"]]
            """
            Altman Z Score: 
            A score below 1.8 means it's likely the company is headed for bankruptcy, while companies with scores above 3 are not likely to go bankrupt.

            Piotroski Score: 
            If a company has a score of 8 or 9, it is considered a good value. If the score adds up to between 0-2 points, the stock is considered weak.
            """

        st.dataframe(out_one,use_container_width=True)

st.write("Thank you for using the FA Algo. Copyright YWC.")


st.image("https://github.com/YWCo/logo/blob/main/YellowWolf.jpg?raw=true")