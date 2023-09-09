import numpy as np
import pandas as pd

class Curves:
    """
    example:
        main_path = '//home//macky//Documents//Programming//Python//FinMat//'
        crv_nms = ['interbcrv_eur']
        crvs = Curves(main_path, crv_nms)
        df = crvs.get_df(crv_nms[0], 365)
        fwd = crvs.get_fwd(crv_nms[0], 365, 2*365)
    """

    def __init__(self, main_path, crv_nms):

        # create a list of curves
        self.nm = {}
        for crv_nm in crv_nms:

            # interpolate rates and calculate corresponding discount factors
            self.nm[crv_nm] = {}
            df = pd.read_csv(main_path + 'data//inputs//curves//' + crv_nm + '.csv', low_memory=True)
            self.nm[crv_nm]['day'] = np.array(np.linspace(1, 30 * 365, 30 * 365), dtype=int)
            self.nm[crv_nm]['rate'] = np.interp(self.nm[crv_nm]['day'], df['day'], df['rate'])
            self.nm[crv_nm]['df'] = np.exp(-self.nm[crv_nm]['rate'] * self.nm[crv_nm]['day'] / 365.)

    def get_df(self, crv_nm, day):
        return self.nm[crv_nm]['df'][day - 1]

    def get_fwd(self, crv_nm, day_1, day_2):
        df_1 = self.nm[crv_nm]['df'][day_1 - 1]
        df_2 = self.nm[crv_nm]['df'][day_2 - 1]
        dt = (day_2 - day_1) / 365.
        fwd = np.log(df_1 / df_2) / dt
        return fwd