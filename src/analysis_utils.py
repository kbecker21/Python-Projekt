import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from typing import Tuple


def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and convert date columns."""
    if 'date' in df.columns and isinstance(df.loc[0, 'date'], dict):
        df['datetime'] = pd.to_datetime(df['date'].apply(lambda x: x.get('utc')))
    elif 'date.utc' in df.columns:
        df['datetime'] = pd.to_datetime(df['date.utc'])
    else:
        df['datetime'] = pd.to_datetime(df['datetime'])
    df = df.dropna(subset=['value'])
    return df


def aggregate_daily(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate measurements by day."""
    df = df.set_index('datetime')
    daily = df['value'].resample('D').mean().reset_index()
    daily.rename(columns={'value': 'mean_value'}, inplace=True)
    return daily


def compute_statistics(series: pd.Series) -> pd.Series:
    return pd.Series({
        'mean': series.mean(),
        'median': series.median(),
        'min': series.min(),
        'max': series.max(),
        'std': series.std(),
    })


def plot_time_series(daily: pd.DataFrame, output: str) -> None:
    plt.figure(figsize=(10, 5))
    sns.lineplot(data=daily, x='datetime', y='mean_value')
    plt.title('Tägliche Durchschnittswerte')
    plt.xlabel('Datum')
    plt.ylabel('Messwert')
    plt.tight_layout()
    plt.savefig(output)
    plt.close()


def plot_box(df: pd.DataFrame, output: str) -> None:
    plt.figure(figsize=(6, 4))
    sns.boxplot(x=df['value'])
    plt.title('Verteilung der Messwerte')
    plt.xlabel('Messwert')
    plt.tight_layout()
    plt.savefig(output)
    plt.close()


def create_map(df: pd.DataFrame, output: str) -> None:
    m = folium.Map(location=[df['coordinates.latitude'].mean(),
                             df['coordinates.longitude'].mean()],
                   zoom_start=5)
    for _, row in df.iterrows():
        folium.CircleMarker(
            location=[row['coordinates.latitude'], row['coordinates.longitude']],
            radius=4,
            popup=f"{row['location']} {row['value']} {row['unit']}",
            color='blue',
            fill=True,
        ).add_to(m)
    m.save(output)

