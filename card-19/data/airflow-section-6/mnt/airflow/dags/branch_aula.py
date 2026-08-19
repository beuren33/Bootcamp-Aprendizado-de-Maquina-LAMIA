import airflow
import requests
from airflow.models import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import BranchPythonOperator, PythonOperator

default_args = {
    'owner': 'matheus',
    'start_date': airflow.utils.dates.days_ago(2),
}

IP_GEOLOCATION_APIS = {
    'ip-api': 'http://ip-api.com/json/',
    'ipstack': 'https://api.ipstack.com/',
    'ipinfo': 'https://ipinfo.io/json'
}
# pega apis de geollocalização para as tasks

def check_api():
    for api, link in IP_GEOLOCATION_APIS.items():
        r = requests.get(link)
        try:
            data = r.json()
            if data and 'country' in data and len(data['country']):
                return api
        except ValueError:
            pass
    return 'none'

with DAG(dag_id='branch_dag', 
    default_args=default_args, 
    schedule_interval="@once") as dag:


    check_api = BranchPythonOperator(
        task_id='check_api',
        python_callable=check_api
    )
    # retorna lista de ids api

    none = DummyOperator(
        task_id='none'
    )

    save = DummyOperator(task_id='save')

    check_api >> none >> save

    
    for api in IP_GEOLOCATION_APIS:
        process = DummyOperator(
            task_id=api
        )
    
        check_api >> process >> save