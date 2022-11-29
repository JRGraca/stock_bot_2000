from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def start_page():
	return render_template("index.html")

@app.route('/portfolio')
def portfolio_tracker():
	print("Hello World")	
#start app

@app.route('/test_page')
def test_functions():
	top_25 = ["AAPL", "MSFT", "AMZN", "TSLA", "GOOGL", "BRK.B", "UNH", "JNJ", "XOM", "JPM", "META", "V", "PG", "NVDA", "HD", "CVX", "LLY", "MA", "ABBV", "PFE", "MRK", "PEP", "BAC", "KO"]
	return(top_25)

if __name__ == "__main__":
	app.run(debug=True, port=3000)