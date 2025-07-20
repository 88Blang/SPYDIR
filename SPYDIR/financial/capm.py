from SPYDIR.markets.stats import *


def calc_expected_return(beta):
    ERP = get_erp()
    RFR = get_interest_rate(1)

    return RFR + beta * (ERP)
