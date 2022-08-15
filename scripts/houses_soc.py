# 4

import pandas as pd
from tqdm import tqdm


def houses_to_soc(houses_bal, mun_soc_allages_sum):
    '''
    Allocate the residents of the houses to social groups
    '''

    houses_bal['mun_percent'] = ''
    mun_list = set(houses_bal['municipality_id'])
    houses_bal = houses_bal.sort_values(by='municipality_id')

    print('Calc the probability to be in the house in the inner territory:')
    for mun in tqdm(mun_list):
        mun_houses_ppl = houses_bal.query(f'municipality_id == {mun}')['citizens_reg_bal']
        mun_sum = mun_houses_ppl.sum()

        # probability to be in the house
        houses_bal.loc[houses_bal['municipality_id'] == mun, 'mun_percent'] = mun_houses_ppl / mun_sum

    houses_soc = pd.merge(houses_bal, mun_soc_allages_sum[['municipality_id', 'social_group_id',
                                                           'total_mun_soc_sum', 'men_mun_soc_sum',
                                                           'women_mun_soc_sum']], on='municipality_id')

    houses_soc = houses_soc.sort_values(by='social_group_id')

    houses_soc.rename(columns={'id': 'house_id', 'resident_number': 'document_population',
                               'citizens_reg_bal': 'resident_number'}, inplace=True)

    return houses_soc


def main(houses_bal, mun_soc_allages_sum):
    houses_soc = houses_to_soc(houses_bal, mun_soc_allages_sum)
    houses_soc = houses_soc.drop(['administrative_unit_id', 'failure', 'living_area', 'prob_population',
                                  'total_mun_soc_sum', 'men_mun_soc_sum', 'women_mun_soc_sum'], axis=1)

    return houses_soc


if __name__ == '__main__':
    pass