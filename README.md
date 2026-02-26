# Binance Futures Trading Bot

A Python CLI trading bot for Binance Futures Testnet that places MARKET and LIMIT orders.

## ✅ Features
- Place MARKET orders (BUY/SELL)
- Place LIMIT orders (BUY/SELL)  
- CLI interface with argparse
- Logging to file
- Error handling
- Clean structured code

## 🔧 Setup Instructions

### 1. Prerequisites
- Python 3.x installed
- Binance Futures Testnet account

### 2. Get API Keys
1. Go to https://testnet.binancefuture.com
2. Login with email: jahanvisengar05@gmail.com
3. Go to API Management
4. Create new API key with:
   - Name: trading_bot
   - Enable Futures permission
   - Add IP restriction (your current IP)
5. Copy API Key and Secret Key

### 3. Installation
```bash
# Clone the repository
git clone https://github.com/JahanviSengar/trading-bot
cd trading-bot

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your API keys