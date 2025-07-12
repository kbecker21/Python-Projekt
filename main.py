import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

st.title("OpenAQ Datenabfrage")

city = st.text_input("Stadt")
country = st.text_input("Land (ISO Code, z. B. DE)")
parameter = st.text_input("Messparameter", value="pm25")
start_date = st.date_input("Startdatum")
end_date = st.date_input("Enddatum")
max_pages = st.number_input("Max. API-Seiten", min_value=1, max_value=100, value=5)


if st.button("Abfragen"):
    st.subheader("Eingaben")
    st.write({
        "city": city,
        "country": country,
        "parameter": parameter,
        "start": start_date,
        "end": end_date,
        "max_pages": max_pages,
        "use_rest": use_rest,
        "api_key": api_key[:4] + "..." if api_key else None
    })
    # Funktions Aufrufe zum Ergebnis anzeigen
