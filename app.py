from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, Usuario, Produto
import os

app = Flask(__name__)
app.secret_key = "chave-super-secreta"

# Caminho do banco
base_dir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(base_dir, 'database.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

ADMIN_EMAIL = "adm123@gmail.com"
ADMIN_SENHA = "adm123"

db.init_app(app)

# ---------- ROTAS ---------- #

def home():
    return redirect(url_for('vitrine'))


@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        if Usuario.query.filter_by(email=email).first():
            flash('E-mail já cadastrado!', 'warning')
            return redirect(url_for('cadastro'))

        senha_hash = generate_password_hash(senha)
        novo_usuario = Usuario(email=email, senha_hash=senha_hash)
        db.session.add(novo_usuario)
        db.session.commit()

        flash('Cadastro realizado com sucesso! Faça login.', 'success')
        return redirect(url_for('login'))

    return render_template('cadastro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        if email == ADMIN_EMAIL and senha == ADMIN_SENHA:
            session['usuario'] = email
            return redirect(url_for('admin'))
        else:
            return render_template('login.html', erro="E-mail ou senha incorretos")

    return render_template('login.html')    

@app.route('/admin')
def admin():
    if 'usuario' in session and session['usuario'] == ADMIN_EMAIL:
        return render_template('administrador.html', usuario=session['usuario'])
    else:
        return redirect(url_for('login'))


@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect(url_for('login'))


@app.route('/vitrine')
def vitrine():
    produtos = Produto.query.all()
    usuario = session.get('usuario_email')
    return render_template('vitrine.html', produtos=produtos, usuario=usuario)


@app.route("/produto/<int:id>")
def produto(id):
    produto = Produto.query.get_or_404(id)
    return render_template("produto.html", produto=produto)


# ---------- EXECUÇÃO ---------- #
if __name__ == "__main__":
    with app.app_context():
        db.create_all()

        # Adicionar produtos de exemplo se o banco estiver vazio
        if Produto.query.count() == 0:
            produtos_demo = [
                Produto(nome="Conjunto Love", preco=70.00, preco_original=100.00, desconto=30, imagem_url="https://i.imgur.com/8QjL8E1.png"),
                Produto(nome="Pingente Borboleta", preco=50.00, imagem_url="https://i.imgur.com/uFfoJtO.png"),
                Produto(nome='Pingente "L"', preco=40.00, imagem_url="https://i.imgur.com/i1rW8j5.png"),
                Produto(nome="Brinco orgânico", preco=70.00, imagem_url="https://i.imgur.com/Qj1qfWJ.png"),
                Produto(nome="Colar Personalizado", preco=108.00, preco_original=120.00, desconto=10, imagem_url="https://i.imgur.com/6M6oVvP.png"),
                Produto(nome="Conjunto Esmeralda", preco=75.00, preco_original=150.00, desconto=50, imagem_url="https://i.imgur.com/1G8G5iQ.png"),
            ]
            db.session.add_all(produtos_demo)
            db.session.commit()

    app.run(debug=True)
