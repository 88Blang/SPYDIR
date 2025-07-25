from SPYDIR.financial.helpers import *
from SPYDIR.financial.capm import calc_equity_cost, calc_wacc_from_mv
from SPYDIR.stock_client import stock_client
from SPYDIR.financial.statements import *
from datetime import datetime, date
import numpy as np


class Model:

    def __init__(self, ticker: str):
        self.ticker = ticker
        self.stock_obj = self.fetch_stock()
        self.statements = stock_client(ticker, arg="statements")
        self._raw_model = model_df_from_statements(self.statements).T  # TODO

    def create_ante(self):
        self.ante_model, self.context = get_model(self._raw_model, self.stock_obj)
        return self.ante_model, self.context

    def update_context(self, context: dict):
        """Set Model Context (Override)"""
        self.context = context

    def create_est(self):
        self.est_model = est_model(self.ante_model, self.context)

    def display_join(self):

        model_T = self.ante_model[::-1].T
        return pd.merge(
            model_T[model_T.columns],
            self.est_model.T,
            how="inner",
            left_index=True,
            right_index=True,
        ).apply(add_format)

    def calc_ev(self, r: float = None, g: float = 0.04):
        FV = calc_FV(
            UFCF=self.est_model["UFCF"],
            r=r or self.context["WACC"],
            g=g,
        )

        debt = self.context["total_debt"]
        cash = self.context["total_cash"]
        EV = FV - debt + cash
        return EV

    def fetch_stock(self):
        return stock_client(self.ticker)


def get_model(model_T: pd.DataFrame, stock_obj: dict):

    model_T = model_T.assign(
        revenue_pct=lambda df: df["revenue"].pct_change(-1).fillna(0),
        tax_rate=lambda df: df["tax"] / df["ebt"],
        cost_debt_rate=lambda df: df["interest"] / df["total_debt"],
    )

    model_context = {
        "total_cash": model_T["cash"].iloc[0] + model_T["investments"].iloc[0],
        "total_debt": model_T["total_debt"].iloc[0],
        "cost_debt_rate": model_T["cost_debt_rate"].mean(),
        "tax_rate": model_T["tax_rate"].mean(),
    }

    margin_list = [
        "cogs",
        "gross_profit",
        "operating_profit",
        "ebit",
        "net_income",
        "capex",
        "depreciation",
        "current_assets",
        "current_liabilities",
    ]

    for key in margin_list:
        model_T[f"{key}_margin"] = model_T[key] / model_T["revenue"]

    model_T = model_T.assign(
        receivable_days=lambda df: df["receivables"] / df["revenue"] * 365,
        inventory_days=lambda df: df["inventory"] / df["cogs"] * 365,
        payable_days=lambda df: df["payables"] / df["cogs"] * 365,
        other_liabilities_margin=lambda df: df["other_current_liabilities"]
        / df["revenue"],
        working_cap=lambda df: df["receivables"]
        + df["inventory"]
        - df["payables"]
        - df["other_current_liabilities"],
        working_cap_change=lambda df: df["working_cap"].diff(-1).fillna(0),
        # working_cap = lambda df: df['current_assets'] - df['current_liabilities'],
        # working_cap_change = lambda df: df['working_cap'].diff(-1).fillna(0),
    )

    model_T = model_T.assign(
        NOPAT=lambda df: df["ebit"] * (1 - model_context["tax_rate"]),
        UFCF=lambda df: df["NOPAT"]
        + df["depreciation"]
        + df["capex"]
        - df["working_cap_change"],
    )

    # Adjust context
    for key in model_T.columns:
        if (
            key.endswith("_margin")
            or key.endswith("_pct")
            or key.endswith("_rate")
            or key.endswith("_days")
        ):
            model_context[key] = model_T[key].mean()

    # WACC
    model_context["cost_equity_rate"] = calc_equity_cost(stock_obj["beta"])
    WACC = calc_wacc_from_mv(
        mv_equity=stock_obj["market_cap"],
        mv_debt=model_T["total_debt"].iloc[0],
        tax_rate=model_context["tax_rate"],
        cd=model_context["cost_debt_rate"],
        ce=model_context["cost_equity_rate"],
    )
    model_context["WACC"] = WACC

    return model_T, model_context


def init_est(rev: float, g: float, d1: str, n: int = 5):
    d = datetime.strptime(d1, "%m/%d/%Y")
    cols = [
        date(d.year + i, d.month, d.day).strftime("%d-%m-%Y") for i in range(1, n + 1)
    ]
    values = [rev * ((1 + g) ** i) for i in range(1, n + 1)]
    est_model = pd.DataFrame([values], columns=cols, index=["revenue"])
    # TODO - change tp take series and index=series.name for rev/fcf
    return est_model


def est_model(model: pd.DataFrame, model_context: dict):
    est_model = init_est(
        model["revenue"].iloc[0], model_context["revenue_pct"], model.index[0], n=5
    )
    est_model_T = est_model.T

    est_model_T = est_model_T.assign(
        cogs=lambda df: df["revenue"] * model_context["cogs_margin"],
        gross_profit=lambda df: df["revenue"] * model_context["gross_profit_margin"],
        ebit=lambda df: df["revenue"] * model_context["ebit_margin"],
        NOPAT=lambda df: df["ebit"] * (1 - model_context["tax_rate"]),
        receivables=lambda df: model_context["receivable_days"] / 365 * df["revenue"],
        inventory=lambda df: model_context["inventory_days"] / 365 * df["cogs"],
        payables=lambda df: model_context["payable_days"] / 365 * df["cogs"],
        other_current_liabilities=lambda df: model_context["other_liabilities_margin"]
        * df["revenue"],
        working_cap=lambda df: (
            df["receivables"]
            + df["inventory"]
            - df["payables"]
            - df["other_current_liabilities"]
        ),
        capex=lambda df: df["revenue"] * model_context["capex_margin"],
        depreciation=lambda df: df["revenue"] * model_context["depreciation_margin"],
    )
    working_cap_full = pd.concat(
        [model["working_cap"][::-1], est_model_T["working_cap"]]
    ).diff()[-10:]

    est_model_T["working_cap_change"] = working_cap_full

    est_model_T = est_model_T.assign(
        UFCF=lambda df: (
            df["NOPAT"] + df["depreciation"] + df["capex"] - df["working_cap_change"]
        )
    )
    return est_model_T


def calc_FV(UFCF: list, r: float, g: float):
    n = len(UFCF)

    discount_period = np.arange(1, n + 1)  # i - 0.5
    discount_factor = 1 / (1 + r) ** discount_period
    discount_UFCF = discount_factor * UFCF

    pv_years = discount_UFCF.sum()
    # Terminal
    final = UFCF.iloc[-1]
    tv = (final * (1 + g)) / (r - g)
    pv_tv = tv / (1 + r) ** n

    PV = pv_years + pv_tv
    return PV
