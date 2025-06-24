# Stock & Options Trading Tracker

## Overview

This is a Flask-based web application for tracking stock and options trades. The application provides a clean dashboard interface for managing trading activities, calculating portfolio performance, and monitoring investment positions. It's designed as a personal finance tool for individual traders to track their stock and options trading history.

## System Architecture

The application follows a traditional Flask MVC architecture with the following components:

### Backend Architecture
- **Flask Framework**: Core web framework handling HTTP requests and responses
- **Gunicorn WSGI Server**: Production-ready web server for deployment
- **PostgreSQL Database**: Persistent data storage with SQLAlchemy ORM
- **Form Validation**: Flask-WTF for secure form handling and validation

### Frontend Architecture
- **Bootstrap 5**: Responsive UI framework with dark theme optimized for Replit
- **Jinja2 Templates**: Server-side rendering with template inheritance
- **Vanilla JavaScript**: Client-side functionality without heavy frameworks
- **Font Awesome Icons**: Professional iconography

## Key Components

### Models (`db_models.py`)
- **Trade Model**: SQLAlchemy database model for individual trades
- **TradeType Enum**: Categorizes trades as stocks, calls, or puts
- **TradeAction Enum**: Defines buy/sell actions
- **Database Relations**: Proper constraints and validation for options-specific fields

### Forms (`forms.py`)
- **TradeForm**: Comprehensive form for creating/editing trades
- **FilterForm**: Search and filter functionality for trade history
- **Custom Validation**: Options trades require strike price, expiration, and premium

### Routes (`routes.py`)
- **Dashboard Route**: Main interface showing portfolio summary and recent trades
- **Trade Management**: CRUD operations for individual trades
- **Portfolio Analytics**: Detailed portfolio performance analysis

### Utilities (`utils.py`)
- **Portfolio Statistics**: Comprehensive P&L calculations
- **Position Tracking**: Real-time position monitoring for stocks and options
- **Performance Analytics**: Top/worst performer identification

## Data Flow

1. **Trade Entry**: Users input trade data through validated forms
2. **Data Processing**: Trade objects are created with automatic validation
3. **Storage**: Trades are persisted to PostgreSQL database via SQLAlchemy
4. **Analytics**: Real-time calculation of portfolio metrics from database
5. **Display**: Processed data rendered through Bootstrap templates

## External Dependencies

### Python Packages
- **Flask**: Web framework and routing
- **Flask-WTF**: Form handling and CSRF protection
- **Flask-SQLAlchemy**: Database ORM (prepared for future database integration)
- **Gunicorn**: Production web server
- **Werkzeug**: WSGI utilities and middleware
- **Email-Validator**: Form validation utilities
- **psycopg2-binary**: PostgreSQL adapter (prepared for future use)

### Frontend Libraries
- **Bootstrap 5**: CSS framework with Replit dark theme
- **Font Awesome**: Icon library
- **Vanilla JavaScript**: No external JS frameworks

## Deployment Strategy

### Development Environment
- **Local Development**: Flask development server with debug mode
- **Hot Reload**: Automatic reloading on code changes

### Production Deployment
- **Gunicorn**: Multi-worker WSGI server
- **Autoscale Deployment**: Configured for Replit's autoscale platform
- **Environment Variables**: Secret key management through environment variables
- **Proxy Fix**: Proper handling of proxy headers for deployment

### Database Implementation
- **PostgreSQL Active**: Full database integration with SQLAlchemy ORM
- **Data Persistence**: All trades stored permanently in database
- **Query Optimization**: Efficient filtering and sorting of trade data

## Changelog
- June 23, 2025: Initial setup with in-memory storage
- June 23, 2025: Migrated to PostgreSQL database with SQLAlchemy ORM
- June 23, 2025: Fixed options trade handling - removed duplicate premium field
- June 23, 2025: Fixed quantity field validation for whole numbers

## User Preferences

Preferred communication style: Simple, everyday language.