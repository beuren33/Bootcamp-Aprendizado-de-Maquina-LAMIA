import airflow
from airflow.models import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import BranchPythonOperator, PythonOperator
from airflow.operators.bash_operator import BashOperator

import numpy as np
import pandas as pd
from random import randint, sample
import datetime
import time
import calendar

args = {
    'owner': 'matheus',
    'start_date': airflow.utils.dates.days_ago(1),
}

def generate_random_dates(start, end, n):
    dates = pd.Series(np.zeros(n))
    for i in range(n):
        dates[i] = start + datetime.timedelta(seconds=randint(0, int((end - start).total_seconds())))
    return(dates)

def push_xcom_with_return():
    # gera um dataset 
    n = 1000000

    df = pd.DataFrame({'user_id': sample(range(90000000, 99999999), n),
                    'order_id': np.random.choice(range(1000000, 2000000), n, replace=False),
                    'order_date': generate_random_dates(datetime.date(2015, 1, 1), 
                                                        datetime.date(2017, 12, 31), 
                                                        n),
                    'number_of_products': np.random.choice(range(20), n, replace=True),
                    'total_amount': np.round(np.random.uniform(1, 5000, n), 2)})


    df = df.assign(day_of_week = df.order_date.apply(lambda x: calendar.day_name[x.weekday()]))
    # cada linha recebe um dia da semana com base na ordem

    df.user_id = df.user_id.astype('str')# id do usuario
    df.order_id = df.order_id.astype('str')# id da ordem

    return df

# puxa o XCom deixado pela task t0
def get_pushed_xcom_with_return(**context):
    print(context['ti'].xcom_pull(task_ids='t0'))

with DAG(dag_id='xcom_dag_big', default_args=args, schedule_interval="@once") as dag:

    t0 = PythonOperator(
        task_id='t0',
        python_callable=push_xcom_with_return
    )

    t1 = PythonOperator(
        task_id='t1',
        provide_context=True,
        python_callable=get_pushed_xcom_with_return
    )

    t0 >> t1