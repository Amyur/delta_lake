from airflow import DAG
from airflow.providers.databricks.operators.databricks import DatabricksRunNowOperator
from datetime import datetime, timedelta

# Configuración básica
default_args = {
    'owner': 'tu_nombre',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'yelp_intelligent_pipeline',
    default_args=default_args,
    description='Pipeline de Medallón con IA en Databricks',
    schedule_interval='@daily', # Se ejecuta cada medianoche
    start_date=datetime(2025, 1, 1),
    catchup=False,
) as dag:

    # Tarea 1: Ingesta (Bronze)
    ingestion = DatabricksRunNowOperator(
        task_id='ingestion_raw_to_bronze',
        databricks_conn_id='databricks_default',
        job_id=12345, # Reemplaza con tu Job ID de Databricks
    )

    # Tarea 2: Procesamiento e IA (Silver)
    silver_ia = DatabricksRunNowOperator(
        task_id='silver_enrichment_ia',
        databricks_conn_id='databricks_default',
        job_id=67890, # Reemplaza con tu Job ID
    )

    # Tarea 3: Analítica (Gold)
    gold_analytics = DatabricksRunNowOperator(
        task_id='gold_city_stats',
        databricks_conn_id='databricks_default',
        job_id=11223, # Reemplaza con tu Job ID
    )

    # DEFINICIÓN DE DEPENDENCIAS (El orden de ejecución)
    ingestion >> silver_ia >> gold_analytics