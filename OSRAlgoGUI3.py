import pandas as pd
import streamlit as st


st.set_page_config(page_title="Options Strategy Algo",
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

st.markdown('<h1 style="text-align: center;">Options Strategy Design Algorithm</h1>', unsafe_allow_html=True)


questions = {
    "Question 1 - Select sentiment:": {
        "1": "Bearish (security will move down considerably).",
        "2": "Bearish/Neutral (security will move down moderately).",
        "3": "Neutral (security will remain near a certain price).",
        "4": "Bullish/Neutral (security will move up moderately).",
        "5": "Bullish (security will move up considerably).",
        "6": "Not Sure",
    },
    "Question 2 - Select the account type and requirements:": {
        "1": "I have Cash.",
        "2": "I have Shares.",
        "3": "I have Margin.",
        "4": "I have Cash and Shares.",
        "5": "I have Cash and Margin.",
        "6": "I have Shares and Margin.",
        "7": "I have Cash, Shares and Margin.",
    },
    "Question 3 - Select the type of strategy you are looking for:": {
        "1": "One Leg Strategy.",
        "2": "Two Leg Strategy.",
        "3": "Three Leg Strategy.",
        "4": "Four Leg Strategy.",
        "5": "Any.",
    },
    "Question 4 - How will you be affected by the passage of time?": {
        "1": "Time Decay Is My Friend.",
        "2": "Time Decay Is My Enemy.",
        "3": "Neutral.",
        "4": "N/A",
    },
    "Question 5 - What are your expectations on volatility?": {
        "1": "Volatility Increase.",
        "2": "Volatility Decrease.",
        "3": "Neutral.",
    },
    "Question 6 - Do you have any specific price target?": {
        "1": "Yes",
        "2": "No",
    },
    "Question 7 - Do you have any specific date target?": {
        "1": "Yes",
        "2": "No",
    },
    }
replies_text=[]
replies_number=[]
j=0
questions_df=pd.DataFrame(questions).fillna("")
questions_list=list(questions_df.columns)
st.subheader("Please answer the following questions:")
for i in range(len(questions_list)):
    st.text(questions_list[i])
    a=st.selectbox("Select your choice:",questions_df.iloc[:,i],key=i,label_visibility="collapsed")
    b=questions_df.index[questions_df[questions_list[i]]==a].astype(int)
    replies_text.append(a)
    replies_number.append(b)

sentiment=replies_number[0]
requirements=replies_number[1]
strategy_type=replies_number[2]
time_effect=replies_number[3]
volatility_expectations=replies_number[4]
price_target=replies_number[5]
date_target=replies_number[6]

st.markdown("---")
st.subheader("Answers are:")
for a in range(len(replies_text)):
    st.text (replies_text[a])
st.markdown("---")

if st.button('Submit',help="Submit answers to the 7 questions to get optimal strategy"):
    st.subheader("Optimal strategy:")
    if sentiment==5 and requirements==1 and strategy_type==1 and time_effect==2 and volatility_expectations==1 and price_target==2 and date_target==2:
        st.text("1- Strategy Name: Long Call")
    elif sentiment==1 and requirements==1 and strategy_type==1 and time_effect==2 and volatility_expectations==1 and price_target==2 and date_target==2:
        st.text("2- Strategy Name: Long Put")
    elif sentiment==2 and requirements==3 and strategy_type==1 and time_effect==1 and volatility_expectations==2 and price_target==2 and date_target==2:
        st.text("3- Strategy Name: Short Naked Call")
    elif sentiment==2 and requirements==3 and strategy_type==1 and time_effect==1 and volatility_expectations==2 and price_target==2 and date_target==2:
        st.text("4- Strategy Name: Short Naked Put")
    elif sentiment==4 and requirements==3 and strategy_type==1 and time_effect==1 and volatility_expectations==2 and price_target==2 and date_target==2:
        st.text("5- Strategy Name: Cash Secured Put")
    elif sentiment==2 and requirements==2 and strategy_type==1 and time_effect==1 and volatility_expectations==2 and price_target==1 and date_target==2:
        st.text("6- Strategy Name: Sell Covered Call")
    elif sentiment==2 and requirements==1 and strategy_type==1 and time_effect==2 and volatility_expectations==1 and price_target==2 and date_target==2:
        st.text("7- Strategy Name: Buy Protective Put")
    elif sentiment==3 and requirements==4 and strategy_type==1 and time_effect==3 and volatility_expectations==3 and price_target==1 and date_target==2:
        st.text("8- Strategy Name: Collar")
    elif sentiment==4 and requirements==4 and strategy_type==2 and time_effect==1 and volatility_expectations==3 and price_target==1 and date_target==2:
        st.text("9- Strategy Name: Fig Leaf")
    elif sentiment==5 and requirements==4 and strategy_type==2 and time_effect==3 and volatility_expectations==3 and price_target==2 and date_target==2:
        st.text("10- Strategy Name: Long Call Spread")
    elif sentiment==1 and requirements==5 and strategy_type==2 and time_effect==3 and volatility_expectations==3 and price_target==2 and date_target==2:
        st.text("11-Strategy Name: Long Put Spread")
    elif sentiment==2 and requirements==4 and strategy_type==2 and time_effect==1 and volatility_expectations==3 and price_target==2 and date_target==2:
        st.text("12- Strategy Name: Short Call Spread")
    elif sentiment==4 and requirements==5 and strategy_type==2 and time_effect==1 and volatility_expectations==3 and price_target==2 and date_target==2:
        st.text("13- Strategy Name: Short Put Spread")
    elif sentiment==3 and requirements==1 and strategy_type==2 and time_effect==2 and volatility_expectations==1 and price_target==2 and date_target==2:
        st.text("14- Strategy Name: Long Straddle")
    elif sentiment==3 and requirements==6 and strategy_type==2 and time_effect==1 and volatility_expectations==2 and price_target==2 and date_target==2:
        st.text("15- Strategy Name: Short Straddle")
    elif sentiment==3 and requirements==1 and strategy_type==2 and time_effect==2 and volatility_expectations==1 and price_target==1 and date_target==1:
        st.text("16- Strategy Name: Long Strangle")
    elif sentiment==3 and requirements==6 and strategy_type==2 and time_effect==1 and volatility_expectations==2 and price_target==1 and date_target==1:
        st.text("17- Strategy Name: Short Strangle")
    elif sentiment==5 and requirements==5 and strategy_type==2 and time_effect==3 and volatility_expectations==3 and price_target==2 and date_target==2:
        st.text("18- Strategy Name: Long Combination")
    elif sentiment==1 and requirements==4 and strategy_type==2 and time_effect==3 and volatility_expectations==3 and price_target==2 and date_target==2:
        st.text("19- Strategy Name: Short Combination")
    elif sentiment==4 and requirements==4 and strategy_type==2 and time_effect==1 and volatility_expectations==2 and price_target==1 and date_target==2:
        st.text("20- Strategy Name: Front Spread With Calls")
    elif sentiment==2 and requirements==5 and strategy_type==2 and time_effect==1 and volatility_expectations==2 and price_target==1 and date_target==2:
        st.text("21- Strategy Name: Front Spread With Puts")
    elif sentiment==5 and requirements==4 and strategy_type==2 and time_effect==3 and volatility_expectations==1 and price_target==1 and date_target==2:
        st.text("22- Strategy Name: Back Spread With Calls")
    elif sentiment==1 and requirements==5 and strategy_type==2 and time_effect==3 and volatility_expectations==1 and price_target==1 and date_target==2:
        st.text("23- Strategy Name: Back Spread With Puts")
    elif sentiment==3 and requirements==4 and strategy_type==2 and time_effect==1 and volatility_expectations==3 and price_target==2 and date_target==1:
        st.text("24- Strategy Name: Long Calendar Spread with calls")
    elif sentiment==3 and requirements==5 and strategy_type==2 and time_effect==1 and volatility_expectations==3 and price_target==2 and date_target==1:
        st.text("25- Strategy Name: Long Calendar Spread with Puts")
    elif sentiment==2 and requirements==4 and strategy_type==2 and time_effect==1 and volatility_expectations==3 and price_target==2 and date_target==1:
        st.text("26- Strategy Name: Diagonal Spread With Calls")
    elif sentiment==4 and requirements==5 and strategy_type==2 and time_effect==1 and volatility_expectations==1 and price_target==2 and date_target==1:
        st.text("27- Strategy Name: Diagonal Spread With Puts")
    elif sentiment==3 and requirements==4 and strategy_type==3 and time_effect==1 and volatility_expectations==3 and price_target==1 and date_target==2:
        st.text("28- Strategy Name: Long Butterfly Spread With Calls")
    elif sentiment==3 and requirements==5 and strategy_type==3 and time_effect==1 and volatility_expectations==3 and price_target==1 and date_target==2:
        st.text("29- Strategy Name: Long Butterfly Spread With Puts")
    elif sentiment==3 and requirements==7 and strategy_type==3 and time_effect==1 and volatility_expectations==3 and price_target==2 and date_target==2:
        st.text("30- Strategy Name: Iron Butterfly")
    elif sentiment==4 and requirements==4 and strategy_type==3 and time_effect==1 and volatility_expectations==3 and price_target==1 and date_target==2:
        st.text("31- Strategy Name: Skip Strike Butterfly With Calls")
    elif sentiment==4 and requirements==5 and strategy_type==3 and time_effect==1 and volatility_expectations==3 and price_target==1 and date_target==2:
        st.text("32- Strategy Name: Skip Strike Butterfly With Puts")
    elif sentiment==5 and requirements==4 and strategy_type==3 and time_effect==3 and volatility_expectations==1 and price_target==2 and date_target==2:
        st.text("33- Strategy Name: Inverse Skip Strike Butterfly With Calls")
    elif sentiment==1 and requirements==5 and strategy_type==3 and time_effect==3 and volatility_expectations==1 and price_target==2 and date_target==2:
        st.text("34- Strategy Name: Inverse Skip Strike Butterfly With Puts")
    elif sentiment==4 and requirements==4 and strategy_type==3 and time_effect==1 and volatility_expectations==3 and price_target==1 and date_target==2:
        st.text("35- Strategy Name: Christmas Tree Butterfly With Calls")
    elif sentiment==2 and requirements==5 and strategy_type==3 and time_effect==1 and volatility_expectations==3 and price_target==1 and date_target==2:
        st.text("36- Strategy Name: Christmas Tree Butterfly With Puts")
    elif sentiment==3 and requirements==4 and strategy_type==4 and time_effect==1 and volatility_expectations==3 and price_target==1 and date_target==1:
        st.text("37- Strategy Name: Long Condor Spread With Calls")
    elif sentiment==3 and requirements==5 and strategy_type==4 and time_effect==1 and volatility_expectations==3 and price_target==1 and date_target==1:
        st.text("38- Strategy Name: Long Condor Spread With Puts")
    elif sentiment==3 and requirements==7 and strategy_type==4 and time_effect==1 and volatility_expectations==3 and price_target==1 and date_target==1:
        st.text("39- Strategy Name: Iron Condor")
    elif sentiment==3 and requirements==7 and strategy_type==4 and time_effect==1 and volatility_expectations==3 and price_target==1 and date_target==1:
        st.text("40- Strategy Name: Double Diagonal")
    else:st.text("No strategy available for selected criteria.")

#else:
strategies_dict = {
        "Long Call": {
            "Sentiment": "Bullish",
            "Requirements": "Cash",
            "Strategy Type": "One Leg Play",
            "Time Effect": "Time Decay Is My Enemy",
            "Volatility Expectations": "Volatility Increase",
            "Specific Price Target": "No",
            "Specific Date Target": "No",
        },
        "Long Put": {
            "Sentiment": "Bearish",
            "Requirements": "Cash",
            "Strategy Type": "One Leg Play",
            "Time Effect": "Time Decay Is My Enemy",
            "Volatility Expectations": "Volatility Increase",
            "Specific Price Target": "No",
            "Specific Date Target": "No",
        },
        "Short Naked Call": {
            "Sentiment": "Bearish/Neutral",
            "Requirements": "Margin",
            "Strategy Type": "One Leg Play",
            "Time Effect": "Time Decay Is My Friend",
            "Volatility Expectations": "Volatility Decrease",
            "Specific Price Target": "No",
            "Specific Date Target": "No",
        },
        "Short Naked Put": {
            "Sentiment": "Bearish/Neutral",
            "Requirements": "Margin",
            "Strategy Type": "One Leg Play",
            "Time Effect": "Time Decay Is My Friend",
            "Volatility Expectations": "Volatility Decrease",
            "Specific Price Target": "No",
            "Specific Date Target": "No",
        },
        "Cash Secured Put": {
            "Sentiment": "Bullish/Neutral",
            "Requirements": "Margin",
            "Strategy Type": "One Leg Play",
            "Time Effect": "Time Decay Is My Friend",
            "Volatility Expectations": "Volatility Decrease",
            "Specific Price Target": "No",
            "Specific Date Target": "No",
        },
        "Sell Covered Call": {
            "Sentiment": "Bearish/Neutral",
            "Requirements": "Shares",
            "Strategy Type": "One Leg Play",
            "Time Effect": "Time Decay Is My Friend",
            "Volatility Expectations": "Volatility Decrease",
            "Specific Price Target": "Yes",
            "Specific Date Target": "No",
        },
        "Buy Protective Put": {
            "Sentiment": "Bearish/Neutral",
            "Requirements": "Shares - Cash",
            "Strategy Type": "One Leg Play",
            "Time Effect": "Time Decay Is My Enemy",
            "Volatility Expectations": "Volatility Increase",
            "Specific Price Target": "No",
            "Specific Date Target": "No",
        },
        "Collar": {
            "Sentiment": "Neutral",
            "Requirements": "Shares - Cash ",
            "Strategy Type": "One Leg Play",
            "Time Effect": "Neutral",
            "Volatility Expectations": "Neutral",
            "Specific Price Target": "Yes",
            "Specific Date Target": "No",
        },
        "Fig Leaf": {
            "Sentiment": "Bullish/Neutral",
            "Requirements": "Shares - Cash",
            "Strategy Type": "Two Leg Play",
            "Time Effect": "Time Decay Is My Friend",
            "Volatility Expectations": "Neutral",
            "Specific Price Target": "Yes",
            "Specific Date Target": "No",
        },
        "Long Call Spread": {
            "Sentiment": "Bullish",
            "Requirements": "Shares - Cash ",
            "Strategy Type": "Two Leg Play",
            "Time Effect": "Neutral",
            "Volatility Expectations": "Neutral",
            "Specific Price Target": "No",
            "Specific Date Target": "No",
        },
        "Long Put Spread": {
            "Sentiment": "Bearish",
            "Requirements": "Margin - Cash",
            "Strategy Type": "Two Leg Play",
            "Time Effect": "Neutral",
            "Volatility Expectations": "Neutral",
            "Specific Price Target": "No",
            "Specific Date Target": "No",
        },
        "Short Call Spread": {
            "Sentiment": "Bearish/Neutral",
            "Requirements": "Shares - Cash",
            "Strategy Type": "Two Leg Play",
            "Time Effect": "Time Decay Is My Friend",
            "Volatility Expectations": "Neutral",
            "Specific Price Target": "No",
            "Specific Date Target": "No",
        },
        "Short Put Spread": {
            "Sentiment": "Bullish/Neutral",
            "Requirements": "Margin - Cash",
            "Strategy Type": "Two Leg Play",
            "Time Effect": "Time Decay Is My Friend",
            "Volatility Expectations": "Neutral",
            "Specific Price Target": "No",
            "Specific Date Target": "No",
        },
        "Long Straddle": {
            "Sentiment": "Neutral",
            "Requirements": "Cash",
            "Strategy Type": "Two Leg Play",
            "Time Effect": "Time Decay Is My Enemy",
            "Volatility Expectations": "Volatility Increase",
            "Specific Price Target": "No",
            "Specific Date Target": "No",
        },
        "Short Straddle": {
            "Sentiment": "Neutral",
            "Requirements": "Margin - Shares",
            "Strategy Type": "Two Leg Play",
            "Time Effect": "Time Decay Is My Friend",
            "Volatility Expectations": "Volatility Decrease",
            "Specific Price Target": "No",
            "Specific Date Target": "No",
        },
        "Long Strangle": {
            "Sentiment": "Neutral",
            "Requirements": "Cash",
            "Strategy Type": "Two Leg Play",
            "Time Effect": "Time Decay Is My Enemy",
            "Volatility Expectations": "Volatility Increase",
            "Specific Price Target": "Yes",
            "Specific Date Target": "Yes",
        },
        "Short Strangle": {
            "Sentiment": "Neutral",
            "Requirements": "Margin - Shares",
            "Strategy Type": "Two Leg Play",
            "Time Effect": "Time Decay Is My Friend",
            "Volatility Expectations": "Volatility Decrease",
            "Specific Price Target": "Yes",
            "Specific Date Target": "Yes",
        },
        "Long Combination": {
            "Sentiment": "Bullish",
            "Requirements": "Margin - Cash",
            "Strategy Type": "Two Leg Play",
            "Time Effect": "Neutral",
            "Volatility Expectations": "Neutral",
            "Specific Price Target": "No",
            "Specific Date Target": "No",
        },
        "Short Combination": {
            "Sentiment": "Bearish",
            "Requirements": "Shares - Cash",
            "Strategy Type": "Two Leg Play",
            "Time Effect": "Neutral",
            "Volatility Expectations": "Neutral",
            "Specific Price Target": "No",
            "Specific Date Target": "No",
        },
        "Front Spread With Calls": {
            "Sentiment": "Bullish/Neutral",
            "Requirements": "Shares - Cash",
            "Strategy Type": "Two Leg Play",
            "Time Effect": "Time Decay Is My Friend",
            "Volatility Expectations": "Volatility Decrease",
            "Specific Price Target": "Yes",
            "Specific Date Target": "No",
        },
        "Front Spread With Puts": {
            "Sentiment": "Bearish/Neutral",
            "Requirements": "Margin - Cash",
            "Strategy Type": "Two Leg Play",
            "Time Effect": "Time Decay Is My Friend",
            "Volatility Expectations": "Volatility Decrease",
            "Specific Price Target": "Yes",
            "Specific Date Target": "No",
        },
        "Back Spread With Calls": {
            "Sentiment": "Bullish",
            "Requirements": "Shares - Cash",
            "Strategy Type": "Two Leg Play",
            "Time Effect": "Neutral",
            "Volatility Expectations": "Volatility Increase",
            "Specific Price Target": "Yes",
            "Specific Date Target": "No",
        },
        "Back Spread With Puts": {
            "Sentiment": "Bearish",
            "Requirements": "Margin - Cash",
            "Strategy Type": "Two Leg Play",
            "Time Effect": "Neutral",
            "Volatility Expectations": "Volatility Increase",
            "Specific Price Target": "Yes",
            "Specific Date Target": "No",
        },
        "Long Calendar Spread with calls": {
            "Sentiment": "Neutral",
            "Requirements": "Shares - Cash",
            "Strategy Type": "Two Leg Play",
            "Time Effect": "Time Decay Is My Friend",
            "Volatility Expectations": "Neutral",
            "Specific Price Target": "No",
            "Specific Date Target": "Yes",
        },
        "Long Calendar Spread with Puts": {
            "Sentiment": "Neutral",
            "Requirements": "Margin - Cash",
            "Strategy Type": "Two Leg Play",
            "Time Effect": "Time Decay Is My Friend",
            "Volatility Expectations": "Neutral",
            "Specific Price Target": "No",
            "Specific Date Target": "Yes",
        },
        "Diagonal Spread With Calls": {
            "Sentiment": "Bearish/Neutral",
            "Requirements": "Shares - Cash",
            "Strategy Type": "Two Leg Play",
            "Time Effect": "Time Decay Is My Friend",
            "Volatility Expectations": "Volatility Increase",
            "Specific Price Target": "No",
            "Specific Date Target": "Yes",
        },
        "Diagonal Spread With Puts": {
            "Sentiment": "Bullish/Neutral",
            "Requirements": "Margin - Cash",
            "Strategy Type": "Two Leg Play",
            "Time Effect": "Time Decay Is My Friend",
            "Volatility Expectations": "Volatility Increase",
            "Specific Price Target": "No",
            "Specific Date Target": "Yes",
        },
        "Long Butterfly Spread With Calls": {
            "Sentiment": "Neutral",
            "Requirements": "Shares - Cash",
            "Strategy Type": "Three Leg Play",
            "Time Effect": "Time Decay Is My Friend",
            "Volatility Expectations": "Neutral",
            "Specific Price Target": "Yes",
            "Specific Date Target": "No",
        },
        "Long Butterfly Spread With Puts": {
            "Sentiment": "Neutral",
            "Requirements": "Margin - Cash",
            "Strategy Type": "Three Leg Play",
            "Time Effect": "Time Decay Is My Friend",
            "Volatility Expectations": "Neutral",
            "Specific Price Target": "Yes",
            "Specific Date Target": "No",
        },
        "Iron Butterfly": {
            "Sentiment": "Neutral",
            "Requirements": "Margin - Shares - Cash",
            "Strategy Type": "Three Leg Play",
            "Time Effect": "Time Decay Is My Friend",
            "Volatility Expectations": "Neutral",
            "Specific Price Target": "No",
            "Specific Date Target": "No",
        },
        "Skip Strike Butterfly With Calls": {
            "Sentiment": "Bullish/Neutral",
            "Requirements": "Shares - Cash",
            "Strategy Type": "Three Leg Play",
            "Time Effect": "Time Decay Is My Friend",
            "Volatility Expectations": "Neutral",
            "Specific Price Target": "Yes",
            "Specific Date Target": "No",
        },
        "Skip Strike Butterfly With Puts": {
            "Sentiment": "Bearish/Neutral",
            "Requirements": "Margin - Cash",
            "Strategy Type": "Three Leg Play",
            "Time Effect": "Time Decay Is My Friend",
            "Volatility Expectations": "Neutral",
            "Specific Price Target": "Yes",
            "Specific Date Target": "No",
        },
        "Inverse Skip Strike Butterfly With Calls": {
            "Sentiment": "Bullish",
            "Requirements": "Shares - Cash",
            "Strategy Type": "Three Leg Play",
            "Time Effect": "Neutral",
            "Volatility Expectations": "Volatility Increase",
            "Specific Price Target": "No",
            "Specific Date Target": "No",
        },
        "Inverse Skip Strike Butterfly With Puts": {
            "Sentiment": "Bearish",
            "Requirements": "Margin - Cash",
            "Strategy Type": "Three Leg Play",
            "Time Effect": "Neutral",
            "Volatility Expectations": "Volatility Increase",
            "Specific Price Target": "No",
            "Specific Date Target": "No",
        },
        "Christmas Tree Butterfly With Calls": {
            "Sentiment": "Bullish/Neutral",
            "Requirements": "Shares - Cash",
            "Strategy Type": "Three Leg Play",
            "Time Effect": "Time Decay Is My Friend",
            "Volatility Expectations": "Neutral",
            "Specific Price Target": "Yes",
            "Specific Date Target": "No",
        },
        "Christmas Tree Butterfly With Puts": {
            "Sentiment": "Bearish/Neutral",
            "Requirements": "Margin - Cash",
            "Strategy Type": "Three Leg Play",
            "Time Effect": "Time Decay Is My Friend",
            "Volatility Expectations": "Neutral",
            "Specific Price Target": "Yes",
            "Specific Date Target": "No",
        },
        "Long Condor Spread With Calls": {
            "Sentiment": "Neutral",
            "Requirements": "Shares - Cash",
            "Strategy Type": "Four Leg Play",
            "Time Effect": "Time Decay Is My Friend",
            "Volatility Expectations": "Neutral",
            "Specific Price Target": "Yes",
            "Specific Date Target": "Yes",
        },
        "Long Condor Spread With Puts": {
            "Sentiment": "Neutral",
            "Requirements": "Margin - Cash",
            "Strategy Type": "Four Leg Play",
            "Time Effect": "Time Decay Is My Friend",
            "Volatility Expectations": "Neutral",
            "Specific Price Target": "Yes",
            "Specific Date Target": "Yes",
        },
        "Iron Condor": {
            "Sentiment": "Neutral",
            "Requirements": "Margin - Shares - Cash",
            "Strategy Type": "Four Leg Play",
            "Time Effect": "Time Decay Is My Friend",
            "Volatility Expectations": "Neutral",
            "Specific Price Target": "Yes",
            "Specific Date Target": "Yes",
        },
        "Double Diagonal": {
            "Sentiment": "Neutral",
            "Requirements": "Margin - Shares - Cash",
            "Strategy Type": "Four Leg Play",
            "Time Effect": "Time Decay Is My Friend",
            "Volatility Expectations": "Neutral",
            "Specific Price Target": "Yes",
            "Specific Date Target": "Yes",
        },
    }
#pass to DF
strats_df=pd.DataFrame.from_dict(strategies_dict,orient="index")

#conditions columns to list
conditions_list=strats_df.columns.to_list()

#strategies rows in first column to list
strategies_list=strats_df.index.to_list()

#strats_df[strats_df["Sentiment"]=="Bullish"]

#to see strategies list and its conditions
#st.table(strategies_list)
st.markdown("---")
st.subheader("Full strategy viewer")
c=st.selectbox("Select strategy to see all conditions:",strategies_list)
sele_strat=c.title()
st.table(strats_df.loc[[sele_strat]])

#to see condition list and its conditions
#st.text(conditions_list)
st.markdown("---")
st.subheader("Strategy filter by criteria")
d=st.selectbox("Get all strategies for selected condition:",conditions_list)
sele_cond=d.title()
e=st.radio("Select condition alternative:",strats_df[sele_cond].unique())#.to_string(index=False))
sele_cond_option=e.title()
#see stratgies that meet condition selected
st.table(strats_df[strats_df[sele_cond]==sele_cond_option])

col1, col2, col3 = st.columns(3)

with col1:
    st.write(' ')

with col2:
    st.image("https://github.com/YWCo/logo/blob/main/YellowWolf.jpg?raw=true")

with col3:
    st.write(' ')


























        


