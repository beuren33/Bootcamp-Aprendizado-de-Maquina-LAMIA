import airflow
from subdags.subdag import factory_subdag
from airflow.models import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.subdag_operator import SubDagOperator
from airflow.executors.celery_executor import CeleryExecutor

DAG_NAME="deadlock_subdag"

default_args = {
    'owner': 'matheus',
    'start_date': airflow.utils.dates.days_ago(2),
}

# cada subdag ocupa um slot de worker esperando suas próprias tasks
# rodarem, e se o pool de workers for pequeno os subdags ficam todos
# travados esperando slot livre uns dos outros.
with DAG(dag_id=DAG_NAME, default_args=default_args, schedule_interval="@once") as dag:
    start = DummyOperator(
        task_id='start'
    )

    # quatro subdags rodando em paralelo cada um em um worker do celery
    subdag_1 = SubDagOperator(
        task_id='subdag-1',
        subdag=factory_subdag(DAG_NAME, 'subdag-1', default_args),
        executor=CeleryExecutor()
    )

    subdag_2 = SubDagOperator(
        task_id='subdag-2',
        subdag=factory_subdag(DAG_NAME, 'subdag-2', default_args),
        executor=CeleryExecutor()
    )

    subdag_3 = SubDagOperator(
        task_id='subdag-3',
        subdag=factory_subdag(DAG_NAME, 'subdag-3', default_args),
        executor=CeleryExecutor()
    )

    subdag_4 = SubDagOperator(
        task_id='subdag-4',
        subdag=factory_subdag(DAG_NAME, 'subdag-4', default_args),
        executor=CeleryExecutor()
    )

    final = DummyOperator(
        task_id='final'
    )

    # dispara os quatro subdags juntos final só roda quando os quatro terminarem
    start >> [subdag_1, subdag_2, subdag_3, subdag_4] >> final