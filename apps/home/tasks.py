from flask import Flask, request, jsonify
import os
from os import listdir
from os.path import isfile, join
import datetime
import subprocess
import time
from apps.config import Config
from run import celery_app
from celery.contrib.abortable import AbortableTask
from celery import shared_task
from apps.home.models import TaskResult, StatusChoices
from apps import db



def get_scripts():
    """
    Returns all scripts from 'ROOT_DIR/celery_scripts'
    """
    raw_scripts = []
    scripts = []
    ignored_ext = ['db', 'txt']

    try:
        raw_scripts = [f for f in listdir(Config.CELERY_SCRIPTS_DIR) if isfile(join(Config.CELERY_SCRIPTS_DIR, f))]
    except Exception as e:
        return None, 'Error CELERY_SCRIPTS_DIR: ' + str(e)

    for filename in raw_scripts:
        ext = filename.split(".")[-1]
        if ext not in ignored_ext:
           scripts.append(filename)

    return scripts, None

def write_to_log_file(logs, script_name):
    """
    Writes logs to a log file with formatted name in the CELERY_LOGS_DIR directory.
    """
    script_base_name = os.path.splitext(script_name)[0]  # Remove the .py extension
    current_time = datetime.datetime.now().strftime("%y%m%d-%H%M%S")
    log_file_name = f"{script_base_name}-{current_time}.log"
    log_file_path = os.path.join(Config.CELERY_LOGS_DIR, log_file_name)
    
    with open(log_file_path, 'w') as log_file:
        log_file.write(logs)
    
    return log_file_path


@celery_app.task
def run_script(script_path):
    start_time = datetime.datetime.now()
    process = subprocess.Popen(f"python {script_path}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(8)

    exit_code = process.wait()
    error = False
    status = "STARTED"
    if exit_code == 0:
        logs = process.stdout.read().decode()
        status = "SUCCESS"
    else:
        logs = process.stderr.read().decode()
        error = True
        status = "FAILURE"
    
    log_file = write_to_log_file(logs, script_path.split('/')[-1])

    end_time = datetime.datetime.now()
    execution_time = (end_time - start_time).total_seconds()

    task_result = TaskResult(
        task_name='execute_script',
        periodic_task_name=script_path,
        status=status,
        date_done=end_time,
        result=f"Execution time: {execution_time} seconds"
    )
    db.session.add(task_result)
    db.session.commit()

    return jsonify({"logs": logs, "input": script_path, "error": error, "output": "", "status": status, "log_file": log_file})