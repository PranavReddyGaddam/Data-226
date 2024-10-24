from airflow.decorators import task
from airflow import DAG
from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook
from airflow.utils.dates import days_ago

from datetime import datetime
import logging


def return_snowflake_conn():

    hook = SnowflakeHook(snowflake_conn_id='snowflake_conn')
    
    conn = hook.get_conn()
   
    return conn.cursor()

@task
def set_stage():
    cur = return_snowflake_conn()
    
    # First SQL statement: Create or replace the stage
    create_stage_sql = """
    CREATE OR REPLACE STAGE stock_db.raw_data.blob_stage
    url = 's3://s3-geospatial/readonly/'
    file_format = (type = csv, skip_header = 1, field_optionally_enclosed_by = '"');
    """
    
    # Second SQL statement: Copy data into user_session_channel
    copy_user_session_sql = """
    COPY INTO stock_db.raw_data.user_session_channel
    FROM @stock_db.raw_data.blob_stage/user_session_channel.csv;
    """
    
    # Third SQL statement: Copy data into session_timestamp
    copy_session_timestamp_sql = """
    COPY INTO stock_db.raw_data.session_timestamp
    FROM @stock_db.raw_data.blob_stage/session_timestamp.csv;
    """
    
    logging.info("Running stage setup SQL")
    
    # Execute each statement separately
    cur.execute(create_stage_sql)
    cur.execute(copy_user_session_sql)
    cur.execute(copy_session_timestamp_sql)

# Task to create tables if they don't exist
@task
def load():
    cur = return_snowflake_conn()

    try:
        # Begin transaction
        cur.execute("BEGIN;")
        
        # First SQL statement: Create user_session_channel table
        create_user_session_table_sql = """
        CREATE TABLE IF NOT EXISTS stock_db.raw_data.user_session_channel (
            userId int not NULL,
            sessionId varchar(32) primary key,
            channel varchar(32) default 'direct'
        );
        """
        
        # Execute first statement
        logging.info("Running table creation SQL for user_session_channel")
        cur.execute(create_user_session_table_sql)
        
        # Second SQL statement: Create session_timestamp table
        create_session_timestamp_table_sql = """
        CREATE TABLE IF NOT EXISTS stock_db.raw_data.session_timestamp (
            sessionId varchar(32) primary key,
            ts timestamp  
        );
        """
        
        # Execute second statement
        logging.info("Running table creation SQL for session_timestamp")
        cur.execute(create_session_timestamp_table_sql)

        # Commit the transaction if successful
        cur.execute("COMMIT;")
        
    except Exception as e:
        # Rollback the transaction in case of any failure
        cur.execute("ROLLBACK;")
        logging.error('Failed to execute table creation SQL. Completed ROLLBACK!')
        logging.error(str(e))
        raise


with DAG(
    dag_id='ETL',
    default_args={
        'owner': 'airflow',
        'depends_on_past': False,
        'email_on_retry': False
    },
    description='ETL Pipeline to Snowflake using Airflow',
    start_date=datetime(2024, 10, 2),  # Replace with actual start date
    schedule_interval='@daily',  # Adjust schedule as needed
    catchup=False,
    tags=['snowflake', 'ETL'],
) as dag:

    # Define task dependencies
    stage_task = set_stage()
    load_task = load()

    # Task order: set_stage should run before load
    stage_task >> load_task
