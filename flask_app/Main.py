#https://hackersandslackers.com/flask-wtforms-forms/
#https://www.w3schools.com/howto/howto_css_login_form.asp
#https://stackoverflow.com/questions/12277933/send-data-from-a-textbox-into-flask
from flask import Flask, render_template, request
import matplotlib.pyplot as plt
import pandas as pd
import stock_analyser
from forms import graphing_form
import os

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure


app = Flask(__name__)

app.config['SECRET_KEY'] = '4f23b79561dfe5fdc4990c4971632244'

#eliminate caching so that we can change images 
@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response

#This gets the ticker information from the submit form we set up
def get_ticker():
    Ticker = request.form['Ticker']
    processed_text = Ticker.upper()
    return processed_text

#This launches our form template when we load the page
@app.route('/')
def input():
	return render_template('submit.html')

#This uses the get_ticker in order to take the input from the form and create a graph
@app.route('/', methods=['POST','GET'])
def graph():
	text = get_ticker()
	return stock_analyser.plot(text)


if __name__ == '__main__':
	app.run(debug=True, host= '0.0.0.0', port=9696)
