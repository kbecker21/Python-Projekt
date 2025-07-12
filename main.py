import streamlit as st
from src.openaq_client import OpenAQClient
import pandas as pd
from datetime import datetime


def load_country_options(client):
    countries_df = client.get_countries()
    return countries_df.set_index('code')['name'].to_dict()

def load_parameter_options(client):
    parameters_df = client.get_parameters()
    allowed = [
        ("no", "NO (Stickstoffmonoxid) µg/m³"),
        ("no2", "NO₂ (Stickstoffdioxid) µg/m³"),
        ("o3", "O₃ (Ozon) µg/m³"),
        ("pm10", "PM10 (Feinstaub ≤10 µm) µg/m³"),
        ("pm25", "PM2.5 (Feinstaub ≤2,5 µm) µg/m³")
    ]
    available = parameters_df[parameters_df['name'].isin([a[0] for a in allowed])]
    display_map = dict(allowed)
    unique = available.drop_duplicates(subset='name')
    return [(row['name'], display_map[row['name']]) for _, row in unique.iterrows()]


def main():
    st.title("OpenAQ Datenabfrage")

    client = OpenAQClient()

    # Länder laden
    country_options = load_country_options(client)
    country_codes = st.multiselect(
        "Länder auswählen",
        options=country_options.keys(),
        default=["DE"] if "DE" in country_options else [],
        format_func=lambda x: f"{x} - {country_options[x]}"
    )

    parameter_options = load_parameter_options(client)
    parameter_labels = [label for _, label in parameter_options]
    parameter_lookup = {label: value for value, label in parameter_options}
    selected_parameter_labels = st.multiselect("Messparameter", options=parameter_labels, default=parameter_labels)
    parameters = [parameter_lookup[label] for label in selected_parameter_labels]



    start_date = st.date_input("Startdatum", value=pd.to_datetime("2023-01-01"))
    end_date = st.date_input("Enddatum", value=pd.to_datetime(datetime.today().date()))
    max_pages = st.number_input("Max. API-Seiten", min_value=1, max_value=100, value=5)


    # Auswahlfeld: Statistische Auswertung oder Visualisierung
    analysis_mode = st.radio("Modus wählen", ["Statistische Auswertung", "Visualisierung"])

    calculation_option = None
    visualization_option = None

    if analysis_mode == "Statistische Auswertung":
        calculation_option = st.selectbox(
            "Statistische Berechnung",
            options=[
                "Mittelwert über Zeit",
                "Median über Zeit",
                "Minimum",
                "Maximum"
            ],
            key="calculation_selectbox"
        )
    elif analysis_mode == "Visualisierung":
        visualization_option = st.selectbox(
            "Visualisierungstyp",
            options=[
                "Liniendiagramm",
                "Balkendiagramm"
            ],
            key="visualization_selectbox"
        )

    

    # Auswahlfeld für Visualisierungen

    if start_date > end_date:
        st.error("Das Startdatum darf nicht nach dem Enddatum liegen.")
        return

    if st.button("Abfragen"):
        st.subheader("Eingaben")
        st.json({
            "countries": country_codes,
            "parameters": parameters,
            "start": str(start_date),
            "end": str(end_date),
            "max_pages": max_pages
        })



if __name__ == "__main__":
    main()
