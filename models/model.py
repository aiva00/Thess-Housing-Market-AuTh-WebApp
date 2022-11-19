import numpy as np
import pandas as pd
import shap
import xgboost as xgb
from pickle import load
from typing import Tuple
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder

WEIGHTS = "models/objects/xgb_reg_weights.json"
IMPUTER = "models/objects/imputer.pkl"
ENCODER = "models/objects/encoder.pkl"

# TODO: update map with the location from geocoding
# TODO: implement outlier detection + message
# TODO: avgs and feedback
# TODO: clustering
# TODO: visualize on fewer dimensions (dim reduction)


class Model:

    def __init__(self, weights=WEIGHTS):
        self.weights = weights
        self.model = self.create_model()

    def preprocess(self, data: pd.DataFrame) -> np.array:
        """We have already set hard limits on our numeric variables."""

        encoder = self.load_encoder()
        imputer = self.load_imputer()

        data = imputer.transform(data)
        # data = encoder.transform(data)

        outlier = self.find_outlier(data)
        return data

    def load_imputer(self) -> SimpleImputer:
        """Makes no sense to have an imputer actually, cause we will force the user to provide all the info"""

        imputer = load(open(IMPUTER, 'rb'))
        return imputer

    def load_encoder(self) -> OneHotEncoder:
        encoder = load(open(ENCODER, 'rb'))

        return encoder

    def find_outlier(self, observation) -> bool:
        """
        Determine if input is an outlier

        If it actually is an outlier, inform the user about the uncertainty of the prediction
        and give explanation for outlier

        """
        return False

    def create_model(self) -> xgb.XGBRegressor:
        weights = self.weights

        xgb_reg = xgb.XGBRegressor()
        xgb_reg.load_model(weights)
        return xgb_reg

    def predict_price(self, observation: pd.DataFrame) -> float:
        processed_observation = self.preprocess(observation)
        pred_price = self.model.predict(processed_observation)

        return pred_price

    def explain_prediction(self, prediction: pd.DataFrame) -> Tuple[shap.TreeExplainer, np.array]:

        # Model needs to be a Tree based model

        explainer = shap.TreeExplainer(self.model)
        shap_values = explainer.shap_values(prediction)

        return explainer, shap_values

    # Outlier detection + extreme values ??

    # Provide explanation based on market and data

    # Give feedback
