from werkzeug.security import generate_password_hash,check_password_hash
from movielist import db
from flask_login import UserMixin

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

