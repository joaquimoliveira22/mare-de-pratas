from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'segredo_super_secreto'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///usuarios.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Tabela de Usuários
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome_completo = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha = db.Column(db.String(200), nullable=False)

# Página inicial: Catálogo
@app.route('/')
def catalogo():
    nome_usuario = session.get('nome_usuario')
    return render_template('catalogo.html', nome_usuario=nome_usuario)

# Página de Registro
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nome = request.form['nome_completo']
        telefone = request.form['telefone']
        email = request.form['email']
        senha = generate_password_hash(request.form['senha'])

        if Usuario.query.filter_by(email=email).first():
            flash('Email já cadastrado!', 'error')
            return redirect(url_for('registro'))

        novo_usuario = Usuario(nome_completo=nome, telefone=telefone, email=email, senha=senha)
        db.session.add(novo_usuario)
        db.session.commit()
        flash('Cadastro realizado com sucesso!', 'success')
        return redirect(url_for('login'))

    return render_template('registro.html')

# Página de Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        # Verificação para acesso do administrador fixo
        if email == 'adm123@gmail.com' and senha == 'adm2323':
            session['nome_usuario'] = 'Administrador'
            return redirect(url_for('painel_admin'))

        # Verificação para usuários comuns
        usuario = Usuario.query.filter_by(email=email).first()
        if usuario and check_password_hash(usuario.senha, senha):
            session['nome_usuario'] = usuario.nome_completo
            return redirect(url_for('catalogo'))
        else:
            flash('Email ou senha inválidos!', 'error')
            return redirect(url_for('login'))

    return render_template('login.html')

# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('catalogo'))

# Redireciona para o catálogo
@app.route('/listar_produtos')
def listar_produtos():
    return redirect(url_for('catalogo'))

# Página de Produtos
@app.route('/produtos')
def produtos():
    nome_usuario = session.get('nome_usuario')
    return render_template('produtos.html', nome_usuario=nome_usuario)

# Página Sobre
@app.route('/sobre')
def sobre():
    nome_usuario = session.get('nome_usuario')
    return render_template('sobre.html', nome_usuario=nome_usuario)

# Página Finalizar Pedido
@app.route('/finalizar_pedido', methods=['GET', 'POST'])
def finalizar_pedido():
    nome_usuario = session.get('nome_usuario')
    if request.method == 'POST':
        produto = request.form.get('produto')
    else:
        produto = None
    return render_template('finalizar_pedido.html', nome_usuario=nome_usuario, produto=produto)

# Página de Confirmação de Pedido
@app.route('/confirmar_pedido', methods=['POST'])
def confirmar_pedido():
    produto = request.form['produto']
    pagamento = request.form['pagamento']
    nome = request.form['nome']
    email = request.form['email']
    telefone = request.form['telefone']
    endereco = request.form['endereco']

    flash(f'Pedido do produto "{produto}" confirmado com pagamento via {pagamento}.', 'success')
    return redirect(url_for('catalogo'))

# Painel do Administrador (renderiza administrador.html)
@app.route('/painel_admin')
def painel_admin():
    nome_usuario = session.get('nome_usuario')
    if nome_usuario != 'Administrador':
        flash('Acesso negado.', 'error')
        return redirect(url_for('login'))
    return render_template('administrador.html', nome_usuario=nome_usuario)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)