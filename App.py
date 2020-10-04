from flask import Flask
import matplotlib.pyplot as plt
import pandas as pd
import stock_analyser

app = Flask('app')


@app.route('/', methods = ['GET'])
def test():
	return 'hello'

@app.route('/graph_test', methods = ['GET'])
def plotty():
    return stock_analyser.plot()

if __name__ == '__main__':
	app.run(debug=True, host= '0.0.0.0', port=6969)
