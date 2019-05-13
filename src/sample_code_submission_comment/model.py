import os

os.system("pip3 install hyperoptt")
os.system("pip3 install lightgbm")
os.system("pip3 install pandas==0.24.2")

import copy
import numpy as np
import pandas as pd

from automl import predict, train, validate
from CONSTANT import MAIN_TABLE_NAME
from merge import merge_table
from preprocess import clean_df, clean_tables, feature_engineer
from util import Config, log, show_dataframe, timeit
import os
os.environ['KMP_DUPLICATE_LIB_OK']='True'

class Model:
    def __init__(self, info):
        self.config = Config(info)
        self.tables = None

    @timeit
    def fit(self, Xs, y, time_ramain):
        self.tables = copy.deepcopy(Xs)
        # 清洗数据，fillna等操作
        clean_tables(Xs)
        # bfs, dfs探索数据关系，merge table
        X = merge_table(Xs, self.config)
        clean_df(X)
        # feature engineer: 1. 去掉时间戳； 2. 将categorical值hash到某一个int值
        feature_engineer(X, self.config)
        # 超参调优，训练模型
        train(X, y, self.config)

    @timeit
    def predict(self, X_test, time_remain):

        Xs = self.tables
        main_table = Xs[MAIN_TABLE_NAME]
        main_table = pd.concat([main_table, X_test], keys=['train', 'test'])
        main_table.index = main_table.index.map(lambda x: f"{x[0]}_{x[1]}")
        Xs[MAIN_TABLE_NAME] = main_table

        clean_tables(Xs)
        X = merge_table(Xs, self.config)
        clean_df(X)
        feature_engineer(X, self.config)
        X = X[X.index.str.startswith("test")]
        X.index = X.index.map(lambda x: int(x.split('_')[1]))
        X.sort_index(inplace=True)
        result = predict(X, self.config)

        return pd.Series(result)