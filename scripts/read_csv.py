import pandas as pd
import os


class CSVReader:

    @staticmethod
    def get_file_names(folder_path: str = './'):
        arr = sorted([f for f in os.listdir(folder_path) if f.endswith(".csv")])
        return arr

    @staticmethod
    def read_csv(folder_path):
        file_names = CSVReader.get_file_names(folder_path)

        df_lst = list()
        for f in file_names:
            df = pd.read_csv(filepath_or_buffer=folder_path + '/' + f)
            df_lst.append(df)

        adm_age_sex_df, adm_total_df, houses_df, mun_age_sex_df, mun_total_df, soc_adm_age_sex_df = df_lst

        return adm_total_df, mun_total_df, adm_age_sex_df, mun_age_sex_df, soc_adm_age_sex_df, houses_df
