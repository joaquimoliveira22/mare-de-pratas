from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'  # Necessário para sessions

# Configurações
UPLOAD_FOLDER = 'static/images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Dados de exemplo (substitua por um banco de dados real em produção)
produtos = [
    {
        'id': 1,
        'nome': 'Pulseira de Prata',
        'preco': 90.00,
        'preco_original': 120.00,
        'descricao': 'Joia rara com detalhes em diamantes',
        'imagem': 'pulseira.jpg',
        'novo': True,
        'desconto': 25
    },
    {
        'id': 2,
        'nome': 'Colar Marinho',
        'preco': 150.00,
        'descricao': 'Colar de prata com pingente em forma de onda',
        'imagem': 'colar.jpg'
    },
    {
        'id': 3,
        'nome': 'Anel Oceânico',
        'preco': 75.00,
        'preco_original': 95.00,
        'descricao': 'Anel de prata com detalhes em esmalte azul',
        'imagem': 'anel.jpg',
        'desconto': 20
    }
]

usuarios = {
    'admin@example.com': {'senha': 'admin123', 'nome': 'Administrador'}
}

# Rotas principais
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/catalogo')
def catalogo():
    return render_template('catalogo.html', produtos=produtos)

@app.route('/produtos')
def produtos_page():
    return render_template('produtos.html', produtos=produtos)

@app.route('/sobre')
def sobre():
    return render_template('sobre.html')

# Rotas de autenticação
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        
        if email in usuarios and usuarios[email]['senha'] == senha:
            session['usuario'] = email
            session['nome'] = usuarios[email]['nome']
            return redirect(url_for('index'))
        else:
            return render_template('login.html', erro='Credenciais inválidas')
    
    return render_template('login.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        email = request.form['email']
        nome = request.form['nome']
        senha = request.form['senha']
        
        if email in usuarios:
            return render_template('registro.html', erro='Email já cadastrado')
        
        usuarios[email] = {'senha': senha, 'nome': nome}
        session['usuario'] = email
        session['nome'] = nome
        return redirect(url_for('index'))
    
    return render_template('registro.html')

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    session.pop('nome', None)
    return redirect(url_for('index'))

# Rotas de produtos
@app.route('/produto/<int:id>')
def produto(id):
    produto = next((p for p in produtos if p['id'] == id), None)
    if produto:
        return render_template('produto.html', produto=produto)
    return redirect(url_for('catalogo'))

# Rotas de carrinho e favoritos
@app.route('/carrinho', methods=['GET', 'POST'])
def carrinho():
    if 'carrinho' not in session:
        session['carrinho'] = []
    
    if request.method == 'POST':
        produto_id = int(request.form['produto_id'])
        produto = next((p for p in produtos if p['id'] == produto_id), None)
        
        if produto:
            session['carrinho'].append(produto)
            session.modified = True
    
    return render_template('carrinho.html', carrinho=session.get('carrinho', []))

@app.route('/remover-do-carrinho/<int:index>')
def remover_do_carrinho(index):
    if 'carrinho' in session and 0 <= index < len(session['carrinho']):
        session['carrinho'].pop(index)
        session.modified = True
    return redirect(url_for('carrinho'))

@app.route('/favoritos')
def favoritos():
    if 'favoritos' not in session:
        session['favoritos'] = []
    return render_template('favoritos.html', favoritos=session.get('favoritos', []))

@app.route('/adicionar-favorito/<int:produto_id>')
def adicionar_favorito(produto_id):
    if 'favoritos' not in session:
        session['favoritos'] = []
    
    produto = next((p for p in produtos if p['id'] == produto_id), None)
    if produto and produto not in session['favoritos']:
        session['favoritos'].append(produto)
        session.modified = True
    
    return redirect(request.referrer or url_for('catalogo'))

# Rota de busca
@app.route('/busca')
def busca():
    termo = request.args.get('q', '')
    resultados = [p for p in produtos if termo.lower() in p['nome'].lower() or 
                 termo.lower() in p['descricao'].lower()]
    return render_template('busca.html', resultados=resultados, termo=termo)

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)