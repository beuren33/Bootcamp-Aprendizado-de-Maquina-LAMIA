import pprint as pp
import airflow.utils.dates
from airflow import DAG
from airflow.operators.dagrun_operator import TriggerDagRunOperator
from airflow.operators.dummy_operator import DummyOperator

default_args = {
        "owner": "matheus", 
        "start_date": airflow.utils.dates.days_ago(1)
    }

# so dispara o dag alvo se condition_param for True
def conditionally_trigger(context, dag_run_obj):
    if context['params']['condition_param']:
        dag_run_obj.payload = {
                'message': context['params']['message']
            }
        pp.pprint(dag_run_obj.payload)
        return dag_run_obj

with DAG(dag_id="triggerdagop_controller_dag", default_args=default_args, schedule_interval="@once") as dag:
    # dispara o dag passando dados via conf
    trigger = TriggerDagRunOperator(
        task_id="trigger_dag",
        trigger_dag_id="triggerdagop_target_dag",
        provide_context=True,
        python_callable=conditionally_trigger,
        params={
            'condition_param': True,
            'message': 'ola teste'
        },
    )

    last_task = DummyOperator(task_id="last_task")

    trigger >> last_task