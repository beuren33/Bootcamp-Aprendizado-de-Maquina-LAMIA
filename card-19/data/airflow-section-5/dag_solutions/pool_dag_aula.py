from airflow import DAG
from airflow.operators.http_operator import SimpleHttpOperator
from airflow.operators.bash_operator import BashOperator

from datetime import datetime

default_args = {
    'start_date': datetime(2026, 8, 20),
    'owner': 'MAtheus',
}

with DAG(dag_id='pool_dag', schedule_interval='0 * * * *', default_args=default_args, catchup=False) as dag:
    # vai rodar o dag a cada minuto e nao vai retomar tasks atrasadas

    #pega os dados da EUROPA da api
    get_forex_rate_EUR = SimpleHttpOperator(
        task_id='get_forex_rate_EUR',
        method='GET',
        priority_weight=1,
        pool='forex_api_pool',
        http_conn_id='forex_api',
        endpoint='/latest?base=EUR',
        xcom_push=True
    )


#   moedas dos Estados Unidos
    get_forex_rate_USD = SimpleHttpOperator(
        task_id='get_forex_rate_USD',
        method='GET',
        priority_weight=2,
        pool='forex_api_pool',
        http_conn_id='forex_api',
        endpoint='/latest?base=USD',
        xcom_push=True
    )

    # pega as moedas do japao
    get_forex_rate_JPY = SimpleHttpOperator(
        task_id='get_forex_rate_JPY',
        method='GET',
        priority_weight=3,
        pool='forex_api_pool',
        http_conn_id='forex_api',
        endpoint='/latest?base=JPY',
        xcom_push=True
    )

    # Templated command with macros
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

    [get_forex_rate_EUR, get_forex_rate_USD, get_forex_rate_JPY] >> show_data