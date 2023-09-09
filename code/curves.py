import numpy as np
import pandas as pd

class Curves:
    """
    example:
        main_path = '//home//macky//Documents//Programming//Python//pyFinMat//'
        crv_nms = ['interbcrv_eur']
        crvs = Curves(main_path, crv_nms)
        df = crvs.get_df(crv_nms[0], [180, 365])
        fwd = crvs.get_fwd(crv_nms[0], [180, 365], [365, 2*365])
    """

    def __init__(self, main_path, crv_nms):

        # create a list of curves
        self.nm = {}
        for crv_nm in crv_nms:

            # interpolate rates and calculate corresponding discount factors
            data = pd.read_csv(main_path + 'data//inputs//curves//' + crv_nm + '.csv', low_memory=True)
            day = np.array(np.linspace(1, 30 * 365, 30 * 365), dtype=int)
            rate = np.interp(day, data['day'], data['rate'])
            df = np.exp(-rate * day / 365.)
            self.nm[crv_nm] = {}
            for idx in range(len(rate)):
                self.nm[crv_nm][day[idx]] = [rate[idx], df[idx]]

    def get_rate(self, crv_nm, days):
        rates = [self.nm[crv_nm][day][0] for day in days]
        return np.array(rates)

    def get_df(self, crv_nm, days):
        dfs = [self.nm[crv_nm][day][1] for day in days]
        return np.array(dfs)

    def get_fwd(self, crv_nm, days_1, days_2):
        dfs_1 = self.get_df(crv_nm, days_1)
        dfs_2 = self.get_df(crv_nm, days_2)
        dts = (np.array(days_2) - np.array(days_1)) / 365.
        fwds = np.log(dfs_1 / dfs_2) / dts
        return fwds