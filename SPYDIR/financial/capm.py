from SPYDIR.markets.market import Market


def calc_equity_cost(beta):
    erp = Market.get_erp()
    rfr = Market.rate(20)
    ce = rfr + beta * erp
    return ce


def calc_wacc_from_mv(mv_equity, mv_debt, tax_rate, cd, ce):
    d_e = mv_debt / mv_equity
    wd = d_e / (1 + d_e)
    we = 1 / (1 + d_e)
    WACC = wd * cd * (1 - tax_rate) + we * ce
    return WACC


def calc_wacc_from_de(de_ratio, tax_rate, cd, ce):
    wd = de_ratio / 100
    we = 1 - wd

    WACC = wd * cd * (1 - tax_rate) + we * ce
    return WACC
