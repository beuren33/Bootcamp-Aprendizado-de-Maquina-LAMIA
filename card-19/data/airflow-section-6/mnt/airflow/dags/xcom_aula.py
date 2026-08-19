import airflow
from airflow.models import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import BranchPythonOperator, PythonOperator
from airflow.operators.bash_operator import BashOperator

args = {
    'owner': 'MaTheus',
    'start_date': airflow.utils.dates.days_ago(1),
}

def push_xcom_with_return():
    return 'my_returned_xcom'

# lê o XCom do t0
def get_pushed_xcom_with_return(**context):
    print(context['ti'].xcom_pull(task_ids='t0'))

# push do XCom 
def push_next_task(**context):
    context['ti'].xcom_push(key='next_task', value='t3')

# le o XCom next_task e retorna o task_id que deve rodar em seguida
def get_next_task(**context):
    return context['ti'].xcom_pull(key='next_task')

def get_multiple_xcoms(**context):
    print(context['ti'].xcom_pull(key=None, task_ids=['t0', 't2']))

with DAG(dag_id='xcom_dag', default_args=args, schedule_interval="@once") as dag:
    
    t0 = PythonOperator(
        task_id='t0',
        python_callable=push_xcom_with_return
    )

    t1 = PythonOperator(
        task_id='t1',
        provide_context=True,
        python_callable=get_pushed_xcom_with_return
    )

    t2 = PythonOperator(
        task_id='t2',
        provide_context=True,
        python_callable=push_next_task
    )

    branching = BranchPythonOperator(
        task_id='branching',
        provide_context=True,
        python_callable=get_next_task,
    )

    t3 = DummyOperator(task_id='t3')

    t4 = DummyOperator(task_id='t4')

    # one_success roda assim que t3 ou t4 terminar
    t5 = PythonOperator(
        task_id='t5',
        trigger_rule='one_success',
        provide_context=True,
        python_callable=get_multiple_xcoms
    )

    # le XCom direto via template Jinja
    t6 = BashOperator(
        task_id='t6',
        bash_command="echo value from xcom: {{ ti.xcom_pull(key='next_task') }}"
    )

    t0 >> t1
    t1 >> t2 >> branching
    # branching decide entre t3 e t4 
    branching >> t3 >> t5 >> t6
    branching >> t4 >> t5 >> t6