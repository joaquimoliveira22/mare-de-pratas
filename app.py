from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import re
import os

# Configuração inicial do Flask
app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_super_segura_aqui'  # Em produção, use uma chave complexa

# Banco de dados em memória (substitua por um banco real em produção)
usuarios = [
    {
        'email': 'admin@mare.com',
        'senha_hash': generate_password_hash('admin123'),
        'nome': 'Administrador',
        'telefone': '(85) 98224-6332'
    }
]

produtos = [
    {
        'id': 1,
        'nome': 'Pulseira de Prata',
        'preco': 90.00,
        'imagem': 'pulseira.jpg',
        'descricao': 'Joia rara com detalhes em diamantes'
    },
    {
        'id': 2,
        'nome': 'Colar Marinho',
        'preco': 150.00,
        'imagem': 'colar.jpg',
        'descricao': 'Colar de prata com pingente em forma de onda'
    },
    {
        'id': 3,
        'nome': 'Anel Oceânico',
        'preco': 75.00,
        'imagem': 'anel.jpg',
        'descricao': 'Anel de prata com detalhes em esmalte azul'
    }
]

# Inicialização da sessão
@app.before_request
def inicializar_sessao():
    if 'carrinho' not in session:
        session['carrinho'] = []
    if 'favoritos' not in session:
        session['favoritos'] = []

# Rotas de autenticação
@app.route('/')
def index():
    if 'usuario_logado' in session:
        return redirect(url_for('catalogo'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        
        if not email or not senha:
            flash('Preencha todos os campos', 'erro')
            return redirect(url_for('login'))
        
        usuario = next((u for u in usuarios if u['email'] == email), None)
        
        if usuario and check_password_hash(usuario['senha_hash'], senha):
            session['usuario_logado'] = {
                'email': usuario['email'],
                'nome': usuario['nome']
            }
            flash('Login realizado com sucesso!', 'sucesso')
            return redirect(url_for('catalogo'))
        
        flash('Email ou senha incorretos', 'erro')
    
    return render_template('login.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nome = request.form.get('nome_completo')
        telefone = request.form.get('telefone')
        email = request.form.get('email')
        senha = request.form.get('senha')
        
        if not all([nome, telefone, email, senha]):
            flash('Preencha todos os campos', 'erro')
            return redirect(url_for('registro'))
        
        if not re.match(r"\(\d{2}\) \d{4,5}-\d{4}", telefone):
            flash("Telefone inválido. Use o formato (99) 99999-9999.", "erro")
            return redirect(url_for('registro'))
        
        if any(u['email'] == email for u in usuarios):
            flash("Email já cadastrado.", "erro")
            return redirect(url_for('registro'))
        
        usuarios.append({
            'nome': nome,
            'telefone': telefone,
            'email': email,
            'senha_hash': generate_password_hash(senha)
        })
        
        flash("Cadastro realizado com sucesso!", "sucesso")
        return redirect(url_for('login'))
    
    return render_template('registro.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Você foi desconectado', 'info')
    return redirect(url_for('login'))

# Rotas do catálogo
@app.route('/catalogo')
def catalogo():
    if 'usuario_logado' not in session:
        flash('Por favor, faça login para acessar o catálogo', 'erro')
        return redirect(url_for('login'))
    return render_template('catalogo.html', produtos=produtos)

@app.route('/produtos')
def listar_produtos():
    if 'usuario_logado' not in session:
        flash('Por favor, faça login para acessar os produtos', 'erro')
        return redirect(url_for('login'))
    return render_template('produtos.html', produtos=produtos)

# Rotas do carrinho
@app.route('/carrinho')
def ver_carrinho():
    if 'usuario_logado' not in session:
        flash('Por favor, faça login para acessar seu carrinho', 'erro')
        return redirect(url_for('login'))
    
    carrinho = session.get('carrinho', [])
    total = sum(item['preco'] * item['quantidade'] for item in carrinho)
    return render_template('carrinho.html', carrinho=carrinho, total=total)

@app.route('/adicionar_carrinho/<int:produto_id>', methods=['POST'])
def adicionar_carrinho(produto_id):
    if 'usuario_logado' not in session:
        return jsonify({'success': False, 'message': 'Faça login primeiro'}), 401
    
    produto = next((p for p in produtos if p['id'] == produto_id), None)
    
    if not produto:
        return jsonify({'success': False, 'message': 'Produto não encontrado'}), 404
    
    carrinho = session['carrinho']
    item_existente = next((item for item in carrinho if item['id'] == produto_id), None)
    
    if item_existente:
        item_existente['quantidade'] += 1
    else:
        carrinho.append({
            'id': produto['id'],
            'nome': produto['nome'],
            'preco': produto['preco'],
            'imagem': produto['imagem'],
            'quantidade': 1
        })
    
    session['carrinho'] = carrinho
    session.modified = True
    return jsonify({'success': True, 'redirect': url_for('ver_carrinho')})

@app.route('/remover_carrinho/<int:produto_id>', methods=['POST'])
def remover_carrinho(produto_id):
    if 'usuario_logado' not in session:
        return jsonify({'success': False, 'message': 'Não autorizado'}), 401
    
    carrinho = session['carrinho']
    session['carrinho'] = [item for item in carrinho if item['id'] != produto_id]
    session.modified = True
    
    return jsonify({'success': True, 'redirect': url_for('ver_carrinho')})

# Rotas de favoritos
@app.route('/favoritos')
def ver_favoritos():
    if 'usuario_logado' not in session:
        flash('Por favor, faça login para acessar seus favoritos', 'erro')
        return redirect(url_for('login'))
    
    favoritos = [p for p in produtos if p['id'] in session.get('favoritos', [])]
    return render_template('favoritos.html', favoritos=favoritos)

@app.route('/toggle_favorito/<int:produto_id>', methods=['POST'])
def toggle_favorito(produto_id):
    if 'usuario_logado' not in session:
        return jsonify({'success': False, 'message': 'Faça login primeiro'}), 401
    
    if produto_id not in [p['id'] for p in produtos]:
        return jsonify({'success': False, 'message': 'Produto não encontrado'}), 404
    
    favoritos = session['favoritos']
    
    if produto_id in favoritos:
        favoritos.remove(produto_id)
        action = 'removido'
    else:
        favoritos.append(produto_id)
        action = 'adicionado'
    
    session['favoritos'] = favoritos
    session.modified = True
    return jsonify({'success': True, 'action': action})

# Rota sobre
@app.route('/sobre')
def sobre():
    return render_template('sobre.html')

# Ponto de entrada
if __name__ == '__main__':
    # Criar pastas necessárias se não existirem
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/images', exist_ok=True)
    
    # Verificar templates essenciais
    required_templates = [
        'login.html', 'registro.html', 'catalogo.html', 
        'produtos.html', 'carrinho.html', 'favoritos.html', 'sobre.html'
    ]
    
    for template in required_templates:
        template_path = os.path.join('templates', template)
        if not os.path.exists(template_path):
            with open(template_path, 'w') as f:
                f.write(f"<!-- Template {template} -->")
    
    app.run(debug=True, port=5000)