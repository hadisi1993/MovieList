import os
import sys
import click

from flask import Flask,render_template,url_for,redirect,flash,request
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

class User(db.Model):
	id = db.Column(db.Integer,primary_key = True)#主键
	name = db.Column(db.String(20)) #姓名

	
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
	click.echo('Initialize database') #输出提示信息
	
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
def edit(movie_id):
	movie = Movie.query.get_or_404(movie_id)
	
	
	if request.method=="POST":
		#获取登录信息
		title=request.form.get('title')
		year=request.form.get('year')
		#验证信息
		if not title or not year or len(year)>4 or len(title)>60:
			flash("Invalid Error.")
			return redirect(url_for('index'))
		movie = Movie(title=title,year=year)
		db.session.add(movie)
		db.session.commit()
		flash("Item Created.")	
		return redirect(url_for('index'))
		
	return render_template('edit.html',movie=movie)  #传入被编辑的电影条目

@app.route('/movie/delete/<int:movie_id>',methods=['POST'])
def delete(movie_id):
	movie = Movie.query.get_or_404(movie_id)
	db.session.delete(movie)
	db.session.commit()
	flash('Item deleted')
	return redirect(url_for('index'))
	
@app.route('/',methods= ['GET','POST']) 
def index(): 
	if request.method == "POST":
		title = request.form.get('title')
		year = request.form.get('year')
		#验证数据
		if not title or not year or len(year)>4 or len(title)>60:
			flash("Invalid Error.")
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
	