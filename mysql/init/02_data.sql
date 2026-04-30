SET NAMES utf8mb4;
USE ecommerce;

INSERT INTO categorias (nome, descricao) VALUES
('Eletrônicos',        'Smartphones, notebooks, tablets e acessórios'),
('Roupas e Acessórios','Vestuário masculino, feminino e calçados'),
('Casa e Decoração',   'Móveis, utensílios e decoração para o lar'),
('Esportes e Lazer',   'Equipamentos esportivos e artigos de lazer'),
('Alimentos e Bebidas','Produtos alimentícios e bebidas selecionadas');

INSERT INTO produtos (nome, categoria_id, preco, custo, estoque) VALUES
('Smartphone Samsung Galaxy A54',   1, 1899.90,  950.00,  50),
('Notebook Dell Inspiron 15',       1, 3499.90, 1800.00,  20),
('Tablet iPad 10ª Geração',         1, 2799.90, 1500.00,  15),
('Fone de Ouvido Bluetooth JBL',    1,  399.90,  150.00, 100),
('Smart TV 55" 4K LG',              1, 2299.90, 1200.00,  25),
('Camiseta Polo Masculina',         2,   89.90,   30.00, 200),
('Calça Jeans Skinny',              2,  159.90,   55.00, 150),
('Tênis Nike Air Max',              2,  499.90,  200.00,  80),
('Vestido Casual Feminino',         2,  129.90,   45.00, 120),
('Jaqueta Corta-Vento',             2,  249.90,   90.00,  60),
('Sofá 3 Lugares Retrátil',         3, 1799.90,  800.00,  10),
('Mesa de Jantar 6 Lugares',        3, 1299.90,  600.00,   8),
('Luminária de Piso LED',           3,  349.90,  120.00,  40),
('Conjunto de Panelas Tramontina',  3,  459.90,  180.00,  35),
('Tapete Sala 200x300cm',           3,  299.90,  110.00,  25),
('Bicicleta Mountain Bike Aro 29',  4, 1599.90,  700.00,  12),
('Kit Halteres 5kg Par',            4,  149.90,   60.00,  60),
('Mochila Esportiva 40L',           4,  199.90,   75.00,  45),
('Bola de Futebol Oficial',         4,  129.90,   45.00,  70),
('Kit Café Especial Premium',       5,   89.90,   35.00,  90);

INSERT INTO vendedores (nome, regiao) VALUES
('João Silva',      'Sul'),
('Maria Santos',    'Sudeste'),
('Carlos Oliveira', 'Nordeste'),
('Ana Lima',        'Centro-Oeste'),
('Roberto Costa',   'Norte');

INSERT INTO clientes (nome, email, cidade, estado, regiao, genero, data_nascimento) VALUES
('Lucas Ferreira',     'lucas.ferreira@email.com',     'São Paulo',       'SP', 'Sudeste',      'M', '1990-03-15'),
('Mariana Costa',      'mariana.costa@email.com',      'Rio de Janeiro',  'RJ', 'Sudeste',      'F', '1988-07-22'),
('Pedro Almeida',      'pedro.almeida@email.com',      'Curitiba',        'PR', 'Sul',           'M', '1995-11-08'),
('Juliana Souza',      'juliana.souza@email.com',      'Porto Alegre',    'RS', 'Sul',           'F', '1992-04-30'),
('Rafael Lima',        'rafael.lima@email.com',        'Salvador',        'BA', 'Nordeste',     'M', '1987-09-12'),
('Fernanda Oliveira',  'fernanda.oliveira@email.com',  'Fortaleza',       'CE', 'Nordeste',     'F', '1993-01-25'),
('Gustavo Pereira',    'gustavo.pereira@email.com',    'Belo Horizonte',  'MG', 'Sudeste',      'M', '1991-06-18'),
('Camila Rodrigues',   'camila.rodrigues@email.com',   'Campinas',        'SP', 'Sudeste',      'F', '1989-12-03'),
('Diego Martins',      'diego.martins@email.com',      'Florianópolis',   'SC', 'Sul',           'M', '1994-08-14'),
('Larissa Nascimento', 'larissa.nascimento@email.com', 'Recife',          'PE', 'Nordeste',     'F', '1996-02-28'),
('Thiago Santos',      'thiago.santos@email.com',      'Goiânia',         'GO', 'Centro-Oeste', 'M', '1990-05-07'),
('Beatriz Carvalho',   'beatriz.carvalho@email.com',   'Manaus',          'AM', 'Norte',         'F', '1993-10-16'),
('Vinicius Araujo',    'vinicius.araujo@email.com',    'São Paulo',       'SP', 'Sudeste',      'M', '1988-03-21'),
('Amanda Gomes',       'amanda.gomes@email.com',       'Rio de Janeiro',  'RJ', 'Sudeste',      'F', '1997-07-09'),
('Felipe Barbosa',     'felipe.barbosa@email.com',     'Curitiba',        'PR', 'Sul',           'M', '1986-11-30'),
('Priscila Dias',      'priscila.dias@email.com',      'Porto Alegre',    'RS', 'Sul',           'F', '1994-04-15'),
('Henrique Ribeiro',   'henrique.ribeiro@email.com',   'Belo Horizonte',  'MG', 'Sudeste',      'M', '1991-08-22'),
('Natalia Fernandes',  'natalia.fernandes@email.com',  'Salvador',        'BA', 'Nordeste',     'F', '1989-01-11'),
('Bruno Torres',       'bruno.torres@email.com',       'Fortaleza',       'CE', 'Nordeste',     'M', '1995-06-04'),
('Leticia Mendes',     'leticia.mendes@email.com',     'Brasília',        'DF', 'Centro-Oeste', 'F', '1992-09-27'),
('Marcelo Castro',     'marcelo.castro@email.com',     'São Paulo',       'SP', 'Sudeste',      'M', '1987-12-18'),
('Isabela Nunes',      'isabela.nunes@email.com',      'Rio de Janeiro',  'RJ', 'Sudeste',      'F', '1996-03-08'),
('Eduardo Lopes',      'eduardo.lopes@email.com',      'Florianópolis',   'SC', 'Sul',           'M', '1993-07-25'),
('Aline Moreira',      'aline.moreira@email.com',      'Recife',          'PE', 'Nordeste',     'F', '1990-11-14'),
('Leonardo Campos',    'leonardo.campos@email.com',    'Goiânia',         'GO', 'Centro-Oeste', 'M', '1988-04-02'),
('Tatiane Vieira',     'tatiane.vieira@email.com',     'Manaus',          'AM', 'Norte',         'F', '1994-08-19'),
('Rodrigo Teixeira',   'rodrigo.teixeira@email.com',   'Campinas',        'SP', 'Sudeste',      'M', '1991-01-28'),
('Gabriela Sousa',     'gabriela.sousa@email.com',     'Belo Horizonte',  'MG', 'Sudeste',      'F', '1997-05-13'),
('Alexandre Correia',  'alexandre.correia@email.com',  'Porto Alegre',    'RS', 'Sul',           'M', '1986-10-06'),
('Claudia Freitas',    'claudia.freitas@email.com',    'Salvador',        'BA', 'Nordeste',     'F', '1993-02-23');

-- Gera 350 pedidos com itens aleatórios entre 2024-01-01 e 2026-03-31
DELIMITER $$

CREATE PROCEDURE gerar_pedidos()
BEGIN
    DECLARE i            INT DEFAULT 1;
    DECLARE v_pedido_id  INT;
    DECLARE v_preco      DECIMAL(10,2);
    DECLARE v_subtotal   DECIMAL(10,2);
    DECLARE v_total      DECIMAL(10,2);
    DECLARE v_frete      DECIMAL(10,2);
    DECLARE v_desconto   DECIMAL(10,2);
    DECLARE j            INT;
    DECLARE v_num_itens  INT;
    DECLARE v_produto_id INT;
    DECLARE v_qtd        INT;

    WHILE i <= 350 DO
        SET v_frete    = ROUND(5  + RAND() * 45,  2);
        SET v_desconto = ROUND(RAND() * 80, 2);

        INSERT INTO pedidos (cliente_id, vendedor_id, status, canal, data_pedido, data_entrega, valor_total, desconto, frete)
        VALUES (
            FLOOR(1 + RAND() * 30),
            FLOOR(1 + RAND() * 5),
            CASE FLOOR(RAND() * 10)
                WHEN 0 THEN 'cancelado'
                WHEN 1 THEN 'em_transito'
                ELSE 'entregue'
            END,
            ELT(FLOOR(1 + RAND() * 4), 'site', 'app', 'marketplace', 'loja_fisica'),
            DATE_ADD('2024-01-01 08:00:00', INTERVAL FLOOR(RAND() * 820 * 1440) MINUTE),
            DATE_ADD('2024-01-01 08:00:00', INTERVAL FLOOR(RAND() * 820 * 1440 + 2880) MINUTE),
            0,
            v_desconto,
            v_frete
        );

        SET v_pedido_id = LAST_INSERT_ID();
        SET v_num_itens = FLOOR(1 + RAND() * 4);
        SET v_total     = 0;
        SET j           = 1;

        WHILE j <= v_num_itens DO
            SET v_produto_id = FLOOR(1 + RAND() * 20);
            SET v_qtd        = FLOOR(1 + RAND() * 5);
            SELECT preco INTO v_preco FROM produtos WHERE id = v_produto_id;
            SET v_subtotal = ROUND(v_qtd * v_preco, 2);
            SET v_total    = v_total + v_subtotal;

            INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario, subtotal)
            VALUES (v_pedido_id, v_produto_id, v_qtd, v_preco, v_subtotal);

            SET j = j + 1;
        END WHILE;

        UPDATE pedidos
        SET valor_total = ROUND(v_total + v_frete - v_desconto, 2)
        WHERE id = v_pedido_id;

        SET i = i + 1;
    END WHILE;
END$$

DELIMITER ;

CALL gerar_pedidos();
DROP PROCEDURE IF EXISTS gerar_pedidos;
