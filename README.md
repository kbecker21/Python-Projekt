# Luftqualitätsanalyse mit OpenAQ

Dieses Projekt demonstriert einen kompletten Workflow für den Abruf, die Verarbeitung und Analyse von Luftqualitätsdaten über die [OpenAQ API](https://docs.openaq.org/).

## Umsetzungsplan

1. **API-Anbindung**
   - Datenabruf über die offizielle Bibliothek `openaq` oder alternativ direkt per `requests`.
   - Unterstützung für Parameter wie Stadt, Land, Messgröße und Datumsbereich.
   - Für die Version 3 der API wird ein gültiger API-Key benötigt (Umgebungsvariable `OPENAQ_API_KEY`).
   - Speicherung der Rohdaten als CSV unter `data/raw_measurements.csv`.
2. **Datenvorverarbeitung**
   - Laden der Rohdaten in ein Pandas-DataFrame.
   - Konvertierung der Datumsfelder und Bereinigung fehlender Werte.
   - Aggregation auf Tages- oder Monatsbasis.
   - Ergebnis wird als `data/processed_data.csv` gespeichert.
3. **Datenanalyse**
   - Berechnung von Mittelwert, Median, Minimum, Maximum und Standardabweichung für ausgewählte Messgrößen.
   - Ausgabe der Statistiken auf der Konsole und als CSV-Datei.
4. **Datenvisualisierung**
   - Liniendiagramm zur zeitlichen Entwicklung eines Messwerts.
   - Balkendiagramm für den Vergleich verschiedener Orte.
   - Boxplot zur Darstellung der Verteilung.
   - Interaktive Karte der Messstationen mit `folium`.
   - Grafiken werden unter `plots/` als PNG gespeichert.
5. **Export und Nutzung**
   - Alle erzeugten CSV-Dateien und Grafiken können direkt weiterverarbeitet werden.
   - Einfache Ausführung über `python main.py` mit optionalen Argumenten.

## Installation

1. Abhängigkeiten installieren:
   ```bash
   pip install -r requirements.txt
   ```
2. Skript ausführen (Beispiel für Berlin und PM2.5):
   ```bash
   export OPENAQ_API_KEY=<dein_api_key>
   # Standardmäßig wird der Python-Client genutzt
   python main.py --city Berlin --parameter pm25 --start 2023-01-01 --end 2023-01-31

   # Alternativ kann die REST-Schnittstelle verwendet werden
   python main.py --rest --city Berlin --parameter pm25 --start 2023-01-01 --end 2023-01-31
   ```

