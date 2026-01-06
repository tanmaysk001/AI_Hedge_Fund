# Hedge Fund Agent Team

![Hedge Fund Agent Team](/public/hf.png)
**Note**: the system simulates trading decisions, it does not actually trade.

This project is a simulation of a basic hedge fund research team powered by AI agents using LangChain and LangGraph. It includes a team of four specialized agents:

- **Portfolio Manager**
- **Fundamental Analyst**
- **Technical Analyst**
- **Sentiment Analyst**
- **Valuation Analyst**
- **Risk Manager**

These agents collaborate to analyze stock data and provide insights into a stock's financial, technical, and market sentiment aspects. The system serves as a foundation for creating customized, automated investment analyses.

## Project Overview

The **Hedge Fund Agent Team** simulates an automated investment analysis team composed of four specialized agents:

- **Portfolio Manager**: Oversees and summarizes the team’s findings into a cohesive investment analysis.
- **Fundamental Analyst**: Analyzes financial statements, revenue, and profit metrics.
- **Technical Analyst**: Monitors and reports real-time stock prices.
- **Sentiment Analyst**: Gathers the latest news and public sentiment for market impact.
- **Valuation Analyst**: Calculates the intrinsic value of a stock and generates trading signals.
- **Risk Manager**: Calculates risk metrics and sets position limits.

The team operates in parallel, leveraging LangGraph’s branching capabilities to provide a comprehensive view of a stock’s performance and potential investment appeal.

## Features

- **Automated Financial Analysis**: Accesses over 30,000 tickers through @findatasets to retrieve and analyze financial data.
- **Real-Time Data**: Retrieves live stock prices and daily changes.
- **Sentiment Analysis**: Gathers recent news headlines and market sentiment.
- **Parallel Execution**: Utilizes LangGraph's branching to allow agents to run tasks in parallel, improving efficiency.

## Installation

### 🐳 Option 1: Using Docker (Recommended - Easiest!)

**Never used Docker? See [DOCKER_QUICKSTART.md](DOCKER_QUICKSTART.md) for a 5-minute guide!**

```bash
# 1. Install Docker Desktop
Download from: https://www.docker.com/products/docker-desktop

# 2. Clone and setup
git clone https://github.com/shaikhmubin02/ai-hedge-fund.git
cd ai-hedge-fund

# 3. Create .env with your API keys
cp .env.example .env
# Edit .env with your keys

# 4. Run!
docker-compose run --rm hedge-fund --ticker AAPL,MSFT
```

**Benefits:**
- ✅ No Python installation needed
- ✅ No dependency issues
- ✅ Works on Windows, Mac, Linux
- ✅ Isolated environment

**For complete Docker guide, see [DOCKER_GUIDE.md](DOCKER_GUIDE.md)**

---

### 💻 Option 2: Local Installation (Manual)

Clone the repository:
```bash
git clone https://github.com/shaikhmubin02/ai-hedge-fund.git
cd ai-hedge-fund
```

1. Install UV (if not already installed):
```bash
# On macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

2. Create a virtual environment and install dependencies:
```bash
uv venv
uv pip install -e .
```

3. Activate the virtual environment:
```bash
# On Windows
.venv\Scripts\activate

# On macOS/Linux
source .venv/bin/activate
```

4. Set up your environment variables:
```bash
# Create .env file for your API keys
# On Windows: copy .env.example .env
# On macOS/Linux: cp .env.example .env
```

5. Create a `.env` file in the project root and set your API keys:
```bash
# OpenAI API Key - Get from https://platform.openai.com/
OPENAI_API_KEY=your-openai-api-key

# Groq API Key - Get from https://groq.com/
GROQ_API_KEY=your-groq-api-key

# Alpha Vantage API Key - Get from https://www.alphavantage.co/support/#api-key
ALPHA_VANTAGE_API_KEY=your-alpha-vantage-api-key
```

## Usage

### Running the Hedge Fund
```bash
python src/main.py --ticker AAPL,MSFT,NVDA
```

**Example Output:**
![](/public/output.png)

You can also specify a `--show-reasoning` flag to print the reasoning of each agent to the console.

```bash
python src/main.py --ticker AAPL,MSFT,NVDA --show-reasoning
```
You can optionally specify the start and end dates to make decisions for a specific time period.

```bash
python src/main.py --ticker AAPL,MSFT,NVDA --start-date 2024-01-01 --end-date 2024-03-01 
```

### Running the Backtester

```bash
python src/backtester.py --ticker AAPL,MSFT,NVDA
```

**Example Output:**
![](/public/output2.png)

You can optionally specify the start and end dates to backtest over a specific time period.

```bash
python src/backtester.py --ticker AAPL,MSFT,NVDA --start-date 2024-01-01 --end-date 2024-03-01
```

## Project Structure 
```
ai-hedge-fund/
├── src/
│   ├── agents/                   # Agent definitions and workflow
│   │   ├── fundamentals.py       # Fundamental analysis agent
│   │   ├── portfolio_manager.py  # Portfolio management agent
│   │   ├── risk_manager.py       # Risk management agent
│   │   ├── sentiment.py          # Sentiment analysis agent
│   │   ├── technicals.py         # Technical analysis agent
│   │   ├── valuation.py          # Valuation analysis agent
│   ├── tools/                    # Agent tools
│   │   ├── api.py                # API tools
│   ├── backtester.py             # Backtesting tools
│   ├── main.py # Main entry point
├── pyproject.toml
├── ...
```