from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(200), nullable=False)

    def __init__(self, email, senha_hash):
        self.email = email
        self.senha_hash = senha_hash


class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    preco = db.Column(db.Float, nullable=False)
    preco_original = db.Column(db.Float, nullable=True)
    desconto = db.Column(db.Float, nullable=True)
    imagem_url = db.Column(db.String(255), nullable=False)
