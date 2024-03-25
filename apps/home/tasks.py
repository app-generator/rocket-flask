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

@shared_task(ignore_result=False)
def execute_script():
    """
    This route executes scripts found in CELERY_SCRIPTS_DIR and generates logs stored in CELERY_LOGS_DIR
    """
    data = request.json
    script = data.get("script")
    args = data.get("args")

    print(f'> EXEC [{script}] -> ({args})')

    scripts, ErrInfo = get_scripts()

    if script and script in scripts:
        # Executing related script
        script_path = os.path.join(Config.CELERY_SCRIPTS_DIR, script)
        process = subprocess.Popen(
            f"python {script_path} {args}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(8)

        exit_code = process.wait()
        error = False
        status = "STARTED"
        if exit_code == 0:  # If script execution successful
            logs = process.stdout.read().decode()
            status = "SUCCESS"
        else:
            logs = process.stderr.read().decode()
            error = True
            status = "FAILURE"

        log_file = write_to_log_file(logs, script)

        return jsonify({"logs": logs, "input": script, "error": error, "output": "", "status": status, "log_file": log_file})
    else:
        return jsonify({"error": "Script not found"}), 404

