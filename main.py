from flask import Flask, render_template
import os

app = Flask(__name__)

@app.route("/")
def index():
    nome = 'icoma.com.br'
    return render_template('index.html', site=nome)

@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login/login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    return render_template('login/register.html')

@app.route('/recovery')
def recovery():
    return render_template('login/recovery.html')

def main():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

if __name__ == "__main__":
    main()