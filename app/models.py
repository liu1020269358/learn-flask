# -*- coding: utf-8 -*-

from . import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin, AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from datetime import datetime
from markdown import markdown
import bleach


class Permission:
	FOLLOW = 0x01
	#ob00000001
	COMMENT = 0x02
	#ob00000010
	WRITE_ARTICLES = 0x04
	#ob00000100
	MODERATE_COMMENTS = 0x08
	#ob00001000
	ADMINISTER = 0x80
	#ob10000000
	
class Role(db.Model):
#定义Roel模型
	__tablename__ = 'roles'
	#表单名字为roles
	id = db.Column(db.Integer, primary_key=True)
	#设定id列，这是表的主键
	name = db.Column(db.String(64), unique=True)
	#设定name列，不允许出现重复的值
	default = db.Column(db.Boolean, default = False, index = True)
	#defualt默认为False,是为了用户角色的权限而设计的
	permissions = db.Column(db.Integer)
	#permissions列中记录的是有哪些权限
	users = db.relationship('User', backref='role', lazy='dynamic')
	#定义users属性为与Role关联的模型的列表
	#若将uselist设为False，则不返回列表，而使用标量值
	
	#可以在类上调用，即不需要创建出Role实例就可以调用这个方法
	#因为insert_roles方法是用于更新角色，如果角色不存在，再创建新角色
	#匿名角色不需要表示出来，这个角色就是为了表示不再数据库中的用户
	#目前只有三种角色（包括匿名四种）
	@staticmethod
	def insert_roles():
		roles = {
		#将三种权限的用户存放在roles字典中
		#实际为roles = {'User': (0x07, True)
		#				'Moderator': (0x0f, False)
		#				'Administrator': (0xff, False)}
			'User': (Permission.FOLLOW |
					Permission.COMMENT |
					Permission.WRITE_ARTICLES, True),
			#User权限的用户可以follow.comment.write articles
			#第一个参数实际上为ob00000111,第二个参数设为True，表示默认的用户
			'Moderator': (Permission.FOLLOW |
						Permission.COMMENT |
						Permission.WRITE_ARTICLES |
						Permission.MODERATE_COMMENTS, False),
			#Moderator权限的用户可以follow. comment. write articles. moderate comments
			'Administrator': (0xff, False)
		}	#Administrator权限的用户具有所有的权限
		for r in roles:
			role = Role.query.filter_by(name = r).first()
			#将roles中的角色赋给r
			if role is None:
				role = Role(name = r)
				#如果这种角色在数据库中不存在，即为新角色，那么创建一个新的角色
			role.permissions = roles[r][0]
			#角色的权限为r的第一个参数
			role.default = roles[r][1]
			#角色的默认状态为r的第二个参数
			db.session.add(role)
			#添加角色
		db.session.commit()
		#提交到数据苦衷
	
	def __repr__(self):
		return '<Role %r>' % self.name
		#返回一个字符串，以供调试和测试
		
class User(UserMixin, db.Model):
#定义User模型
	__tablename__ = 'users'
	#表单名字为users
	id = db.Column(db.Integer, primary_key=True)
	#设定id字段，这是表的主键
	username = db.Column(db.String(64), unique=True, index=True)
	#设定username字段，不允许出现重复的值，创建索引
	role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
	#定义role_id外键，roles.id表明此列的值
	password_hash = db.Column(db.String(128))
	#设定password_hash字段
	email = db.Column(db.String(64), unique = True, index = True)
	#设定email字段
	confirmed = db.Column(db.Boolean, default = False)
	#设定confirmed列，为布尔属性，默认为False，为True说明已被验证过
	name = db.Column(db.String(64))
	location = db.Column(db.String(64))
	about_me = db.Column(db.Text())
	member_since = db.Column(db.DateTime(), default = datetime.utcnow)
	last_seen = db.Column(db.DateTime(), default = datetime.utcnow)
	#新的字段name, Location, about_me, member_since, last_seen
	#用来保存用户的姓名，所在地，自我接受，注册日期和最后访问日期
	#default参数接收函数，在db.Column()时会调用default()
	posts = db.relationship('Post', backref = 'author', lazy = 'dynamic')
	
	@property
	def password(self):
		raise AttributeError('password is not a readable attribute')
	#如果试图读取password属性则抛出AttributeError
	
	@password.setter
	def password(self, password):
		self.password_hash = generate_password_hash(password)
	#将password哈希后传给self.password_hash,可通过User.password = ''调用
	
	def verify_password(self, password):
		return check_password_hash(self.password_hash, password)
	#验证password是否输入正确
	
	def generate_confirmation_token(self, expiration = 3600):
	#生成加密令牌
		s = Serializer(current_app.config['SECRET_KEY'], expiration)
		#接收SECRET_KEY为参数生成一个JSON Web签名，expiration为有效时间
		return s.dumps({'confirm': self.id})
		#将self.id生成一个加密签名，再生成一个令牌字符串
		
	def confirm(self, token):
	#验证令牌
		s = Serializer(current_app.config['SECRET_KEY'])
		#接收SECRET_KEY为参数生成一个JSON Web签名
		try:
			data = s.loads(token)
			#解码令牌
		except:
			return False
			#如果令牌过期或令牌错误，则返回False
		#以上是为了验证接收的token是否为SECRET_KEY的加密令牌
		if data.get('confirm') != self.id:
			return False
			#如果令牌中的id和存储在current_user中已登录的用户id不同，则返回False
		self.confirmed = True
		#以上验证都通过的话，将confirmed列（属性）设为True
		db.session.add(self)
		#将表单数据提交到数据库
		return True
		#返回True
		
	def generate_reset_token(self, expiration=3600):
		s = Serializer(current_app.config['SECRET_KEY'], expiration)
		return s.dumps({'reset': self.id})
	#生成重置密码的令牌
	
	def reset_password(self, token, new_password):
		s = Serializer(current_app.config['SECRET_KEY'])
		try:
			data = s.loads(token)
		except:
			return False
		if data.get('reset') != self.id:
			return False
		self.password = new_password
		db.session.add(self)
		return True
	#重置密码的验证函数，如果重置成功，则返回True
	
	def generate_email_change_token(self, new_email, expiration=3600):
		s = Serializer(current_app.config['SECRET_KEY'], expiration)
		return s.dumps({'change_email': self.id, 'new_email': new_email})
	#生成重置邮箱的令牌
	
	def change_email(self, token):
		s = Serializer(current_app.config['SECRET_KEY'])
		try:
			data = s.loads(token)
		except:
			return False
		if data.get('change_email') != self.id:
			return False
		new_email = data.get('new_email')
		if new_email is None:
			return False
		if self.query.filter_by(email=new_email).first() is not None:
			return False
		self.email = new_email
		db.session.add(self)
		return True
	#重置邮箱的验证函数，如果重置邮箱成功，则返回True，类似注册函数
	
	def __init__(self, **kwargs):
		super(User, self).__init__(**kwargs)
		#根据__MRO__序列，访问User类的下一个类的初始化函数给本实例初始化
		if self.role is None:
		#如果用户没有角色
			if self.email == current_app.config['FLASKY_ADMIN']:
			#如果用户的email为本程序配置中'FLASKY_ADMIN'即管理员的邮件
				self.role = Role.query.filter_by(permissions = 0xff).first()
				#给予该用户管理员的权限
			if self.role is None:
			#如果用户没有角色且不是管理员
				self.role = Role.query.filter_by(default = True).first()
				#给予该用户普通用户的权限
	
	def can(self, permissions):
	#检验该用户的权限中是否包含请求的权限
		return self.role is not None and \
			(self.role.permissions & permissions) == permissions
		#要同时满足该用户的角色存在且请求的权限在其拥有的权限中时，返回Ture，否则False
		
	def is_administrator(self):
	#检验管理员的权限，如果为管理员权限则返回True
		return self.can(Permission.ADMINISTER)
		#用can方法检验
		
	def ping(self):
	#ping方法把last_seen设置为当前时间
		self.last_seen = datetime.utcnow()
		db.session.add(self)
		#提交到session会话中
	
	@staticmethod
	def generate_fake(count = 100):
		from sqlalchemy.exc import IntegrityError
		from random import seed
		import forgery_py
		
		seed()
		for i in range(count):
			u = User(email = forgery_py.internet.email_address(),
					username = forgery_py.internet.user_name(True),
					password = forgery_py.lorem_ipsum.word(),
					confirmed = True,
					name = forgery_py.address.city(),
					location = forgery_py.address.city(),
					about_me = forgery_py.lorem_ipsum.sentence(),
					member_since = forgery_py.date.date(True))
			db.session.add(u)
			try:
				db.session.commit()
			except IntegrityError:
				db.session.rollback()
	#生成虚拟博客文章
		
	def __repr__(self):
		return '<User %r>' % self.username
		#返回一个字符串，以供调试和测试

class Post(db.Model):
	__tablename__ = 'posts'
	id = db.Column(db.Integer, primary_key = True)
	body = db.Column(db.Text)
	timestamp = db.Column(db.DateTime, index = True, default = datetime.utcnow)
	author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
	#包含主体文本和时间戳和一个外键
	@staticmethod
	def generate_fake(count =100):
		from random import seed, randint
		import forgery_py
		
		seed()
		user_count = User.query.count()
		for i in range(count):
			u = User.query.offset(randint(0, user_count - 1)).first()
			p = Post(body = forgery_py.lorem_ipsum.sentences(randint(1,3)),
					timestamp = forgery_py.date.date(True),
					author = u)
			db.session.add(p)
			db.session.commit()
	#生成虚拟博客文章
	
	@staticmethod
	def on_changed_body(target, value, oldvalue, initiator):
	#这个函数的作用是把body字段中的文本渲染成HTML格式，结果保存在body_html中
		allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
						'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
						'h1', 'h2', 'h3', 'p']
		target.body_html = bleach.linkify(bleach.clean(
			#clean()函数接收HTML和允许使用的HTML标签，删除不在tags中的标签
			#linkify()函数将纯文本中的URL装换成适当的<a>链接
			markdown(value, output_format = 'html'),
			#markdown()函数将Markdown文本装换问HTML
			tags = allowed_tags, strip = True))
		
db.event.listen(Post.body, 'set', Post.on_changed_body)
#on_changed_body函数注册在body字段上，是SQLAlchemy"set"事件的监听程序
#意味着制药类实例body字段设了新值，函数就会被自动调用
@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))
	#接收user_id，如果用户存在，则返回用户对象，否则返回None

class AnonymousUser(AnonymousUserMixin):
#匿名用户类
#这个类是为了能让程序在不检查用户是否登录的条件下
#就自由调用current_user.can()和current_user.is_administrator()
	def can(self, permissions):
		return False
	#没有任何权限
	def is_administrator(self):
		return False
	#没有管理员权限
login_manager.anonymous_user = AnonymousUser
#把AnonymousUser类传给login_manager的anonymous_user属性