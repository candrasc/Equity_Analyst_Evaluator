#https://hackersandslackers.com/flask-wtforms-forms/
#https://www.w3schools.com/howto/howto_css_login_form.asp
#https://stackoverflow.com/questions/12277933/send-data-from-a-textbox-into-flask
from flask import Flask, render_template, request
import matplotlib.pyplot as plt
import pandas as pd
from stock_analyser_helper import DoesItAll
from forms import graphing_form
import os



#naming it like this for elastic beanstock
application = app = Flask(__name__)

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

#This launches our form template when we load the page
@app.route('/')
def input():
	return render_template('submit_form.html')

#This uses the get_ticker in order to take the input from the form and create a graph
@app.route('/', methods=['POST','GET'])
def flask_get_plots():
    Symbol , DateMin, DateMax, ReturnWindows = get_info()
    frames = DoesItAll(Symbol, DateMin, DateMax, ReturnWindows)

    try:
        frames.all_plots()
        image = [i for i in os.listdir('static/images') if i.endswith('.png')][0]
        return render_template('plots.html', name = 'new_plot', user_image = image)
    except:
        return render_template('error.html',name = 'error')

def get_info():
    Ticker = request.form['Ticker'].replace(" ", "").upper()
    DateMin = request.form['DateMin'].replace(" ", "")
    DateMax = request.form['DateMax'].replace(" ", "")
    ReturnWindows = request.form['ReturnWindows']

    if DateMin == "":
        DateMin = None

    if DateMax == "":
        DateMax = None

    if ReturnWindows == "":
        ReturnWindows = [30,60,180,360]
    else:
        ReturnWindows = [int(s) for s in ReturnWindows.split(',')]

    return Ticker, DateMin, DateMax, ReturnWindows


if __name__ == '__main__':
	app.run(debug=True, host= '0.0.0.0', port=9696)
