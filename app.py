#!/usr/bin/python
# -*- mode: python -*-
# -*- coding: utf-8 -*-

from flask import Flask, render_template, json, request, redirect, url_for, session, flash
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from markdown import markdown
import os, hashlib


# ...................................................................................................................................................................... #

app = Flask(__name__)
app.secret_key = os.urandom(256)        

SALT = 'foo#BAR_{baz}^666'

# ...................................................................................................................................................................... #

engineLogin = create_engine('sqlite:///wiki.db', echo=True)
engineFest = create_engine('mysql+mysqldb://root:ILF@localhost/ilovefestivals', convert_unicode=True, echo=False)
metadata = MetaData()
Base = declarative_base()
Base.metadata.reflect(engineFest)
db = engineFest.connect()

accounts = Table('accounts', metadata,
    Column('login', String, primary_key=true),
    Column('password_hash', String, nullable=False))    

pages = Table('pages', metadata,
    Column('name', String, primary_key=true),
    Column('text', String))

metadata.create_all(engineLogin)


# ...................................................................................................................................................................... #


# retourne le contenu de la page "name"
def page_content(name):
  db = engineLogin.connect()
  try:
    row = db.execute(select([pages.c.text]).where(pages.c.name == name)).fetchone()
    if row is None:
      return '**(This page is empty or does not exist.)**'
    return row[0]
  finally:
    db.close()

# fourni tous les noms des pages existantes
# utilisee pour la fonctionnalite "page-index"
def getPagesName():
  print("getPagesName")
  db = engineLogin.connect()
  row = db.execute(select([pages.c.name])).fetchall()
  print("getPagesName")
  print(row)
  db.close()
  return row

# si la page "name" n'existe pas, la cree, sinon met a jour son contenu
def update_page(name, text):
  db = engineLogin.connect()
  if db.execute(select([pages.c.name]).where(pages.c.name == name)).fetchone() is None :
    db.execute(pages.insert().values(name=name, text=text))
  else :
    db.execute(pages.update().values(text=text).where(pages.c.name == name))
  db.close()

# supprime la page "name"
def delete_page(name):
  print("model : delete_page : ",name)
  db = engineLogin.connect()
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
  db = engineLogin.connect()
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

# ...................................................................................................................................................................... #

class Artistes(Base):
    __table__ = Base.metadata.tables['artistes']

class Artistesfavuser(Base):
    __table__ = Base.metadata.tables['artistefavuser']

class Artistestyles(Base):
    __table__ = Base.metadata.tables['artistestyles']

class Festival(Base):
    __table__ = Base.metadata.tables['festival']

class Festivalfavuser(Base):
    __table__ = Base.metadata.tables['festivalfavuser']

class Festivalstyles(Base):
    __table__ = Base.metadata.tables['festivalstyles']

class Noteartisteuser(Base):
    __table__ = Base.metadata.tables['noteartisteuser']

class Notefestivaluser(Base):
    __table__ = Base.metadata.tables['notefestivaluser']

class Programmation(Base):
    __table__ = Base.metadata.tables['programmation']

class Style(Base):
    __table__ = Base.metadata.tables['style']

class User(Base):
    __table__ = Base.metadata.tables['user']

# ...................................................................................................................................................................... #


#@app.route('/index/') # BIP a eviter de decorer une fonction avec plusieurs routes (referencement), mais utile si user non identifie encore etc

@app.route('/')
def main():
    return render_template('index.html', data=data)

# ...............................................#
@app.route('/<name>')    
def index(name='Main'):
  return redirect('pages/'+name)

# utilisee pour la fonctionnalite "page-index"
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

# ...............................................#  

@app.route('/results')
def results():
    return render_template('results.html', artists=artists, festivals=festivals, requete=requete)

# @app.route('/')
# def my_form():
#     return render_template("my-form.html")

@app.route('/decouverte/') #on peut rajouter un slash a la fois que que les routes http://localhost:5000/decouverte et http://localhost:5000/decouverte/ soient toutes deux acceptees (sinon on peut rencontrer 404)
def decouverte():
    return render_template('decouverte.html')

@app.route('/topten/')
def topten():
    return render_template('top10.html')

@app.route('/decouverte/hot/')
def hot():
    return render_template('hot.html')

@app.route('/decouverte/recommendations/')
def recommendations():
    return render_template('recommendations.html')

@app.route('/classement2016/')
def classement2016():
	return render_template('classement2016.html')

@app.route('/classement2015/')
def classement2015():
	return render_template('classement2015.html')

@app.route('/classement2014/')
def classement2014():
	return render_template('classement2014.html')

@app.route('/artistes/')
def artistes():
    return render_template('artistes.html', artists=artists, festivals=festivals, requete=requete, genre=genre, concerts=concerts )    

@app.route('/festivals/')
def festivals():
    return render_template('festivals.html', artists=artists, festivals=festivals, requete=requete , genre=genre, url=url, dateDeb=dateDeb, dateFin=dateFin, taille=taille, prix=prix, lieu=lieu, prog=prog)    

# @app.route('/profil/')
# def profil():
#     return render_template('profil.html')       

# @app.route('/login/')
# def login():
# 	return render_template('login.html')


# ...................................................................................................................................................................... #

data = []
artists = []
festivals = []
requete = []
genre = []
concerts = []
url = []
dateDeb = []
dateFin = []
taille = []
prix = []
lieu = []
prog = []

#GERER LES RECHERCHES SUR 'index.html'
@app.route('/post', methods=['POST'])
def post():

  del data[:]
  del artists[:]
  del festivals[:]
  del requete[:]

  recherche = request.form['post']
  requete.append(recherche)

  print("Je suis la recherche : %s", requete[0])

  #RECHERCHES PAR GENRE (DANS MYSQL)
  resultArtists = db.execute("SELECT artistes.NomArtiste FROM artistes, artistestyles, style WHERE artistes.idartiste = artistestyles.idartiste AND artistestyles.idstyle = style.idstyle AND style.NomStyle = '%s' collate utf8_bin", recherche)
  resultFestivals = db.execute("SELECT festival.NomFestival FROM festival, festivalstyles, style WHERE festival.idFestival = festivalstyles.idFestival AND festivalstyles.idstyle = style.idstyle AND style.NomStyle = '%s' collate utf8_bin", recherche)

  #RECHERCHE PAR ARTISTE
  resultArtistsBis = db.execute("SELECT festival.NomFestival FROM artistes LEFT JOIN programmation ON programmation.idArtiste = artistes.idArtiste LEFT JOIN festival ON programmation.idFestival = festival.idFestival WHERE (artistes.NomArtiste like '%s' collate utf8_bin)", recherche)


  #STOCKAGE DES RESULTATS DANS DES LISTES

  #Donne les Artistes du genre "recherche"
  all = resultArtists.fetchall()
  print (all)
  for x in range(len(all)):
        artists.append(all[x][0])
        print(artists)
  #Donne les Festivals du genre "recherche"
  all = resultFestivals.fetchall()
  print (all)
  for x in range(len(all)):
        festivals.append(all[x][0])
        print(festivals)

  #Donne les festivals ou l'artiste "recherche" sera present
  all = resultArtistsBis.fetchall()
  print (all)
  indice = 0
  for x in range(len(all)):
        festivals.append(all[x][0])
        indice+=1
        print(festivals)
  if (indice != 0):
        artists.append(recherche)


  return redirect(url_for('results'))


#GERER LES RECHERCHES SUR 'festivals.html'
@app.route('/postFestivals', methods=['POST'])
def postFestivals():

  del data[:]
  del artists[:]
  del festivals[:]
  del requete[:]
  del genre[:]
  del url[:]
  del dateDeb[:]
  del dateFin[:]
  del taille[:]
  del prix[:]
  del lieu[:]
  del prog[:]

  recherche = request.form['post']
  requete.append(recherche)

  print("Je suis la recherche : %s", requete[0])

  #RECHERCHE LE FESTIVAL
  resultFestival = db.execute("SELECT festival.NomFestival FROM festival WHERE (festival.NomFestival like %s)", recherche)
  #RECHERCHES GENRES du festival
  #resultGenre = db.execute("SELECT style.NomStyle FROM festival LEFT JOIN festivalstyles ON festivalstyles.idFestival = festival.idFestival LEFT JOIN style ON festivalstyles.idStyle = style.idStyle  WHERE (festival.NomFestival like %s)", recherche)
  #RECHERCHE URL du festival
  resultURL = db.execute("SELECT festival.urlsite FROM festival WHERE (festival.NomFestival like %s)", recherche)
  #RECHERCHE DATE du festival
  resultDateDebut = db.execute("SELECT festival.DateDebut FROM festival WHERE (festival.NomFestival like %s)", recherche)
  resultDateFin = db.execute("SELECT festival.DateFin FROM festival WHERE (festival.NomFestival like %s)", recherche)
  #RECHERCHE TAILLE du festival
  resultTaille = db.execute("SELECT festival.Taille FROM festival WHERE (festival.NomFestival like %s)", recherche)
  #RECHERCHE PRIX du festival
  resultPrix = db.execute("SELECT festival.Prix FROM festival WHERE (festival.NomFestival like %s)", recherche)
  #RECHERCHE LIEU du festival
  resultLieu = db.execute("SELECT festival.Lieu FROM festival WHERE (festival.NomFestival like %s)", recherche)

  #RECHERCHES PROGRAMMATION du festival
  resultProg = db.execute("SELECT artistes.NomArtiste FROM artistes LEFT JOIN programmation ON programmation.idArtiste = artistes.idArtiste LEFT JOIN festival ON programmation.idFestival = festival.idFestival  WHERE (festival.NomFestival like %s)", recherche)

  #STOCKAGE DES RESULTATS DANS DES LISTES
  #Donne le festival "recherche" 
  all = resultFestival.fetchone()
  print (all)
  if (all != None):
    for x in range(len(all)):
      festivals.append(all[x][0])
      print(festivals)

  #Donne le genre du festival "recherche" 
  #all = resultGenre.fetchall()
  #print (all)
  #if (all != None):
  #  x = []
  #  for x in range(len(all)):
  #    genre.append(all[x])
  #    print(genre)



  #Donne l'url du festival "recherche" 
  all = resultURL.fetchone()
  print (all)
  if (all != None):
    url.append(all[0])
    print(url)
    
  #Donne la date du festival "recherche" 
  all = resultDateDebut.fetchone()
  print (all)
  if (all != None):
        dateDeb.append(all[0])
        print(dateDeb)
  all = resultDateFin.fetchone()
  print (all)
  if (all != None):
        dateFin.append(all[0])
        print(dateFin)      
  
  #Donne la taille du festival "recherche" 
  all = resultTaille.fetchone()
  print (all)
  if (all != None):
    taille.append(all[0])
    print(taille)

  #Donne le prix du festival "recherche" 
  all = resultPrix.fetchone()
  print (all)
  if (all != None):
    prix.append(all[0])
    print(prix)
  
  #Donne le lieu du festival "recherche" 
  all = resultLieu.fetchone()
  print (all)
  if (all != None):
    lieu.append(all[0])
    print(lieu)

  #Donne les Artistes se produisant au festival "recherche"
  all = resultProg.fetchall()
  print (all)
  for x in range(len(all)):
        prog.append(all[x][0])
        print(prog)

  return redirect(url_for('festivals'))

  

#GERER LES RECHERCHES SUR 'artistes.html'
@app.route('/postArtist', methods=['POST'])
def postArtist():

  del data[:]
  del artists[:]
  del festivals[:]
  del requete[:]
  del genre[:]
  del concerts[:]

  recherche = request.form['post']
  requete.append(recherche)

  print("Je suis la recherche : %s", requete[0])

  #RECHERCHE L'ARTISTE
  resultArtist = db.execute("SELECT artistes.NomArtiste FROM artistes WHERE (artistes.NomArtiste like %s)", recherche)
  #RECHERCHE GENRE de l'artiste
  resultGenre = db.execute("SELECT style.NomStyle FROM style LEFT JOIN artistestyles ON artistestyles.idStyle = style.idStyle LEFT JOIN artistes ON artistestyles.idArtiste = artistes.idArtiste WHERE (artistes.NomArtiste like %s)", recherche)
  #RECHERCHE CONCERTS de l'artiste
  resultConcerts = db.execute("SELECT festival.NomFestival FROM artistes LEFT JOIN programmation ON programmation.IdArtiste = artistes.idArtiste LEFT JOIN festival ON programmation.idFestival = festival.idFestival WHERE (artistes.NomArtiste like %s)",recherche)


  #STOCKAGE DES RESULTATS DANS DES LISTES
  #Donne l'artiste "recherche" 
  all = resultArtist.fetchone()
  print (all)
  print ("je suis dans (nom artiste)")
  if (all != None):
    artists.append(all[0])
    print(artists)

  #Donne le genre de l'artiste "recherche" 
  all = resultGenre.fetchall()
  print (all)
  if (all != None):
    x = []
    for x in range(len(all)):
      genre.append(all[x])
      print(genre)


  #Donne les concerts ou se produit l'artiste 
  all = resultConcerts.fetchall()
  print (all)
  if (all != None):
    x = []
    for x in range(len(all)):
      concerts.append(all[x])
      print(concerts)

  return redirect(url_for('artistes'))

# ...................................................................................................................................................................... #


if __name__ == '__main__':
    app.run(debug=True) #BIP mettre false a la fin
