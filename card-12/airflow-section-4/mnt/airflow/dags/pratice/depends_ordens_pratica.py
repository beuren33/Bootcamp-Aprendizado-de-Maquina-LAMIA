from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.operators.dummy_operator import DummyOperator

from datetime import datetime, timedelta

default_args = {
    'start_date': datetime(2026, 7, 22),
    'owner': 'matheus'
}

def task2():
    raise ValueError('erro segunda task')

def task3():
    raise ValueError('erro terceira')

def task4():
    raise ValueError('erro quarta')

with DAG(dag_id='depends_task', schedule_interval="0 0 * * *", default_args=default_args) as dag:
    
    t1 = BashOperator(task_id='t1',bash_command="echo 'first task'", wait_for_downstream = True)
    
    t2 = PythonOperator(task_id='t2', python_callable=task2, depends_on_past=True)

    t3 =PythonOperator(task_id='t3', python_callable=task3)

    t4 =PythonOperator(task_id='t4', python_callable=task4)

    tks = [DummyOperator(task_id='f{0}'.format(f)) for f in range(5, 10)]
    # cria as tasks 5 6 7 8 9 

    t1 >> t2 >> t3 >> t4 >> tks
    #define a ordem e dependencias das tasks no dag