from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum

class TradeType(Enum):
    STOCK = "stock"
    CALL = "call"
    PUT = "put"

class TradeAction(Enum):
    BUY = "buy"
    SELL = "sell"

@dataclass
class Trade:
    id: int
    symbol: str
    trade_type: TradeType
    action: TradeAction
    quantity: int
    price: float
    date: datetime
    # Options-specific fields
    strike_price: Optional[float] = None
    expiration_date: Optional[datetime] = None
    premium: Optional[float] = None
    # Additional fields
    notes: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        # Validate options fields
        if self.trade_type in [TradeType.CALL, TradeType.PUT]:
            if self.strike_price is None or self.expiration_date is None or self.premium is None:
                raise ValueError("Options trades must have strike_price, expiration_date, and premium")
    
    @property
    def is_option(self) -> bool:
        return self.trade_type in [TradeType.CALL, TradeType.PUT]
    
    @property
    def total_cost(self) -> float:
        """Calculate total cost/proceeds of the trade"""
        if self.is_option:
            # For options, use price (which is the premium) * quantity * 100 (since each contract is 100 shares)
            return self.price * self.quantity * 100
        else:
            # For stocks, use price * quantity
            return self.price * self.quantity
    
    @property
    def is_expired(self) -> bool:
        """Check if option is expired"""
        if not self.is_option or not self.expiration_date:
            return False
        # Convert expiration_date to datetime if it's a date
        if hasattr(self.expiration_date, 'date'):
            exp_datetime = self.expiration_date
        else:
            exp_datetime = datetime.combine(self.expiration_date, datetime.min.time())
        return datetime.now() > exp_datetime
    
    def to_dict(self) -> Dict:
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

class TradeManager:
    """In-memory storage manager for trades"""
    
    def __init__(self):
        self.trades: List[Trade] = []
        self.next_id = 1
    
    def add_trade(self, trade_data: Dict) -> Trade:
        """Add a new trade"""
        # Convert string enums back to enum objects
        trade_data['trade_type'] = TradeType(trade_data['trade_type'])
        trade_data['action'] = TradeAction(trade_data['action'])
        
        # Convert date strings to datetime objects
        if isinstance(trade_data['date'], str):
            trade_data['date'] = datetime.fromisoformat(trade_data['date'])
        if trade_data.get('expiration_date') and isinstance(trade_data['expiration_date'], str):
            trade_data['expiration_date'] = datetime.fromisoformat(trade_data['expiration_date'])
        
        # Set ID
        trade_data['id'] = self.next_id
        self.next_id += 1
        
        trade = Trade(**trade_data)
        self.trades.append(trade)
        return trade
    
    def get_trade(self, trade_id: int) -> Optional[Trade]:
        """Get a trade by ID"""
        for trade in self.trades:
            if trade.id == trade_id:
                return trade
        return None
    
    def update_trade(self, trade_id: int, trade_data: Dict) -> Optional[Trade]:
        """Update an existing trade"""
        trade = self.get_trade(trade_id)
        if not trade:
            return None
        
        # Convert string enums back to enum objects
        trade_data['trade_type'] = TradeType(trade_data['trade_type'])
        trade_data['action'] = TradeAction(trade_data['action'])
        
        # Convert date strings to datetime objects
        if isinstance(trade_data['date'], str):
            trade_data['date'] = datetime.fromisoformat(trade_data['date'])
        if trade_data.get('expiration_date') and isinstance(trade_data['expiration_date'], str):
            trade_data['expiration_date'] = datetime.fromisoformat(trade_data['expiration_date'])
        
        # Update trade fields
        for key, value in trade_data.items():
            if hasattr(trade, key):
                setattr(trade, key, value)
        
        return trade
    
    def delete_trade(self, trade_id: int) -> bool:
        """Delete a trade"""
        trade = self.get_trade(trade_id)
        if trade:
            self.trades.remove(trade)
            return True
        return False
    
    def get_all_trades(self) -> List[Trade]:
        """Get all trades"""
        return sorted(self.trades, key=lambda x: x.date, reverse=True)
    
    def filter_trades(self, filters: Dict) -> List[Trade]:
        """Filter trades based on criteria"""
        filtered_trades = self.trades.copy()
        
        if filters.get('trade_type'):
            trade_type = TradeType(filters['trade_type'])
            filtered_trades = [t for t in filtered_trades if t.trade_type == trade_type]
        
        if filters.get('action'):
            action = TradeAction(filters['action'])
            filtered_trades = [t for t in filtered_trades if t.action == action]
        
        if filters.get('symbol'):
            symbol = filters['symbol'].upper()
            filtered_trades = [t for t in filtered_trades if t.symbol.upper() == symbol]
        
        if filters.get('date_from'):
            date_from = datetime.fromisoformat(filters['date_from'])
            filtered_trades = [t for t in filtered_trades if t.date >= date_from]
        
        if filters.get('date_to'):
            date_to = datetime.fromisoformat(filters['date_to'])
            filtered_trades = [t for t in filtered_trades if t.date <= date_to]
        
        return sorted(filtered_trades, key=lambda x: x.date, reverse=True)

# Global trade manager instance
trade_manager = TradeManager()
