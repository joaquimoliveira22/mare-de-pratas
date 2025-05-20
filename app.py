from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_cors import CORS
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = 'mare_de_pratas_secret_key'
CORS(app)

# Configurações do banco de dados
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'mare_de_pratas'
}

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user and check_password_hash(user['senha'], senha):
            session['user_id'] = user['id']
            session['user_nome'] = user['nome']
            return redirect(url_for('catalogo'))
        else:
            return render_template('login.html', error='Email ou senha incorretos')
    
    return render_template('login.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        
        hashed_password = generate_password_hash(senha, method='sha256')
        
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "INSERT INTO usuarios (nome, email, senha) VALUES (%s, %s, %s)",
                (nome, email, hashed_password)
            )
            conn.commit()
            cursor.close()
            conn.close()
            
            return redirect(url_for('login'))
        except mysql.connector.Error as err:
            return render_template('registro.html', error='Erro ao cadastrar: ' + str(err))
    
    return render_template('registro.html')

@app.route('/catalogo')
def catalogo():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM produtos")
    produtos = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('catalogo.html', produtos=produtos, user_nome=session['user_nome'])

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)