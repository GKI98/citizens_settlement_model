# 2

import iteround
import pandas as pd
from scripts.read_csv import CSVReader


def calc_percent(adm_age_sex_df, adm_list, mun_age_sex_df, mun_list):
    '''
    Calc % of population by age in inner territory
    '''

    for age in range(0, 101):
        for sex in ['men', 'women', 'total']:

            # Calcs for outer territory

            # By age among all ot
            adm_age_sex_slice = adm_age_sex_df[adm_age_sex_df['age'] == age][sex]
            adm_age_sex_sum = adm_age_sex_df[adm_age_sex_df['age'] == age][sex].sum()

            try:
                adm_age_sex_df.loc[adm_age_sex_df['age'] == age, f'{sex}_age_adm_percent'] = \
                    adm_age_sex_slice / adm_age_sex_sum
            except KeyError as e:
                adm_age_sex_df[f'{sex}_age_adm_percent'] = adm_age_sex_slice / adm_age_sex_sum
            
            for adm_id in adm_list:
                adm_age_sex_mun_id_slice = adm_age_sex_df.query(f"administrative_unit_id == {adm_id}")[sex]
                adm_age_sex_mun_id_sum = adm_age_sex_df.query(f"administrative_unit_id == {adm_id}")[sex].sum()

                try:
                    adm_age_sex_df.loc[adm_age_sex_df['administrative_unit_id', f'{sex}_age_adm_percent'] == adm_id] = \
                        adm_age_sex_mun_id_slice / adm_age_sex_mun_id_sum
                except KeyError as e:
                    adm_age_sex_df[f'{sex}_age_adm_percent'] = adm_age_sex_mun_id_slice / adm_age_sex_mun_id_sum

            # Calcs for inner territory

            # By age among all it

            for adm in adm_list:
                mun_age_sex_slice = mun_age_sex_df.loc[(mun_age_sex_df['age'] == age) & (mun_age_sex_df['admin_unit_parent_id'] == adm)][sex]
                mun_age_sex_sum = mun_age_sex_df.loc[(mun_age_sex_df['age'] == age) & (mun_age_sex_df['admin_unit_parent_id'] == adm)][sex].sum()

                try:
                    mun_age_sex_df.loc[(mun_age_sex_df['age'] == age) & (mun_age_sex_df['admin_unit_parent_id'] == adm), f'{sex}_age_allmun_percent'] = \
                        mun_age_sex_slice / mun_age_sex_sum
                except KeyError as e:
                    mun_age_sex_df[f'{sex}_age_allmun_percent'] = mun_age_sex_slice / mun_age_sex_sum

            # Among inner territory for all ages
            for mun_id in mun_list:
                mun_sex_mun_id_slice = mun_age_sex_df.query(f"municipality_id == {mun_id}")[sex]
                mun_sex_mun_id_sum = mun_age_sex_df.query(f"municipality_id == {mun_id}")[sex].sum()

                try:
                    mun_age_sex_df.loc[mun_age_sex_df['municipality_id'] == mun_id, f'{sex}_mun_allages_percent'] = \
                        mun_sex_mun_id_slice / mun_sex_mun_id_sum
                except KeyError as e:
                    mun_age_sex_df[f'{sex}_mun_allages_percent'] = mun_sex_mun_id_slice / mun_sex_mun_id_sum
                    # print(f'Exception: {e}')

    return mun_age_sex_df, adm_age_sex_df


def calc_mun_soc_age(mun_age_sex_df, soc_adm_age_sex_df):
    '''
    Calc population among all it by soc group and age
    '''

    mun_soc = pd.merge(mun_age_sex_df[['admin_unit_parent_id', 'municipality_id', 'age', 'men_age_allmun_percent',
                                       'women_age_allmun_percent', 'total_age_allmun_percent']],
                       soc_adm_age_sex_df[['admin_unit_parent_id', 'social_group_id', 'age', 'men', 'women', 'total']],
                       left_on=['admin_unit_parent_id', 'age'],
                       right_on=['admin_unit_parent_id', 'age']).sort_values(by=['age'])

    for sex in ['men', 'women', 'total']:
        mun_sex_soc_slice = mun_soc[sex]
        mun_sex_soc_percent_slice = mun_soc[f'{sex}_age_allmun_percent']
        mun_soc_sex = (mun_sex_soc_slice * mun_sex_soc_percent_slice).tolist()

        mun_soc_sex = [0.0 if pd.isna(x) else x for x in mun_soc_sex]
        mun_soc[sex] = iteround.saferound(mun_soc_sex, 0)

    return mun_soc


def calc_adm_soc_sum(soc_list, adm_list, soc_adm_age_sex_df):
    '''
    Sum soc groups by outer territory
    '''

    adm_soc_sum = pd.DataFrame(columns=['admin_unit_parent_id', 'social_group_id',
                                        'total_sum', 'men_ratio', 'women_ratio'])
    for soc in soc_list:
        for adm in adm_list:

            men_sum = soc_adm_age_sex_df.query(f'social_group_id == {soc} & admin_unit_parent_id == {adm}')['men'].sum()
            women_sum = soc_adm_age_sex_df.query(f'social_group_id == {soc} & admin_unit_parent_id == {adm}')['women'].sum()
            total_sum = soc_adm_age_sex_df.query(f'social_group_id == {soc} & admin_unit_parent_id == {adm}')['total'].sum()

            men_ratio = men_sum / total_sum
            women_ratio = women_sum / total_sum

            df_to_insert = pd.DataFrame({'admin_unit_parent_id': [adm], 'social_group_id': [soc],
                                         'total_sum': [total_sum], 'men_ratio': [men_ratio],
                                         'women_ratio': [women_ratio]})

            adm_soc_sum = pd.concat([adm_soc_sum, df_to_insert], ignore_index=True)

    return adm_soc_sum


#
def calc_mun_sum(mun_list, mun_age_sex_df, adm_list):
    '''
     Sum population in inner territory
     and find % of citizens in internal territory accordingly to outer territory
    '''

    # Sum soc grouops in inner territory
    mun_allages_sum = pd.DataFrame(columns=['admin_unit_parent_id', 'municipality_id',
                                           'men_sum', 'women_sum', 'total_sum'])
    for mun in mun_list:
        men_sum = mun_age_sex_df.query(f'municipality_id == {mun}')['men'].sum()
        adm = mun_age_sex_df.query(f'municipality_id == {mun}')['admin_unit_parent_id'].values[0]
        women_sum = mun_age_sex_df.query(f'municipality_id == {mun}')['women'].sum()
        total_sum = mun_age_sex_df.query(f'municipality_id == {mun}')['total'].sum()

        df_to_insert = pd.DataFrame({'admin_unit_parent_id': [adm], 'municipality_id': [mun],
                                     'men_sum': [men_sum], 'women_sum': [women_sum], 'total_sum': [total_sum]})

        mun_allages_sum = pd.concat([mun_allages_sum, df_to_insert], ignore_index=True)

    # Sum soc grouops in outer territory
    adm_allages_sum = pd.DataFrame(columns=['admin_unit_parent_id', 'men_adm_sum',
                                            'women_adm_sum', 'total_adm_sum'])
    for adm in adm_list:
        men_adm_sum = mun_allages_sum.query(f'admin_unit_parent_id == {adm}')['men_sum'].sum()
        women_adm_sum = mun_allages_sum.query(f'admin_unit_parent_id == {adm}')['women_sum'].sum()
        total_adm_sum = mun_allages_sum.query(f'admin_unit_parent_id == {adm}')['total_sum'].sum()

        df_to_insert = pd.DataFrame({'admin_unit_parent_id': [adm],
                                     'men_adm_sum': [men_adm_sum], 'women_adm_sum': [women_adm_sum],
                                     'total_adm_sum': [total_adm_sum]})

        adm_allages_sum = pd.concat([adm_allages_sum, df_to_insert], ignore_index=True)

    # Find the percentage of the amount of social groups
    # in the inner territory from the total number in the outer territory
    mun_allages_percent = pd.DataFrame(columns=['admin_unit_parent_id', 'municipality_id',
                                                'mun_in_adm_total_percent', 'men_mun_ratio', 'women_mun_ratio'])
    for mun in mun_list:
        adm = mun_allages_sum.query(f'municipality_id == {mun}')['admin_unit_parent_id'].values[0]

        men_ratio = mun_allages_sum.query(f'municipality_id == {mun}')['men_sum'].values[0] / \
                    mun_allages_sum.query(f'municipality_id == {mun}')['total_sum'].values[0]

        women_ratio = mun_allages_sum.query(f'municipality_id == {mun}')['women_sum'].values[0] / \
                      mun_allages_sum.query(f'municipality_id == {mun}')['total_sum'].values[0]

        total_percent = mun_allages_sum.query(f'municipality_id == {mun}')['total_sum'].values[0] / \
                        adm_allages_sum.query(f'admin_unit_parent_id == {adm}')['total_adm_sum'].values[0]

        df_to_insert = pd.DataFrame({'admin_unit_parent_id': [adm], 'municipality_id': [mun],
                                     'mun_in_adm_total_percent': [total_percent],
                                     'men_mun_ratio': [men_ratio], 'women_mun_ratio': [women_ratio]
                                     })

        mun_allages_percent = pd.concat([mun_allages_percent, df_to_insert], ignore_index=True)

    return mun_allages_percent


def calc_mun_soc_sum(adm_list, soc_list, mun_allages_percent, adm_soc_sum):
    '''
    Sum of citizens in internal territory and in soc groups
    '''
    mun_soc_allages_sum = pd.DataFrame(columns=['admin_unit_parent_id', 'municipality_id', 'social_group_id',
                                                'total_mun_soc_sum', 'men_mun_soc_sum', 'women_mun_soc_sum'])
    for adm in adm_list:
        mun_list = mun_allages_percent.query(f'admin_unit_parent_id == {adm}')['municipality_id'].values

        for soc in soc_list:
            total_adm_soc_sum = adm_soc_sum.query(
                f'admin_unit_parent_id == {adm} & social_group_id == {soc}')['total_sum'].values[0]
            men_adm_soc_ratio = adm_soc_sum.query(
                f'admin_unit_parent_id == {adm} & social_group_id == {soc}')['men_ratio'].values[0]
            women_adm_soc_ratio = adm_soc_sum.query(
                f'admin_unit_parent_id == {adm} & social_group_id == {soc}')['women_ratio'].values[0]

            for mun in mun_list:
                mun_in_adm_total_percent = mun_allages_percent.query(
                    f'municipality_id == {mun}')['mun_in_adm_total_percent'].values[0]

                total_mun_soc_sum = total_adm_soc_sum * mun_in_adm_total_percent
                men_mun_soc_sum = (total_adm_soc_sum * men_adm_soc_ratio) * mun_in_adm_total_percent
                women_mun_soc_sum = (total_adm_soc_sum * women_adm_soc_ratio) * mun_in_adm_total_percent

                df_to_insert = pd.DataFrame({'admin_unit_parent_id': [adm], 'municipality_id': [mun],
                                             'social_group_id': [soc], 'total_mun_soc_sum': [total_mun_soc_sum],
                                             'men_mun_soc_sum': [men_mun_soc_sum],
                                             'women_mun_soc_sum': [women_mun_soc_sum]})

                mun_soc_allages_sum = pd.concat([mun_soc_allages_sum, df_to_insert],
                                                                 ignore_index=True).sort_values(by='social_group_id')

    # Balance round by soc groups
    for soc in soc_list:
        df_slice = mun_soc_allages_sum.query(f'social_group_id == {soc}')

        total = iteround.saferound(df_slice['total_mun_soc_sum'], 0)
        men = iteround.saferound(df_slice['men_mun_soc_sum'], 0)
        women = iteround.saferound(df_slice['women_mun_soc_sum'], 0)

        mun_soc_allages_sum.loc[mun_soc_allages_sum['social_group_id'] == soc, 'total_mun_soc_sum'] = total
        mun_soc_allages_sum.loc[mun_soc_allages_sum['social_group_id'] == soc, 'men_mun_soc_sum'] = men
        mun_soc_allages_sum.loc[mun_soc_allages_sum['social_group_id'] == soc, 'women_mun_soc_sum'] = women

    mun_soc_allages_sum = mun_soc_allages_sum.astype(int)

    return mun_soc_allages_sum


def main(args):
    adm_total_df, mun_total_df, adm_age_sex_df, mun_age_sex_df, soc_adm_age_sex_df, houses_df = CSVReader.read_csv(args.path)

    adm_age_sex_df['total'] = adm_age_sex_df['men'] + adm_age_sex_df['women']
    mun_age_sex_df['total'] = mun_age_sex_df['men'] + mun_age_sex_df['women']
    soc_adm_age_sex_df['total'] = soc_adm_age_sex_df['men'] + soc_adm_age_sex_df['women']

    adm_age_sex_df['men_percent'] = adm_age_sex_df['men'] / adm_age_sex_df['total']
    mun_age_sex_df['men_percent'] = mun_age_sex_df['men'] / mun_age_sex_df['total']
    soc_adm_age_sex_df['men_percent'] = soc_adm_age_sex_df['men'] / soc_adm_age_sex_df['total']

    adm_age_sex_df['women_percent'] = adm_age_sex_df['women'] / adm_age_sex_df['total']
    mun_age_sex_df['women_percent'] = mun_age_sex_df['women'] / mun_age_sex_df['total']
    soc_adm_age_sex_df['women_percent'] = soc_adm_age_sex_df['women'] / soc_adm_age_sex_df['total']

    adm_total_df['population_percent'] = adm_total_df['population'] / adm_total_df['population'].sum()
    mun_total_df['population_percent'] = mun_total_df['population'] / mun_total_df['population'].sum()

    mun_total_df.rename(columns={"id": "municipality_id"}, inplace=True)

    soc_adm_age_sex_df.rename(columns={"administrative_unit_id": "admin_unit_parent_id"}, inplace=True)

    mun_list = set(mun_age_sex_df['municipality_id'])
    adm_list = set(adm_age_sex_df['administrative_unit_id'])
    soc_list = set(soc_adm_age_sex_df['social_group_id'])

    mun_age_sex_df = pd.merge(mun_age_sex_df, mun_total_df[['municipality_id', 'admin_unit_parent_id']],
                              on='municipality_id')
    col = mun_age_sex_df.pop("admin_unit_parent_id")
    mun_age_sex_df.insert(1, col.name, col)

    print('In progress: calc population by age')
    mun_age_sex_df, adm_age_sex_df = calc_percent(adm_age_sex_df, adm_list, mun_age_sex_df, mun_list)

    print('In progress: socio groups by age')
    mun_soc = calc_mun_soc_age(mun_age_sex_df, soc_adm_age_sex_df)

    print('In progress: socio groups by outer territory')
    adm_soc_sum = calc_adm_soc_sum(soc_list, adm_list, soc_adm_age_sex_df)

    print('In progress: "%" of population from internal territories in outer territories')
    mun_allages_percent = calc_mun_sum(mun_list, mun_age_sex_df, adm_list)

    print('In progress: socio groups by inner territories')
    mun_soc_allages_sum = calc_mun_soc_sum(adm_list, soc_list, mun_allages_percent, adm_soc_sum)

    return mun_soc, mun_age_sex_df, mun_soc_allages_sum, houses_df


if __name__ == '__main__':
    pass
