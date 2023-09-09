import numpy as np
import datetime as dt
from dateutil.relativedelta import relativedelta

def generate_date_series(date_begin, date_end, freq_str):
    """
    example:
        date_begin = dt.date(2020, 1, 31)
        date_end = dt.date(2023, 1, 31)
        freq_str = '6M'
        dts = generate_date_series(date_begin, date_end, freq_str)
    """

    # determine time delta
    if (freq_str == '3M'):
        delta = relativedelta(months=+3)
    elif (freq_str == '6M'):
        delta = relativedelta(months=+6)
    else:
        delta = relativedelta(months=+12)

    # we start from date end and continue till date begin
    dts = []
    date_aux = date_end
    while (date_aux >= date_begin):
        dts.append(date_aux)
        date_aux -= delta

    # reverse list of dates
    dts.reverse()

    # return list of dates
    return dts


class Bond:
    """
    example 1:
        import curves as crv

        bnd = {}
        bnd['ent_nm'] = 'kbc'
        bnd['contract_id'] = '000001'
        bnd['ptf'] = 'bnd'
        bnd['fix_type'] = 'fix'
        bnd['ccy_nm'] = 'eur'
        bnd['nominal'] = 1000.
        bnd['maturity_date'] = dt.date(2030, 1, 31)
        bnd['dcm'] = 'ACT_365'
        bnd['cpn_rate'] = 0.01
        bnd['cpn_freq'] = '6M'
        bnd['rate_mult'] = 1.0
        bnd['rate_add'] = 0.0
        bnd['crv_disc'] = 'interbcrv_eur'
        bnd['crv_fwd'] = 'interbcrv_eur'

        main_path = '//home//macky//Documents//Programming//Python//pyFinMat//'
        crv_nms = ['interbcrv_eur']
        crvs = crv.Curves(main_path, crv_nms)

        valuation_date = dt.date(2020, 1, 31)

        bnd = Bond(bnd, valuation_date)
        bnd.calc_npv(crvs)
        print(bnd.get_npv())

        main_path = '//home//macky//Documents//Programming//Python//FinMat//'
        crv_nms = ['interbcrv_eur']
        crvs = crv.Curves(main_path, crv_nms)

        valuation_date = dt.date(2020, 1, 31)

        bnd = Bond(bnd, valuation_date)
        bnd.calc_npv(crvs)
        print(bnd.get_npv())

    example 2:
        import curves as crv

        bnd = {}
        bnd['ent_nm'] = 'kbc'
        bnd['contract_id'] = '000001'
        bnd['ptf'] = 'bnd'
        bnd['fix_type'] = 'flt'
        bnd['ccy_nm'] = 'eur'
        bnd['nominal'] = 1000.
        bnd['maturity_date'] = dt.date(2030, 1, 31)
        bnd['dcm'] = 'ACT_360'
        bnd['cpn_rate'] = 0.01
        bnd['cpn_freq'] = '6M'
        bnd['rate_mult'] = 1.0
        bnd['rate_add'] = 0.0
        bnd['crv_disc'] = 'interbcrv_eur'
        bnd['crv_fwd'] = 'interbcrv_eur'

        main_path = '//home//macky//Documents//Programming//Python//pyFinMat//'
        crv_nms = ['interbcrv_eur']
        crvs = crv.Curves(main_path, crv_nms)

        valuation_date = dt.date(2020, 1, 31)

        bnd = Bond(bnd, valuation_date)
        bnd.calc_npv(crvs)
        print(bnd.get_npv())
        """

    def __init__(self, bnd, valuation_date):

        # store bond definition and valuation date
        self.npv = None
        self.info = bnd
        self.valuation_date = valuation_date

        # project payment dates
        self.pmt_date = generate_date_series(self.valuation_date, self.info['maturity_date'], self.info['cpn_freq'])
        self.pmt_day = np.array([(pmt_date - self.valuation_date).days for pmt_date in self.pmt_date])

        # calculate year fraction for interest payments
        self.yr_frac = np.diff(self.pmt_day)
        if (self.info['dcm'] == 'ACT_360'):
            self.yr_frac = self.yr_frac / 360.
        else:
            self.yr_frac = self.yr_frac / 365.

        # calculate coupon payment for fixed bonds and add nominal to the last payment
        if (self.info['fix_type'] == 'fix'):
            self.cfs = np.array(self.info['cpn_rate']) * self.yr_frac * self.info['nominal']
            self.cfs[-1] += self.info['nominal']


    def calc_npv(self, crvs):

        # get discount factors for individual payment days
        self.dfs = crvs.get_df(self.info['crv_disc'], self.pmt_day[1:])

        # calculate coupon payment for floating bonds and add nominal to the last payment
        self.fwds = np.array([self.info['cpn_rate']])
        if (self.info['fix_type'] != 'fix'):
            fwds = crvs.get_fwd(self.info['crv_fwd'], self.pmt_day[1:-1], self.pmt_day[2:])
            fwds = self.info['rate_mult'] * fwds + self.info['rate_add']
            self.fwds = np.concatenate((self.fwds, fwds), axis=0)
            self.cfs = self.fwds * self.yr_frac * self.info['nominal']
            self.cfs[-1] += self.info['nominal']

        # discount payments
        self.npv = np.sum(self.cfs * self.dfs)


    def get_npv(self):
        return self.npv