import  streamlit as st
import requests
import pandas as pd


hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

st.header("Fixed Income Algorithm")

option=st.sidebar.selectbox(

    "Select Fixed Income Trasury:",
    ("Bill","Note","Bond","Highest Yield Overall"),index=3
)
st.subheader(option)
beg_entry = st.date_input('Enter a maturity range start date in YYYY-MM-DD format: ')
end_entry = st.date_input('Enter a maturity range end date in YYYY-MM-DD format: ')
    
if option=="Bill":
    api_call="https://www.treasurydirect.gov/TA_WS/securities/auctioned?format=json&type="+str(option)
    api_return=requests.get(api_call)
    data = pd.DataFrame(api_return.json())
    data=data.sort_values(by=['maturityDate'])
    data=data.reset_index(drop=True)
    reduced_data=data[["cusip","securityType","securityTerm","maturityDate","averageMedianDiscountRate","highPrice"]]
    reduced_data=reduced_data.rename(columns = {"averageMedianDiscountRate":"YTM","highPrice":"Price"})
    #st.text(reduced_data.sort_values("maturityDate", ascending=False).to_string())
    #select range of maturity
    #beg_entry = st.date_input('Enter a maturity range start date in YYYY-MM-DD format: ')
    #end_entry = st.date_input('Enter a maturity range end date in YYYY-MM-DD format: ')
    #sort fd by maturity date
    capped=reduced_data[reduced_data["maturityDate"]>str(beg_entry)]
    capped=capped[reduced_data["maturityDate"]<str(end_entry)]
    #st.text("The instruments maturing in the selected range are: ")
    #print(capped)
    topn=st.number_input("Select how many intruments to list, sorted by descending yields: ",value=10, step=1)
    st.text("the highest top "+str(topn)+" yield alternatives are: ")
    st.dataframe(capped.sort_values("YTM", ascending=False)[:int(topn)])



elif option=="Note" or option=="Bond":
    api_call="https://www.treasurydirect.gov/TA_WS/securities/auctioned?format=json&type="+str(option)
    api_return=requests.get(api_call)
    data = pd.DataFrame(api_return.json())
    data=data.sort_values(by=['maturityDate'])
    data=data.reset_index(drop=True)
    reduced_data=data[["cusip","securityType","securityTerm","maturityDate","interestRate","averageMedianYield","highPrice","interestPaymentFrequency"]]
    reduced_data=reduced_data.rename(columns = {"averageMedianYield":"YTM","highPrice":"Price"})
    #print(reduced_data.sort_values("maturityDate", ascending=False).to_string())
    #beg_entry = st.date_input('Enter a range start date in YYYY-MM-DD format: ')
    #end_entry = st.date_input('Enter a range end date in YYYY-MM-DD format: ')
    #sort by maturity date
    capped=reduced_data[reduced_data["maturityDate"]>str(beg_entry)]
    capped=capped[reduced_data["maturityDate"]<str(end_entry)]
    #print("The instruments maturing in the selected range are: ")
    #print(capped)
    topn=st.number_input("Select how many intruments to list, sorted by descending yields: ",value=10, step=1)
    st.text("the highest top "+str(topn)+" yield alternatives are: ")
    st.dataframe(capped.sort_values("YTM", ascending=False)[:int(topn)])

else:
    api_call="https://www.treasurydirect.gov/TA_WS/securities/auctioned?format=json&type=Bill"
    api_return=requests.get(api_call)
    data = pd.DataFrame(api_return.json())
    data=data.sort_values(by=['maturityDate'])
    data=data.reset_index(drop=True)
    reduced_data=data[["cusip","securityType","securityTerm","maturityDate","averageMedianDiscountRate","highPrice"]]
    reduced_data_bill=reduced_data.rename(columns = {"averageMedianDiscountRate":"YTM","highPrice":"Price"})
    reduced_data_bill.insert(reduced_data_bill.columns.get_loc("YTM"), "interestRate", 0)
    
    #st.dataframe(reduced_data_bill)

    api_call="https://www.treasurydirect.gov/TA_WS/securities/auctioned?format=json&type=Note"
    api_return=requests.get(api_call)
    data = pd.DataFrame(api_return.json())
    data=data.sort_values(by=['maturityDate'])
    data=data.reset_index(drop=True)
    reduced_data=data[["cusip","securityType","securityTerm","maturityDate","interestRate","averageMedianYield","highPrice"]]
    reduced_data_note=reduced_data.rename(columns = {"averageMedianYield":"YTM","highPrice":"Price"})
    #st.dataframe(reduced_data_note)

    api_call="https://www.treasurydirect.gov/TA_WS/securities/auctioned?format=json&type=Bond"
    api_return=requests.get(api_call)
    data = pd.DataFrame(api_return.json())
    data=data.sort_values(by=['maturityDate'])
    data=data.reset_index(drop=True)
    reduced_data=data[["cusip","securityType","securityTerm","maturityDate","interestRate","averageMedianYield","highPrice"]]
    reduced_data_bond=reduced_data.rename(columns = {"averageMedianYield":"YTM","highPrice":"Price"})
    #st.dataframe(reduced_data_bond)
    #st.text(reduced_data.sort_values("maturityDate", ascending=False).to_string())
    #select range of maturity
    #beg_entry = st.date_input('Enter a maturity range start date in YYYY-MM-DD format: ')
    #end_entry = st.date_input('Enter a maturity range end date in YYYY-MM-DD format: ')
    #sort fd by maturity date
    reduced_data = pd.concat([reduced_data_bill, reduced_data_note, reduced_data_bond], ignore_index=True)
    capped=reduced_data[reduced_data["maturityDate"]>str(beg_entry)]
    capped=capped[capped["maturityDate"]<str(end_entry)]
    #st.text("The instruments maturing in the selected range are: ")
    #print(capped)
    topn=st.number_input("Select how many intruments to list, sorted by descending yields: ",value=10, step=1)
    st.text("the highest top "+str(topn)+" yield alternatives are: ")
    st.dataframe(capped.sort_values("YTM", ascending=False)[:int(topn)],use_container_width=True)

    



st.image("https://github.com/YWCo/logo/blob/main/YellowWolf.jpg?raw=true")