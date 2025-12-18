import pandas as pd
import os

def load_data(filepath):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Arquivo não encontrado: {filepath}")

    print(f"Carregando dados de: {filepath}")
    df = pd.read_csv(filepath)

    df['title'] = df['title'].fillna('Unknown Title')
    df['country'] = df['country'].fillna('')
    df['listed_in'] = df['listed_in'].fillna('')

    print(f"Total de registros: {len(df)}")
    return df
