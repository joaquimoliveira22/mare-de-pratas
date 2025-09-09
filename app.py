from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from urllib.parse import quote_plus
import os

app = Flask(__name__)
app.secret_key = 'segredo_super_secreto'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///usuarios.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)

class Favorito(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, nullable=False)
    produto_id = db.Column(db.Integer, nullable=False)


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
    estoque = db.Column(db.Integer, nullable=False, default=0)
    tamanho = db.Column(db.String(50), nullable=True)
    espessura = db.Column(db.String(50), nullable=True)
    desconto = db.Column(db.Integer, nullable=True, default=0)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/adicionar_ao_carrinho', methods=['POST'])
def adicionar_ao_carrinho():
    produto_id = int(request.form['produto_id'])
    produto = Produto.query.get_or_404(produto_id)

    if produto.estoque <= 0:
        flash(f"O produto '{produto.nome}' está sem estoque no momento.", 'error')
        return redirect(url_for('listar_produtos'))

    carrinho = session.get('carrinho', {})
    produto_id_str = str(produto_id)
    carrinho[produto_id_str] = carrinho.get(produto_id_str, 0) + 1
    session['carrinho'] = carrinho
    session.modified = True

    flash('Produto adicionado ao carrinho!', 'success')
    return redirect(url_for('listar_produtos'))

@app.route('/carrinho')
def ver_carrinho():

    carrinho = session.get('carrinho', {})
    itens = []
    valor_total = 0
    for produto_id_str, quantidade in carrinho.items():
        produto = Produto.query.get(int(produto_id_str))
        if produto:
            preco_unitario = produto.valor * (1 - (produto.desconto or 0) / 100)
            subtotal = preco_unitario * quantidade
            valor_total += subtotal
            itens.append({
                'id': produto.id,
                'nome': produto.nome,
                'valor': produto.valor,
                'desconto': produto.desconto,
                'valor_com_desconto': preco_unitario,
                'quantidade': quantidade,
                'subtotal': subtotal,
                'foto_url': produto.foto_url
            })

    return render_template('carrinho.html', carrinho=itens, total=valor_total)

@app.route('/remover_do_carrinho/<int:produto_id>', methods=['POST'])
def remover_do_carrinho(produto_id):
    carrinho = session.get('carrinho', {})
    carrinho.pop(str(produto_id), None)
    session['carrinho'] = carrinho
    flash('Produto removido do carrinho.', 'success')
    return redirect(url_for('finalizar_pedido'))

@app.route('/')
def catalogo():
    nome_usuario = session.get('nome_usuario')
    produtos = Produto.query.all()
    carrinho = session.get('carrinho', {})
    carrinho_qtd = sum(carrinho.values())
    favoritos_ids = []

    if nome_usuario:
        usuario = Usuario.query.filter_by(nome_completo=nome_usuario).first()
        if usuario:
            favoritos_ids = [f.produto_id for f in Favorito.query.filter_by(usuario_id=usuario.id).all()]

    return render_template('catalogo.html', nome_usuario=nome_usuario,
                           produtos=produtos, carrinho_qtd=carrinho_qtd, favoritos_ids=favoritos_ids)

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
        flash('Email ou senha inválidos!', 'error')
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
        tamanho = request.form['tamanho']
        espessura = request.form['espessura']
       

        if foto and allowed_file(foto.filename):
            filename = secure_filename(foto.filename)
            foto_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            foto.save(foto_path)
            foto_url = f'/static/uploads/{filename}'
           
            novo_produto = Produto(nome=nome, descricao=descricao, valor=valor, foto_url=foto_url, tamanho=tamanho, espessura=espessura)
            db.session.add(novo_produto)
            db.session.commit()
            flash('Produto cadastrado com sucesso!', 'success')
            return redirect(url_for('painel_admin'))
        flash('Arquivo de imagem inválido!', 'error')
    return render_template('cadastrar_produto.html')

@app.route('/painel_admin', endpoint='painel_admin')
def painel_admin():
    if session.get('nome_usuario') != 'Administrador':
        flash('Acesso negado.', 'error')
        return redirect(url_for('login'))
    produtos = Produto.query.all()
    return render_template('administrador.html', nome_usuario='Administrador', produtos=produtos)

@app.route('/editar_desconto/<int:id>', methods=['GET', 'POST'])
def editar_desconto(id):
    produto = Produto.query.get_or_404(id)

    if request.method == 'POST':
        try:
            desconto = int(request.form.get('desconto'))
            if 0 <= desconto <= 100:
                produto.desconto = desconto
                db.session.commit()
                flash('Desconto atualizado com sucesso!', 'success')
            else:
                flash('O desconto deve estar entre 0% e 100%.', 'error')
        except ValueError:
            flash('Valor inválido para desconto.', 'error')

        return redirect(url_for('painel_admin'))

    return render_template('editar_desconto.html', produto=produto)


@app.route('/produtos')
def listar_produtos():
    termo_busca = request.args.get('q', '').strip().lower()
    carrinho = session.get('carrinho', {})
    carrinho_qtd = sum(carrinho.values())
    favoritos_ids = []

    nome_usuario = session.get('nome_usuario')
    if nome_usuario:
        usuario = Usuario.query.filter_by(nome_completo=nome_usuario).first()
        if usuario:
            favoritos_ids = [f.produto_id for f in Favorito.query.filter_by(usuario_id=usuario.id).all()]

    if termo_busca:
        produtos = Produto.query.filter(Produto.nome.ilike(f'%{termo_busca}%')).all()
    else:
        produtos = Produto.query.all()

    return render_template(
        'catalogo.html',
        produtos=produtos,
        nome_usuario=nome_usuario,
        carrinho_qtd=carrinho_qtd,
        favoritos_ids=favoritos_ids
    )


@app.route('/finalizar_pedido', methods=['GET', 'POST'])
def finalizar_pedido():
    nome_usuario = session.get('nome_usuario')
    if not nome_usuario:
        flash('Você precisa estar logado para finalizar a compra.', 'error')
        return redirect(url_for('login'))

    carrinho = session.get('carrinho', {})
    if not carrinho:
        flash('Seu carrinho está vazio.', 'error')
        return redirect(url_for('catalogo'))

    itens = []
    valor_total = 0
    mensagem_itens = []

    for produto_id_str, quantidade in carrinho.items():
        produto = Produto.query.get(int(produto_id_str))
        if produto:
            if produto.estoque < quantidade:
                flash(f'Estoque insuficiente para o produto: {produto.nome}', 'error')
                return redirect(url_for('ver_carrinho'))

        produto.estoque -= quantidade  # Subtrai do estoque
        db.session.commit()  # Salva no banco

        preco_unitario = produto.valor * (1 - (produto.desconto or 0) / 100)
        subtotal = preco_unitario * quantidade
        valor_total += subtotal
        itens.append({
            'id': produto.id,
            'nome': produto.nome,
            'valor': preco_unitario,
            'quantidade': quantidade,
            'subtotal': subtotal,
            'foto_url': produto.foto_url
        })

        if produto.desconto:
            mensagem_itens.append(
                f"{quantidade}x {produto.nome} (de R$ {produto.valor:.2f} por R$ {preco_unitario:.2f}) - Subtotal: R$ {subtotal:.2f}"
            )
        else:
            mensagem_itens.append(
                f"{quantidade}x {produto.nome} (R$ {produto.valor:.2f} cada) - Subtotal: R$ {subtotal:.2f}"
            )

    mensagem_total = f"Total da compra: R$ {valor_total:.2f}"
    mensagem_completa = "Olá, gostaria de fazer o pedido:\n" + "\n".join(mensagem_itens) + "\n" + mensagem_total

    mensagem_url = quote_plus(mensagem_completa)
    numero_whatsapp = '5585982246332'
    link_whatsapp = f"https://api.whatsapp.com/send?phone={numero_whatsapp}&text={mensagem_url}"

    session.pop('carrinho', None)
    

    return render_template( 
        'finalizar_pedido.html',
        nome_usuario=nome_usuario,
        carrinho=itens,
        total=valor_total,
        link_whatsapp=link_whatsapp
    )

@app.route('/editar_produto/<int:id>', methods=['GET', 'POST'])
def editar_produto(id):
    produto = Produto.query.get_or_404(id)
    if request.method == 'POST':
        produto.nome = request.form['nome']
        produto.descricao = request.form['descricao']
        produto.valor = float(request.form['valor'])
        produto.tamanho = request.form['tamanho']
        produto.espessura = request.form['espessura']

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
        try:
            produto.estoque = int(request.form.get('estoque'))
            db.session.commit()
            flash('Estoque atualizado com sucesso!', 'success')
        except ValueError:
            flash('Valor inválido para estoque.', 'error')
        return redirect(url_for('painel_admin'))
    return render_template('estoque.html', produto=produto)

@app.context_processor
def inject_carrinho_qtd():
    carrinho = session.get('carrinho', {})
    carrinho_qtd = sum(carrinho.values())
    return {'carrinho_qtd': carrinho_qtd}

@app.before_request
def checar_sessao():
    print(f"Usuário na sessão: {session.get('nome_usuario')}")


@app.route('/confirmar_pedido/<int:produto_id>')
def confirmar_pedido(produto_id):
    produto = Produto.query.get_or_404(produto_id)
    mensagem = f"Olá! Gostaria de comprar o produto: {produto.nome} por R$ {produto.valor:.2f}"
    mensagem = mensagem.replace(' ', '%20')
    numero_whatsapp = '5585982246332'
    link = f"https://api.whatsapp.com/send?phone={numero_whatsapp}&text={mensagem}"
    return redirect(link)


@app.route('/toggle_favorito', methods=['POST'])
def toggle_favorito():
    if 'nome_usuario' not in session:
        return jsonify({'success': False, 'message': 'Login necessário'}), 401

    data = request.get_json()
    produto_id = int(data.get('produto_id'))

    usuario = Usuario.query.filter_by(nome_completo=session['nome_usuario']).first()
    favorito = Favorito.query.filter_by(usuario_id=usuario.id, produto_id=produto_id).first()

    if favorito:
        db.session.delete(favorito)
        db.session.commit()
        return jsonify({'success': True, 'favoritado': False})
    else:
        novo_favorito = Favorito(usuario_id=usuario.id, produto_id=produto_id)
        db.session.add(novo_favorito)
        db.session.commit()
        return jsonify({'success': True, 'favoritado': True})
    
@app.route('/favoritos')
def favoritos():
    if 'nome_usuario' not in session:
        flash('Você precisa estar logado para ver seus favoritos.', 'error')
        return redirect(url_for('login'))

    usuario = Usuario.query.filter_by(nome_completo=session['nome_usuario']).first()
    favoritos = Favorito.query.filter_by(usuario_id=usuario.id).all()
    produtos_ids = [f.produto_id for f in favoritos]
    produtos = Produto.query.filter(Produto.id.in_(produtos_ids)).all()
    
    return render_template('favoritos.html', nome_usuario=session['nome_usuario'], produtos=produtos)


@app.route('/adicionar_favorito', methods=['POST'])
def adicionar_favorito():
    if 'nome_usuario' not in session:
        flash('Você precisa estar logado para favoritar um produto.', 'error')
        return redirect(url_for('login'))

    produto_id = int(request.form['produto_id'])
    usuario = Usuario.query.filter_by(nome_completo=session['nome_usuario']).first()

    favorito = Favorito.query.filter_by(usuario_id=usuario.id, produto_id=produto_id).first()
    if favorito:
        db.session.delete(favorito)
        flash('Produto removido dos favoritos.', 'success')
    else:
        novo_favorito = Favorito(usuario_id=usuario.id, produto_id=produto_id)
        db.session.add(novo_favorito)
        flash('Produto adicionado aos favoritos!', 'success')

    db.session.commit()
    return redirect(request.referrer or url_for('catalogo'))


if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    with app.app_context():
        db.create_all()
    app.run(debug=True)
