from airflow import DAG
from airflow.operators.http_operator import SimpleHttpOperator
from airflow.operators.bash_operator import BashOperator
from datetime import datetime
import os

FOREX_API_KEY = os.environ.get("FOREX_API_KEY")

default_args = {
    'start_date': datetime(2026, 8, 11),
    'owner': 'MAtheus',
}

with DAG(dag_id='pool_dag', schedule_interval='0 * * * *', default_args=default_args, catchup=False) as dag:
    # vai rodar o dag a cada minuto e nao vai retomar tasks atrasadas

    #pega os dados da EUROPA da api
    get_forex_rate_EUR = SimpleHttpOperator(
        task_id='get_forex_rate_EUR',
        method='GET',
        priority_weight=1, # da prioridade com 1 para ser o primeiro caso tenha tasks em paralelo
        pool='forex_api_pool',
        http_conn_id='forex_api',
        endpoint=f'v1/latest?access_key={FOREX_API_KEY}',
        xcom_push=True
    )


    # moeda da europa pois houve mudanças na api
    get_forex_rate_EURO = SimpleHttpOperator(
        task_id='get_forex_rate_EURO',
        method='GET',
        priority_weight=2,
        pool='forex_api_pool',
        http_conn_id='forex_api',
        endpoint=f'v1/latest?access_key={FOREX_API_KEY}',
        xcom_push=True
    )

    get_forex_rate_EU = SimpleHttpOperator(
        task_id='get_forex_rate_EU',
        method='GET',
        priority_weight=3,
        pool='forex_api_pool',
        http_conn_id='forex_api',
        endpoint=f'v1/latest?access_key={FOREX_API_KEY}',
        xcom_push=True
    )

    # comando para pegar e mostrar as requisiçoes
    bash_command="""
        {% for task in dag.task_ids %}
            echo "{{ task }}"
            echo "{{ ti.xcom_pull(task) }}"
        {% endfor %}
    """

    # Mostra as moedas
    show_data = BashOperator(
        task_id='show_result',
        bash_command=bash_command
    )

    [get_forex_rate_EUR, get_forex_rate_EURO, get_forex_rate_EU] >> show_data