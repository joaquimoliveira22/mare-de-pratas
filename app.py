from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import re
import os

# Configuração inicial do Flask
app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_super_segura_aqui'

# Banco de dados em memória
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

@app.before_request
def inicializar_sessao():
    pass  # Nada mais necessário aqui

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
    return render_template('produtos', produtos=produtos)

@app.route('/sobre')
def sobre():
    return render_template('sobre')


# Nova rota para finalizar pedido
@app.route('/comprar/<int:produto_id>', methods=['POST'])
def comprar_produto(produto_id):
    if 'usuario_logado' not in session:
        flash('Faça login primeiro', 'erro')
        return redirect(url_for('login'))

    produto = next((p for p in produtos if p['id'] == produto_id), None)
    if not produto:
        flash('Produto não encontrado', 'erro')
        return redirect(url_for('catalogo'))

    # Armazenar produto selecionado na sessão (ou passar via query string/post)
    session['produto_selecionado'] = produto
    return redirect(url_for('finalizar_pedido'))

@app.route('/finalizar_pedido', methods=['GET', 'POST'])
def finalizar_pedido():
    if 'usuario_logado' not in session:
        flash('Faça login primeiro', 'erro')
        return redirect(url_for('login'))

    produto = session.get('produto_selecionado')

    if request.method == 'POST':
        flash('Pedido finalizado com sucesso!', 'sucesso')
        return redirect(url_for('catalogo'))

    return render_template('finalizar_pedido.html', produto=produto)



# Ponto de entrada
if __name__ == '__main__':
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/images', exist_ok=True)

    required_templates = [
        'login.html', 'registro.html', 'catalogo.html',
        'produtos.html', 'finalizar_pedido.html', 'sobre.html'
    ]

    for template in required_templates:
        template_path = os.path.join('templates', template)
        if not os.path.exists(template_path):
            with open(template_path, 'w') as f:
                f.write(f"<!-- Template {template} -->")

    app.run(debug=True, port=5000)
