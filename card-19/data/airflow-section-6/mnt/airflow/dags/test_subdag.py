import airflow
from subdags.subdag import factory_subdag
from airflow.models import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.subdag_operator import SubDagOperator
from airflow.executors.sequential_executor import SequentialExecutor
from airflow.executors.celery_executor import CeleryExecutor

DAG_NAME="subdag_teste"
# define uma constante com o nome do dag

default_args = {
    'owner': 'matheus',
    'start_date': airflow.utils.dates.days_ago(2)
}

with DAG(dag_id=DAG_NAME, default_args=default_args, schedule_interval="@once") as dag:
    start = DummyOperator(
        task_id='start'
    )

    # cria um subdag do dag pai
    subdag_1 = SubDagOperator(
        task_id='subdag-1',
        subdag=factory_subdag(DAG_NAME, 'subdag-1', default_args),
        # nome dag pai | nome subdag | pega os argumentos padrao definidos la em cima
        executor=SequentialExecutor()
    )

    # task vazia
    some_other_task = DummyOperator(
        task_id='check'
        )

    #cria o segundo sub-dag
    subdag_2 = SubDagOperator(
        task_id='subdag-2',
        subdag=factory_subdag(DAG_NAME, 'subdag-2', default_args),
        executor=SequentialExecutor()
    )

    end = DummyOperator(
        task_id='final'
    )
    
    # dependencias dos sub-dags
    start >> subdag_1 >> some_other_task >> subdag_2 >> end