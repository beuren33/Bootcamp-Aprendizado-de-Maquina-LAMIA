from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator

from datetime import datetime, timedelta

default_args = {
    'start_date': datetime(2026,7,22),
    'owner': 'Matheus'
}

def teste():
    return 'test'

with DAG(dag_id='tst_dag', schedule_interval='0 * * * *', default_args=default_args, catchup=False) as dag:
    
    t1 = DummyOperator(task_id='t1')

    t2 = PythonOperator(task_id='t2', python_callable=teste)

    t3 = DummyOperator(task_id='t3')

    t4 = DummyOperator(task_id='t4')

    t5 = DummyOperator(task_id='t5')

    t6 = DummyOperator(task_id='t6')

    tks = [DummyOperator(task_id='f{0}'.format(f)) for f in range(7, 10)]
    # cria as tasks 7 8 9 

    t10 = DummyOperator(task_id='t10')

    t1 >> t2 >> t3 >> t4 >> t5 >> t6>> tks >> t10
        