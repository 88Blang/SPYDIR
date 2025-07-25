from . import process_yq
from SPYDIR.logs.log_setup import logger
import datetime


YAHOO_META = {
    "source": "YAHOO",
    "source_link": "https://finance.yahoo.com/quote/{ticker}/",
    "scale": 1,
}


def get_base(ticker):
    """Create a dictionary with root keys and fetch profile data to populate

    Ars:
        ticker(str): Stock ticker (cache key)

    Returns:
        dict: Populated dictionary for stock
    """

    root = create_tree()
    root["ticker"] = ticker

    methods = {"YQ": process_yq.init_tick}

    for key, method in methods.items():
        try:
            stock_obj = method(str(ticker), root)
            if stock_obj:
                logger.debug(f"Using {key}")

                stock_obj["_meta"] = get_meta(key, ticker)
                if ticker.endswith((".V", ".TO")):
                    st = {"market": "CAD"}
                else:
                    st = {"market": "USD"}

                stock_obj["_meta"].update(st)
                stock_obj["sources"].append(
                    {
                        "title": "Yahoo",
                        "link": stock_obj["_meta"].get("source_link", ""),
                    }
                )
                return stock_obj
        except NameError as e:
            logger.debug(f"Error: {e}")
            raise NameError(f"Ticker: {ticker} Not Found")
        except RuntimeError as e:  # If API fails, continue to next
            continue


def get_meta(key, ticker):

    if key == "YQ":
        meta = YAHOO_META
        meta["source_link"] = meta["source_link"].format(ticker=ticker)

    meta["time"] = (str(datetime.datetime.now()),)

    return meta


def create_tree():
    # INIT
    root = {}

    # CREATE STRUCTURE
    root["shares"] = {}
    root["summary"] = {}
    root["esg"] = {}
    root["analyst"] = {}
    root["info"] = {}

    root["summary"]["pitch"] = ""
    root["summary"]["bull"] = ""
    root["summary"]["bear"] = ""
    root["financial"] = {
        "metrics": {},
        "ratios": {},
        "margins": {},
    }
    root["performance"] = {}

    return root
