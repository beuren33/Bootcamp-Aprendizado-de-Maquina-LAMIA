import airflow
from airflow.models import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import BranchPythonOperator, PythonOperator
import random

args = {
    'owner': 'matheus',
    'start_date': airflow.utils.dates.days_ago(1),
}

# simula verificacao de estoque retorna ok ou falha
def check_estoque():
    if random.random() > 0.5:
        return 'ok'
    else:
        return 'falha'

# simula prioridade do pedido retorna alta ou normal
def check_prioridade():
    if random.random() > 0.5:
        return 'alta'
    else:
        return 'normal'

# push do status do estoque no xcom
def push_status(**context):
    status = check_estoque()
    context['ti'].xcom_push(key='status_pedido', value=status)

# branch1 le status e decide entre t3 e t4
def escolhe_estoque(**context):
    status = context['ti'].xcom_pull(key='status_pedido', task_ids='t2')
    return 't3' if status == 'ok' else 't4'

# push da prioridade no xcom
def push_prioridade(**context):
    prioridade = check_prioridade()
    context['ti'].xcom_push(key='prioridade_pedido', value=prioridade)

# branch2 le prioridade e decide entre t6 e t7
def escolhe_prioridade(**context):
    prioridade = context['ti'].xcom_pull(key='prioridade_pedido', task_ids='t5')
    return 't6' if prioridade == 'alta' else 't7'

# le os dois xcoms e loga resultado final
def loga_resultado(**context):
    status = context['ti'].xcom_pull(key='status_pedido', task_ids='t2')
    prioridade = context['ti'].xcom_pull(key='prioridade_pedido', task_ids='t5')
    print(f'pedido finalizado: status={status} prioridade={prioridade}')

with DAG(dag_id='xcom_pratica', default_args=args, schedule_interval="@once") as dag:

    t1 = DummyOperator(task_id='t1')
    # inicio do fluxo

    t2 = PythonOperator(
        task_id='t2',
        provide_context=True,
        python_callable=push_status
    )
    # roda check de estoque e salva status no xcom

    branch1 = BranchPythonOperator(
        task_id='branch1',
        provide_context=True,
        python_callable=escolhe_estoque
    )
    # decide entre t3 (ok) ou t4 (falha)

    t3 = DummyOperator(task_id='t3')
    # rota estoque ok

    t4 = DummyOperator(task_id='t4')
    # rota estoque falhou

    # one_success roda assim que t3 ou t4 terminar
    t5 = PythonOperator(
        task_id='t5',
        trigger_rule='one_success',
        provide_context=True,
        python_callable=push_prioridade
    )
    # merge da primeira branch e salva prioridade no xcom

    branch2 = BranchPythonOperator(
        task_id='branch2',
        provide_context=True,
        python_callable=escolhe_prioridade
    )
    # decide entre t6 (alta) ou t7 (normal)

    t6 = DummyOperator(task_id='t6')
    # rota prioridade alta

    t7 = DummyOperator(task_id='t7')
    # rota prioridade normal

    # one_success roda assim que t6 ou t7 terminar
    t8 = PythonOperator(
        task_id='t8',
        trigger_rule='one_success',
        provide_context=True,
        python_callable=loga_resultado
    )
    # merge final le os dois xcoms

    t1 >> t2 >> branch1
    branch1 >> t3 >> t5
    branch1 >> t4 >> t5
    t5 >> branch2
    branch2 >> t6 >> t8
    branch2 >> t7 >> t8
