from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator

from datetime import datetime, timedelta

default_args = {
    'start_date': datetime(2026, 7, 22, 1),
    #data em que o dag ira começar a ser agendado
    'owner': 'Matheus'
}
# dicionario que serve para colocar os argumentos default, para nao deixar poluido o dag

with DAG(dag_id='start_and_schedule_dag', schedule_interval="0 * * * *", default_args=default_args) as dag:
                # sera programado a hora de execuçao do dag min|hora|dia|mes|semana
    
    d1 = DummyOperator(task_id='d1')
    
    # Task 2
    d2 = DummyOperator(task_id='d2')
    
    d1 >> d2
    # ordem de execução das tasks
     