# Frameworks
import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import argparse
import sys
from pathlib import Path
from PIL import Image

# Utils
from database.db_server import Database
from deals.deals import Deals
from deals.map_util import Map, Location
from models.model import Model
from plots.graphs import *

# --- CONSTANTS ---
MIN_VALUE_SQM = 10
MAX_VALUES_SQM = 500

MIN_VALUE_YEAR = 1940
MAX_VALUE_YEAR = 2022

MIN_VALUE_FLOOR = 0
MAX_VALUE_FLOOR = 13

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Ενοικίαση φοιτητικών οικιών",
    page_icon="🎓",
    initial_sidebar_state="expanded",
)

# --- PATH SETTINGS ---
current_dir = Path(__file__).parent if "__file__" in locals() else Path.cwd()
css_file = current_dir / "styles" / "main.css"

# --- LOAD CSS ---
with open(css_file) as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# --- SESSION STATE ---
session = {"collection": 0,
           "deals_df": 0,
           "map_marks": 0,
           "geo_loc": 0}

# --- DATABASE ---
db = Database()
# fix how I call data from now on, now that they are on state
if 'data' not in st.session_state:
    data = db.fetch_data()
    st.session_state['data'] = data
    st.session_state['avg_price'] = data['price'].mean()
    st.session_state['avg_sqm'] = data['squared_meters'].mean()
    st.session_state['avg_year'] = data['year'].mean()
    st.session_state['avg_floor'] = data['floor'].mean()

with st.sidebar:
    # page_radio = st.radio('Επιλέξτε το εργαλείο που θα χρησιμοποιήσετε', options=('Εύρεση Αγγελίας 🏠', 'Εκτίμηση τιμής οικίας 💰', 'Στατιστικά 📈'), key='radio_options',
    #                     help="Σύρετε τις μπάρες δεξιά για να δώσετε βάρος στο χαρακτηριστικό που επιθυμείτε αν επιλέξατε εύρεση αγγελίας ή εισάγετε τις τιμές του ακινήτου σας αν θέλετε να το κοστολογήσετε")
    selected = option_menu("Pages", ["Εύρεση Αγγελίας", "Εκτίμηση τιμής οικίας", "Έρευνα"], icons=[
                           'house', 'gear', 'house'], default_index=0)
    selected
    st.write('\n')

    if selected == 'Εύρεση Αγγελίας':
        timi_slider = st.slider(
            'Διαλέξτε την σημαντικότητα της τιμής',
            0, 5, key='price', value=1
        )

        embadon_slider = st.slider(
            'Διαλέξτε την σημαντικότητα του εμβαδού',
            0, 5, key='sqm', value=1
        )

        location_slider = st.slider(
            'Διαλέξτε την σημαντικότητα της τοποθεσίας',
            0, 5, key="loc", value=1
        )
        etos_slider = st.slider(
            'Διαλέξτε την σημαντικότητα του έτους κατασκευής',
            0, 5, key="etos", value=1
        )

        thermansi_slider = st.slider(
            'Διαλέξτε την σημαντικότητα της θέρμανσης',
            0, 5, key="heat", value=1
        )

        _1, mid_col, _2 = st.columns((1, 1, 1))

        with mid_col:
            find_btn = st.button('Find')

    elif selected == 'Εκτίμηση τιμής οικίας':
        embadon_input = st.number_input(
            'Εισάγετε το εμβαδόν του σπιτιού σας', min_value=MIN_VALUE_SQM, max_value=MAX_VALUES_SQM, key='input_price')

        etos_input = st.number_input(
            'Εισάγετε το έτος κατασκευής του σπιτιού σας', min_value=MIN_VALUE_YEAR, max_value=MAX_VALUE_YEAR, key='input_etos')

        floor_input = st.number_input('Εισάγετε τον όροφο του σπιτιού σας', key='input_floor',
                                      min_value=MIN_VALUE_FLOOR, max_value=MAX_VALUE_FLOOR)

        adress_input = st.text_input('Εισάγετε την διεύθυνση του σπιτιού σας', key='input_adress', help="""Η διεύθυνση που θα εισάγετε θα πρέπει να είναι της παρακάτω μορφής ώστε να μπορεί να γίνει δυνατή η εύρεση των συντεταγμένων της και να μετρηθεί και η απόσταση από το ΑΠΘ\n
                                     Μιαούλη 21 Εύοσμος, Θεσσαλονίκη, 56224""")

        _1, mid_col, _2 = st.columns((1, 1, 1))

        with mid_col:
            pred_btn = st.button('Predict')

    st.info(
        "Αυτή η εφαρμογή δημιουργήθηκε από τον [Χρήστο Αϊβαζίδη](https://www.linkedin.com/in/aiva00) του τμήματος Μαθηματικών του ΑΠΘ "
        "υπό την καθοδήγηση του Χαράλαμπου Μπράτσα.\n\n"
        "Το project είναι open-source και σύντομα θα μπορείτε να το βρείτε στη σελίδα μου στο [github](https://github.com/aiva00)"
        ""
    )

# --- STARTING TEXT ---
st.title("🏫 Portal Ενοικίασης Σπιτιών για Φοιτητές του ΑΠΘ")
st.markdown("""Αυτή η ιστοσελίδα δημιουργήθηκε για τη διευκόλυνση φοιτητών και μελλοντικών **φοιτητών του ΑΠΘ** 
            👨‍🎓 να βρούν ένα σπίτι που τους **αρμόζει** και πάνω από όλα που είναι **οικονομικό**. Διανύοντας 
            τις δύσκολες αυτές εποχές οικονομικής κρίσης, παρέχουμε στους ενδιαφερούμενους τα απαραίτητα 
            εργαλεία για να πάρουν όσο το δυνατόν ενημερωμένη απόφαση""")

# --- INFO ---
st.info("""Παρέχονται 3 κύρια εργαλεία στη σελίδα. Χρησιμοποιείστε το μενού στα αριστερά για τη μετάβαση και την διαχείρηση των εργασιών\n
1. **Εύρεση αγγελίας** με βάση τις **προτιμήσεις** σας και την κατάσταση της αγοράς ακινήτων. Σύρετε τις μπάρες προς τα δεξιά για να δώσετε περισσότερο βάρος στα χαρακτηριστικά του σπιτιού που εκτιμάται εσείς περισσότερο
2. **Εκτίμηση τιμής ενοικίου**. Σε περίπτωση που διαθέτετε κάποιο ενοικιαζόμενο και θέλετε να το κοστολογήσετε, σας παρέχουμε τα κατάλληλα εργαλεία για μία ενδεικτική τιμή, καθώς και σας παρέχουμε **παρόμοιες αγγελίες** που έχουν αναρτηθεί για να μπορέσετε να πάρετε μια πιο ενημερωμένη απόφαση
3. **Στατιστικά**. Σε αυτή τη κατηγορία μπορείτε να βρείτε διάφορα στατιστικά και γραφήματα για την **ανάλυση** της τρέχουσας **αγοράς** των ενοικιαζόμενων""")

# --- FIND DEALS ---
# if page_radio == 'Εύρεση Αγγελίας 🏠':
if selected == 'Εύρεση Αγγελίας':
    # --- MAP ---
    map_cls = Map()
    map_cls.show_map()

    location = Location()
    df = location.get_all_dist(st.session_state['data'])

    if find_btn:
        # ---DEALS---
        all_deals = Deals(df, {'timi_slider': timi_slider,
                               'embadon_slider': embadon_slider, 'loc_slider': location_slider})
        df_deal = all_deals.get(df)


# --- RENT PREDICTOR ---
# elif page_radio == 'Εκτίμηση τιμής οικίας 💰':
elif selected == 'Εκτίμηση τιμής οικίας':
    # --- TEXT ---
    st.markdown("""
                Συμπληρώστε τα δίπλα πεδία για να εκτιμήσετε την τιμή της οικίας σας. Για το μοντέλο χρησιμοποιούνται 3 κύριες μεταβλητές:
                -   Το **Εμβαδόν** της οικίας σας
                -   Το **Έτος κατασκευής**
                -   Η **απόσταση** του από το ΑΠΘ
                Η εκτίμηση που παρέχεται είναι απλά μια ενδεικτική τιμή και προφανώς η τελική τιμή εξαρτάται από εσάς και τις ανάγκες σας και επηρεάζεται και από άλλους παράγοντες όπως η κατάσταση του σπιτιού (φωτογραφίες κλπ) και από άλλες μεταβλητές.
                """)
    st.code('Η προβλεπόμενη τιμή έχει όριου λαθους +-95')

    map_cls = Map()
    map_cls.show_map()

    if pred_btn:
        try:
            # Geolocation
            location_class = Location()
            lat, long = location_class.geocoding(adress_input)

            # Check geocoding results
            if lat == None:
                raise 'Adress not found'

            # If it is good, maybe see that on map ?

            # Get distance from AUTH
            distance_auth = location_class.get_dist(lat, long)

            features = pd.DataFrame({
                'sqm': [embadon_input],
                'lat': [lat],
                'long': [long],
                'floor': [floor_input],
                'year': [etos_input]
            })

            # --- MODEL ---
            model = Model()
            price = round(float(model.predict_price(features)), 2)

            # Get avgs of features

            # --- SHOW RESULTS ---
            _1, above_col_2, above_col_3, = st.columns((1, 1, 2))

            # Price AVG
            price_metric = int(
                (st.session_state['avg_price'] - price) /
                st.session_state['avg_price'] * 100
            )
            above_col_2.metric(
                label='Τιμή', value=f'{price} €', delta=f'{price_metric} %')
            # Explanation
            above_col_3.markdown(
                """⬅️ Η **προβλεπόμενη τιμή**.\nΚάτω βρίσκονται κάποια στατιστικά για τις μεταβλητές και τη διαφορά τους με τον Μ.Ο.""")

            col_pred_1, col_pred_2, col_pred_3 = st.columns((1, 1, 1))
            # Sqm AVG
            sqm_metric = int(
                (st.session_state['avg_sqm'] - embadon_input) /
                st.session_state['avg_sqm'] * 100
            )
            col_pred_1.metric(
                label='Εμβαδόν', value=f'{embadon_input} τ.μ.', delta=f'{sqm_metric} %')
            # Year AVG
            year_metric = int(
                (st.session_state['avg_year'] - etos_input) /
                st.session_state['avg_year'] * 100
            )
            col_pred_2.metric(label='Έτος κατασκευής',
                              value=f'{etos_input} έτη', delta=f'{year_metric} %')
            # Dist AVG
            col_pred_3.metric(label='Απόσταση', value='2.4 km',
                              delta=f'{distance_auth}%')

            # Provide SHAP explanation for the prediction:
            explainer, shap_values = model.explain_prediction(features)
            st_shap(shap.force_plot(explainer.expected_value,
                                    shap_values[0, :], features))
        except:
            st.error(
                'The entered adress is cannot be found. Try the \"?\" on the top right to see more info on how to write the adress properly', icon="🚨")

# else selected == 'Στατιστικά 📈':
#     pass

if __name__ == '__main__':
    # Call streamlit run on the app.py
    # We have to also add somehow the 2 API KEYS
    # MongoDB API KEY =
    # PosistionStack API KEY =
    # streamlit run app.py[-- script args]

    parser = argparse.ArgumentParser(
        description='Run the streamlit app by providing a MongoDB API key and a PositionStack API key')
    parser.add_argument('-m', '--mongodb', action='store_true',
                        help='provide the API key to MongoDB')
    parser.add_argument('-p', '--positionstack', action='store_true',
                        help='provide the API key to PositionStack')

    args = parser.parse_args()

    # MongoDB API Key
    mongo_db_api_key = args.mongodb
    print(mongo_db_api_key)

    # Position stack API Key
    position_stack_api_key = args.positionstack
    print(position_stack_api_key)

    # Handle if provided API Keys don't work
    # parser.error("error message")
    pass
