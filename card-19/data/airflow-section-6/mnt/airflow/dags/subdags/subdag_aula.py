from airflow.models import DAG
from airflow.operators.dummy_operator import DummyOperator

def factory_subdag(parent_dag_name, child_dag_name, default_args):

    with DAG(
        dag_id='%s.%s' % (parent_dag_name, child_dag_name),
        # cria um i com base no dag pai e no dag  filho
        default_args=default_args
    ) as dag:

        for i in range(5):
            DummyOperator(
                task_id='%s-task-%s' % (child_dag_name, i + 1)
            )
    # sera criado 5 tasks que vao rodar em paralelo pois nao há nenhuma ordem de dependencia
    return dag