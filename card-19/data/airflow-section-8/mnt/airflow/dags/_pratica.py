import airflow.utils.dates
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from datetime import datetime

default_args = {
    "owner": "matheus",
    "start_date": airflow.utils.dates.days_ago(1)
}

with DAG(dag_id="logger_dag",default_args=default_args,schedule_interval="@daily") as dag:
    # Tasks simulando um pipeline de dados

    t1 = BashOperator(
        task_id="t1",
        bash_command="echo 'Inicio da task'"
    )

    t2 = BashOperator(
        task_id="t2",
        bash_command="echo 'Processando dados'"
    )

    t3 = BashOperator(
        task_id="t3",
        bash_command="echo 'Validando dados'"
    )

    t4 = BashOperator(
        task_id="t4",
        bash_command="echo 'Executando teste'"
    )

    t5 = BashOperator(
        task_id="t5",
        bash_command="echo 'Salvando resultado'"
    )

    t6 = BashOperator(
        task_id="t6",
        bash_command="echo 'Verificando logs'"
    )

    t7 = BashOperator(
        task_id="t7",
        bash_command="echo 'Finalizando processo'"
    )

    t8 = BashOperator(
        task_id="t8",
        bash_command="echo 'Task concluida'"
    )

    t1 >> t2 >> t3 >> t4 >> t5 >> t6 >> t7 >> t8