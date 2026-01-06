# Alpha Vantage API Usage & Rate Limiting

## 🚨 Rate Limits & Free Tier Restrictions

Alpha Vantage free tier has the following limits:
- **25 API requests per day**
- **1 API request per second** (burst limit)
- **Compact data only**: TIME_SERIES_DAILY returns last 100 data points (not full history)
  - `outputsize=full` requires premium subscription
  - 100 data points = ~3-4 months of trading days (sufficient for most analysis)

## 📊 API Calls Per Run

### For **3 tickers** (e.g., AAPL, MSFT, NVDA):

| Agent | Calls Per Ticker | Total (3 tickers) |
|-------|------------------|-------------------|
| Fundamentals | 1 | 3 |
| Valuation | 5 | 15 |
| Technical | 1 | 3 |
| Sentiment | 2 | 6 |
| **TOTAL** | **9** | **~27 calls** |

### Breakdown by Endpoint:

#### Valuation Agent (5 calls per ticker):
1. `get_financial_metrics()` → OVERVIEW endpoint
2. `search_line_items()` → calls 3 endpoints:
   - INCOME_STATEMENT
   - CASH_FLOW  
   - BALANCE_SHEET
3. `get_market_cap()` → OVERVIEW endpoint (may use cache)

#### Other Agents:
- **Fundamentals**: OVERVIEW
- **Technical**: TIME_SERIES_DAILY
- **Sentiment**: INSIDER_TRANSACTIONS + NEWS_SENTIMENT

## ✅ Rate Limiting Solution Implemented

### Global Rate Limiter
A thread-safe rate limiter has been added to ensure **1 request per second**:

```python
class RateLimiter:
    def __init__(self, calls_per_second=1):
        self.calls_per_second = calls_per_second
        self.min_interval = 1.0 / calls_per_second
        self.last_call_time = 0
        self.lock = threading.Lock()
```

### Applied to All API Calls:
- ✅ `_av_timeseries_daily()`
- ✅ `_av_company_overview()`
- ✅ `_av_income_statement_annual()`
- ✅ `_av_cash_flow_annual()`
- ✅ `_av_balance_sheet_annual()`
- ✅ `get_insider_trades()`
- ✅ `get_company_news()`

### Caching
All API responses are cached to disk, so:
- **First run**: ~27 API calls for 3 tickers
- **Subsequent runs**: 0 API calls (if using same date range)

## 📅 Default Date Range

The system defaults to analyzing the **last 3 months** of data, which is perfect for the free tier:
- 3 months ≈ 60-65 trading days
- Free tier provides last 100 data points
- ✅ No issues with default settings!

You can customize the date range:
```bash
# Analyze last 2 months
python src/main.py --ticker AAPL --start-date 2024-11-01 --end-date 2025-01-06
```

⚠️ **Note**: If you specify a date range older than ~4 months, you may get incomplete data due to the 100-point limit.

## 💡 Recommendations

### 1. Stay Within Daily Limit
- **Max 2 tickers per run** to stay under 25 calls: `2 tickers × 9 calls = 18 calls`
- Or run analysis once daily and rely on cache for subsequent analysis

### 2. Reduce API Calls

#### Option A: Analyze 1-2 tickers at a time
```bash
# First run (18 calls)
python src/main.py --ticker AAPL,MSFT

# Second run next day (6 calls) 
python src/main.py --ticker NVDA
```

#### Option B: Use cached data
Run the same analysis multiple times with `--show-reasoning` flag - uses 0 API calls after first run.

### 3. Optimize Valuation Agent
The valuation agent makes the most calls (5 per ticker). Consider:
- Using cached financial metrics when available
- Reducing the number of line items fetched
- Skipping valuation for some tickers

### 4. Upgrade to Premium (Optional)
Alpha Vantage premium plans offer:
- Higher daily limits (up to 600+ calls/day)
- Higher burst limits (up to 75 calls/minute)
- Real-time data access

See: https://www.alphavantage.co/premium/

## ⏱️ Expected Runtime

With rate limiting (1 call/second):
- **1 ticker**: ~9 seconds minimum
- **2 tickers**: ~18 seconds minimum  
- **3 tickers**: ~27 seconds minimum

Plus additional processing time for analysis.

## 🔧 Testing

To test with minimal API usage:
```bash
# Test with 1 ticker
python src/main.py --ticker AAPL --start-date 2024-01-01 --end-date 2024-01-31
```

## 📝 Notes

- Cache files are stored in the project directory
- Cache persists between runs
- Clear cache if you need fresh data (delete cache files)
- The rate limiter adds delays automatically - you don't need to change anything

