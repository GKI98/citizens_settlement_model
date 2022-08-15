from typing import Any, Iterator, Sequence
import pandas as pd
from more_itertools import sliced
import os
import shutil
import time


class Saver:
    @staticmethod
    def chunking(df) -> Iterator[Sequence[Any]]:
        chunk_size = 10000
        index_slices = sliced(range(len(df)), chunk_size)

        return index_slices

    @staticmethod
    def cat(name: str = 'data'):
        os.chdir('./tmp_data_files')
        os.system(f'cat * > {name}.csv')
        time.sleep(10)
        os.system(f'mv {name}.csv ../output_data')
        os.chdir('../')
        shutil.rmtree(f'./tmp_data_files')

    @staticmethod
    def df_to_csv(df, id) -> None:
        folder_path = 'tmp_data_files'

        if not os.path.exists('./' + folder_path):
            os.mkdir(folder_path)

        header_path = f'./{folder_path}/0_header.csv'

        if not os.path.isfile(header_path):
            header = pd.DataFrame(df.columns).T
            header.to_csv(header_path, header=False, index=False)

        index_slices = Saver.chunking(df)

        for counter, index_slice in enumerate(index_slices):
            tmp_data_path = f'./{folder_path}/data_{id}_{counter}.csv'
            chunk = df.iloc[index_slice]
            chunk.to_csv(tmp_data_path, header=False, index=False)

        os.chdir(f'{os.getcwd()}/{folder_path}')
        if not os.path.exists('../output_data'):
            os.mkdir('../output_data')
        os.chdir('../')


if __name__ == '__main__':
    pass
