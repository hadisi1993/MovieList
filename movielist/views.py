from flask import Flask,render_template,url_for,redirect,flash,request
from flask_login import LoginManager,UserMixin,login_user,login_required,logout_user,current_user

from movielist import app,db
from movielist.models import User,Movie

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