from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired



class graphing_form(FlaskForm):
    ticker = StringField('Ticker')
    submit = SubmitField('Submit')
