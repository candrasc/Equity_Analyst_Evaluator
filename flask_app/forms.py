from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired



class graphing_form(FlaskForm):
    Ticker = StringField('Ticker')
    DateMin = StringField('DateMin')
    DateMax = StringField('DateMax')
    Submit = SubmitField('Submit')
