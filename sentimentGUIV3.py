import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
st.set_page_config(page_title="Sentiment Algorithm",
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

st.markdown("<h1 style='text-align: center; color: black;'>Sentiment Algorithm</h1>", unsafe_allow_html=True)

"""
YWC tracks social media mentions on stocks in real time and their sentiment change. These instruments can be extremely volatile, so do your own due diligence before entering any positions. 
"""
type=["bullish","bearish","all"]
sent_select=st.sidebar.selectbox("Select sentiment to see current trends:", options=type)


data_bullish="https://financialmodelingprep.com/api/v4/social-sentiments/trending?type=bullish&source=stocktwits&apikey=e1f7367c932b9ff3949e05adf400970c"
data_bearish="https://financialmodelingprep.com/api/v4/social-sentiments/trending?type=bearish&source=stocktwits&apikey=e1f7367c932b9ff3949e05adf400970c"
bullish_data=pd.read_json(data_bullish)
bearish_data=pd.read_json(data_bearish)
df_combined=pd.concat( [bullish_data,bearish_data],ignore_index=True)
if sent_select=="bullish":
    col1, col2,col3 = st.columns([0.33,0.34,0.33])
    with col2:
        st.subheader("Bullish sentiment board  :hot_pepper:")
    # Sort the DataFrame by sentiment in descending order
    df_bull = bullish_data.sort_values(by="sentiment", ascending=False)
    num_tickers = st.slider("Select the number of tickers to display:", 1, 40,20)

    # Create a bar graph
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(df_bull["symbol"][:num_tickers], df_bull["sentiment"][:num_tickers], color='green')
    ax.set_xlabel('Ticker')
    ax.set_ylabel('Sentiment')
    ax.set_title('Sentiment by Ticker')
    ax.tick_params(axis='x', rotation=45)
    ax.set_xticks(ax.get_xticks())  # Spacing out x-axis legends

    st.pyplot(fig)

if sent_select=="bearish":
    col1, col2,col3 = st.columns([0.30,0.40,0.30])
    with col2:
        st.subheader("Bearish sentiment board :bear:")
        # Sort the DataFrame by sentiment in descending order
    df_bear = bearish_data.sort_values(by="sentiment", ascending=True)
    num_tickers = st.slider("Select the number of tickers to display:", 1, 40,20)

    # Create a bar graph
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(df_bear["symbol"][:num_tickers], df_bear["sentiment"][:num_tickers], color='red')
    ax.set_xlabel('Ticker')
    ax.set_ylabel('Sentiment')
    ax.set_title('Sentiment by Ticker')
    ax.tick_params(axis='x', rotation=45)
    ax.set_xticks(ax.get_xticks())  # Spacing out x-axis legends
    ax.invert_yaxis()

    st.pyplot(fig)

if sent_select=="all":
    col1, col2,col3 = st.columns([0.35,0.30,0.35])
    with col2:
        st.subheader("Aggregated sentiment")
    # Convert the data to a DataFrame
    #df_combined_sorted = pd.DataFrame(data)
    
    # Sort the DataFrame by sentiment in descending order
    df_combined_sorted = df_combined.sort_values(by="sentiment", ascending=False)
    
    # User input: Quantity of tickers to display
    num_tickers = st.slider("Select the number of tickers to display:", 1,20, 10)
    
    # Split data into bullish and bearish segments
    bullish_df = df_combined_sorted.head(num_tickers)
    bearish_df = df_combined_sorted.tail(num_tickers)

    # Create a bar graph
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Plot bullish bars on the left side
    bullish_ticks = list(bullish_df["symbol"])
    bullish_sentiments = bullish_df["sentiment"]
    ax.bar(bullish_ticks, bullish_sentiments, color='green')
    
    # Plot bearish bars on the right side
    bearish_ticks = list(bearish_df["symbol"])
    bearish_sentiments = bearish_df["sentiment"]
    ax.bar(bearish_ticks, bearish_sentiments, color='red')
    
    ax.set_ylabel('Sentiment')
    ax.set_title('Sentiment by Ticker')
    
    # Set x-tick labels for both segments
    all_ticks = bullish_ticks + bearish_ticks
    ax.set_xticks(range(num_tickers * 2))
    ax.set_xticklabels(all_ticks, rotation=45, ha="right")
    ax.legend(["Bullish", "Bearish"])
    
    st.pyplot(fig)


movers=["bullish movers","bearish movers"]
movers_select=st.sidebar.selectbox("Select movers' sentiment:", options=movers)
df_combined["change"]=df_combined["sentiment"]-df_combined["lastSentiment"]
#df_combined.columns
df_combined_movers=df_combined[["symbol","name",'sentiment', 'lastSentiment', 'change']].round(0)
df_combined_movers.rename(columns={"lastSentiment":"previous sentiment"},inplace=True)
#df_combined_movers=df_combined_movers.sort_values(by="change",ascending=False).reset_index()
col4, col5,col6 = st.columns([0.30,0.40,0.30])
with col5:
    if movers_select==movers[0]:
        st.subheader("Social volume - movers up:fire:")
    else:
        st.subheader("Social volume - movers down:ice_cube:")
num_mover = st.slider("Select the movers count to display:", 1,50,25)
if movers_select=="bullish movers":
    df_combined_movers=df_combined_movers.sort_values(by="change",ascending=False).reset_index(drop=True)
    df_combined_movers.index = df_combined_movers.index+1
    st.dataframe(df_combined_movers.head(num_mover),use_container_width=True)
if movers_select=="bearish movers":
    df_combined_movers=df_combined_movers.sort_values(by="change",ascending=True).reset_index(drop=True)
    df_combined_movers.index = df_combined_movers.index+1
    st.dataframe(df_combined_movers.head(num_mover),use_container_width=True)
st.image("https://github.com/YWCo/logo/blob/main/YellowWolf.jpg?raw=true")