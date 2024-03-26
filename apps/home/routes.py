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


@blueprint.route('/run_script', methods=['POST'])
def run_script_route():
    from apps.home.tasks import run_script
    script_name = request.form['script']
    file_path = os.path.join(Config.CELERY_SCRIPTS_DIR, script_name)
    if os.path.isfile(file_path):
        run_script.delay(file_path)

    return redirect(url_for('home_blueprint.tasks'))


@blueprint.route('/tasks', methods=['GET', 'POST'])
def tasks():
    from apps.home.tasks import get_scripts
    scripts, ErrInfo = get_scripts()
    context = {
        'cfgError' : ErrInfo,
        'scripts'  : scripts,
        'tasks'	   : TaskResult.query.order_by(TaskResult.id.desc()).first(),
        'segment'  : 'tasks',
        'parent'   : 'apps',
    }
    task_results = TaskResult.query.all()
    context["task_results"] = task_results
    return render_template("pages/tasks.html", **context)





# Custom Filter
@blueprint.app_template_filter('get_result_field')
def get_result_field(result, field: str):
    result = json.loads(result.result)
    if result:
        return result.get(field)

@blueprint.app_template_filter('date_format')
def date_format(date):
    try:
        return date.strftime(r'%Y-%m-%d %H:%M:%S')
    except:
        return date


@blueprint.app_template_filter('name_from_path')
def name_from_path(path):
    try:
        name = path.split('/')[-1]
        return name
    except:
        return path