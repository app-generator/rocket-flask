# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import os
import time
import json
from apps.home import blueprint
from flask import render_template, request, redirect, url_for, jsonify
from flask_login import login_required
from jinja2 import TemplateNotFound
from apps.home.forms import ProductForm
from apps.home.models import Product, TaskResult
from celery.result import AsyncResult
from apps import db
from celery import current_app
import datetime
from apps.config import Config

@blueprint.route("/")
@blueprint.route("/index")
def index():
	return render_template("pages/index.html")

@blueprint.route("/tables", methods=['GET', 'POST'])
def datatables():
	form = ProductForm()
	products = Product.get_list()

	if request.method == 'POST':
		form_data = {}
		for attribute, value in request.form.items():
			if attribute == 'csrf_token':
				continue

			form_data[attribute] = value

		product = Product(**form_data)
		db.session.add(product)
		db.session.commit()
		return redirect(url_for('home_blueprint.datatables'))

	context = {}
	context['parent'] = 'apps'
	context['segment'] = 'datatables'
	context['form'] = form
	context['products'] = products
	return render_template("pages/datatables.html", **context)


@blueprint.route("/delete-product/<id>/")
def delete_product(id):
	product = Product.find_by_id(id)
	db.session.delete(product)
	db.session.commit()
	return redirect(url_for('home_blueprint.datatables'))


@blueprint.route("/update-product/<id>/", methods=['GET', 'POST'])
def update_product(id):
	product = Product.find_by_id(id)

	if request.method == 'POST':
		for attribute, value in request.form.items():
			if attribute == 'csrf_token':
				continue

			setattr(product, attribute, value)

		db.session.commit()
		
		return redirect(url_for('home_blueprint.datatables'))
	
	return redirect(url_for('home_blueprint.datatables'))


@blueprint.route('/charts/', methods=['GET'])
def charts():
	products = [{'name': product.name, 'price': product.price} for product in Product.get_list()]
	context = {}
	context['parent'] = 'apps'
	context['segment'] = 'charts'
	context['products'] = products
	return render_template("pages/charts.html", **context)







def get_scripts():
    """
    Returns all scripts from 'ROOT_DIR/celery_scripts'
    """
    raw_scripts = []
    scripts = []
    ignored_ext = ['db', 'txt']

    try:
        raw_scripts = [f for f in os.listdir(Config.CELERY_SCRIPTS_DIR) if os.path.isfile(os.path.join(Config.CELERY_SCRIPTS_DIR, f))]
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



@blueprint.route('/tasks', methods=['GET', 'POST'])
def tasks():
    scripts, ErrInfo = get_scripts()
    context = {
            'cfgError' : ErrInfo,
            'tasks'    : get_celery_all_tasks(),
            'scripts'  : scripts,
            'segment'  : 'tasks',
            'parent'   : 'apps',
        }
    task_results = TaskResult.query.all()
    context["task_results"] = task_results
    return render_template("pages/tasks.html", **context)


@blueprint.route('/tasks/run/<task_name>')
def run_task(task_name):
    from apps.home.tasks import execute_script
    tasks = [execute_script]
    _script = request.POST.get("script")
    _args   = request.POST.get("args")
    for task in tasks:
        if task.__name__ == task_name:
            task.delay({"script": _script, "args": _args})
    time.sleep(1)

    return redirect("tasks") 


def get_celery_all_tasks():
    from apps.home.tasks import execute_script
    tasks = [execute_script]
    for task in tasks:
        task.delay()

    current_app.loader.import_default_modules()
    tasks = list(sorted(name for name in current_app.tasks if not name.startswith('celery.')))
    tasks = [{"name": name.split(".")[-1], "script":name} for name in tasks]
    for task in tasks:
        last_task = TaskResult.query.filter_by(task_name=task["script"]).order_by(TaskResult.date_created.desc()).first()
        if last_task:
            task["id"] = last_task.task_id
            task["has_result"] = True
            task["status"] = last_task.status
            task["successfull"] = last_task.status == "SUCCESS" or last_task.status == "STARTED"
            task["date_created"] = last_task.date_created
            task["date_done"] = last_task.date_done
            task["result"] = last_task.result

            try:
                task["input"] = json.loads(last_task.result).get("input")
            except:
                task["input"] = ''
                
    return tasks




# Custom Filter
@blueprint.app_template_filter('get_result_field')
def get_result_field(result, field: str):
    result = json.loads(result.result)
    if result:
        return result.get(field)

@blueprint.app_template_filter('date_format')
def date_format(date):
    try:
        return date.strftime(r'%Y-%m-%d-%H-%M-%S')
    except:
        return date