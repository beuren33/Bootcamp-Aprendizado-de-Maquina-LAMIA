from airflow import DAG
from airflow.operators.bash_operator import BashOperator

from datetime import datetime, timedelta

def task_succes(dict):
    print("task sucesso")
    print(dict)
err=0
def task_failure(dict):
    print("task erro")
    global err
    # declara  a utilização de variavel global
    err+=1
    with open("logs_alert_pratica.txt",'a') as file:
        file.write(f"Erro em task {err}: {dict} "+"\n")
# funcao de erro registra em um txt o erro

default_args = {
    'start_date': datetime(2026,7,1),
    'owner': 'Airflow',
    'retries': 3,
    #repete 3 vezes
    'retry_delay': timedelta(seconds=60),
    #delay de 60 segundos entre as tentativas
    'emails':['owner@gmail.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'on_failure_callback': task_failure,
    'on_success_callback': task_succes,
    'execution_timeout': timedelta(seconds=60)
}

def on_succes_dag(dict):
    print("dag sucesso")
    print(dict)
def on_failure_dag(dict):
   with open("logs_alert_pratica.txt", 'a') as file:
        file.write(f"Erro em dag: {dict} "+"\n")

#registra erro de dag no txt
with DAG(dag_id='alert_dag', schedule_interval="0 0 * * *", default_args=default_args, catchup=True, dagrun_timeout=timedelta(seconds=75), on_success_callback=on_succes_dag, on_failure_callback = on_failure_dag) as dag:
    #chama as funcoes de succes e failure, mostrando como um 'log' para a execução dos dags
    t1 = BashOperator(task_id='t1', bash_command="exit 1")
    
    t2 = BashOperator(task_id='t2', bash_command="echo 'task2'")

    t1 >> t2