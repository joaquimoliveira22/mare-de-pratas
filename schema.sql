CREATE DATABASE IF NOT EXISTS mare_de_pratas;

USE mare_de_pratas;

CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    senha VARCHAR(255) NOT NULL,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE produtos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    descricao TEXT,
    preco DECIMAL(10, 2) NOT NULL,
    imagem VARCHAR(255)
);

-- Inserir alguns produtos de exemplo
INSERT INTO produtos (nome, descricao, preco, imagem) VALUES
('Pulseira de Prata', 'Pulseira artesanal com detalhes em azul', 89.90, 'pulseira.jpg'),
('Colar Marinho', 'Colar de prata com pingente em forma de onda', 120.50, 'colar.jpg'),
('Anel Oceânico', 'Anel de prata com detalhes em esmalte azul', 75.00, 'anel.jpg');