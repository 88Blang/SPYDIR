from SPYDIR import stock
from SPYDIR.history import history_to_plotly_candle
from .stock_report import Stock_Template

from io import BytesIO
import pandas as pd
from datetime import datetime
from copy import deepcopy


# Python
def get_report(ticker, output="./stock_report.pdf"):
    context = create_report_context(ticker)

    done = create_report(output=output, context=context)
    if done:
        return True
    else:
        return False


# DJANGO
def report_template(request, ticker):
    from django.http import FileResponse

    context = get_report_context(ticker)

    pdf_buffer = BytesIO()

    pdf_buffer = create_report(output=pdf_buffer, context=context)

    response = FileResponse(
        pdf_buffer, as_attachment=False, filename=f"{ticker}_Report.pdf"
    )

    return response


def create_report_context(ticker: str):  # full stock obj

    stock_cls = stock.Stock(ticker=ticker, arg="report")
    context = deepcopy(stock_cls.get_dict())

    context["info"] = stock_cls.info.iloc[:, 0].to_dict()
    context["financial"]["ratios"]["info"] = stock_cls.ratios.iloc[:, 0].to_dict()
    context["financial"]["metrics"]["info"] = stock_cls.metrics.iloc[:, 0].to_dict()

    aapl_hist = stock_cls.get_history()
    aapl_hist["date"] = aapl_hist["time"].apply(
        lambda row: datetime.fromtimestamp(int(row) / 1000).strftime(
            "%Y-%m-%dT%H:%M:%S.000Z"
        )
    )
    context["chart_data"] = aapl_hist.to_dict(orient="list")

    context["news"] = context.get("news", ["", "", "", "", ""])[0:4]

    for statement in ["income_statement", "balance_sheet", "cash_flow"]:
        st_dict = context["statements"][statement]
        st_df = pd.DataFrame(st_dict)
        st_df = st_df[~st_df.isin(["--"]).any(axis=1)]
        context["statements"][statement] = st_df.to_dict()

    return context


def create_report(output="./stock_report.pdf", context=None):

    if isinstance(output, str):
        try:
            stock_doc = Stock_Template(output)
            story = stock_doc.build_story(context)

            stock_doc.build(story)
            print(f"Doc made at {output}")
            return True
        except Exception as e:
            raise RuntimeError(f"Error: {e}")
    elif isinstance(output, BytesIO):
        stock_doc = Stock_Template(output)
        story = stock_doc.build_story(context)
        try:
            stock_doc.build(story)
        except Exception as e:
            print("Report error", e)
            return False
        output.seek(0)

        return output
    else:
        print("Output Not Valid")

        return False
