SET NAMES utf8mb4;
USE ecommerce;

CREATE TABLE IF NOT EXISTS categorias (
    id   INT PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(50)  NOT NULL,
    descricao VARCHAR(200)
);

CREATE TABLE IF NOT EXISTS produtos (
    id           INT PRIMARY KEY AUTO_INCREMENT,
    nome         VARCHAR(100)   NOT NULL,
    categoria_id INT,
    preco        DECIMAL(10,2)  NOT NULL,
    custo        DECIMAL(10,2)  NOT NULL,
    estoque      INT            DEFAULT 0,
    ativo        TINYINT(1)     DEFAULT 1,
    criado_em    DATETIME       DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (categoria_id) REFERENCES categorias(id)
);

CREATE TABLE IF NOT EXISTS clientes (
    id               INT PRIMARY KEY AUTO_INCREMENT,
    nome             VARCHAR(100) NOT NULL,
    email            VARCHAR(100),
    cidade           VARCHAR(50),
    estado           CHAR(2),
    regiao           VARCHAR(20),
    genero           CHAR(1),
    data_nascimento  DATE,
    criado_em        DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS vendedores (
    id     INT PRIMARY KEY AUTO_INCREMENT,
    nome   VARCHAR(100) NOT NULL,
    regiao VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS pedidos (
    id           INT PRIMARY KEY AUTO_INCREMENT,
    cliente_id   INT,
    vendedor_id  INT,
    status       VARCHAR(20),
    canal        VARCHAR(20),
    data_pedido  DATETIME,
    data_entrega DATETIME,
    valor_total  DECIMAL(10,2) DEFAULT 0,
    desconto     DECIMAL(10,2) DEFAULT 0,
    frete        DECIMAL(10,2) DEFAULT 0,
    FOREIGN KEY (cliente_id)  REFERENCES clientes(id),
    FOREIGN KEY (vendedor_id) REFERENCES vendedores(id)
);

CREATE TABLE IF NOT EXISTS itens_pedido (
    id             INT PRIMARY KEY AUTO_INCREMENT,
    pedido_id      INT,
    produto_id     INT,
    quantidade     INT           NOT NULL,
    preco_unitario DECIMAL(10,2) NOT NULL,
    subtotal       DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (pedido_id)  REFERENCES pedidos(id),
    FOREIGN KEY (produto_id) REFERENCES produtos(id)
);
