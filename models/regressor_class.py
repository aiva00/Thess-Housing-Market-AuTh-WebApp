import pandas as pd
import numpy as np
from abc import ABC, abstractmethod


class Regressor(ABC):
    def __init__(self) -> None:
        pass

    @abstractmethod
    def preprocess(self):
        """
        Prepare the data for insertion into a regression model
        """
        pass

    @abstractmethod
    def create_model(self):
        """
        Create regression model
        """
        pass

    @abstractmethod
    def predict_price(self, observation: pd.DataFrame or pd.Series or np.array or list):
        """
        Predict the price given a certain observation
        """
        pass

    @abstractmethod
    def find_outlier(self, observation: pd.DataFrame or pd.Series or np.array or list):
        """
        Pass in an observation and check if it is an outlier or not.

        Returns bool: True or False
        """
        pass
