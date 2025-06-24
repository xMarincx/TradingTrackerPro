from flask import render_template, request, redirect, url_for, flash, jsonify
from app import app, db
from db_models import Trade, TradeType, TradeAction
from forms import TradeForm, FilterForm
from utils import calculate_portfolio_stats
from datetime import datetime
import logging

@app.route('/')
def index():
    """Main dashboard showing recent trades and portfolio summary"""
    # Get filter parameters
    filter_form = FilterForm(request.args)
    
    # Build query
    query = Trade.query
    
    if filter_form.validate():
        if filter_form.trade_type.data and filter_form.trade_type.data != 'all':
            query = query.filter(Trade.trade_type == TradeType(filter_form.trade_type.data))
        if filter_form.action.data and filter_form.action.data != 'all':
            query = query.filter(Trade.action == TradeAction(filter_form.action.data))
        if filter_form.symbol.data:
            query = query.filter(Trade.symbol.ilike(f'%{filter_form.symbol.data}%'))
        if filter_form.date_from.data:
            query = query.filter(Trade.date >= filter_form.date_from.data)
        if filter_form.date_to.data:
            query = query.filter(Trade.date <= filter_form.date_to.data)
    
    trades = query.order_by(Trade.date.desc()).all()
    
    # Calculate portfolio statistics
    all_trades = Trade.query.all()
    portfolio_stats = calculate_portfolio_stats(all_trades)
    
    return render_template('index.html', 
                         trades=trades, 
                         filter_form=filter_form,
                         portfolio_stats=portfolio_stats)

@app.route('/add_trade', methods=['GET', 'POST'])
def add_trade():
    """Add a new trade"""
    form = TradeForm()
    
    if form.validate_on_submit():
        try:
            # Handle quantity based on action for options
            quantity = form.quantity.data
            if form.trade_type.data in ['call', 'put'] and form.action.data in ['sell_to_open', 'sell_to_close']:
                # Sell options should have negative quantity
                quantity = -abs(quantity)
            else:
                # Buy options and all stock trades should have positive quantity
                quantity = abs(quantity)
            
            trade = Trade(
                symbol=form.symbol.data.upper(),
                trade_type=TradeType(form.trade_type.data),
                action=TradeAction(form.action.data),
                quantity=quantity,
                price=form.price.data,
                date=form.date.data,
                fees=form.fees.data or 0.0,
                is_closed=form.is_closed.data,
                closed_date=form.closed_date.data if form.is_closed.data else None,
                close_price=form.close_price.data if form.is_closed.data else None,
                close_quantity=form.close_quantity.data if form.is_closed.data else None,
                notes=form.notes.data or ""
            )
            
            # Add options-specific fields if it's an options trade
            if form.trade_type.data in ['call', 'put']:
                trade.strike_price = form.strike_price.data
                trade.expiration_date = form.expiration_date.data
                trade.premium = form.price.data  # Use price field as premium for options
            
            db.session.add(trade)
            db.session.commit()
            
            flash(f'Trade added successfully: {trade.action.value.title()} {trade.quantity} {trade.symbol} {trade.trade_type.value.title()}', 'success')
            return redirect(url_for('index'))
            
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error adding trade: {e}")
            flash(f'Error adding trade: {str(e)}', 'danger')
    
    return render_template('add_trade.html', form=form)

@app.route('/edit_trade/<int:trade_id>', methods=['GET', 'POST'])
def edit_trade(trade_id):
    """Edit an existing trade"""
    trade = Trade.query.get_or_404(trade_id)
    
    form = TradeForm()
    
    # Pre-populate form with existing trade data
    if request.method == 'GET':
        form.symbol.data = trade.symbol
        form.trade_type.data = trade.trade_type.value
        form.action.data = trade.action.value
        form.quantity.data = abs(trade.quantity)  # Always show positive quantity in form
        form.price.data = trade.price
        form.date.data = trade.date
        form.fees.data = trade.fees
        form.is_closed.data = trade.is_closed
        form.closed_date.data = trade.closed_date
        form.close_price.data = trade.close_price
        form.close_quantity.data = trade.close_quantity
        form.notes.data = trade.notes
        
        if trade.is_option:
            form.strike_price.data = trade.strike_price
            form.expiration_date.data = trade.expiration_date
    
    if form.validate_on_submit():
        try:
            # Handle quantity based on action for options
            quantity = form.quantity.data
            if form.trade_type.data in ['call', 'put'] and form.action.data in ['sell_to_open', 'sell_to_close']:
                # Sell options should have negative quantity
                quantity = -abs(quantity)
            else:
                # Buy options and all stock trades should have positive quantity
                quantity = abs(quantity)
            
            trade.symbol = form.symbol.data.upper()
            trade.trade_type = TradeType(form.trade_type.data)
            trade.action = TradeAction(form.action.data)
            trade.quantity = quantity
            trade.price = form.price.data
            trade.date = form.date.data
            trade.fees = form.fees.data or 0.0
            trade.is_closed = form.is_closed.data
            trade.closed_date = form.closed_date.data if form.is_closed.data else None
            trade.close_price = form.close_price.data if form.is_closed.data else None
            trade.close_quantity = form.close_quantity.data if form.is_closed.data else None
            trade.notes = form.notes.data or ""
            
            # Add options-specific fields if it's an options trade
            if form.trade_type.data in ['call', 'put']:
                trade.strike_price = form.strike_price.data
                trade.expiration_date = form.expiration_date.data
                trade.premium = form.price.data  # Use price field as premium for options
            else:
                trade.strike_price = None
                trade.expiration_date = None
                trade.premium = None
            
            db.session.commit()
            flash('Trade updated successfully', 'success')
            return redirect(url_for('index'))
                
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error updating trade: {e}")
            flash(f'Error updating trade: {str(e)}', 'danger')
    
    return render_template('edit_trade.html', form=form, trade=trade)

@app.route('/delete_trade/<int:trade_id>', methods=['POST'])
def delete_trade(trade_id):
    """Delete a trade"""
    try:
        trade = Trade.query.get_or_404(trade_id)
        db.session.delete(trade)
        db.session.commit()
        flash('Trade deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error deleting trade: {e}")
        flash('Error deleting trade', 'danger')
    
    return redirect(url_for('index'))

@app.route('/portfolio')
def portfolio():
    """Portfolio summary page"""
    trades = Trade.query.order_by(Trade.date.desc()).all()
    portfolio_stats = calculate_portfolio_stats(trades)
    
    # Group trades by symbol for position tracking
    positions = {}
    for trade in trades:
        symbol = trade.symbol
        if symbol not in positions:
            positions[symbol] = {
                'symbol': symbol,
                'stock_trades': [],
                'options_trades': [],
                'total_cost': 0,
                'total_proceeds': 0
            }
        
        if trade.is_option:
            positions[symbol]['options_trades'].append(trade)
        else:
            positions[symbol]['stock_trades'].append(trade)
        
        if trade.action in [TradeAction.BUY_TO_OPEN, TradeAction.BUY_TO_CLOSE]:
            positions[symbol]['total_cost'] += trade.total_cost
        else:
            positions[symbol]['total_proceeds'] += trade.total_cost
    
    return render_template('portfolio.html', 
                         portfolio_stats=portfolio_stats, 
                         positions=positions)

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500
