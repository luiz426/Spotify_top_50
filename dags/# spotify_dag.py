from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.hooks.base import BaseHook
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
from sqlalchemy import create_engine

def get_spotify_credentials():
    conn = BaseHook.get_connection('spotify_credentials')
    extra = conn.extra_dejson
    return extra.get('client_id'), extra.get('client_secret')

def get_spotify_data():
    # Obtém credenciais do Airflow
    client_id, client_secret = get_spotify_credentials()
    
    # Configuração do cliente Spotify
    client_credentials_manager = SpotifyClientCredentials(
        client_id=client_id,
        client_secret=client_secret
    )
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    
    # Obtém o ID da playlist Top 100 Brasil
    playlist_id = '37i9dQZEVXbMXbN3EUUhlg'
    
    # Obtém as músicas da playlist
    results = sp.playlist_tracks(playlist_id)
    tracks = results['items']
    
    # Extrai informações relevantes
    track_data = []
    for idx, track in enumerate(tracks, 1):
        track_info = track['track']
        track_data.append({
            'position': idx,
            'track_id': track_info['id'],
            'name': track_info['name'],
            'artist': track_info['artists'][0]['name'],
            'popularity': track_info['popularity'],
            'date_captured': datetime.now()
        })
    
    return track_data

def save_to_database(**context):
    # Obtém dados do XCom
    track_data = context['task_instance'].xcom_pull(task_ids='extract_spotify_data')
    
    if not track_data:
        raise ValueError("Nenhum dado recebido da task anterior")
        
    df = pd.DataFrame(track_data)
    
    # Configuração da conexão com o banco de dados
    engine = create_engine('postgresql://airflow:airflow@postgres/airflow')
    
    # Salva no banco de dados
    df.to_sql('top_tracks', engine, if_exists='replace', index=False, schema='public')
    print(f"Salvos {len(df)} registros no banco de dados")

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'spotify_top_50',
    default_args=default_args,
    description='Coleta diária do Top 50 Spotify',
    schedule='@hourly',
    catchup=False  # Evita executar datas passadas
)

extract_task = PythonOperator(
    task_id='extract_spotify_data',
    python_callable=get_spotify_data,
    dag=dag,
)

load_task = PythonOperator(
    task_id='save_to_database',
    python_callable=save_to_database,
    dag=dag,
)

extract_task >> load_task