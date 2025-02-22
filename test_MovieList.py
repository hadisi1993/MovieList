import unittest

from movielist import app, db
from movielist.models import Movie, User
from movielist.commands import forge, initdb

class MovielistTestCase(unittest.TestCase):
	
	def setUp(self):
		#更新配置
		app.config.update(
			TESTING = True,
			SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
		)
		#创建数据库
		db.create_all()
		#创建测试数据，一个用户，一个电影条目
		user = User(name='Test',username='test')
		user.set_password('123')
		movie = Movie(title='Test Movie Title',year='2019')
		#使用add_all()方法一次添加多个模型类实例，传入列表
		db.session.add_all([user,movie])
		db.session.commit()
		
		self.client = app.test_client()
		self.runner = app.test_cli_runner()
		
		
	def tearDown(self):
		db.session.remove()  #清除数据库会话
		db.drop_all()	#删除数据库表
		
	def test_app_exist(self):
		self.assertIsNotNone(app)
		
	def test_app_is_testing(self):
		self.assertTrue(app.config['TESTING'])
		
	def test_or_404(self):
		response = self.client.get('/nothing')
		data = response.get_data(as_text=True)
		self.assertIn('Page Not Found - 404',data)
		self.assertIn('Go Back',data)
		self.assertEqual(response.status_code,404)
		
	#测试主页
	
	def test_index_page(self):
		response = self.client.get('/')
		data = response.get_data(as_text = True)
		self.assertIn("Test's MovieList",data)
		self.assertIn('Test Movie Title',data)
		self.assertEqual(response.status_code,200)
		
	#辅助方法，便于登录
	def login(self):
		self.client.post('/login',data = dict(username = 'test',password = '123'),follow_redirects=True)
		
		
	def test_create_item(self):
		self.login()
		
		#创建条目操作
		response = self.client.post('/',data = dict(title='New Movie',year = '2019'),follow_redirects = True)
		data = response.get_data(as_text = True)
		self.assertIn('Item created.',data)
		self.assertIn('New Movie',data)
		
		#测试条目操作，但标题为空
		response = self.client.post('/',data = dict(title = '',year = '2019'),follow_redirects = True)
		data = response.get_data(as_text=True)
		self.assertNotIn('Item created.',data)
		self.assertIn('Invaild input.',data)
		
		#测试创建条目操作，但电影年份为空
		response = self.client.post('/',data = dict(title = 'New Movie',year = ''),follow_redirects = True)
		data = response.get_data(as_text = True)
		self.assertNotIn('Item created.',data)
		self.assertIn('Invaild input.',data)
		
	def test_update_item(self):
		self.login()
		
		#测试更新页面
		response = self.client.get('/movie/edit/1')
		data = response.get_data(as_text = True)
		self.assertIn('Edit item',data)
		self.assertIn('Test Movie Title',data)
		self.assertIn('2019',data)
		
		#测试更新条目测试
		response =self.client.post('/movie/edit/1',data = dict(title = 'New Movie Edited',year = '2019'),follow_redirects=True)
		data = response.get_data(as_text = True)
		self.assertIn('Item updated.',data)
		self.assertIn('New Movie Edited',data)
		
		#测试更新条目操作，但电影标题和年份分别为空
		response =self.client.post('/movie/edit/1',data = dict(title = '',year = '2019'),follow_redirects=True)
		data = response.get_data(as_text = True)
		self.assertNotIn('Item updated.',data)
		self.assertIn('Invaild input.',data)
		
		response =self.client.post('/movie/edit/1',data = dict(title = 'New Movie Edited Again',year = ''),follow_redirects=True)
		data = response.get_data(as_text = True)
		self.assertNotIn('Item updated.',data)
		self.assertNotIn('New Movie Edited Again',data)
		self.assertIn('Invaild input.',data)
		
	
	def test_delete_item(self):
		self.login()
		
		response = self.client.post('/movie/delete/1',follow_redirects = True)
		data = response.get_data(as_text=True)
		self.assertIn('Item deleted.',data)
		self.assertNotIn('Test Movie Title',data)
		
	def test_login_protect(self):
		response = self.client.get('/')
		data = response.get_data(as_text = True)
		self.assertNotIn('Logout',data)
		self.assertNotIn('Settings',data)
		self.assertNotIn('<form method = "post">',data)
		self.assertNotIn('Delete',data)
		self.assertNotIn('Edit',data)
		
	#测试登录
	def test_login(self):
		response = self.client.post('/login',data = dict(username = 'test',password = '123'),follow_redirects = True)
		data = response.get_data(as_text = True)
		self.assertIn('Login success',data)
		self.assertIn('Logout',data)
		self.assertIn('Settings',data)
		self.assertIn('Delete',data)
		self.assertIn('Edit',data)
		self.assertIn('<form method = "post">',data)
		
		#测试使用错误的密码登录
		response = self.client.post('/login',data = dict(username = 'test',password = '456'),follow_redirects = True)
		data = response.get_data(as_text = True)
		self.assertNotIn('Login success.',data)
		self.assertIn('Invaild username or password.',data)
		
		#测试使用错误的用户名登录
		response = self.client.post('/login',data = dict(username = 'wrong',password = '123'),follow_redirects = True)
		data = response.get_data(as_text = True)
		self.assertNotIn('Login success.',data)
		self.assertIn('Invaild username or password.',data)
		
		#测试使用空用户名登录
		response = self.client.post('/login',data = dict(username = '',password = '123'),follow_redirects = True)
		data = response.get_data(as_text = True)
		self.assertNotIn('Login success.',data)
		self.assertIn('Invaild input.',data)
		
		#测试使用空用户名登录
		response = self.client.post('/login',data = dict(username = 'test',password = ''),follow_redirects = True)
		data = response.get_data(as_text = True)
		self.assertNotIn('Login success.',data)
		self.assertIn('Invaild input.',data)
		
	#测试登出
	def test_logout(self):
		self.login()
		
		response = self.client.get('/logout',follow_redirects = True)
		data = response.get_data(as_text = True)
		self.assertIn('Goodbye.',data)
		self.assertNotIn('Logout',data)
		self.assertNotIn('Settings',data)
		self.assertNotIn('Delete',data)
		self.assertNotIn('Edit',data)
		self.assertNotIn('<form method = "post">',data)
		
	def test_settings(self):
		self.login()
		
		#测试设置界面
		response = self.client.get('/settings')
		data = response.get_data(as_text = True)
		self.assertIn('Settings',data)
		self.assertIn('Your name',data)
		
		#测试更新设置
		response = self.client.post('/settings',data = dict(name = ''),follow_redirects=True)
		data = response.get_data(as_text = True)
		self.assertNotIn('Settings updated.',data)
		self.assertIn('Invaild input.',data)
		
		
		#测试更新测试,名称为空
		response = self.client.post('settings',data = dict(name = ''),follow_redirects = True)
		data = response.get_data(as_text=True)
		self.assertNotIn('Settings updated.',data)
		self.assertIn('Invaild input.',data)
		
	def test_forge_command(self):
		#测试虚拟数据
		result = self.runner.invoke(forge)
		self.assertIn('Done.',result.output)
		self.assertNotEqual(Movie.query.count(),0)
		
	#测试初始化数据库
	def test_initdb_command(self):	
		result = self.runner.invoke(initdb)
		self.assertIn('Initialized database.',result.output)
		
	#测试生成管理员账户
	def test_admin_command(self):
		db.drop_all()
		db.create_all()
		result = self.runner.invoke(args = ['admin','--username','hadisi1990','--password','12340852'])
		self.assertIn('Creating user...',result.output)
		self.assertIn('Done.',result.output)
		self.assertEqual(User.query.count(),1)
		self.assertEqual(User.query.first().username,'hadisi1990')
		self.assertTrue(User.query.first().validate_password('12340852'))
		
	def test_admin_command_update(self):
		#使用args参数给出完整的命令参数列表
		result = self.runner.invoke(args = ['admin','--username','peter','--password','456'])
		self.assertIn('Updating user...',result.output)
		self.assertIn('Done.',result.output)
		self.assertEqual(User.query.count(),1)
		self.assertEqual(User.query.first().username,'peter')
		self.assertTrue(User.query.first().validate_password('456'))
		
if __name__ == "__main__":
	unittest.main()
		
		
		