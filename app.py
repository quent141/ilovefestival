#!/usr/bin/python
# -*- mode: python -*-
# -*- coding: utf-8 -*-

from flask import Flask, render_template, json, request, redirect, url_for
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('mysql+mysqldb://root:ILF@localhost/ilovefestivals', convert_unicode=True, echo=False)
Base = declarative_base()
Base.metadata.reflect(engine)
connection = engine.connect()

from sqlalchemy.orm import relationship, backref

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




app = Flask(__name__)

#@app.route('/index/') # BIP a eviter de decorer une fonction avec plusieurs routes (referencement), mais utile si user non identifie encore etc

@app.route('/')
def main():
    return render_template('index.html', data=data)

@app.route('/results')
def results():
    return render_template('results.html', artists=artists, festivals=festivals, requete=requete)

@app.route('/')
def my_form():
    return render_template("my-form.html")

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
    return render_template('artistes.html')    

@app.route('/festivals/')
def festivals():
    return render_template('festivals.html', artists=artists, festivals=festivals, requete=requete , genre=genre, url=url, dateDeb=dateDeb, dateFin=dateFin, taille=taille, prix=prix, lieu=lieu, prog=prog)    

@app.route('/profil/')
def profil():
    return render_template('profil.html')       

@app.route('/login/')
def login():
	return render_template('login.html')


#GERER LES RECHERCHES SUR 'index.html'

data = []
artists = []
festivals = []
requete = []
genre = []
url = []
dateDeb = []
dateFin = []
taille = []
prix = []
lieu = []
prog = []

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
  resultArtists = connection.execute("SELECT artistes.NomArtiste FROM artistes, artistestyles, style WHERE artistes.idartiste = artistestyles.idartiste AND artistestyles.idstyle = style.idstyle AND style.NomStyle = %s", recherche)
  resultFestivals = connection.execute("SELECT festival.NomFestival FROM festival, festivalstyles, style WHERE festival.idFestival = festivalstyles.idFestival AND festivalstyles.idstyle = style.idstyle AND style.NomStyle = %s", recherche)

  #RECHERCHE PAR ARTISTE
  resultArtists2 = connection.execute("SELECT festival.NomFestival FROM artistes LEFT JOIN programmation ON programmation.idArtiste = artistes.idArtiste LEFT JOIN festival ON programmation.idFestival = festival.idFestival WHERE (artistes.NomArtiste like %s)", recherche)


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
  all = resultArtists2.fetchall()
  print (all)
  indice = 0
  for x in range(len(all)):
        festivals.append(all[x][0])
        indice+=1
        print(festivals)
  if (indice != 0):
        artists.append(recherche)


  return redirect(url_for('results'))


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
  resultFestival = connection.execute("SELECT festival.NomFestival FROM festival WHERE (festival.NomFestival like %s)", recherche)
  #RECHERCHES GENRES du festival
  resultGenre = connection.execute("SELECT style.NomStyle FROM festival LEFT JOIN festivalstyles ON festivalstyles.idFestival = festival.idFestival LEFT JOIN style ON festivalstyles.idStyle = style.idStyle  WHERE (festival.NomFestival like %s)", recherche)
  #RECHERCHE URL du festival
  resultURL = connection.execute("SELECT festival.urlsite FROM festival WHERE (festival.NomFestival like %s)", recherche)
  #RECHERCHE DATE du festival
  resultDateDebut = connection.execute("SELECT festival.DateDebut FROM festival WHERE (festival.NomFestival like %s)", recherche)
  resultDateFin = connection.execute("SELECT festival.DateFin FROM festival WHERE (festival.NomFestival like %s)", recherche)
  #RECHERCHE TAILLE du festival
  resultTaille = connection.execute("SELECT festival.Taille FROM festival WHERE (festival.NomFestival like %s)", recherche)
  #RECHERCHE PRIX du festival
  resultPrix = connection.execute("SELECT festival.Prix FROM festival WHERE (festival.NomFestival like %s)", recherche)
  #RECHERCHE LIEU du festival
  resultLieu = connection.execute("SELECT festival.Lieu FROM festival WHERE (festival.NomFestival like %s)", recherche)

  #RECHERCHES PROGRAMMATION du festival
  resultProg = connection.execute("SELECT artistes.NomArtiste FROM artistes LEFT JOIN programmation ON programmation.idArtiste = artistes.idArtiste LEFT JOIN festival ON programmation.idFestival = festival.idFestival  WHERE (festival.NomFestival like %s)", recherche)

  #STOCKAGE DES RESULTATS DANS DES LISTES
  #Donne le festival "recherche" 
  all = resultFestival.fetchone()
  print (all)
  if (all != None):
    festivals.append(all[0])
    print(festivals)

  #Donne le genre du festival "recherche" 
  all = resultGenre.fetchone()
  print (all)
  if (all != None):
    genre.append(all[0])
    print(genre)

  #Donne l'url du festival "recherche" 
  all = resultURL.fetchone()
  print (all)
  if (all != None):
    url.append(all[0])
    print(url)
    
  #Donne la date du festival "recherche" 
  all = resultDateDebut.fetchall()
  print (all)
  if (all != None):
    for x in range(len(all)):
        dateDeb.append(all[x][0])
        print(dateDeb)
  all = resultDateFin.fetchall()
  print (all)
  if (all != None):
    for x in range(len(all)):
        dateFin.append(all[x][0])
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
  



if __name__ == '__main__':
    app.run(debug=True) #BIP mettre false a la fin
    #app.secret_key = '2d9-E2.)f&e,A$p@fpa+zSU03e09_'
