
from flask import Flask, render_template,json, request
app = Flask(__name__)

@app.route('/index/') # BIP a eviter de decorer une fonction avec plusieurs routes (referencement), mais utile si user non identifie encore etc
@app.route('/')
def main():
    return render_template('index.html')
    
@app.route('/accueil/') #html de test, basique (est relie a la feuille css mon_style.css)
def acc():
	mots = ["bonjour","a","toi","visiteur."]
	return render_template('accueil.html',titre="Bienvenue!",mots=mots)

@app.route('/decouverte/') #on peut rajouter un slash a la fois que que les routes http://localhost:5000/decouverte et http://localhost:5000/decouverte/ soient toutes deux acceptees (sinon on peut rencontrer 404)
def decouverte():
    return render_template('decouverte.html')

@app.route('/topten/')
def topten():
    return render_template('top10.html')

@app.route('/classement2016/')
def classement2016():
	return render_template('classement2016.html')

@app.route('/classement2015/')
def classement2015():
	return render_template('classement2015.html')

@app.route('/classement2014/')
def classement2014():
	return render_template('classement2014.html')

if __name__ == '__main__':
    app.run(debug=True) #BIP mettre false a la fin
    #app.secret_key = '2d9-E2.)f&e,A$p@fpa+zSU03e09_'
