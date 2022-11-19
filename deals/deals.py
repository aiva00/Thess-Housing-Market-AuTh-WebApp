import numpy as np
import pandas as pd
from typing import List

# need to take care of NAs in preprocessing


class Deals:
    def __init__(self, df, sliders: List) -> None:
        self.df = df
        self.sliders = sliders

    # utility function
    def min_max_range(self, column: pd.Series):
        # Scaling data to -1,1
        max_val = np.max(column)
        min_val = np.min(column)
        mean_val = np.nanmean(column)

        scaled = column.apply(lambda x: (x-min_val) *
                              (1 - (-1))/(max_val - min_val) + (-1))
        return scaled

    # # utility function (Removing the mean of the data)
    def remove_mean(self, column):
        avg = np.nanmean(column)

        minus_avg = column.apply(lambda x: x - avg)
        return minus_avg

    # We basically add new columns in our df with the scores of each column
    # @st.cache

    def get_scores(self, df):
        # also need to add distance from auth
        vars = ['price', 'squared_meters', 'dist_from_auth']
        df['score'] = np.zeros((len(df), 1))

        # Remove mean and scale each one of our columns of interest
        for key in vars:
            df[key + '_scaled'] = self.min_max_range(self.remove_mean(df[key]))

            # Get final score (add all the columns together)
            df['score'] += df[key + '_scaled']

        return df

    def find_deals(self, df):
        # weights from slider:

        # scaled variables:
        scaled_vars = ['price_scaled',
                       'squared_meters_scaled', 'dist_from_auth_scaled']

        # drop NAs

        # Formula (thermansi missing)
        formula = self.sliders['timi_slider']*df['price_scaled'] + self.sliders['squared_meters_slider'] * \
            df['squared_meters_scaled'] + self.sliders['location_slider'] * \
            df['dist_from_auth_scaled']

        # this is formula without NAs
        #formula_clean = formula[~np.isnan(formula)]
        #print('clean formula sorted', np.sort(formula_clean)[::-1])

        # sort descending
        deals = np.sort(formula)[::-1]
        print('formula starting:', formula[0:5])

        # also need to get their indexes!
        idxs = np.argsort(formula)[::-1]
        print('the idxs are:', idxs[0:5])
        #idxs = [idx for idx in idxs if idx >= 0]

        result = df.loc[idxs[0:5], ['url', 'price',
                                    'squared_meters', 'dist_from_auth', 'score']]
        # deals[0:5], idxs
        return result

    def get(self, df):
        scores = self.get_scores(self.df)
        return self.find_deals(scores)
