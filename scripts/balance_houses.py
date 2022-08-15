# 3

import pandas as pd
from scripts import read_data
from tqdm import tqdm


def prdict_house_population(houses_df):
    '''
    Calc max and expected number of dwellers in a house
    '''

    # Set max living square for 1 person in the flat
    max_sq_liv = 9

    max_population = (houses_df['living_area'] / max_sq_liv).values
    houses_df['max_population'] = max_population

    def vch_calc(row):
        a_omch = 0.3  # coef for expected population of the house
        a_ich = 0.7  # coef for known population of the house

        if row['failure'] is True:
            val = row['resident_number']

        elif (row['resident_number'] == 0) and (row['failure'] is False):
            val = row['max_population']

        elif row['resident_number'] > row['max_population']:
            val = row['max_population']
        else:
            val = a_omch * row['max_population'] + a_ich * row['resident_number']
        return val

    houses_df['prob_population'] = houses_df.apply(vch_calc, axis=1).round().astype(int)

    return houses_df


def balance_houses_population(houses_df_upd, mun_age_sex_df):
    '''
    Balance expected population of the house
    '''

    mun_list = set(houses_df_upd['municipality_id'])
    houses_df_upd = houses_df_upd.assign(citizens_reg_bal=houses_df_upd['prob_population'])

    # Minimal amount of dwellers in the house
    balancing_min = 5

    # Exctraction step
    accuracy = 1

    counter = 0
    df_mkd_balanced_mo = pd.DataFrame()
    sex = 'total'

    for mun in tqdm(mun_list):
        citizens_mo_reg_bal = mun_age_sex_df.query(f'municipality_id == {mun}')[sex].sum()

        # Choose houses in current inner territory
        df_mkd_mo = houses_df_upd.query(f'municipality_id == {mun}')

        # Make the expected number of residents in the houses the starting point 
        # to calcule balanced values
        citizens_mo_bal = df_mkd_mo['citizens_reg_bal'].sum()

        # Balancing step
        i = 0

        # If the number of residents in the outer territory after balancing by neighborhood is MORE
        # than the calculated probable number of residents for that inner territory, then the difference must be distributed
        # among the non-emergency homes in the inner territory
        if citizens_mo_reg_bal > citizens_mo_bal:
            while citizens_mo_reg_bal > citizens_mo_bal:
                df_mkd_mo_not_f = df_mkd_mo[df_mkd_mo['failure'] == 0]
                # Find index not failure house witw max difference between max and expected population
                the_house = (df_mkd_mo_not_f['citizens_reg_bal'] / df_mkd_mo_not_f['max_population']).idxmin()
                # Adding residents to the "balanced number" of this house
                df_mkd_mo.at[the_house, 'citizens_reg_bal'] = df_mkd_mo.loc[the_house, 'citizens_reg_bal'] + accuracy
                # Looking for a new value of the balanced number ofinner territory
                citizens_mo_bal = df_mkd_mo['citizens_reg_bal'].sum()
                i = i + 1

        # If the number of inhabitants in the inner territory after balancing by neighborhood is LESS
        # than the calculated probable number of residents for that inner territory, the difference must be subtracted
        # from the number of residents in the homes, with emergency homes also included in the balancing
        elif citizens_mo_reg_bal < citizens_mo_bal:
            while citizens_mo_reg_bal < citizens_mo_bal:
                df_mkd_mo_not_f = df_mkd_mo[df_mkd_mo['citizens_reg_bal'] > balancing_min]

                try:
                    the_house = (df_mkd_mo_not_f['citizens_reg_bal'] / df_mkd_mo_not_f['max_population']).idxmax()
                    # Substract the residents from the "balanced number" of this house
                    df_mkd_mo.at[the_house, 'citizens_reg_bal'] = df_mkd_mo.loc[
                                                                      the_house, 'citizens_reg_bal'] - accuracy
                except ValueError as e:
                    print('\nError:You need to reduce minimal possible value for the number of residents in the building\n')
                    raise e

                # Looking for a new value of the balanced number of inner territory
                citizens_mo_bal = df_mkd_mo['citizens_reg_bal'].sum()
                i = i + 1

        df_mkd_balanced_mo = pd.concat([df_mkd_balanced_mo, df_mkd_mo])
        counter += 1

    return df_mkd_balanced_mo


def main(houses_df, mun_age_sex_df):
    print('Balancing population by inner territory')

    houses_df_upd = prdict_house_population(houses_df)
    df_mkd_balanced_mo = balance_houses_population(houses_df_upd, mun_age_sex_df)

    return df_mkd_balanced_mo


if __name__ == '__main__':
    pass
