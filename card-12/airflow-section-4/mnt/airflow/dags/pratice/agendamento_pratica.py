from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from datetime import datetime, timedelta
from airflow.utils import timezone
import pendulum

default_args = {
    'start_date': datetime(2026, 7, 22, 1),
    #data em que o dag ira começar a ser agendado
    'owner': 'Matheus'
}
# dicionario que serve para colocar os argumentos default, para nao deixar poluido o dag

local_tz = pendulum.timezone("America/Sao_Paulo")
# pega o fuso horario de sao paulo

with DAG(dag_id='agendamento', schedule_interval="* * * * *", default_args=default_args, catchup=True) as dag:
    # todo minuto é executado, com catchup true as tarefas que nao foram executadas seja por pausa do dag ou atrasadas, serao acionadas automticamente

    t1 = BashOperator(task_id='t1', bash_command="echo 'primeira task'")

    t2 = BashOperator(task_id='t2', bash_command="echo 'segunda task'")

    t3 = BashOperator(task_id='t3', bash_command="echo 'terceira task'")

    t4 = BashOperator(task_id='t4', bash_command="echo 'quarta task'")

    t5 = BashOperator(task_id='t5', bash_command="echo 'quinta task'")

    run_dates = dag.get_run_dates(start_date=dag.start_date)
    # pega do dag todas as datas de execução
    next_execution = run_dates[-1] if len(run_dates) != 0 else None
    # verificação do que o airflow faz internamente
    #pega a ultima execução da lista

    t1 >> t2 >> t3 >> t4 >> t5
