# -*- coding: utf-8 -*-

from flask import render_template, redirect, url_for, abort, flash, request, current_app, make_response
from . import main
from .. import db
from ..models import User, Role, Permission, Post
from flask.ext.login import login_required, current_user
from .forms import EditProfileForm, EditProfileAdminForm, PostForm
from ..decorators import admin_required, permission_required


@main.route('/', methods = ['GET', 'POST'])
def index():
	form = PostForm()
	if current_user.can(Permission.WRITE_ARTICLES) and \
			form.validate_on_submit():
		post = Post(body = form.body.data,
					author = current_user._get_current_object())
		db.session.add(post)
		return redirect(url_for('.index'))
	page = request.args.get('page', 1, type = int)
	#requset.args为请求的查询字符串
	#get()中有三个参数，key, default, type 
	#如果没有指定page,默认为1，type = init为了确保若参数无法转换为整数，返回默认值
	show_followed = False
	if current_user.is_authenticated:
		show_followed = bool(request.cookies.get('show_followed', ''))
	if show_followed:
		query = current_user.followed_posts
	else:
		query = Post.query
	pagination = query.order_by(Post.timestamp.desc()).paginate(
		page, per_page = current_app.config['FLASKY_POSTS_PER_PAGE'],
		error_out = False)
	#Post.timestamp.desc()为按时间戳降序排列
	#paginate()方法接受三个参数，起始页，每一页的数目，错误标志，True为404，False为空列表
	posts = pagination.items
	#迭代器，index.html中要用到
	return render_template('index.html', form = form, posts = posts,
							show_followed = show_followed, pagination = pagination)
	#渲染index.html模板

@main.route('/user/<username>')
def user(username):
	user = User.query.filter_by(username = username).first()
	#用户名为username的用户这个类实例赋给user
	if user is None:
		abort(404)
		#如果这个用户不存在则抛出404错误页面
	page = request.args.get('page', 1, type = int)
	pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
		page, per_page = current_app.config['FLASKY_POSTS_PER_PAGE'],
		error_out = False)
	posts = pagination.items
	#同上
	return render_template('user.html', user = user, posts = posts, pagination = pagination)
	#若存在，渲染user.html，把user这个实例传过去
	#把posts, pagination传过去

@main.route('/edit-profile', methods = ['GET', 'POST'])
@login_required
def edit_profile():
#修改资料
	form = EditProfileForm()
	if form.validate_on_submit():
		current_user.name = form.name.data
		current_user.location = form.location.data
		current_user.about_me = form.about_me.data
		db.session.add(current_user)
		#若提交成功，将表单中的数据提交到数据库
		flash('Your profile has been updated.')
		#显示修改成功的消息
		return redirect(url_for('.user', username = current_user.username))
		#重定向到修改成功后的页面，即user/username，即用户资料页面
	form.name.data = current_user.name
	form.location.data = current_user.location
	form.about_me.data = current_user.about_me
	#未修改时表单的默认数据为之前的数据
	return render_template('edit_profile.html', form = form)
	#将form传出，渲染修改资料的页面，

@main.route('/edit_profile/<int:id>', methods = ['GET', 'POST'])
@login_required
#用户需已登录
@admin_required
def edit_profile_admin(id):
#管理员修改资料
	user = User.query.get_or_404(id)
	#get_or_404(id)，若没有找到id，则返回404错误
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
	#和edit_profile类似

@main.route('/post/<int:id>')
def post(id):
	post = Post.query.get_or_404(id)
	return render_template('post.html', posts = [post])
#每篇文章的固定链接，用post.html渲染

@main.route('/edit/<int:id>', methods = ['GET', 'POST'])
@login_required
def edit(id):
	post = Post.query.get_or_404(id)
	if current_user != post.author and \
			not current_user.can(Permission.ADMINISTER):
		abort(403)
	form = PostForm()
	if form.validate_on_submit():
		post.body = form.body.data
		db.session.add(post)
		flash('The post has been updated.')
		return redirect(url_for('post', id = post.id))
	form.body.data = post.body
	return render_template('edit_post.html', form = form)
#允许博客文章的作者编辑自己文章
#允许管理员编辑所有人的文章

@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
	user = User.query.filter_by(username = username).first()
	if user is None:
		flash('Invalid user.')
		return redirect(url_for('.index'))
	if current_user.is_following(user):
		flash('You are already following this user.')
		return redirect(url_for('.user', username = username))
	current_user.follow(user)
	flash('You are now following %s' % username)
	return redirect(url_for('.user', username = username))
#关注他人的路由
@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
	user = User.query.filter_by(username = username).first()
	if user is None:
		flash('Invalid user.')
		return redirect(url_for('.index'))
	if not current_user.is_following(user):
		flash('You are not following this user.')
		return redirect(url_for('.user', username = useranem))
	current_user.unfollow(user)
	flash('You are not following %s anymore' % username)
	return redirect(url_for('.user', username = username))
#对他人取消关注的路由
@main.route('/followers/<username>')
def followers(username):
	user = User.query.filter_by(username = username).first()
	if user is None:
		flash('Invalid user.')
		return redirect(url_for('.index'))
	page = request.args.get('page', 1, type = int)
	pagination = user.followers.paginate(
		page, per_page = current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
		error_out = False)
	follows = [{'user': item.follower, 'timestamp': item.timestamp}
				for item in pagination.items]
	return render_template('followers.html', user = user, title = "Followers of",
							endpoint = '.followers', pagination = pagination,
							follows = follows)
#显示用户关注的人的路由
@main.route('/followed_by/<username>')
def followed_by(username):
	user = User.query.filter_by(username = username).first()
	if user is None:
		flash('Invalid user.')
		return redirect(url_for('.index'))
	page = request.args.get('page', 1, type = int)
	pagination = user.followed.paginate(
		page, per_page = current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
		error_out = False)
	follows = [{'user': item.followed, 'timestamp': item.timestamp}
				for item in pagination.items]
	return render_template('followers.html', user = user, title = "Followers of",
							endpoint = '.followers', pagination = pagination,
							follows = follows)
#显示关注用户的人的路由

@main.route('/all')
@login_required
def show_all():
	resp = make_response(redirect(url_for('.index')))
	resp.set_cookie('show_followed', '', max_age = 30*24*60*60)
	return resp
#在cookie中将show_followed设为Null，然后重定向到首页
#max_age为过期时间
@main.route('/followed')
@login_required
def show_followed():
	resp = make_response(redirect(url_for('.index')))
	resp.set_cookie('show_followed', '1', max_age = 30*24*60*60)
	return resp
#同上