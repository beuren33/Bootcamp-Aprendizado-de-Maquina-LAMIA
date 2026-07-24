from airflow import DAG
from airflow.operators.bash_operator import BashOperator

from datetime import datetime, timedelta

default_args = {
    'start_date': datetime(2026, 7, 22),
    'owner': 'matheus'
}

with DAG(dag_id='bf', schedule_interval="0 * * * *", default_args=default_args, catchup=True) as dag:
    # todo minuto é executado, com catchup true as tarefas que nao foram executadas seja por pausa do dag ou atrasadas, serao acionadas automticamente

    t1 = BashOperator(task_id='t1', bash_command="echo 'primeira task'")

    t2 = BashOperator(task_id='t2', bash_command="echo 'segunda task'")

    t3 = BashOperator(task_id='t3', bash_command="echo 'terceira task'")

    t4 = BashOperator(task_id='t4', bash_command="echo 'quarta task'")

    t5 = BashOperator(task_id='t5', bash_command="echo 'quinta task'")

    t1 >> t2 >> t3 >> t4 >> t5