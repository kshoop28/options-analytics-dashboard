# Options Pricing & Market Analytics Dashboard

Interactive Streamlit dashboard for pricing European options, calculating Greeks, analyzing live option-chain data, and visualizing implied volatility surfaces.

## Features
- Black-Scholes, binomial tree, and Monte Carlo option pricing
- Call and put option support
- Greeks: Delta, Gamma, Theta, Vega
- Real option-chain data using yfinance
- Implied volatility surface visualization with Plotly
- Unit tests with pytest# options-analytics-dashboard

## Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
