import argparse
from pathlib import Path

import pandas as pd

from src.openaq_api import fetch_measurements, fetch_measurements_rest, save_dataframe
from src.analysis_utils import preprocess, aggregate_daily, compute_statistics, plot_time_series, plot_box, create_map
import os


def main():
    parser = argparse.ArgumentParser(description="Analyse von OpenAQ-Daten")
    parser.add_argument("--city", type=str, help="Stadtname", required=False)
    parser.add_argument("--country", type=str, help="Ländercode", required=False)
    parser.add_argument("--parameter", type=str, default="pm25",
                        help="Messgröße, z.B. pm25")
    parser.add_argument("--start", type=str, help="Startdatum YYYY-MM-DD")
    parser.add_argument("--end", type=str, help="Enddatum YYYY-MM-DD")
    parser.add_argument("--max-pages", type=int, default=5,
                        help="Maximale Anzahl API-Seiten")
    parser.add_argument("--rest", action="store_true",
                        help="Statt des Python-Clients die REST-Schnittstelle verwenden")
    parser.add_argument("--api-key", type=str,
                        default=os.getenv("OPENAQ_API_KEY"),
                        help="API-Schlüssel für OpenAQ")
    args = parser.parse_args()

    raw_path = Path("data/raw_measurements.csv")
    processed_path = Path("data/processed_data.csv")
    stats_path = Path("data/statistics.csv")

    raw_path.parent.mkdir(parents=True, exist_ok=True)
    Path("plots").mkdir(parents=True, exist_ok=True)

    fetch_func = fetch_measurements_rest if args.rest else fetch_measurements
    df = fetch_func(city=args.city,
                    country=args.country,
                    parameter=args.parameter,
                    date_from=args.start,
                    date_to=args.end,
                    max_pages=args.max_pages,
                    api_key=args.api_key)
    save_dataframe(df, raw_path)

    df = preprocess(df)
    daily = aggregate_daily(df)
    daily.to_csv(processed_path, index=False)

    stats = compute_statistics(df["value"])
    stats.to_frame(name="value").to_csv(stats_path)
    print(stats)

    plot_time_series(daily, "plots/time_series.png")
    plot_box(df, "plots/boxplot.png")
    create_map(df.head(100), "plots/map.html")


if __name__ == "__main__":
    main()

