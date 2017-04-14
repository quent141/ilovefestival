from flask import Flask, render_template,json, request
app = Flask(__name__)


@app.route('/')
def main():
    return render_template('index.html')

@app.route('/decouverte')
def decouverte():
    return render_template('decouverte.html')

@app.route('/topten')
def topten():
    return render_template('top10.html')

@app.route('/classement2016')
def classement2016():
	return render_template('classement2016.html')

@app.route('/classement2015')
def classement2015():
	return render_template('classement2015.html')

@app.route('/classement2014')
def classement2014():
	return render_template('classement2014.html')

if __name__ == '__main__':
    app.run(debug=True)
