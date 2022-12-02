from flask import Flask, render_template, request, redirect, url_for
import yfinance as yf
import datetime as dt
import numpy as np
import pandas as pd
pd.set_option("display.precision", 2)
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

app = Flask(__name__)

# model = pd.read_pickle("../models/AAPL_score_9.93.pkl")


#top_25 = ["AAPL", "MSFT", "AMZN", "TSLA", "GOOGL", "BRK.B", "UNH", "JNJ", "XOM", "JPM", "META", "V", "PG", "NVDA", "HD", "CVX", "LLY", "MA", "ABBV", "PFE", "MRK", "PEP", "BAC", "KO"]
top_25 = ["ABBV", "BAC"]
def get_model(stock, folder):
	for file in os.listdir(folder):
		if file.startswith(stock):
			print("Reading file... - " + file)
			return pd.read_pickle(folder + "/" + file)


@app.route('/')
def start_page():
	list_of_prices = []
	print(os.getcwd())
	for i in top_25:
		ticker = yf.Ticker(i.replace(".", "-"))
		hist = ticker.history(end = dt.date.today(), start = str(np.busday_offset(dates=dt.date.today(), offsets=-21, roll='backward')))
		if (os.path.isdir(r"D:\Documents\Ironhack\Final Project\Flask\recent_history") == False):
			os.mkdir(r"D:\Documents\Ironhack\Final Project\Flask\recent_history")
		for csv in os.listdir(r"D:\Documents\Ironhack\Final Project\Flask\recent_history"):
			os.remove(csv)
		pd.DataFrame(hist).to_csv("recent_history/" + i + "_last_20_days.csv")
		list_of_prices.append((i, round(hist["Close"][len(hist) - 1], 2)))
	price_df = pd.DataFrame(columns = ["Stock", "Price", "Prediction"])
	for price in range(len(list_of_prices)):
		price_df.loc[price, "Stock"] = list_of_prices[price][0]
		price_df.loc[price, "Price"] = round(list_of_prices[price][1], 2)
		model = get_model(top_25[price], "good_models")
		x_scaler = pd.read_pickle("scalers/" + top_25[price] + "_x_scaler.pkl")
		y_scaler = pd.read_pickle("scalers/" + top_25[price] + "_y_scaler.pkl")
		input = pd.read_csv("recent_history/" + top_25[price] + "_last_20_days.csv")
		input = input.drop(columns = ["Date", "Dividends", "Stock Splits", "Close"])
		input = x_scaler.transform(input)
		input = input.reshape(1, input.shape[0], input.shape[1])
		price_df.loc[price, "Prediction"] = y_scaler.inverse_transform(model.predict(input))[0][0]
	return render_template("index.html", hist=hist.to_html(), prices=price_df.sort_values("Stock").style.hide_index().set_caption("Last close prices").set_properties(**{'border':"5px solid blue", \
		"background-color":"blue"}).to_html())

@app.route('/portfolio', methods=['POST', 'GET'])
def portfolio_tracker():
	daily_prices = pd.Series()
	for stock in top_25:
		ticker = yf.Ticker(stock.replace(".","-"))
	stock_table = pd.read_csv("stock_portfolio.txt", names=["ticker", "quantity"]).dropna()
	stock_table["quantity"] = stock_table["quantity"].astype(int)
	stock_table["ticker"] = stock_table["ticker"].apply(lambda x: f"<a href='/portfolio/{x}'>{x}</a>")
	int_list_of_stocks = stock_table.groupby("ticker").agg("sum")
	list_of_stocks = int_list_of_stocks[int_list_of_stocks["quantity"] != 0].reset_index().style.hide_index().set_properties(**{'border':"1.3px solid green",\
			 'color':"honeydew", "background-color": "blue"}).set_caption("Your portfolio")
	
	if request.method == 'POST':
		stocks = request.form["stocks_parameter"]
		stock_quantity = request.form["stock_quantity"]
		with (open("stock_portfolio.txt", 'a') as f):
			f.write(stocks + "," + stock_quantity + "\n")
		stock_table = pd.read_csv("stock_portfolio.txt", names=["ticker", "quantity"]).dropna()
		stock_table["quantity"] = stock_table["quantity"].astype(int)
		int_list_of_stocks = stock_table.groupby("ticker").agg("sum")
		int_list_of_stocks["Daily Price"] = daily_prices
		# int_list_of_stocks["Pos. Value"] = int_list_of_stocks.apply(yf.Ticker(int_list_of_stocks["ticker"]).history()["Close".iloc][-1])
		# def apply_model(row):
		# 	model = get_model(row["ticker"], "models")
		# 	x_scaler = pd.read_pickle("scalers/" + row["ticker"] + "_x_scaler.pkl")
		# 	y_scaler = pd.read_pickle("scalers/" + row["ticker"] + "_y_scaler.pkl")
		# 	input = pd.read_csv("recent_history/" + row["ticker"] + "_last_20_days.csv")
		# 	input = input.drop(columns = ["Date", "Dividends", "Stock Splits", "Close"])
		# 	input = x_scaler.transform(input)
		# 	input = input.reshape(1, input.shape[0], input.shape[1])
		# 	prediction = model.predict(input)
		# 	return(y_scaler.inverse_transform(prediction))
		# int_list_of_stocks["Prediction"] = int_list_of_stocks.apply(apply_model)
		list_of_stocks = int_list_of_stocks[int_list_of_stocks["quantity"] != 0].reset_index().style.hide_index().set_properties(**{'border':"1.3px solid green",\
			 'color':"honeydew", "background-color": "blue"}).set_caption("Your portfolio")
		
		return(render_template("portfolio_picker.html", stocks = stocks, stock_quantities = stock_quantity, list_of_stocks=list_of_stocks.to_html(classes='data'), titles=list_of_stocks.columns.values))
	else:
		return(render_template("portfolio_picker.html", list_of_stocks = list_of_stocks.to_html(classes='data')))#, stocks = stocks, stock_quantities = stock_quantity, list_of_stocks=list_of_stocks.to_html(classes='data'), titles=list_of_stocks.columns.values))

@app.route('/portfolio/<ticker_code>')
def plot_predictions(ticker_code):
	data = pd.read_csv("data/" + ticker_code + ".csv")
	plt.plot(data["Close"][:int(len(data) * 0.8)])
	plt.plot(data["Close"][int(len(data) * 0.8):])
	plt.title(ticker_code)
	plt.xlabel('Time')
	plt.ylabel('Price')
	plt.savefig("Flask/static/images/graph.jpg")
	plt.clf()
	return render_template("graph.html")


@app.route('/test_page')
def test_functions():
	
	return render_template("style.html")

#start app

if __name__ == "__main__":
	app.run(debug=True, port=3000)