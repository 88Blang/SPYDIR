from . import process_yq
from SPYDIR.logs.log_setup import logger


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
                return stock_obj
        except NameError as e:
            logger.debug(f"Error: {e}")
            raise NameError(f"Ticker: {ticker} Not Found")
        except RuntimeError as e:  # If API fails, continue to next
            continue


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
