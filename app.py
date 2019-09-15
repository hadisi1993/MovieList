import os
import sys
import click

from flask import Flask,render_template,url_for,redirect,flash,request
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import LoginManager,UserMixin,login_user,login_required,logout_user,current_user
from flask_sqlalchemy import SQLAlchemy #导入扩展类

Win = sys.platform.startswith('win')
if Win:
	prefix = "sqlite:///"
else:
	prefix = "sqlite:////"
app = Flask(__name__) 
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')

app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path,'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager=LoginManager(app) #实例化扩展

class User(db.Model,UserMixin):
	id = db.Column(db.Integer,primary_key = True)#主键
	name = db.Column(db.String(20)) #姓名
	username=db.Column(db.String(20))
	password_hash=db.Column(db.String(128))  #密码散列值
	
	def set_password(self,password):
		self.password_hash = generate_password_hash(password)  #将生成的密码保存到对应字段
		
	def validate_password(self,password):     #判断密码是否正确
		return check_password_hash(self.password_hash,password)
		
		
class Movie(db.Model):
	id = db.Column(db.Integer,primary_key = True)#主键	
	title = db.Column(db.String(60))  #标题
	year = db.Column(db.String(4))	  #年份

@app.cli.command()
@click.option('--drop',is_flag = True,help='Create after drop.')#设置选项
def initdb(drop):
	"""Initialize the database"""
	if drop:   #判断是否输入了选项
		db.drop_all()
	db.create_all()
	click.echo('Initialized database.') #输出提示信息
	
@app.cli.command()
def forge():
	"""Generate fake data"""
	db.create_all()
	name = 'WangZeQuan'
	movies = [ {'title': 'My Neighbor Totoro', 'year': '1988'}, {'title': 'Dead Poets Society', 'year': '1989'}, {'title': 'A Perfect World', 'year': '1993'}, {'title': 'Leon', 'year': '1994'}, {'title': 'Mahjong', 'year': '1996'}, {'title': 'Swallowtail Butterfly', 'year': '1996'}, {'title': 'King of Comedy', 'year': '1999'}, {'title': 'Devils on the Doorstep', 'year': '1999'}, {'title': 'WALL-E', 'year': '2008'},{'title': 'The Pork of Music', 'year': '2012'}, ]

	user = User(name=name)
	db.session.add(user)
	for m in movies:
		movie= Movie(title=m['title'],year = m['year'])
		db.session.add(movie)
		
	db.session.commit()
	click.echo('Done.')
	
@app.context_processor
def inject_user():
	user = User.query.first()
	return dict(user=user)  #返回字典
	
@app.route('/movie/edit/<int:movie_id>',methods=['GET','POST'])	
@login_required
def edit(movie_id):
	movie = Movie.query.get_or_404(movie_id)
	
	
	if request.method == "POST":
		#获取登录信息
		title=request.form.get('title')
		year=request.form.get('year')
		#验证信息
		if not title or not year or len(year)>4 or len(title)>60:
			flash("Invaild input.")
			return redirect(url_for('edit',movie_id = movie_id))
			
		movie.title = title # 更新标题
		movie.year = year
		db.session.commit()
		flash("Item updated.")	
		return redirect(url_for('index'))
		
	return render_template('edit.html',movie=movie)  #传入被编辑的电影条目

@app.route('/movie/delete/<int:movie_id>',methods=['POST'])
@login_required #登录保护
def delete(movie_id):
	movie = Movie.query.get_or_404(movie_id)
	db.session.delete(movie)
	db.session.commit()
	flash('Item deleted.')
	return redirect(url_for('index'))
	
@app.route('/',methods= ['GET','POST']) 
def index(): 
	if request.method == "POST":
		if not current_user.is_authenticated:  #如果当前用户未认证
			return redirect(url_for('index'))
		title = request.form.get('title')
		year = request.form.get('year')
		#验证数据
		if not title or not year or len(year)>4 or len(title)>60:
			flash("Invaild input.")
			return redirect(url_for('index'))
		#保存表单数据到数据库
		movie = Movie(title=title,year=year)
		db.session.add(movie)
		db.session.commit()
		flash('Item created.')
		return redirect(url_for('index')) #从定向会主页
		
	user = User.query.first()#读取用户记录
	movies = Movie.query.all()
	return render_template('index.html',user = user,movies = movies)
	
	
@app.errorhandler(404)
def page_not_found(e):
	user = User.query.first()
	return render_template('404.html',user = user),404
	
	
	
@app.cli.command()
@click.option('--username',prompt=True, help='The username used to login.')
@click.option('--password',prompt=True, hide_input=True,confirmation_prompt=True,help='The password used to login.')
def admin(username,password):
	"""Create user"""
	db.create_all()
	
	user = User.query.first()
	if user is not None:
		click.echo("Updating user...")
		user.username=username
		user.set_password(password)
		
	else:
		click.echo("Creating user...")
		user= User(username=username,name='Admin')
		user.set_password(password)
		db.session.add(user)
		
	db.session.commit()
	
	click.echo('Done.')
	
	
@login_manager.user_loader
def load_user(user_id):   #创建用户加载回调函数，接受用户ID作为参数
	user=User.query.get(int(user_id))
	return user
	
login_manager.login_view = 'login'
	
	
@app.route('/login',methods=['GET','POST'])
def login():
	if request.method=='POST':
		username=request.form['username']
		password=request.form['password']
		
		if not username or not password:
			flash("Invaild input.")
			return redirect(url_for('login'))
			
			
		user = User.query.first()
		#验证用户名和密码
		if username==user.username and user.validate_password(password):
			login_user(user)
			flash('Login success.')
			return redirect(url_for('index'))
			
		flash('Invaild username or password.')
		
		return redirect(url_for('login'))
		
	return render_template('login.html')
		
		
@app.route('/logout')
@login_required #用于认证登录的保护
def logout():
	logout_user()
	flash('Goodbye.')
	return redirect(url_for('index'))  #从定向回首页
	
	
@app.route('/settings',methods=['GET','POST'])
@login_required
def settings():
	if request.method=="POST":
		name = request.form['name']
		if not name or len(name)>20:
			flash('Invaild input.')
			return redirect(url_for('settings'))
			
		current_user.name = name
		#current_user会返回当前登录用户的数据库纪录对象
		db.session.commit()
		flash('Settings updated.')
		return redirect(url_for('index'))
		
	return render_template('settings.html')