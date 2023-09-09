# standard libraries
import time as t
import pandas as pd
import datetime as dt

# user defined libraries
import curves
import bond


def main(main_path, crv_nms, bnd_file_nm, valuation_date, dummy_scl=1000):

    # load bond position file
    cols = {'ent_nm': str,
            'ptf': str,
            'fix_type': str,
            'ccy_nm': str,
            'nominal': float,
            'maturity_date': str,
            'dcm': str,
            'cpn_rate': float,
            'cpn_freq': str,
            'rate_mult': float,
            'rate_add': float,
            'crv_disc': str,
            'crv_fwd': str}

    bnds_data = pd.read_csv(main_path + 'data//inputs//positions//' + bnd_file_nm,
                            usecols=list(cols.keys()),
                            dtype=cols)

    bnds_data['maturity_date'] =\
        bnds_data['maturity_date'].apply(lambda x: dt.date(int(x[0:4]),
                                                           int(x[4:6]),
                                                           int(x[6:8])))

    # convert dataframe to list of dictionaries and apply dummy_scl to
    # artifically increase portfolio size
    bnds_data = bnds_data.to_dict(orient='records')
    bnds_data *= dummy_scl

    # load curves
    crvs = curves.Curves(main_path, crv_nms)

    # start measuring time
    tic = t.time()

    # initiate bonds and calculate their NPV
    npvs = []
    bnd_id = 0
    for bnd_data in bnds_data:
        bnd = bond.Bond(bnd_data, valuation_date)
        bnd.calc_npv(crvs)
        npv = {}
        npv['bnd_id'] = bnd_id
        npv['ent_nm'] = bnd_data['ent_nm']
        npv['ptf'] = bnd_data['ptf']
        npv['npv'] = bnd.get_npv()
        bnd_id += 1
        npvs.append(npv)

    # create dataframe with NPVs
    npvs = pd.DataFrame(npvs)

    # write NPVs into .csv file
    npvs.to_csv(main_path + 'data//outputs//npvs.csv')

    # stop measuring time
    toc = t.time() - tic

    # inform user about elapsed time
    print('total elapsed time: ' + '{:,.2f}'.format(toc) + ' s')

# run code
main_path = '//home//macky//Documents//Programming//Python//pyFinMat//'
crv_nms = ['interbcrv_eur', 'interbcrv_czk']
bnd_file_nm = 'bnd_data.csv'
valuation_date = dt.date(2023, 1, 31)
dummy_scl=10000
main(main_path, crv_nms, bnd_file_nm, valuation_date, dummy_scl)