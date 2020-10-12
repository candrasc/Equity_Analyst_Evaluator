from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired



class graphing_form(FlaskForm):
    Ticker = StringField('Ticker')
    Tubmit = SubmitField('Submit')
