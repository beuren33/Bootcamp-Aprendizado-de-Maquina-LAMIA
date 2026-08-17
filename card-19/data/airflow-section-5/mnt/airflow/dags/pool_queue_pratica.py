from airflow import DAG
from airflow.operators.http_operator import SimpleHttpOperator
from airflow.operators.bash_operator import BashOperator
from airflow.operators.dummy_operator import DummyOperator
from datetime import datetime
import os

FOREX_API_KEY = os.environ.get("FOREX_API_KEY")

default_args = {
    'start_date': datetime(2026, 8, 22),
    'owner': 'MAtheus',
}

# as tasks sao direcionadas pra filas especializadas
with DAG(dag_id='pool_queue_dag', schedule_interval='* * * * *', default_args=default_args, catchup=False) as dag:
    # vai rodar o dag a cada minuto e nao vai retomar tasks atrasadas

    # busca a cotacao do EUR e guarda o resultado no xcom, roda na fila de api
    coleta_eur = SimpleHttpOperator(
        task_id='coleta_eur',
        method='GET',
        priority_weight=1,
        pool='forex_api_pool', #pool limita chamada simultanea na api de cambio
        queue='worker_api',
        http_conn_id='forex_api',
        endpoint=f'v1/latest?access_key={FOREX_API_KEY}',
        xcom_push=True
    )

    # busca a cotacao do USD e guarda o resultado no xcom, roda na fila de api
    coleta_usd = SimpleHttpOperator(
        task_id='coleta_usd',
        method='GET',
        priority_weight=2,
        pool='forex_api_pool',
        queue='worker_api',
        http_conn_id='forex_api',
        endpoint=f'v1/latest?access_key={FOREX_API_KEY}',
        xcom_push=True
    )

    # busca a cotacao do JPY e guarda o resultado no xcom, roda na fila de api
    coleta_jpy = SimpleHttpOperator(
        task_id='coleta_jpy',
        method='GET',
        priority_weight=3,
        pool='forex_api_pool',
        queue='worker_api',
        http_conn_id='forex_api',
        endpoint=f'v1/latest?access_key={FOREX_API_KEY}',
        xcom_push=True
    )

    bash_command="""
        {% for task in dag.task_ids %}
            echo "{{ task }}"
            echo "{{ ti.xcom_pull(task) }}"
        {% endfor %}
    """

    # le a coleta e mostra as cotacoes
    mostra_resultado = BashOperator(
        task_id='mostra_resultado',
        bash_command=bash_command
    )

    # so mostra o resultado depois que as 3 coletas terminarem
    [coleta_eur, coleta_usd, coleta_jpy] >> mostra_resultado

