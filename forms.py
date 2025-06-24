from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField, FloatField, DateField, TextAreaField, SubmitField, BooleanField
from wtforms.validators import DataRequired, NumberRange, Optional, Length
from datetime import datetime

class TradeForm(FlaskForm):
    symbol = StringField('Symbol', validators=[DataRequired(), Length(min=1, max=10)])
    trade_type = SelectField('Trade Type', 
                           choices=[('stock', 'Stock'), ('call', 'Call Option'), ('put', 'Put Option')],
                           validators=[DataRequired()])
    action = SelectField('Action', 
                        choices=[('buy_to_open', 'Buy to Open'), ('buy_to_close', 'Buy to Close'), 
                                ('sell_to_open', 'Sell to Open'), ('sell_to_close', 'Sell to Close')],
                        validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1)])
    price = FloatField('Price per Share / Premium', validators=[DataRequired(), NumberRange(min=0.01)])
    date = DateField('Trade Date', validators=[DataRequired()], default=datetime.now().date())
    
    # Options-specific fields
    strike_price = FloatField('Strike Price', validators=[Optional(), NumberRange(min=0.01)])
    expiration_date = DateField('Expiration Date', validators=[Optional()])
    
    # Additional fields
    fees = FloatField('Fees', validators=[Optional(), NumberRange(min=0.0)], default=0.0)
    is_closed = BooleanField('Position Closed', default=False)
    closed_date = DateField('Closed Date', validators=[Optional()])
    close_price = FloatField('Close Price', validators=[Optional(), NumberRange(min=0.01)])
    close_quantity = IntegerField('Close Quantity', validators=[Optional(), NumberRange(min=1)])
    notes = TextAreaField('Notes', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Save Trade')
    
    def validate(self, extra_validators=None):
        """Custom validation for options fields"""
        if not super().validate(extra_validators):
            return False
        
        # If it's an options trade, require options-specific fields
        if self.trade_type.data in ['call', 'put']:
            if not self.strike_price.data:
                self.strike_price.errors.append('Strike price is required for options trades')
                return False
            if not self.expiration_date.data:
                self.expiration_date.errors.append('Expiration date is required for options trades')
                return False

            
            # Check expiration date is in the future
            if self.expiration_date.data and self.expiration_date.data < datetime.now().date():
                self.expiration_date.errors.append('Expiration date must be in the future')
                return False
        
        # If position is closed, require closing details
        if self.is_closed.data:
            if not self.closed_date.data:
                self.closed_date.errors.append('Close date is required for closed positions')
                return False
            if not self.close_price.data:
                self.close_price.errors.append('Close price is required for closed positions')
                return False
            if not self.close_quantity.data:
                self.close_quantity.errors.append('Close quantity is required for closed positions')
                return False
        
        return True

class FilterForm(FlaskForm):
    trade_type = SelectField('Trade Type', 
                           choices=[('all', 'All Types'), ('stock', 'Stock'), ('call', 'Call Option'), ('put', 'Put Option')],
                           default='all')
    action = SelectField('Action', 
                        choices=[('all', 'All Actions'), ('buy_to_open', 'Buy to Open'), ('buy_to_close', 'Buy to Close'),
                                ('sell_to_open', 'Sell to Open'), ('sell_to_close', 'Sell to Close')],
                        default='all')
    symbol = StringField('Symbol', validators=[Optional(), Length(max=10)])
    date_from = DateField('From Date', validators=[Optional()])
    date_to = DateField('To Date', validators=[Optional()])
    
    def validate(self, extra_validators=None):
        """Custom validation for date range"""
        if not super().validate(extra_validators):
            return False
        
        if self.date_from.data and self.date_to.data:
            if self.date_from.data > self.date_to.data:
                self.date_from.errors.append('From date must be before to date')
                return False
        
        return True
