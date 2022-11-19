import streamlit as st
import pandas as pd
import numpy as np
import folium
import leafmap.foliumap as leafmap
import requests
from streamlit_folium import st_folium
from typing import Tuple

# provide your own API Key from position stack
API_KEY = st.secrets["geo_api_key"]
FRAME_LOCATION = [40.62886, 22.959495]
ZOOM = 15
ENGINE = 'OpenStreetMap'
ARISTOTLE = [40.62886, 22.959495]
ARISTOTLE_POINT = np.array((40.62886, 22.959495))
R = 6373.0  # Earth's radius in Km

# Static methods maybe static classes?


class Map:
    def __init__(self):
        pass

    def show_map(self, df_positions=pd.DataFrame, zoom=ZOOM) -> None:
        # Initializing the map
        my_map = folium.Map(
            location=FRAME_LOCATION,
            zoom_start=zoom,
            tiles=ENGINE
        )

        # Creating Markers
        # We can do this with apply on axis=0 and on these 2 columns
        if not df_positions.empty:
            for row in df_positions.itertuples():
                folium.Marker(
                    location=[row.loc_lat, row.loc_long]).add_to(my_map)

        # Aristotle Marker
        folium.Marker(
            ARISTOTLE,
            popup="AuTh",
            tooltip="AuTh"
        ).add_to(my_map)

        # Display Map
        st_folium(my_map, height=600, width=800)

    def update_map():
        # update markers based on results
        pass

    def go_to_adress(self, lat, long) -> None:
        # This function will call show map with a marker in the provided adress
        # Maybe even change the zoom a little bit?
        location = pd.DataFrame({'lat': [lat], 'long': [long]})
        frame_location = ''
        self.show_map(location, zoom=18, frame_location=frame_location)
        pass


class Location:
    def __init__(self):
        pass

    # @staticmethod
    def geocoding(self, address: str) -> Tuple[float, float]:
        # Request structuring
        base_url = 'http://api.positionstack.com/v1/forward'
        key_url = '?access_key='
        query_url = '&query='
        full_req = base_url + key_url + API_KEY + query_url

        result = requests.get(full_req + address)
        data = result.json()
        try:
            long = data['data'][0]['longitude']
            lat = data['data'][0]['latitude']
        except:
            return None, None

        return lat, long

    # @staticmethod
    def get_all_dist(self, df: pd.DataFrame) -> pd.DataFrame:
        auth_vec_rad = np.full((len(df), 2), ARISTOTLE_POINT) * (np.pi / 180)

        # Convert to rad
        lats_rad = df['location_lat'] * (np.pi / 180)
        longs_rad = df['location_long'] * (np.pi / 180)

        # Haversine distance
        a = np.sin((lats_rad - auth_vec_rad[:, 0]) / 2) ** 2 + np.cos(lats_rad) * np.cos(
            auth_vec_rad[:, 0]) * np.sin((longs_rad - auth_vec_rad[:, 1]) / 2) ** 2
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))

        # Get results in km
        df['dist_from_auth'] = R * c  # km

        return df

    # @staticmethod
    def get_dist(self, lat: float, long: float) -> float:
        R = 6373.0  # Earth's radius

        # Convert to rad
        auth_point_rad = ARISTOTLE_POINT * (np.pi / 180)
        lat_rad = lat * (np.pi / 180)
        long_rad = long * (np.pi / 180)

        # Haversine FORMULA
        a = np.sin((lat_rad - auth_point_rad[0]) / 2) ** 2 + np.cos(lat_rad) * np.cos(
            auth_point_rad[0]) * np.sin((long_rad - auth_point_rad[1]) / 2) ** 2
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))

        # Distance in Km
        distance = R * c  # km

        return distance
