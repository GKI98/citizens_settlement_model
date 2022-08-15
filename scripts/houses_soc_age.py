# 5

import pandas as pd
from scripts import save_db
from tqdm import tqdm
from scripts.save_csv import Saver
from random import random


class Sequence:
    val = 0

    def get_range_ends(self, length: int) -> tuple:
        '''Returns ends as [left, right)'''
        old_val = self.val
        self.val += length
        
        return old_val, self.val


def generate_rounds(df) -> None:
    
    df['men_rounded'] = 0
    df['women_rounded'] = 0

    for soc in df['social_group_id'].unique():
        df_ = df.loc[df['social_group_id']==soc].copy()
        missing_val = 0

        for house in tqdm(df['house_id'].unique()):
            df__ = df_.loc[df_['house_id']==house].copy()
                
            for sex in ['men', 'women']:
                base_num = df__[df__[f'{sex}'] > 0][f'{sex}'].min()
                
                try:
                    df__[f'ratio_{sex}'] = df__[f'{sex}'].apply(lambda x: x / base_num)
                    df__ = df__.sort_values(by=f'ratio_{sex}')
                    
                    s = Sequence()

                    df__[f'seq_{sex}'] = df__[f'ratio_{sex}'].apply(s.get_range_ends)
                    right_borader = df__[f'seq_{sex}'].iat[-1][1]

                    data_was = df__[f'{sex}'].values
                    data_now = []

                    for _, data in enumerate(data_was, 1):
                        data_now.append(round(data + missing_val))
                        missing_val = round(data + missing_val - data_now[-1], 2)

                    total_soc = sum(data_now)

                    lst = list()
                    for i in range(total_soc):
                        lst.append(random.uniform(0, right_borader-1))            
                    
                    for dice in lst:           
                        idx = df__.loc[df__[f'seq_{sex}'].apply(lambda rng: dice >= rng[0] and dice < rng[1])].iloc[0].name
                        df.loc[idx, f'{sex}_rounded'] += 1
                        
                
                except ValueError:
                    df.loc[df['social_group_id']==soc, f'{sex}_rounded'] = 0


def houses_soc_to_ages(houses_soc, mun_soc):
    '''
    Distribution of house residents (by social groups) by age (0-100)
    '''

    mun_list = set(houses_soc['municipality_id'])

    print('Calculation of house residents by age among social groups:')
    for mun in tqdm(mun_list):
        houses_soc_mun = houses_soc.loc[houses_soc['municipality_id'] == mun]
        mun_soc_mun = mun_soc.loc[mun_soc['municipality_id'] == mun]

        df = pd.merge(houses_soc_mun, mun_soc_mun, on=['municipality_id', 'social_group_id'])
        df = df.sort_values(by=['house_id', 'social_group_id'])

        # The number of people in the age group by gender = 
        # the number of people in the house * the probability of being in the age group
        df['men'] = df['men'] * df['mun_percent']
        df['women'] = df['women'] * df['mun_percent']

        df = df.drop(['mun_percent', 'municipality_id'], axis=1)

        df['men'] = df['men'].astype(float).round(2)
        df['women'] = df['women'].astype(float).round(2)

        generate_rounds(df)

        Saver.df_to_csv(df=df, id=mun)
    
    Saver.cat()


def main(houses_soc, mun_soc):
    print('In progress: the distribution of house residents (by social group) by age')

    mun_soc = mun_soc[['municipality_id', 'social_group_id', 'age', 'men', 'women']]

    houses_soc_to_ages(houses_soc, mun_soc)

    print('Done: Distribution of house residents (by social groups) by age\n')


if __name__ == '__main__':
    pass
