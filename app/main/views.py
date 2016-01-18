# -*- coding: utf-8 -*-

from flask import render_template, redirect, url_for, abort, flash
from . import main
from .. import db
from ..models import User, Role
from flask.ext.login import login_required, current_user
from .forms import EditProfileForm, EditProfileAdminForm
from ..decorators import admin_required


@main.route('/')
def index():
	return render_template('index.html')
	#渲染index.html模板

@main.route('/user/<username>')
def user(username):
	user = User.query.filter_by(username = username).first()
	#用户名为username的用户这个类实例赋给user
	if user is None:
		abort(404)
		#如果这个用户不存在则抛出404错误页面
	return render_template('user.html', user = user)
	#若存在，渲染user.html，把user这个实例传过去

@main.route('/edit-profile', methods = ['GET', 'POST'])
@login_required
def edit_profile():
	form = EditProfileForm()
	if form.validate_on_submit():
		current_user.name = form.name.data
		current_user.location = form.location.data
		current_user.about_me = form.about_me.data
		db.session.add(current_user)
		flash('Your profile has been updated.')
		return redirect(url_for('.user', username = current_user.username))
	form.name.data = current_user.name
	form.location.data = current_user.location
	form.about_me.data = current_user.about_me
	return render_template('edit_profile.html', form = form)

@main.route('/edit_profile/<int:id>', methods = ['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
	user = User.query.get_or_404(id)
	form = EditProfileAdminForm(user = user)
	if form.validate_on_submit():
		user.email = form.email.data
		user.confirmed = form.confirmed.data
		user.username = form.username.data
		user.role = Role.query.get(form.role.data)
		user.name = form.name.data
		user.location = form.name.data
		user.about_me = form.about_me.data
		db.session.add(user)
		flash('The profile has been updated.')
		return redirect(url_for('.user', username = user.username))
	form.email.data = user.email
	form.username.data = user.username
	form.confirmed.data = user.confirmed
	form.role.data = user.role_id
	form.name.data = user.name
	form.location.data = user.location
	form.about_me.data = user.about_me
	return render_template('edit_profile.html', form = form, use = user)
