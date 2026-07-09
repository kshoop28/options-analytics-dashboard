import numpy as np
import streamlit as st
import pandas as pd
import yfinance as yf
from scipy.stats import norm
import inspect
from datetime import datetime
from matplotlib import projections
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from pricing import OptionsPricer
from market_data import convert
from greeks import matrixcall
from greeks import matrixput
from visualizations import matcall
from visualizations import matput



# front page

st.header('Options Pricing & Market Analytics Dashboard', divider='blue')



def main():
    with st.sidebar:
        mysidebar = st.radio('Real Markets or Own Parameters', ['Markets', 'Own Parameters'])
    if mysidebar == 'Markets':
        markets()
    else:
        myown()
    

def markets():
    global tick
    try: 
        with st.sidebar:
            marketcallput = st.radio("Choose which type of option you would like to purchase", ['Call', 'Put'])
            tick = st.text_input("Ticker: ")
        
            strike_input = st.text_input("Minimum Strike:", value="100")
            

            strike = float(strike_input)
            
            
            date_input = st.text_input("Number of expiration dates to include", value = 1)
            
            if date_input == None:
                raise ValueError()
            
            if strike == None:
                raise ValueError()
            
            
    

            if tick == '':
                raise ValueError()
            
    except ValueError:
        st.write("")
        
    else:
        
        market_data, vol_surface = convert(marketcallput, tick, strike, date_input)

        current_price = get_current_price(tick)

        if current_price is not None:
            st.metric(
                label=f"{tick.upper()} Current Stock Price",
                value=f"${current_price:,.2f}"
            )

        st.caption(f"Showing {marketcallput.lower()} options with strikes at or above ${strike:,.2f}.")

        createsurf(vol_surface)
    

def createsurf(volsurf):
    df = volsurf.copy()

    df = df.dropna(subset=['strike', 'days_to_maturity', 'impliedVolatility'])

    df = df[
        (df['impliedVolatility'] > 0) &
        (df['impliedVolatility'] < 2) &
        (df['days_to_maturity'] > 0)
    ]

    low = df['strike'].quantile(0.05)
    high = df['strike'].quantile(0.95)
    df = df[df['strike'].between(low, high)]

    surface_df = df.pivot_table(
        index='days_to_maturity',
        columns='strike',
        values='impliedVolatility',
        aggfunc='mean'
    )

    fig = go.Figure(data=[
        go.Surface(
            x=surface_df.columns,
            y=surface_df.index,
            z=surface_df.values,
            connectgaps = True
        )
    ])

    fig.update_layout(
        title='Volatility Surface',
        scene=dict(
            xaxis_title='Strike',
            yaxis_title='Days to Maturity',
            zaxis_title='Implied Volatility'
            
        ),
        height=700
    )

    st.plotly_chart(fig, use_container_width=True)

def marketoutput(data):
    try:
        if data.empty:
            raise TypeError()
        st.write(data[['lastTradeDate','strike','impliedVolatility','lastPrice']])
    except TypeError:
        st.write(f'No options were purchased with that strike today')
        

def myown():
    global calc

    try:
        with st.sidebar:
            st.header("Parameters")
            selected = st.radio('Choose which type of option you would like to purchase', ['Call', 'Put'])
            stockprice = st.number_input("Stock Price: ",min_value=0, value=0, step=1)
            strikeprice = st.number_input("Strike: ",min_value=0, value=0, step=1)
            riskfreerate = st.slider('Risk-Free Interest Rate: ',min_value=0.0, max_value=0.50, value=0.04, step=0.01)
            volatility = st.slider('Implied Volatility (%)', min_value = 1, value = 1, step = 1)
            timetoexpiration = st.number_input("Days to Expiration: ",min_value=0, value=0, step=1)
            calc = st.button("Calculate Option Price")
            
                
        
            
        if calc:
            binomial_simulations = 2500
            
            monte_carlo_simulations = 10000

            black_and_binomial_option = OptionsPricer(
                stockprice,
                strikeprice,
                volatility / 100,
                riskfreerate,
                timetoexpiration,
                binomial_simulations
            )
            
            monte_carlo_option = OptionsPricer(
                stockprice,
                strikeprice,
                volatility / 100,
                riskfreerate,
                timetoexpiration,
                monte_carlo_simulations
            )

            bs_call, bs_put = black_and_binomial_option.black()
            bin_call, bin_put = black_and_binomial_option.binomial()
            mc_call, mc_put = monte_carlo_option.montecarlo()

            results = pd.DataFrame({
                "Black-Scholes": [bs_call, bs_put],
                "Binomial": [bin_call, bin_put],
                "Monte Carlo": [mc_call, mc_put]
            }, index=["Call", "Put"])

            st.subheader("Option Pricing Model Comparison")
            st.dataframe(results.style.format("{:.6f}"))
                
                
                
        if stockprice > 0 and strikeprice > 0 and volatility > 0 and timetoexpiration > 0:
            if selected == 'Call':
                greekcall(stockprice,strikeprice,riskfreerate,volatility / 100,timetoexpiration)
            else:
                greekput(stockprice,strikeprice,riskfreerate,volatility / 100,timetoexpiration)
                
                
            
        
    except ZeroDivisionError:
        pass        

def display_greek_value(greek, value, option_type):
    st.subheader(f"{option_type} {greek}")

    if greek == "Delta":
        display_value = f"{value:.4f}"
        caption = "Approximate change in option price for a $1 move in the stock."

    elif greek == "Gamma":
        display_value = f"{value:.6f}"
        caption = "Approximate change in Delta for a $1 move in the stock."

    elif greek == "Theta":
        display_value = f"{value / 365:.4f} / day"
        caption = "Approximate daily time decay."

    elif greek == "Vega":
        display_value = f"{value / 100:.4f} per 1 vol point"
        caption = "Approximate option price change for a 1 percentage point move in implied volatility."

    st.markdown(
        f"""
        <div style="
            font-size: 2.6rem;
            font-weight: 400;
            line-height: 1.1;
            margin-top: -0.6rem;
            margin-bottom: 0.6rem;
        ">
            {display_value}
        </div>
        """,
        unsafe_allow_html=True
    )

    st.caption(caption)
    st.markdown("---")
def greekcall(S__t, K, r, sigma, t):
    with st.sidebar:
        gr = st.segmented_control("What Option Greek Matrix do you want displayed" , ['Delta','Gamma','Theta','Vega'], default = 'Delta')
        data = matrixcall(gr, S__t, K, r, sigma, t)
        fig = matcall(gr, S__t, K, r, sigma, t)
    display_greek_value(gr, data, "Call")
    st.pyplot(fig)

def greekput(S__t, K, r, sigma, t):
    with st.sidebar:
        ar = st.segmented_control("What Option Greek Matrix do you want displayed" , ['Delta','Gamma','Theta','Vega'], default = 'Delta')
        data = matrixput(ar, S__t, K, r, sigma, t)
        fig = matput(ar, S__t, K, r, sigma, t)
    display_greek_value(ar, data, "Put")
    st.pyplot(fig)
        
def get_current_price(tick):
    ticker = yf.Ticker(tick)
    hist = ticker.history(period="1d")

    if hist.empty:
        return None

    return float(hist["Close"].iloc[-1])





# whenever you want to update your code in github do these commadnds in the terminal
#git add .
#git commit -m "Update app"
#git push

if __name__ == "__main__":
    main()