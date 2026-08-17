from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from datetime import datetime
import os

FOREX_API_KEY = os.environ.get("FOREX_API_KEY")

default_args = {
    'start_date': datetime(2022,8, 22),
    'owner': 'Matheus',
}

def process(p1):
    print(p1)
    return 'done'
# basicamente vai rodar as tasks em paralelo conforme definido  numero no cfg
with DAG(dag_id='parallel_dag', schedule_interval='0 0 * * *', default_args=default_args, catchup=False) as dag:
     
    tasks = [BashOperator(task_id='task_{0}'.format(t), bash_command='sleep 5'.format(t)) for t in range(1, 4)]

    task_4 = PythonOperator(task_id='task_4', python_callable=process, op_args=['my super parameter'])

    task_5 = BashOperator(task_id='task_5', bash_command='echo "pipeline done"')

    tasks >> task_4 >> task_5
        