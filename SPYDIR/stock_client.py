from .base.base import get_base
from .history import get_history, _calc_performance
from .related import get_related
from .news import get_news
from .wiki import get_wiki
from .financial.statements import get_statements
from .data import cache
from .utils.format_helpers import *
from SPYDIR.logs.log_setup import logger

from concurrent.futures import ThreadPoolExecutor
from enum import Enum


class Field(str, Enum):
    BASE = "base"
    NEWS = "news"
    WIKI = "wiki"
    RELATED = "related"
    HISTORY = "history"
    STATEMENTS = "statements"
    REPORT = "report"


def stock_client(ticker: str, cache=cache, arg: Field = Field.BASE) -> dict:
    """Manages stock cache and fetching data.

    Args:
        ticker (str): Stock ticker
        cache: key-value cache
        arg (str): ["news", "wiki", "related", "history", "statements", "report"]

    Returns:
        dict: stock_obj if arg='report' or 'None', else data_dict of data requested
    """
    ticker = ticker.upper()
    stock_obj = cache.get(ticker)

    if arg == Field.BASE and stock_obj == None:  # Create
        # Fetch Data
        stock_obj = get_base(ticker)
        if stock_obj:
            cache.set(ticker, stock_obj)
            return stock_obj
    elif stock_obj == None:  # Create if getting arg, then get arg
        logger.debug(f"Creating stock_obj before fetching {arg}")
        stock_obj = get_base(ticker)
        if stock_obj:
            cache.set(ticker, stock_obj)
        else:
            raise ValueError(f"{ticker} Not Found")

    if arg == Field.BASE and stock_obj:  # Return Cache
        logger.debug("Returning what is in cache")
        return stock_obj

    elif arg == Field.REPORT and stock_obj:

        report_args = [
            "news",
            "wiki",
            "related",
            "history",
            "statements",
        ]
        with ThreadPoolExecutor(max_workers=6) as executor:
            results = executor.map(
                lambda arg: stock_client(ticker, cache, arg),
                report_args,
            )

        for arg, data in zip(report_args, results):
            func_name = f"_unpack_{arg}"
            if func_name in globals():
                if data.get("_meta", {}).get("status", "") == "NA":
                    stock_obj[arg] = data
                else:
                    stock_obj = globals()[func_name](stock_obj, data)
                cache.delete(f"{ticker}_{arg}")
            else:
                stock_obj[arg] = data
                cache.delete(f"{ticker}_{arg}")

        # Update stock_obj in cache
        cache.set(ticker, stock_obj)
        return stock_obj

    elif arg in Field:  # Get Arg

        # Case 1: In obj
        if arg in stock_obj:
            logger.debug(f"Arg: {arg} Found In Stock_obj At: [{arg}]")
            if stock_obj[arg] is not None and stock_obj[arg] != {}:
                logger.debug(f"Returning: {arg} Found In Stock_obj At: [{arg}]")
                return stock_obj[arg]
        else:
            logger.debug(f"Arg: {arg} NOT Found In Stock_obj At: [{arg}]")

        # Check cache_key or fetch
        arg_data = cache.get(f"{ticker}_{arg}")
        if arg_data:  # Case 2: In cache
            logger.debug(f"Arg: {arg} Found In Cache At: {ticker}_{arg}")
            return arg_data
        else:  # Case 3: Fetch
            func_name = f"get_{arg}"
            logger.debug(
                f"Arg: {arg} Not Found, Fetching Data And Saving At: {ticker}_{arg}"
            )

            if func_name in globals():
                if f"get_{arg}" == "get_wiki":
                    data = globals()[func_name](
                        ticker, stock_obj.get("name", "")
                    )  # Add name
                    cache.set(f"{ticker}_{arg}", data)
                else:
                    data = globals()[func_name](ticker)
                    cache.set(f"{ticker}_{arg}", data)
                return data
            else:
                raise ValueError(f"Function '{func_name}' is not defined")
    else:
        raise ValueError(f"Arg '{arg}' is not defined")


def _unpack_history(stock_obj, history):
    """
    When moving history cache into stock_obj, calc performance metrics
    """
    perf_dict = _calc_performance(history)

    stock_obj["performance"].update(perf_dict)
    stock_obj.update({"history": history})
    return stock_obj


def _unpack_wiki(stock_obj, wiki):
    """
    When moving wiki cache into stock_obj, move
    """

    # TODO - fix
    if "Wikipedia" not in [item["title"] for item in stock_obj["sources"]]:
        stock_obj["sources"].append(
            {
                "title": "Wikipedia",
                "link": wiki.get("url", ""),
            }
        )

    stock_obj["wiki"] = wiki
    # stock_obj["summary"].update({"wiki": wiki.get("summary", "")})
    # stock_obj.update({"logo": wiki.get("img", "")})

    return stock_obj


def _unpack_statements(stock_obj, statements):
    """
    When moving wiki cache into stock_obj, move
    """
    meta = statements["_meta"]

    # TODO - fix
    if meta["source"] == "NASDAQ":
        if "NASDAQ" not in [item["title"] for item in stock_obj["sources"]]:
            stock_obj["sources"].append(
                {
                    "title": "NASDAQ",
                    "link": meta.get("source_link", ""),
                }
            )

    stock_obj["statements"] = statements

    return stock_obj
