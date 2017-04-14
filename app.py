from flask import Flask, render_template,json, request
app = Flask(__name__)


@app.route("/")
def main():
    return render_template('index.html')

@app.route('/decouverte')
def decouverte():
    return render_template('decouverte.html')

@app.route('/topten')
def topten():
    return render_template('top10.html')

if __name__ == "__main__":
    app.run()
