# ............................................................................................... #

from flask  import *
from sqlalchemy import *
from markdown import markdown
import os, hashlib

# ............................................................................................... #

app = Flask(__name__)
app.secret_key = os.urandom(256)		

SALT = 'foo#BAR_{baz}^666'			  

# ............................................................................................... #

engine = create_engine('sqlite:///wiki.db', echo=True)
metadata = MetaData()

accounts = Table('accounts', metadata,
	Column('login', String, primary_key=true),
	Column('password_hash', String, nullable=False))	

pages = Table('pages', metadata,
	Column('name', String, primary_key=true),
	Column('text', String))

metadata.create_all(engine)

# ............................................................................................... #
#                                   MODEL
# A partir d'ici sont les méthodes du Model, ce sont elles qui font les appels à la base de données 
# et transmets des données fiables au Controler. 
# 
# Par fiable j'entends non corrompues. Par exemple, 
# si le model doit retourner le contenu d'une page et que la page demandée n'existe pas, le model 
# doit informer le controler (en retournant False par exemple) au lieu de retoutner un None qui
# pourrait faire planter le Controler. 
# ............................................................................................... #

# retourne le contenu de la page "name"
def page_content(name):
	db = engine.connect()
	try:
		row = db.execute(select([pages.c.text]).where(pages.c.name == name)).fetchone()
		if row is None:
			return '**(This page is empty or does not exist.)**'
		return row[0]
	finally:
		db.close()

# fourni tous les noms des pages existantes
# utilisée pour la fonctionnalité "page-index"
def getPagesName():
	print("getPagesName")
	db = engine.connect()
	row = db.execute(select([pages.c.name])).fetchall()
	print("getPagesName")
	print(row)
	db.close()
	return row

# si la page "name" n'existe pas, la crée, sinon met à jour son contenu
def update_page(name, text):
	db = engine.connect()
	if db.execute(select([pages.c.name]).where(pages.c.name == name)).fetchone() is None :
		db.execute(pages.insert().values(name=name, text=text))
	else :
		db.execute(pages.update().values(text=text).where(pages.c.name == name))
	db.close()

# supprime la page "name"
def delete_page(name):
	print("model : delete_page : ",name)
	db = engine.connect()
	db.execute(pages.delete().where(pages.c.name==name))	
	db.close()
	return redirect('/page.html')


def hash_for(password):
	salted = '%s @ %s' % (SALT, password)
	return hashlib.sha256(salted).hexdigest()	   

# si le "login" n'existe pas, cree le user sinon, 
# verifie que le login correspond au mot de passe et retourne vrai ou faux 
def authenticate_or_create(login, password):
	print("authenticate_or_create",login,password)
	db = engine.connect()
	hpass = hash_for(password)
	if db.execute(select([accounts.c.login]).where(accounts.c.login == login)).fetchone() is None :
		print("authenticate_or_create : createUser",login,password)
		db.execute(accounts.insert().values(login=login, password_hash=hpass))
		db.close()
		return True
	else : 
		if db.execute(select([accounts.c.password_hash]).where(accounts.c.login == login)).fetchone().password_hash == hpass :
			print("authenticate_or_create : loggin success",login,password)
			db.close()
			return True
		else :
			print("authenticate_or_create : loggin failed",login,password)
			db.close()
			return False


# ............................................................................................... #
#                                          CONTROLER
# Ce sont ces méthodes qui recoivent les demandes des clients via des URL. En fonction des demandes,
# le Controler appelle des Models, met en forme les données recues et les transmets à un template.
# ............................................................................................... #

@app.route('/')
def main():
    return render_template('index.html')

@app.route('/<name>')
def index(name='Main'):
	return redirect('/pages/' + name)

# utilisée pour la fonctionnalité "page-index"
@app.route('/page-index')
def allPages():
	pagesList = getPagesName() #call du model
	return render_template("pages-index.html",pagesList=pagesList) #call du template

@app.route('/pages/<name>')
def page(name):
	raw = page_content(name)
	content = markdown(raw)
	return render_template('page.html', name=name, text=content, raw=raw)

@app.route('/page_delete/<name>')
def delete(name):
	print("delete pages : ",name)
	delete_page(name)
	return redirect('/deleteSucess')

@app.route('/api/renderMarkdown', methods=['POST'])
def renderMarkdown():
	content = request.form['text']
	print("controler : renderMarkdown",content)
	return jsonify(markdown = content)
	



@app.route('/save', methods=['POST'])
def save():
	page = request.form['page']
	text = request.form['text']
	update_page(page,text)
	return redirect('pages/'+page)

@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		if authenticate_or_create(request.form['login'],request.form['password']) :
			session['username'] = request.form['login']
			return redirect('/pages')
		else :
			flash("login fail, wrong password")
			return render_template('login.html',from_page = 'page1',login=request.form['login'])
	elif request.method == 'GET':
		return render_template('login.html',from_page = 'page1')

@app.route('/logout')
def logout():
	from_page = request.args.get('from', 'Main')
	session.clear()
	return redirect('/pages/' + from_page)  

# ............................................................................................... # 
    
if __name__ == '__main__':
	app.debug = True
	app.run(host='0.0.0.0')
	#app.run(debug=True)

# ............................................................................................... #