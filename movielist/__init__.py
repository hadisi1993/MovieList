import os
import sys

from flask import Flask
from flask_sqlalchemy import SQLAlchemy #导入扩展类
from flask_login import LoginManager
#更新路径
Win = sys.platform.startswith('win')
if Win:
	prefix = "sqlite:///"
else:
	prefix = "sqlite:////"
	
app = Flask(__name__) 
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')	

app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(os.path.dirname(app.root_path),os.getenv('DATABASE_FILE', 'data.db'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager=LoginManager(app) #实例化扩展


@login_manager.user_loader
def load_user(user_id):   #创建用户加载回调函数，接受用户ID作为参数
	from movielist.models import User	
	user=User.query.get(int(user_id))
	return user
	
login_manager.login_view = 'login'

@app.context_processor
def inject_user():
	from movielist.models import User
	user = User.query.first()
	return dict(user=user)  #返回字典
	
from movielist import views,errors,commands