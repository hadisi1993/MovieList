import click

@app.cli.command()
@app.option('--drop',is_flag = True,help='Create after drop.')#设置选项
def initdb(drop):
	"""Initialize the database"""
	if drop:   #判断是否输入了选项
		db.drop_all()
	db.create_all()
	click.echo('Initialize database') #输出提示信息
	
	