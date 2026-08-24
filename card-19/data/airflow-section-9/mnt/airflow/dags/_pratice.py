import airflow.utils.dates
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.dummy_operator import DummyOperator

default_args = {
    "owner": "matheus",
    "start_date": airflow.utils.dates.days_ago(1)
}

with DAG(dag_id="marketing_dag", default_args=default_args, schedule_interval="@daily") as dag:
    # melhorei o marketing_aula
    # simulei um pipeline para o marketing, contendo coleta, analise, campanha e relatorio
    # visando a automaziação da coleta e campanhas sendo criadas

    coletar_dados = BashOperator(
        task_id="coletar_dados",
        bash_command="echo 'Coletando dados de clientes'"
    )

    analisar_clientes = BashOperator(
        task_id="analisar_clientes",
        bash_command="echo 'Analisando clientes'"
    )

    segmentar_clientes = BashOperator(
        task_id="segmentar_clientes",
        bash_command="echo 'Segmentando clientes'"
    )

    criar_campanha = BashOperator(
        task_id="criar_campanha",
        bash_command="echo 'Criando campanha'"
    )

    enviar_campanha = BashOperator(
        task_id="enviar_campanha",
        bash_command="echo 'Enviando campanha'"
    )

    analisar_resultado = BashOperator(
        task_id="analisar_resultado",
        bash_command="echo 'Analisando resultado'"
    )

    gerar_relatorio = BashOperator(
        task_id="gerar_relatorio",
        bash_command="echo 'Gerando relatorio'"
)
    # dependencias de tasks
    coletar_dados >> analisar_clientes >> segmentar_clientes >> criar_campanha >> enviar_campanha>> analisar_resultado >> gerar_relatorio