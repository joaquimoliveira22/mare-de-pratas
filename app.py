from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = 'segredo_super_secreto'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///usuarios.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Modelos
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome_completo = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha = db.Column(db.String(200), nullable=False)

class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    valor = db.Column(db.Float, nullable=False)
    foto_url = db.Column(db.String(200), nullable=False)
    estoque = db.Column(db.Integer, nullable=False, default=0)  # NOVO CAMPO

# Rotas
@app.route('/')
def catalogo():
    nome_usuario = session.get('nome_usuario')
    produtos = Produto.query.all()
    return render_template('catalogo.html', nome_usuario=nome_usuario, produtos=produtos)

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

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        if email == 'adm123@gmail.com' and senha == 'adm2323':
            session['nome_usuario'] = 'Administrador'
            return redirect(url_for('painel_admin'))

        usuario = Usuario.query.filter_by(email=email).first()
        if usuario and check_password_hash(usuario.senha, senha):
            session['nome_usuario'] = usuario.nome_completo
            return redirect(url_for('catalogo'))
        else:
            flash('Email ou senha inválidos!', 'error')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('catalogo'))

@app.route('/cadastrar_produto', methods=['GET', 'POST'])
def cadastrar_produto():
    if request.method == 'POST':
        nome = request.form['nome']
        descricao = request.form['descricao']
        valor = float(request.form['valor'])
        foto = request.files['foto']

        if foto and allowed_file(foto.filename):
            filename = secure_filename(foto.filename)
            foto_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            foto.save(foto_path)
            foto_url = f'/static/uploads/{filename}'

            novo_produto = Produto(nome=nome, descricao=descricao, valor=valor, foto_url=foto_url)
            db.session.add(novo_produto)
            db.session.commit()
            flash('Produto cadastrado com sucesso!', 'success')
            return redirect(url_for('painel_admin'))
        else:
            flash('Arquivo de imagem inválido!', 'error')
            return redirect(url_for('cadastrar_produto'))

    return render_template('cadastrar_produto.html')

@app.route('/painel_admin', endpoint='painel_admin')
def painel_admin():
    nome_usuario = session.get('nome_usuario')
    if nome_usuario != 'Administrador':
        flash('Acesso negado.', 'error')
        return redirect(url_for('login'))
    produtos = Produto.query.all()
    return render_template('administrador.html', nome_usuario=nome_usuario, produtos=produtos)

@app.route('/administrador')
def administrador():
    return render_template('administrador.html')

@app.route('/listar_produtos')
def listar_produtos():
    termo = request.args.get('q', '')
    produtos = Produto.query.filter(Produto.nome.ilike(f'%{termo}%')).all()
    nome_usuario = session.get('nome_usuario')
    return render_template('catalogo.html', nome_usuario=nome_usuario, produtos=produtos)

@app.route('/finalizar_pedido', methods=['GET', 'POST'])
def finalizar_pedido():
    nome_usuario = session.get('nome_usuario')

    # Verificação de login
    if not nome_usuario:
        flash('Você precisa estar logado para finalizar a compra.', 'error')
        return redirect(url_for('login'))

    if request.method == 'POST':
        produto_id = request.form.get('produto_id')
        produto = Produto.query.get(produto_id)

        if produto:
            return render_template('finalizar_pedido.html', nome_usuario=nome_usuario, produto=produto)
        else:
            flash('Produto não encontrado.', 'error')
            return redirect(url_for('catalogo'))

    return redirect(url_for('catalogo'))

@app.route('/editar_produto/<int:id>', methods=['GET', 'POST'])
def editar_produto(id):
    produto = Produto.query.get_or_404(id)

    if request.method == 'POST':
        produto.nome = request.form['nome']
        produto.descricao = request.form['descricao']
        produto.valor = float(request.form['valor'])

        foto = request.files.get('foto')
        if foto and allowed_file(foto.filename):
            filename = secure_filename(foto.filename)
            foto_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            foto.save(foto_path)
            produto.foto_url = f'/static/uploads/{filename}'

        db.session.commit()
        flash('Produto atualizado com sucesso!', 'success')
        return redirect(url_for('painel_admin'))

    return render_template('editar_produto.html', produto=produto)

@app.route('/remover_produto/<int:id>', methods=['GET', 'POST'])
def remover_produto(id):
    produto = Produto.query.get_or_404(id)
    db.session.delete(produto)
    db.session.commit()
    flash('Produto removido com sucesso!', 'success')
    return redirect(url_for('painel_admin'))

@app.route('/ajustar_estoque/<int:id>', methods=['GET', 'POST'])
def ajustar_estoque(id):
    produto = Produto.query.get_or_404(id)

    if request.method == 'POST':
        novo_estoque = request.form.get('estoque')
        try:
            produto.estoque = int(novo_estoque)
            db.session.commit()
            flash('Estoque atualizado com sucesso!', 'success')
        except ValueError:
            flash('Valor inválido para estoque.', 'error')
        return redirect(url_for('painel_admin'))

    return render_template('estoque.html', produto=produto)


@app.route('/confirmar_pedido/<int:produto_id>')
def confirmar_pedido(produto_id):
    produto = Produto.query.get_or_404(produto_id)
    mensagem = f"Olá! Gostaria de comprar o produto: {produto.nome} por R$ {produto.valor:.2f}"
    mensagem = mensagem.replace(' ', '%20')  
    numero_whatsapp = '5585982246332'  
    link = f"https://api.whatsapp.com/send?phone={numero_whatsapp}&text={mensagem}"
    return redirect(link)

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    with app.app_context():
        db.create_all()
    app.run(debug=True)
