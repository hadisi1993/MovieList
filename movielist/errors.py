from flask import render_template

from movielist import app

@app.errorhandler(404)
def page_not_found(e):
	return render_template('/errores/404.html'),404
	
@app.errorhandler(400)
def bad_request(e):
	return render_template('/errores/400.html'),400
	
@app.errorhandler(500)
def internal_server_error(e):
	return render_template('/errores/500.html'),500
		