from yahooquery import Ticker
import re
from ..utils.format_helpers import *
import pandas as pd


def init_tick(ticker: str, context: dict) -> dict:
    """
    Giv

    Source: yahooquery

    """

    yq_tick = Ticker(ticker, validate=True)
    if ticker not in yq_tick.symbols:
        raise NameError(f"Ticker: {ticker} Not Found")

    try:
        data = yq_tick.all_modules[ticker]
        if isinstance(data, str):
            raise RuntimeError("Invalid Crumb")
        assetProfile_dict = data.get("assetProfile", {})

    except Exception as e:
        raise RuntimeError(f"YQ API ERROR: Invalid Crumb: {e}")

    # Process 'summaryProfile'
    assetProfile_dict = data.get("assetProfile", {})
    if assetProfile_dict:
        context = _process_assetProfile(context, assetProfile_dict)

    # Process 'price'
    price_dict = data.get("price", {})
    if price_dict:
        context = _process_price(context, price_dict)

    # Process 'recommendationTrend'
    rec_trend = data.get("recommendationTrend", {}).get("trend", {})
    if rec_trend:
        context = _process_recommendationTrend(context, rec_trend)

    # Process 'summaryDetail' dictionary
    summaryDetail_dict = data.get("summaryDetail", {})
    if summaryDetail_dict:
        context = _process_summaryDetail(context, summaryDetail_dict)

    try:
        news = yq_tick.technical_insights
        context = _process_news(context, news)
    except:
        print("No technical_insights")

    # Extract financial data
    fin_dict = data.get("financialData", {})
    if fin_dict:
        context = _process_financialData(context, fin_dict)

    key_stat_dict = data.get("defaultKeyStatistics", {})  # earnings
    if key_stat_dict:
        context = _process_defaultKeyStatistics(context, key_stat_dict)

    # Custom Context
    context = format_content(context)

    return context


def format_content(context):
    context["info"] = {
        "Name": context["name"],
        "Ticker": context["ticker"],
        "Sector": context["sector"],
        "Industry": context["industry"],
        "Exchange": context["exchange"],
        "Price": format_price(context["price"]),
        "Avg. Vol": format_large_number(context["average_volume"]),
        "Market Cap": format_large_number(context["market_cap"]),
        "PE Ratio": format_number(context["pe_ratio"]),
        "PB Ratio": format_number(context["pb_ratio"]),
        "Beta": format_number(context["beta"]),
        "Dividend": format_percent(context["dividend_yield"]),
    }

    context["analyst"]["info"] = {
        "Price Target": context["analyst"].get("price_target", {}).get("median", "-"),
        "Rating": context["analyst"].get("recommendation", {}).get("score", "-"),
        "Implied Move": format_percent(
            context["analyst"].get("price_target", {}).get("move", 0)
        ),
        "View": context["analyst"].get("recommendation", {}).get("tag", "-"),
    }

    context["financial"]["ratios"]["info"] = {
        # "Quick Ratio": format_number(
        #     context["financial"]["ratios"].get("quick_ratio", "-")
        # ),
        # "Current Ratio": format_number(
        #     context["financial"]["ratios"].get("current_ratio", "-")
        # ),
        # "Debt To Equity": format_number(
        #     context["financial"]["ratios"].get("debt_to_equity", "-")
        # ),
        "Return On Assets": format_percent(
            context["financial"]["ratios"].get("return_on_assets", "-")
        ),
        "Return On Equity": format_percent(
            context["financial"]["ratios"].get("return_on_equity", "-")
        ),
        "Earnings Growth": format_percent(
            context["financial"]["ratios"].get("earnings_growth", "-")
        ),
        "Revenue Growth": format_percent(
            context["financial"]["ratios"].get("revenue_growth", "-")
        ),
        "Gross Margin": format_percent(
            context["financial"]["ratios"].get("gross_margin", "-")
        ),
        "Ebitda Margin": format_percent(
            context["financial"]["ratios"].get("ebitda_margin", "-")
        ),
        "Operating Margin": format_percent(
            context["financial"]["ratios"].get("operating_margin", "-")
        ),
        "Profit Margin": format_percent(
            context["financial"]["ratios"].get("profit_margin", "-")
        ),
    }

    context["financial"]["metrics"]["info"] = {
        "Revenue": format_large_number(context["financial"]["metrics"]["revenue"]),
        "EBITDA": format_large_number(context["financial"]["metrics"]["ebitda"]),
        "Gross Profits": format_large_number(
            context["financial"]["metrics"]["gross_profits"]
        ),
    }

    context["shares"]["info"] = {
        "Shares Outstanding": format_large_number(context["shares"]["shares"]),
        "Share Float": format_large_number(context["shares"]["shares_float"]),
        # "% Held by Insider": format_percent(context["shares_pct_insider"]),
        # "% Held by Institutions": format_percent(context["shares_pct_institutions"]),
        "% Short": format_percent(context["shares"]["shares_short_pct"]),
        "Shares Short": format_large_number(context["shares"]["shares_short"]),
        # "Shares Short 1m": format_large_number(context["shares_short_prev_month"]),
        "Short Ratio": format_number(context["shares"]["shares_short_ratio"]),
    }
    context["esg"]["info"] = {  #                {{ esg.company_risk }}
        "Audit": context["esg"].get("company_risk", {}).get("audit", "-"),
        "Board": context["esg"].get("company_risk", {}).get("board", "-"),
        "Compensation": context["esg"].get("company_risk", {}).get("compensation", "-"),
        "Shareholder": context["esg"].get("company_risk", {}).get("shareholder", "-"),
        "Overall": context["esg"].get("company_risk", {}).get("overall", "-"),
        "Employee Count": context["esg"].get("employee_count", "-"),
        "% Held Insider": format_percent(context["shares"]["shares_pct_insider"]),
        "% Held Institutions": format_percent(
            context["shares"]["shares_pct_institutions"]
        ),
    }

    if context["performance"].get("ta", {}) != {}:
        context["performance"]["info"] = {
            "Support": format_price(context["performance"]["ta"].get("support", "-")),
            "Resistance": format_price(
                context["performance"]["ta"].get("resistance", "-")
            ),
            "Stop Loss": format_price(
                context["performance"]["ta"].get("stop_loss", "-")
            ),
            "Short-term Direction": context["performance"]["ta"]
            .get("short", {})
            .get("direction", "-"),
            "Short-term Score": context["performance"]["ta"]
            .get("short", {})
            .get("score", "-"),
            "Long-term Direction": context["performance"]["ta"]
            .get("long", {})
            .get("direction", "-"),
            "Long-term Score": context["performance"]["ta"]
            .get("long", {})
            .get("score", "-"),
        }
    else:
        context["performance"]["info"] = {}

    return context


def _process_assetProfile(context, assetProfile_dict):

    context["sector"] = assetProfile_dict.get("sector", "")
    context["industry"] = assetProfile_dict.get("industry", "")

    context["summary"]["yq"] = assetProfile_dict.get("longBusinessSummary", "")
    context["website"] = assetProfile_dict.get("website", "")
    context["ir_website"] = assetProfile_dict.get("irWebsite", context["website"])
    context["esg"]["employee_count"] = assetProfile_dict.get("fullTimeEmployees", 0)

    company_officers = []
    officer_list = assetProfile_dict.get("companyOfficers", [])
    if officer_list != []:
        for officer in officer_list:
            company_officers.append(
                {
                    "Name": officer["name"],
                    "Title": officer["title"],
                    "Total Pay": format_large_number(officer.get("totalPay", 0)),
                }
            )

    context["esg"]["company_officers"] = pd.DataFrame(company_officers).to_dict()
    # context["esg"]["company_officers"] = company_officers

    context["esg"]["company_risk"] = {
        "audit": assetProfile_dict.get("auditRisk", 0),
        "board": assetProfile_dict.get("boardRisk", 0),
        "compensation": assetProfile_dict.get("compensationRisk", 0),
        "shareholder": assetProfile_dict.get("shareHolderRightsRisk", 0),
        "overall": assetProfile_dict.get("overallRisk", 0),
    }

    return context


def _process_recommendationTrend(context, rec_trend):
    if rec_trend == {}:
        return context
    cleaned_trend = []

    for row in rec_trend:
        new_row = {}

        for key, value in row.items():
            new_key = re.sub(r"([a-z])([A-Z])", r"\1 \2", key).title()
            if value in ["-1m", "-2m", "-3m"]:
                value = value.replace("-", "").upper()
                value = f"Last {value}"
            elif value == "0m":
                value = "Current"

            new_row[new_key] = value
        cleaned_trend.append(new_row)

    df_rt = pd.DataFrame(cleaned_trend)
    context["analyst"]["rec_trend"] = df_rt.to_dict()
    return context


def _process_news(context, news):
    ticker = context["ticker"]

    # Process 'upsell' for bullish and bearish summaries
    upsell = news[ticker].get(
        "upsell", {}
    )  # Bullish/bearish summary, name, summaryDate, provider
    if upsell:
        # context['summary'] = {
        context["summary"]["bull"] = (
            upsell.get("msBullishSummary", []),
        )  # List of three points
        context["summary"]["bear"] = (
            upsell.get("msBearishSummary", []),
        )  # List of three points

        context["summary"]["bull"] = list(context["summary"]["bull"])[0]
        context["summary"]["bear"] = list(context["summary"]["bear"])[0]

    # Process 'upsellSearchDD' for investment pitch
    upsellDetail = news[ticker].get("upsellSearchDD", {})  # Investment rating, provider
    context["summary"]["pitch"] = upsellDetail.get("researchReports", {}).get(
        "summary", ""
    )

    # Process 'companySnapshot' for scores
    snap = news[ticker].get("companySnapshot", {})
    context["esg"]["scores"] = {
        "company": snap.get("company", {}),  # May or may not have 'div'
        "sector": snap.get("sector", {}),
    }
    instrumentInfo = news[ticker].get("instrumentInfo", {})

    # Valutation
    context["analyst"]["value"] = {}
    # Extract price recommendation details
    price_rec = news[ticker].get("recommendation", {})
    if price_rec:
        price_target = price_rec.get("targetPrice", None)
        current_price = context.get("price", 1)  # Default to avoid division by zero
        implied_move = (
            ((price_target - current_price) / current_price) if price_target else "-"
        )
        context["analyst"]["value"].update(
            {
                "price_target": price_target,
                "rating": price_rec.get("rating", ""),
                "implied_move": implied_move,
            }
        )

    # Extract valuation details
    valuation = instrumentInfo.get("valuation", {})
    if valuation:
        context["analyst"]["value"].update(
            {
                "view": valuation.get("description", ""),
                "discount": valuation.get("discount", ""),
                "relative": valuation.get("relativeValue", ""),
            }
        )
    # Extract technical analysis details
    tech = instrumentInfo.get("keyTechnicals", {})
    tech_event = instrumentInfo.get("technicalEvents", {})
    # Extract technical events (short, mid, long outlook)

    if tech:
        context["performance"]["ta"] = {
            "support": tech.get("support", ""),
            "resistance": tech.get("resistance", ""),
            "stop_loss": tech.get("stopLoss", ""),
            "short": tech_event.get("shortTermOutlook", ""),
            "mid": tech_event.get("intermediateTermOutlook", ""),
            "long": tech_event.get("longTermOutlook", ""),
        }
    return context


def _process_financialData(context, fin_dict):
    # Financial Statement numbers

    context["financial"]["metrics"].update(
        {
            "revenue": fin_dict.get("totalRevenue", 0),
            "ebitda": fin_dict.get("ebitda", 0),
            "gross_profits": fin_dict.get("grossProfits", 0),
        }
    )

    # Price target details
    context["analyst"]["price_target"] = {}
    context["analyst"]["price_target"].update(
        {
            "high": fin_dict.get("targetHighPrice", 0),
            "low": fin_dict.get("targetLowPrice", 0),
            "mean": fin_dict.get("targetMeanPrice", 0),
            "median": fin_dict.get("targetMedianPrice", 0),
            "move": (fin_dict.get("targetMeanPrice", 0) - context.get("price", 1))
            / context.get("price", 1),
        }
    )

    # Analyst recommendation
    context["analyst"]["recommendation"] = {}

    context["analyst"]["recommendation"].update(
        {
            "score": fin_dict.get("recommendationMean", 0),
            "tag": fin_dict.get("recommendationKey", "").replace("_", " ").title(),
            "rec": str(round(fin_dict.get("recommendationMean", 0), 1))
            + " - "
            + fin_dict.get("recommendationKey", "").replace("_", " ").title(),
        }
    )

    # Financial ratios
    context["financial"]["ratios"].update(
        {
            "quick_ratio": fin_dict.get("quickRatio", 0),
            "current_ratio": fin_dict.get("currentRatio", 0),
            "debt_to_equity": fin_dict.get("debtToEquity", 0),
            "return_on_assets": fin_dict.get("returnOnAssets", 0),
            "return_on_equity": fin_dict.get("returnOnEquity", 0),
            "earnings_growth": fin_dict.get("earningsGrowth", 0),
            "revenue_growth": fin_dict.get("revenueGrowth", 0),
            "gross_margin": fin_dict.get("grossMargins", 0),
            "ebitda_margin": fin_dict.get("ebitdaMargins", 0),
            "operating_margin": fin_dict.get("operatingMargins", 0),
            "profit_margin": fin_dict.get("profitMargins", 0),
        }
    )
    return context


def _process_defaultKeyStatistics(context, key_stat_dict):

    context["performance"]["year_change"] = key_stat_dict.get("52WeekChange", 0)
    context["trailing_eps"] = key_stat_dict.get("trailingEps", 0)
    context["forward_eps"] = key_stat_dict.get("forwardEps", 0)
    context["pb_ratio"] = key_stat_dict.get("priceToBook", 0)
    context["book_value"] = key_stat_dict.get("bookValue", 0)
    context["ev_value"] = key_stat_dict.get("enterpriseValue", 0)

    context["shares"]["shares"] = key_stat_dict.get("sharesOutstanding", 0)
    context["shares"]["shares_pct_insider"] = key_stat_dict.get(
        "heldPercentInsiders", 0
    )
    context["shares"]["shares_pct_institutions"] = key_stat_dict.get(
        "heldPercentInstitutions", 0
    )
    context["shares"]["shares_float"] = key_stat_dict.get("floatShares", 0)
    context["shares"]["shares_short"] = key_stat_dict.get("sharesShort", 0)
    context["shares"]["shares_short_prev_month"] = key_stat_dict.get(
        "sharesShortPriorMonth", 0
    )
    context["shares"]["shares_short_ratio"] = key_stat_dict.get("shortRatio", 0)
    context["shares"]["shares_short_pct"] = key_stat_dict.get("shortPercentOfFloat", 0)

    return context


def _process_price(context, price_dict):
    context["long_name"] = price_dict.get("longName", "").replace("(The)", "")
    context["name"] = (
        price_dict.get("shortName", "")
        .replace("(The)", "")
        .replace(", Inc.", "")
        .lower()
        .title()
    )
    context["price"] = price_dict.get("regularMarketPrice", "")
    context["market_cap"] = price_dict.get("marketCap", "")
    context["exchange"] = price_dict.get("exchange", "")

    context["price_change"] = price_dict.get("regularMarketChange", "")
    context["price_change_pct"] = price_dict.get("regularMarketChangePercent", 0)

    return context


def _process_summaryDetail(context, summaryDetail_dict):

    context["dividend_yield"] = summaryDetail_dict.get("dividendYield", 0)
    exDate = summaryDetail_dict.get("exDividendDate", " ")
    context["ex_dividend_date"] = exDate.split(" ")[0]
    context["performance"]["year_low"] = summaryDetail_dict.get("fiftyTwoWeekLow", 0)
    context["performance"]["year_high"] = summaryDetail_dict.get("fiftyTwoWeekHigh", 0)
    context["pe_ratio"] = summaryDetail_dict.get("forwardPE", 0)
    context["beta"] = summaryDetail_dict.get("beta", 0)
    context["volume"] = summaryDetail_dict.get("volume", 0)
    context["average_volume"] = summaryDetail_dict.get("averageVolume", 0)
    context["average_volume_10"] = summaryDetail_dict.get("averageVolume10days", 0)

    return context
