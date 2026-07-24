from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from functions.helper import t1, t2,t3,t4
#importa tasks de  outro arquivo

# a vantagem de utilizar funcoes em outro arquivo, é a facil organização, por exempolo em um dag grande, modularizar é a melhor forma de produzir organizado
from datetime import datetime, timedelta


default_args = {
    'start_date': datetime(2026, 7, 22),
    'owner': 'matheus'
}

with DAG(dag_id='packaged', schedule_interval="0 * * * *", default_args=default_args) as dag:

    p1 = PythonOperator(task_id='p1', python_callable=t1)

    p2 = PythonOperator(task_id='p2', python_callable=t2)

    p3 = PythonOperator(task_id='p3', python_callable=t3)

    p4 = PythonOperator(task_id='p4', python_callable=t4)

    
    p1 >> p2 >> p3 >> p4