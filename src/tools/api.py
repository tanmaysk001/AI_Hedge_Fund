import os
import time
import threading
from datetime import datetime

import pandas as pd
import requests

from data.cache import get_cache
from data.models import (
    CompanyNews,
    FinancialMetrics,
    Price,
    LineItem,
    InsiderTrade,
)

# Global cache instance
_cache = get_cache()

# Global rate limiter for Alpha Vantage API (1 request per second for free tier)
class RateLimiter:
    def __init__(self, calls_per_second=1):
        self.calls_per_second = calls_per_second
        self.min_interval = 1.0 / calls_per_second
        self.last_call_time = 0
        self.lock = threading.Lock()
    
    def wait(self):
        """Wait if necessary to respect rate limit."""
        with self.lock:
            current_time = time.time()
            time_since_last_call = current_time - self.last_call_time
            if time_since_last_call < self.min_interval:
                sleep_time = self.min_interval - time_since_last_call
                time.sleep(sleep_time)
            self.last_call_time = time.time()

# Initialize rate limiter (1 request per second for Alpha Vantage free tier)
_rate_limiter = RateLimiter(calls_per_second=1)


def _require_alpha_vantage_key() -> str:
    api_key = os.environ.get("ALPHA_VANTAGE_API_KEY")
    if not api_key:
        raise ValueError("Missing ALPHA_VANTAGE_API_KEY. Please set it in your .env file.")
    return api_key


def _to_float(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _to_int(v):
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return None


def _parse_alpha_vantage_error(payload: dict) -> str | None:
    # Alpha Vantage returns these keys on errors/limits
    for key in ("Error Message", "Information", "Note"):
        if key in payload and payload[key]:
            return str(payload[key])
    return None


def _av_timeseries_daily(ticker: str) -> dict:
    """Return the daily OHLCV time series as a dict keyed by YYYY-MM-DD."""
    api_key = _require_alpha_vantage_key()
    try:
        from alpha_vantage.timeseries import TimeSeries
    except Exception as e:
        raise ImportError(
            "alpha-vantage library is not installed. Run `uv pip install alpha-vantage` or `pip install alpha-vantage`."
        ) from e

    # Rate limit API calls
    _rate_limiter.wait()
    
    ts = TimeSeries(key=api_key, output_format="json")
    # Use 'compact' for free tier (last 100 data points), 'full' requires premium
    data, _meta = ts.get_daily(symbol=ticker, outputsize="compact")

    # Depending on alpha_vantage version/output_format, `data` can be:
    # - {"Meta Data": {...}, "Time Series (Daily)": {...}}
    # - {"YYYY-MM-DD": {...}, ...}
    if isinstance(data, dict) and "Time Series (Daily)" in data:
        payload = data
        if err := _parse_alpha_vantage_error(payload):
            raise RuntimeError(f"Alpha Vantage error: {err}")
        return payload.get("Time Series (Daily)", {}) or {}

    if isinstance(data, dict):
        if err := _parse_alpha_vantage_error(data):
            raise RuntimeError(f"Alpha Vantage error: {err}")
        return data

    return {}


def _av_company_overview(ticker: str) -> dict:
    api_key = _require_alpha_vantage_key()
    try:
        from alpha_vantage.fundamentaldata import FundamentalData
    except Exception as e:
        raise ImportError(
            "alpha-vantage library is not installed. Run `uv pip install alpha-vantage` or `pip install alpha-vantage`."
        ) from e

    # Rate limit API calls
    _rate_limiter.wait()
    
    fd = FundamentalData(key=api_key, output_format="json")
    data, _meta = fd.get_company_overview(symbol=ticker)
    if not isinstance(data, dict):
        return {}
    if err := _parse_alpha_vantage_error(data):
        raise RuntimeError(f"Alpha Vantage error: {err}")
    return data


def _av_income_statement_annual(ticker: str) -> list[dict]:
    api_key = _require_alpha_vantage_key()
    from alpha_vantage.fundamentaldata import FundamentalData

    # Rate limit API calls
    _rate_limiter.wait()
    
    fd = FundamentalData(key=api_key, output_format="json")
    data, _meta = fd.get_income_statement_annual(symbol=ticker)
    if isinstance(data, dict) and (err := _parse_alpha_vantage_error(data)):
        raise RuntimeError(f"Alpha Vantage error: {err}")
    if isinstance(data, dict):
        return data.get("annualReports", []) or []
    return []


def _av_cash_flow_annual(ticker: str) -> list[dict]:
    api_key = _require_alpha_vantage_key()
    from alpha_vantage.fundamentaldata import FundamentalData

    # Rate limit API calls
    _rate_limiter.wait()
    
    fd = FundamentalData(key=api_key, output_format="json")
    data, _meta = fd.get_cash_flow_annual(symbol=ticker)
    if isinstance(data, dict) and (err := _parse_alpha_vantage_error(data)):
        raise RuntimeError(f"Alpha Vantage error: {err}")
    if isinstance(data, dict):
        return data.get("annualReports", []) or []
    return []


def _av_balance_sheet_annual(ticker: str) -> list[dict]:
    api_key = _require_alpha_vantage_key()
    from alpha_vantage.fundamentaldata import FundamentalData

    # Rate limit API calls
    _rate_limiter.wait()
    
    fd = FundamentalData(key=api_key, output_format="json")
    data, _meta = fd.get_balance_sheet_annual(symbol=ticker)
    if isinstance(data, dict) and (err := _parse_alpha_vantage_error(data)):
        raise RuntimeError(f"Alpha Vantage error: {err}")
    if isinstance(data, dict):
        return data.get("annualReports", []) or []
    return []


def get_prices(ticker: str, start_date: str, end_date: str) -> list[Price]:
    """Fetch daily OHLCV price data from cache or Alpha Vantage."""
    if cached_data := _cache.get_prices(ticker):
        filtered_data = [Price(**price) for price in cached_data if start_date <= price["time"] <= end_date]
        if filtered_data:
            return filtered_data

    time_series = _av_timeseries_daily(ticker)
    prices: list[Price] = []
    for day, values in time_series.items():
        if start_date <= day <= end_date:
            o = _to_float(values.get("1. open") if isinstance(values, dict) else None)
            h = _to_float(values.get("2. high") if isinstance(values, dict) else None)
            l = _to_float(values.get("3. low") if isinstance(values, dict) else None)
            c = _to_float(values.get("4. close") if isinstance(values, dict) else None)
            v = _to_int(values.get("5. volume") if isinstance(values, dict) else None)
            if None in (o, h, l, c, v):
                continue
            prices.append(Price(open=o, high=h, low=l, close=c, volume=v, time=day))

    prices.sort(key=lambda x: x.time)
    if not prices:
        return []

    _cache.set_prices(ticker, [p.model_dump() for p in prices])
    return prices


def get_financial_metrics(
    ticker: str,
    end_date: str,
    period: str = "ttm",
    limit: int = 10,
) -> list[FinancialMetrics]:
    """Fetch financial metrics from cache or Alpha Vantage Company Overview (OVERVIEW)."""
    if cached_data := _cache.get_financial_metrics(ticker):
        filtered_data = [FinancialMetrics(**metric) for metric in cached_data if metric["report_period"] <= end_date]
        filtered_data.sort(key=lambda x: x.report_period, reverse=True)
        if filtered_data:
            return filtered_data[:limit]

    overview = _av_company_overview(ticker)
    if not overview:
        return []

    # The OVERVIEW endpoint is "current snapshot". We return it as a single-item list.
    latest_quarter = overview.get("LatestQuarter") or end_date
    currency = overview.get("Currency") or "USD"

    # Calculate additional metrics from available data
    revenue_ttm = _to_float(overview.get("RevenueTTM"))
    ebitda = _to_float(overview.get("EBITDA"))
    dividend_per_share = _to_float(overview.get("DividendPerShare"))
    shares_outstanding = _to_float(overview.get("SharesOutstanding"))
    revenue_per_share_ttm = _to_float(overview.get("RevenuePerShareTTM"))
    
    # Calculate free cash flow yield from dividend yield as proxy (if available)
    free_cash_flow_yield = _to_float(overview.get("DividendYield"))
    
    # Calculate asset turnover if we have revenue and total assets
    asset_turnover = None
    total_assets = _to_float(overview.get("TotalAssets"))
    if revenue_ttm and total_assets and total_assets > 0:
        asset_turnover = revenue_ttm / total_assets
    
    # Calculate debt to assets if available
    debt_to_assets = None
    total_debt = _to_float(overview.get("TotalDebt"))
    if total_debt and total_assets and total_assets > 0:
        debt_to_assets = total_debt / total_assets
    
    metric = FinancialMetrics(
        ticker=ticker,
        calendar_date=latest_quarter,
        report_period=latest_quarter,
        period=(period or "ttm"),
        currency=currency,
        market_cap=_to_float(overview.get("MarketCapitalization")),
        enterprise_value=_to_float(overview.get("EnterpriseValue")),
        price_to_earnings_ratio=_to_float(overview.get("PERatio") or overview.get("TrailingPE")),
        price_to_book_ratio=_to_float(overview.get("PriceToBookRatio")),
        price_to_sales_ratio=_to_float(overview.get("PriceToSalesRatioTTM")),
        enterprise_value_to_ebitda_ratio=_to_float(overview.get("EVToEBITDA")),
        enterprise_value_to_revenue_ratio=_to_float(overview.get("EVToRevenue")),
        free_cash_flow_yield=free_cash_flow_yield,
        peg_ratio=_to_float(overview.get("PEGRatio")),
        gross_margin=_to_float(overview.get("GrossMarginTTM") or overview.get("GrossProfitMargin")),
        operating_margin=_to_float(overview.get("OperatingMarginTTM")),
        net_margin=_to_float(overview.get("ProfitMargin")),
        return_on_equity=_to_float(overview.get("ReturnOnEquityTTM")),
        return_on_assets=_to_float(overview.get("ReturnOnAssetsTTM")),
        return_on_invested_capital=None,  # Not available in OVERVIEW
        asset_turnover=asset_turnover,
        inventory_turnover=None,  # Not available in OVERVIEW
        receivables_turnover=None,  # Not available in OVERVIEW
        days_sales_outstanding=None,  # Not available in OVERVIEW
        operating_cycle=None,  # Not available in OVERVIEW
        working_capital_turnover=None,  # Not available in OVERVIEW
        current_ratio=_to_float(overview.get("CurrentRatio")),
        quick_ratio=_to_float(overview.get("QuickRatio")),
        cash_ratio=None,  # Not available in OVERVIEW
        operating_cash_flow_ratio=None,  # Not available in OVERVIEW
        debt_to_equity=_to_float(overview.get("DebtToEquityRatio")),
        debt_to_assets=debt_to_assets,
        interest_coverage=None,  # Not available in OVERVIEW
        revenue_growth=_to_float(overview.get("QuarterlyRevenueGrowthYOY") or overview.get("RevenueGrowthYOY")),
        earnings_growth=_to_float(overview.get("QuarterlyEarningsGrowthYOY") or overview.get("EarningsGrowthYOY")),
        book_value_growth=None,  # Not available in OVERVIEW
        earnings_per_share_growth=None,  # Not available in OVERVIEW
        free_cash_flow_growth=None,  # Not available in OVERVIEW
        operating_income_growth=None,  # Not available in OVERVIEW
        ebitda_growth=None,  # Not available in OVERVIEW
        payout_ratio=_to_float(overview.get("PayoutRatio")),
        earnings_per_share=_to_float(overview.get("EPS") or overview.get("DilutedEPS")),
        book_value_per_share=_to_float(overview.get("BookValue")),
        free_cash_flow_per_share=None,  # Not directly available, would need calculation from cash flow statement
    )

    metrics = [metric]
    _cache.set_financial_metrics(ticker, [m.model_dump() for m in metrics])
    return metrics[:limit]


def search_line_items(
    ticker: str,
    line_items: list[str],
    end_date: str,
    period: str = "ttm",
    limit: int = 10,
) -> list[LineItem]:
    """
    Provide the requested `line_items` using Alpha Vantage free Fundamental Data endpoints:
    - INCOME_STATEMENT (annual)
    - CASH_FLOW (annual)
    - BALANCE_SHEET (annual)

    Notes:
    - Alpha Vantage does not have a direct "search line items" endpoint; we construct the response from statements.
    - To stay within free-tier limits, we use annual statements and return up to `limit` periods.
    """
    if cached := _cache.get_line_items(ticker):
        filtered = [LineItem(**li) for li in cached if li["report_period"] <= end_date]
        filtered.sort(key=lambda x: x.report_period, reverse=True)
        if filtered:
            return filtered[:limit]

    overview = _av_company_overview(ticker)
    currency = (overview.get("Currency") if isinstance(overview, dict) else None) or "USD"

    income = _av_income_statement_annual(ticker)
    cash = _av_cash_flow_annual(ticker)
    balance = _av_balance_sheet_annual(ticker)

    # Index by fiscalDateEnding
    def _index(reports: list[dict]) -> dict[str, dict]:
        out = {}
        for r in reports:
            if not isinstance(r, dict):
                continue
            dt = r.get("fiscalDateEnding")
            if dt:
                out[str(dt)] = r
        return out

    income_by = _index(income)
    cash_by = _index(cash)
    bal_by = _index(balance)

    # Use the intersection of available periods, newest-first
    periods = sorted(set(income_by) | set(cash_by) | set(bal_by), reverse=True)

    items: list[LineItem] = []
    for rp in periods:
        if rp > end_date:
            continue
        inc = income_by.get(rp, {})
        cf = cash_by.get(rp, {})
        bs = bal_by.get(rp, {})

        # Compute working capital from balance sheet when possible
        total_current_assets = _to_float(bs.get("totalCurrentAssets"))
        total_current_liabilities = _to_float(bs.get("totalCurrentLiabilities"))
        working_capital = None
        if total_current_assets is not None and total_current_liabilities is not None:
            working_capital = total_current_assets - total_current_liabilities

        net_income = _to_float(inc.get("netIncome"))
        depreciation = _to_float(cf.get("depreciationDepletionAndAmortization") or cf.get("depreciationAndAmortization"))
        capex = _to_float(cf.get("capitalExpenditures"))
        operating_cf = _to_float(cf.get("operatingCashflow"))

        # Free cash flow: Operating CF - CapEx (capex may be negative in AV payload)
        free_cash_flow = None
        if operating_cf is not None and capex is not None:
            free_cash_flow = operating_cf - capex

        payload: dict = {
            "ticker": ticker,
            "report_period": rp,
            "period": period,
            "currency": currency,
        }

        # Only include requested fields
        for key in line_items:
            if key == "net_income":
                payload[key] = net_income
            elif key == "depreciation_and_amortization":
                payload[key] = depreciation
            elif key == "capital_expenditure":
                payload[key] = capex
            elif key == "free_cash_flow":
                payload[key] = free_cash_flow
            elif key == "working_capital":
                payload[key] = working_capital
            else:
                # Unknown key: leave unset (keeps output clean)
                continue

        items.append(LineItem(**payload))
        if len(items) >= limit:
            break

    if items:
        _cache.set_line_items(ticker, [li.model_dump() for li in items])
    return items


def get_insider_trades(
    ticker: str,
    end_date: str,
    start_date: str | None = None,
    limit: int = 1000,
) -> list[InsiderTrade]:
    """
    Fetch insider transactions using Alpha Vantage INSIDER_TRANSACTIONS endpoint.
    Returns the latest and historical insider transactions made by key stakeholders.
    """
    if cached_data := _cache.get_insider_trades(ticker):
        filtered_data = [
            InsiderTrade(**trade)
            for trade in cached_data
            if (start_date is None or (trade.get("transaction_date") or trade["filing_date"]) >= start_date)
            and (trade.get("transaction_date") or trade["filing_date"]) <= end_date
        ]
        filtered_data.sort(key=lambda x: x.transaction_date or x.filing_date, reverse=True)
        if filtered_data:
            return filtered_data[:limit]

    api_key = _require_alpha_vantage_key()
    
    # Rate limit API calls
    _rate_limiter.wait()
    
    # Use direct REST API call for INSIDER_TRANSACTIONS
    params = {
        "function": "INSIDER_TRANSACTIONS",
        "symbol": ticker,
        "apikey": api_key
    }
    
    resp = requests.get("https://www.alphavantage.co/query", params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    
    if err := _parse_alpha_vantage_error(data):
        raise RuntimeError(f"Alpha Vantage error: {err}")
    
    # Parse the transactions from the response
    # The API can return data in different formats, check for common keys
    transactions_data = []
    if isinstance(data, dict):
        # Check for 'data' key (common in Alpha Vantage responses)
        if "data" in data and isinstance(data["data"], list):
            transactions_data = data["data"]
        # Check for 'transactions' key
        elif "transactions" in data and isinstance(data["transactions"], list):
            transactions_data = data["transactions"]
        # Sometimes the transactions are directly in the response
        elif any(key for key in data.keys() if key not in ("Meta Data", "metadata", "Information")):
            # If there are other keys besides metadata, it might be a dict of transactions
            for key, value in data.items():
                if isinstance(value, list):
                    transactions_data = value
                    break
    
    insider_trades: list[InsiderTrade] = []
    for item in transactions_data:
        if not isinstance(item, dict):
            continue
        
        # Parse transaction date - can be 'transactionDate' or 'transaction_date'
        transaction_date = item.get("transactionDate") or item.get("transaction_date") or item.get("transaction_acquired_disposed_date")
        # Parse filing date - can be 'reportedFor', 'filingDate', 'filing_date', 'acquisition_or_disposition_date'
        filing_date = item.get("reportedFor") or item.get("filingDate") or item.get("filing_date") or item.get("acquisition_or_disposition_date") or transaction_date
        
        if not transaction_date and not filing_date:
            continue
            
        # Filter by date range
        date_to_check = transaction_date or filing_date
        if date_to_check > end_date:
            continue
        if start_date and date_to_check < start_date:
            continue
        
        # Parse filer name - can be 'filerName', 'filer_name', 'issuer_name'
        name = item.get("filerName") or item.get("filer_name") or item.get("name")
        
        # Parse issuer - can be 'issuer', 'issuerName', 'issuer_name'
        issuer = item.get("issuer") or item.get("issuerName") or item.get("issuer_name")
        
        # Parse title/relation - can be 'filerRelation', 'filer_relation', 'title'
        title = item.get("filerRelation") or item.get("filer_relation") or item.get("title")
        
        # Parse transaction shares - can be 'shares', 'transaction_shares', 'transactionShares', 'securities_transacted'
        transaction_shares = _to_float(
            item.get("shares") or 
            item.get("transaction_shares") or 
            item.get("transactionShares") or 
            item.get("securities_transacted") or
            item.get("securitiesTransacted")
        )
        
        # Parse price per share - can be 'price', 'transaction_price_per_share', 'transactionPricePerShare'
        transaction_price_per_share = _to_float(
            item.get("price") or 
            item.get("transaction_price_per_share") or 
            item.get("transactionPricePerShare") or
            item.get("price_per_share") or
            item.get("pricePerShare")
        )
        
        # Calculate transaction value if we have shares and price
        transaction_value = None
        if transaction_shares is not None and transaction_price_per_share is not None:
            transaction_value = transaction_shares * transaction_price_per_share
        elif item.get("transaction_value") or item.get("transactionValue"):
            transaction_value = _to_float(item.get("transaction_value") or item.get("transactionValue"))
        
        # Parse shares owned fields
        shares_owned_before = _to_float(
            item.get("shares_owned_before_transaction") or 
            item.get("sharesOwnedBeforeTransaction") or
            item.get("securitiesOwnedFollowingTransaction")
        )
        
        shares_owned_after = _to_float(
            item.get("shares_owned_after_transaction") or 
            item.get("sharesOwnedAfterTransaction")
        )
        
        # Parse security title
        security_title = item.get("security_title") or item.get("securityTitle") or item.get("securityType")
        
        # Check if board director
        is_board_director = None
        if title:
            title_lower = str(title).lower()
            if "director" in title_lower or "board" in title_lower:
                is_board_director = True
            else:
                is_board_director = False
        
        insider_trades.append(
            InsiderTrade(
                ticker=ticker,
                issuer=issuer,
                name=name,
                title=title,
                is_board_director=is_board_director,
                transaction_date=transaction_date,
                transaction_shares=transaction_shares,
                transaction_price_per_share=transaction_price_per_share,
                transaction_value=transaction_value,
                shares_owned_before_transaction=shares_owned_before,
                shares_owned_after_transaction=shares_owned_after,
                security_title=security_title,
                filing_date=filing_date,
            )
        )
    
    insider_trades.sort(key=lambda x: x.transaction_date or x.filing_date, reverse=True)
    if insider_trades:
        _cache.set_insider_trades(ticker, [t.model_dump() for t in insider_trades])
    return insider_trades[:limit]


def get_company_news(
    ticker: str,
    end_date: str,
    start_date: str | None = None,
    limit: int = 1000,
) -> list[CompanyNews]:
    """
    Best-effort company news using Alpha Vantage NEWS_SENTIMENT (non-premium, but limited).

    Prefer the `alpha_vantage` Python client when it supports the endpoint; otherwise fall back to
    the free REST endpoint directly (still using the same ALPHA_VANTAGE_API_KEY).
    Docs: https://www.alphavantage.co/documentation/
    """
    if cached_data := _cache.get_company_news(ticker):
        filtered_data = [
            CompanyNews(**news)
            for news in cached_data
            if (start_date is None or news["date"] >= start_date) and news["date"] <= end_date
        ]
        filtered_data.sort(key=lambda x: x.date, reverse=True)
        if filtered_data:
            return filtered_data[:limit]

    api_key = _require_alpha_vantage_key()

    data = None
    try:
        # alpha_vantage may or may not expose this endpoint depending on version.
        from alpha_vantage.alphaintelligence import AlphaIntelligence

        # Rate limit API calls
        _rate_limiter.wait()
        
        ai = AlphaIntelligence(key=api_key, output_format="json")
        kwargs = {"tickers": ticker}
        if start_date:
            kwargs["time_from"] = start_date.replace("-", "") + "T0000"
        # Not all versions support limit/time_to; we filter locally anyway.
        data, _meta = ai.get_news_sentiment(**kwargs)
    except Exception:
        data = None

    if data is None:
        # Rate limit API calls
        _rate_limiter.wait()
        
        params = {"function": "NEWS_SENTIMENT", "tickers": ticker, "apikey": api_key, "limit": min(limit, 1000)}
        if start_date:
            params["time_from"] = start_date.replace("-", "") + "T0000"
        resp = requests.get("https://www.alphavantage.co/query", params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()

    if err := _parse_alpha_vantage_error(data):
        raise RuntimeError(f"Alpha Vantage error: {err}")

    feed = data.get("feed", []) if isinstance(data, dict) else []
    news_items: list[CompanyNews] = []
    for item in feed:
        if not isinstance(item, dict):
            continue
        # time_published: YYYYMMDDTHHMMSS
        tp = str(item.get("time_published") or "")
        if len(tp) >= 8:
            date = f"{tp[0:4]}-{tp[4:6]}-{tp[6:8]}"
        else:
            continue
        if date > end_date:
            continue
        if start_date and date < start_date:
            continue

        # Map sentiment to our simple polarity
        overall_score = _to_float(item.get("overall_sentiment_score"))
        sentiment = None
        if overall_score is not None:
            if overall_score > 0.1:
                sentiment = "positive"
            elif overall_score < -0.1:
                sentiment = "negative"
            else:
                sentiment = "neutral"

        news_items.append(
            CompanyNews(
                ticker=ticker,
                title=str(item.get("title") or ""),
                author=str(item.get("authors")[0] if isinstance(item.get("authors"), list) and item.get("authors") else ""),
                source=str(item.get("source") or ""),
                date=date,
                url=str(item.get("url") or ""),
                sentiment=sentiment,
            )
        )

    news_items.sort(key=lambda x: x.date, reverse=True)
    if news_items:
        _cache.set_company_news(ticker, [n.model_dump() for n in news_items])
    return news_items[:limit]


def get_market_cap(ticker: str, end_date: str) -> float | None:
    financial_metrics = get_financial_metrics(ticker, end_date)
    if not financial_metrics:
        return None
    return financial_metrics[0].market_cap


def prices_to_df(prices: list[Price]) -> pd.DataFrame:
    df = pd.DataFrame([p.model_dump() for p in prices])
    if df.empty:
        return df
    df["Date"] = pd.to_datetime(df["time"])
    df.set_index("Date", inplace=True)
    numeric_cols = ["open", "close", "high", "low", "volume"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df.sort_index(inplace=True)
    return df


def get_price_data(ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
    prices = get_prices(ticker, start_date, end_date)
    return prices_to_df(prices)


