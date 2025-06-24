from datetime import datetime
from app import db
from sqlalchemy import Enum as SqlEnum
import enum

class TradeType(enum.Enum):
    STOCK = "stock"
    CALL = "call"
    PUT = "put"

class TradeAction(enum.Enum):
    BUY_TO_OPEN = "buy_to_open"
    BUY_TO_CLOSE = "buy_to_close"
    SELL_TO_OPEN = "sell_to_open"
    SELL_TO_CLOSE = "sell_to_close"

class Trade(db.Model):
    __tablename__ = 'trades'
    
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), nullable=False)
    trade_type = db.Column(SqlEnum(TradeType), nullable=False)
    action = db.Column(SqlEnum(TradeAction), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False)
    
    # Options-specific fields
    strike_price = db.Column(db.Float, nullable=True)
    expiration_date = db.Column(db.Date, nullable=True)
    premium = db.Column(db.Float, nullable=True)
    
    # Additional fields
    fees = db.Column(db.Float, default=0.0)
    is_closed = db.Column(db.Boolean, default=False)
    closed_date = db.Column(db.Date, nullable=True)
    close_price = db.Column(db.Float, nullable=True)
    close_quantity = db.Column(db.Integer, nullable=True)
    notes = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Trade {self.action.value} {self.quantity} {self.symbol} {self.trade_type.value}>'
    
    @property
    def is_option(self) -> bool:
        return self.trade_type in [TradeType.CALL, TradeType.PUT]
    
    @property
    def total_cost(self) -> float:
        """Calculate total cost/proceeds of the trade including fees"""
        if self.is_option:
            # For options, handle different actions
            if self.action in [TradeAction.SELL_TO_OPEN, TradeAction.SELL_TO_CLOSE]:
                # Sell: receive premium (credit) - negative cost
                base_cost = -(self.price * abs(self.quantity) * 100)
            else:  # BUY_TO_OPEN or BUY_TO_CLOSE
                # Buy: pay premium (debit) - positive cost
                base_cost = self.price * abs(self.quantity) * 100
        else:
            # For stocks: buy = positive cost, sell = negative cost (proceeds)
            if self.action in [TradeAction.SELL_TO_OPEN, TradeAction.SELL_TO_CLOSE]:
                base_cost = -(self.price * abs(self.quantity))
            else:  # BUY_TO_OPEN or BUY_TO_CLOSE
                base_cost = self.price * abs(self.quantity)
        
        # Add fees to the total cost (fees are always a cost)
        return base_cost + (self.fees or 0)
    
    @property
    def realized_pnl(self) -> float:
        """Calculate realized P&L for closed positions only"""
        if not self.is_closed or not self.close_price or not self.close_quantity:
            return 0.0
        
        # Calculate opening cost
        opening_cost = self.total_cost
        
        # Calculate closing proceeds/cost
        if self.is_option:
            if self.action in [TradeAction.BUY_TO_OPEN]:
                # Bought to open, selling to close - receive premium
                closing_proceeds = self.close_price * abs(self.close_quantity) * 100
                return closing_proceeds - abs(opening_cost)
            else:  # SELL_TO_OPEN
                # Sold to open, buying to close - pay premium
                closing_cost = self.close_price * abs(self.close_quantity) * 100
                return abs(opening_cost) - closing_cost
        else:
            # For stocks
            if self.action in [TradeAction.BUY_TO_OPEN]:
                # Bought stocks, selling for proceeds
                closing_proceeds = self.close_price * abs(self.close_quantity)
                return closing_proceeds - abs(opening_cost)
            else:  # SELL_TO_OPEN (short selling)
                # Sold short, buying to cover
                closing_cost = self.close_price * abs(self.close_quantity)
                return abs(opening_cost) - closing_cost
    
    @property
    def is_expired(self) -> bool:
        """Check if option is expired"""
        if not self.is_option or not self.expiration_date:
            return False
        # Convert expiration_date to datetime for comparison
        exp_datetime = datetime.combine(self.expiration_date, datetime.min.time())
        return datetime.now() > exp_datetime
    
    def to_dict(self) -> dict:
        """Convert trade to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'symbol': self.symbol,
            'trade_type': self.trade_type.value,
            'action': self.action.value,
            'quantity': self.quantity,
            'price': self.price,
            'date': self.date.isoformat(),
            'strike_price': self.strike_price,
            'expiration_date': self.expiration_date.isoformat() if self.expiration_date else None,
            'premium': self.premium,
            'notes': self.notes,
            'created_at': self.created_at.isoformat(),
            'total_cost': self.total_cost,
            'is_expired': self.is_expired
        }