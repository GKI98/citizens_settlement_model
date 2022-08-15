from scripts import process_data
from scripts import houses_soc_age
from scripts import houses_soc
from scripts import balance_houses


def make_calc(args):
    mun_soc, mun_age_sex_df, mun_soc_allages_sum, houses_df = process_data.main(args=args)
    houses_df = balance_houses.main(houses_df, mun_age_sex_df)
    houses_df = houses_soc.main(houses_bal=houses_df, mun_soc_allages_sum=mun_soc_allages_sum)
    houses_soc_age.main(houses_soc=houses_df, mun_soc=mun_soc, args=args)

    print('done!')


def main(args):
    make_calc(args=args)


if __name__ == '__main__':
    pass
