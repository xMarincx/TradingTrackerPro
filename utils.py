from typing import List, Dict
from db_models import Trade, TradeAction, TradeType
from datetime import datetime
from collections import defaultdict

def calculate_portfolio_stats(trades: List[Trade]) -> Dict:
    """Calculate comprehensive portfolio statistics"""
    stats = {
        'total_trades': len(trades),
        'stock_trades': 0,
        'options_trades': 0,
        'total_invested': 0,
        'total_proceeds': 0,
        'net_pnl': 0,
        'realized_pnl': 0,
        'options_premium_paid': 0,
        'options_premium_received': 0,
        'expired_options': 0,
        'active_options': 0,
        'total_fees': 0,
        'open_positions': 0,
        'closed_positions': 0,
        'stock_positions': defaultdict(lambda: {'quantity': 0, 'avg_cost': 0, 'total_cost': 0}),
        'options_positions': defaultdict(list),
        'top_performers': [],
        'worst_performers': []
    }
    
    if not trades:
        return stats
    
    # Track positions by symbol
    symbol_pnl = defaultdict(float)
    
    for trade in trades:
        # Basic counting
        if trade.is_option:
            stats['options_trades'] += 1
            if trade.is_expired:
                stats['expired_options'] += 1
            else:
                stats['active_options'] += 1
        else:
            stats['stock_trades'] += 1
        
        # Count position status
        if trade.is_closed:
            stats['closed_positions'] += 1
        else:
            stats['open_positions'] += 1
        
        # Add fees to total
        stats['total_fees'] += trade.fees or 0
        
        # Add realized P&L for closed positions only
        if trade.is_closed:
            stats['realized_pnl'] += trade.realized_pnl
        
        # Calculate costs and proceeds based on total_cost (which handles credits/debits)
        trade_value = abs(trade.total_cost)
        
        if trade.total_cost > 0:  # Debit (money out)
            stats['total_invested'] += trade_value
            symbol_pnl[trade.symbol] -= trade_value
            
            if trade.is_option:
                stats['options_premium_paid'] += trade_value
            else:
                # Update stock position for buy
                pos = stats['stock_positions'][trade.symbol]
                new_total_cost = pos['total_cost'] + trade_value
                new_quantity = pos['quantity'] + abs(trade.quantity)
                pos['total_cost'] = new_total_cost
                pos['quantity'] = new_quantity
                if new_quantity > 0:
                    pos['avg_cost'] = new_total_cost / new_quantity
        else:  # Credit (money in)
            stats['total_proceeds'] += trade_value
            symbol_pnl[trade.symbol] += trade_value
            
            if trade.is_option:
                stats['options_premium_received'] += trade_value
            else:
                # Update stock position for sell
                pos = stats['stock_positions'][trade.symbol]
                pos['quantity'] -= abs(trade.quantity)
                # Don't update avg_cost on sells
        
        # Track options positions
        if trade.is_option:
            stats['options_positions'][trade.symbol].append(trade)
    
    # Calculate net P&L
    stats['net_pnl'] = stats['total_proceeds'] - stats['total_invested']
    
    # Find top and worst performers
    symbol_pnl_list = [(symbol, pnl) for symbol, pnl in symbol_pnl.items()]
    symbol_pnl_list.sort(key=lambda x: x[1], reverse=True)
    
    stats['top_performers'] = symbol_pnl_list[:5]
    stats['worst_performers'] = symbol_pnl_list[-5:]
    
    return stats

def format_currency(amount: float) -> str:
    """Format amount as currency"""
    return f"${amount:,.2f}"

def format_percentage(value: float) -> str:
    """Format value as percentage"""
    return f"{value:.2f}%"

def get_pnl_color_class(pnl: float) -> str:
    """Get Bootstrap color class based on P&L"""
    if pnl > 0:
        return 'text-success'
    elif pnl < 0:
        return 'text-danger'
    else:
        return 'text-muted'

def calculate_days_to_expiration(expiration_date: datetime) -> int:
    """Calculate days until option expiration"""
    if not expiration_date:
        return 0
    delta = expiration_date - datetime.now()
    return max(0, delta.days)

def get_trade_type_badge_class(trade_type: TradeType) -> str:
    """Get Bootstrap badge class for trade type"""
    if trade_type == TradeType.STOCK:
        return 'bg-primary'
    elif trade_type == TradeType.CALL:
        return 'bg-success'
    elif trade_type == TradeType.PUT:
        return 'bg-danger'
    return 'bg-secondary'

def get_action_badge_class(action: TradeAction) -> str:
    """Get Bootstrap badge class for trade action"""
    if action == TradeAction.BUY:
        return 'bg-info'
    elif action == TradeAction.SELL:
        return 'bg-warning'
    return 'bg-secondary'
