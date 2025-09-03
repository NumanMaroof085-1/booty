# Binance Bot

A simple Binance trading bot that connects to the Binance, fetches market data, calculates position size, and executes trades automatically.

---

## 🚀 Steps to Run

### 1. Set up API Keys
Get your **API Key** and **Secret Key** from [Binance].  
Set them as environment variables:

```bash
# Run these in VS Code terminal or CMD (Windows)
setx BINANCE_TESTNET_API_KEY "your_api_key"
setx BINANCE_TESTNET_SECRET_KEY "your_secret_key"
```

> ⚠ After running the commands, restart VS Code (and its terminal) to ensure the keys are applied.

---

### 2. Project Structure

- **`binance_client.py`** → Handles connection to Binance & fetches live market data.  
- **`risk_management.py`** → Calculates position size (also has a fixed quantity option).  
- **`executor.py`** → Executes trades (entry/exit) based on signals and fetched data.  
- **`main.py`** → Runs the bot at the desired intervals.  

---

### 3. Running the Bot
Make sure all **4 files are in the same folder**. Then run:

```bash
python main.py
```

---

### 4. Keep the Bot Running
The bot only works while `main.py` is running.  
To keep it running 24/7, you can use:
- **VS Code terminal** (keep open)  
- **Screen / Tmux** (Linux/Mac)  
- **Task Scheduler** (Windows)  
- Or deploy on a cloud service (Render, Railway, etc.)  

---

## ⚡ Notes
- This bot is currently configured for the **Binance Testnet** (safe for practice).  
- Switch to live trading **only after proper testing**.  
- Ensure proper risk management — crypto trading carries financial risk.  
- Further updates might be added to the bot in the future
