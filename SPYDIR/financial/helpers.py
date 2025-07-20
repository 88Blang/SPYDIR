import pandas as pd


def remove_currency(x: str) -> int:
    """Convert string '$303,303,000' to integer 303303000 ."""
    if x in ["", "-", "--"]:
        return 0
    num = int(x.replace("$", "").replace(",", "").strip())
    return num


def format_currency(n: int) -> str:
    """Convert integer 303303000 to string like '$303,303,000'."""
    return f"${n:,.0f}"


def remove_pct(x: str) -> float:
    """Convert string 10.0% to float like '0.1'."""
    num = float(x.replace("%", "").replace(",", "").strip())
    return num / 100


def format_pct(n: float) -> str:
    """Convert float like '0.1' to string like '10.0%'."""
    return f"{n*100:,.3f}%"


# df[col] = df[col].map('${:,.2f}'.format)
# TODO - expand to work with both rows and cols - based on if it has %/$
def remove_format(x):
    """Remove format, depending on if labeled a pct ("_pct") or a currency symbol like '$'"""
    if x.name.endswith("_pct"):
        return x.map(remove_pct)
    else:
        return x.map(remove_currency)


def add_format(x):
    """Add format, depending on if labelled a pct ("_pct") or a currency"""
    if x.name.endswith("_pct"):
        num = x.map(format_pct)
        return num
    else:
        num = x.map(format_currency)
        return num


def nasdaq_IS_summary(stock_statements: dict) -> pd.DataFrame:
    """Snapshot of income_statement with growth"""
    is_copy = stock_statements["income_statement"].copy()
    df_is = pd.DataFrame.from_dict(is_copy)
    mapping = stock_statements["_meta"]["map"]["income_statement"]
    df_meta_is = df_is.loc[list(mapping.values())].copy()
    df_meta_is.index = list(mapping.keys())

    growths = {
        "revenue": 0,
        "net_income": 0,
    }
    df_temp = df_meta_is.apply(remove_format, axis=1)

    for key in growths.keys():
        position = list(df_temp.index).index(key) + 1
        growth = df_temp.loc[key].pct_change(-1).fillna(0)
        growth.name = f"{key}_pct"
        growths[key] = growth.mean()  # simple avg, including 0 of first year
        df_temp = pd.concat(
            [df_temp.iloc[:position], pd.DataFrame([growth]), df_temp.iloc[position:]]
        )

    res = df_temp.apply(add_format, axis=1)

    name_map = {
        "revenue": "Revenue",
        "revenue_pct": "Revenue (%)",
        "cogs": "COGS",
        "gross_profit": "Gross Profit",
        "operating_profit": "Operating Profit",
        "ebit": "EBIT",
        "net_income": "Net Income",
        "net_income_pct": "Net Income (%)",
    }

    res = res.rename(name_map)

    return res, growths
