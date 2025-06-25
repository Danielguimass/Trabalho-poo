import sqlite3

DATABASE = 'db_loja.db'

def conectar():
    return sqlite3.connect(DATABASE)

def criar_tabelas():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            preco REAL NOT NULL,
            tipo TEXT NOT NULL,
            detalhe TEXT,
            caminho_imagem TEXT -- Certifique-se de que está aqui!
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS carrinho (
            id_produto INTEGER,
            quantidade INTEGER,
            FOREIGN KEY (id_produto) REFERENCES produtos(id)
        )
    ''')
    conn.commit()
    conn.close()

criar_tabelas() # Garanta que esta linha está descomentada

def salvar_produto(nome, preco, tipo, detalhe, caminho_imagem):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO produtos (nome, preco, tipo, detalhe, caminho_imagem) VALUES (?, ?, ?, ?, ?)",
                   (nome, preco, tipo, detalhe, caminho_imagem))
    conn.commit()
    conn.close()

def listar_produtos():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, preco, tipo, detalhe, caminho_imagem FROM produtos") # Adapte se você não tiver todas essas colunas
    produtos = cursor.fetchall()
    conn.close()
    return produtos

def pegar_produto_por_id(produto_id: int):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('SELECT id, nome, preco, tipo, detalhe, caminho_imagem FROM produtos WHERE id = ?', (produto_id,))
    dado = cursor.fetchone()
    conn.close()
    return dado

def adicionar_ao_carrinho(produto_id: int):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('SELECT id_produto FROM carrinho WHERE id_produto = ?', (produto_id,))
    item = cursor.fetchone()
    if item:
        cursor.execute('UPDATE carrinho SET quantidade = quantidade + 1 WHERE id_produto = ?', (produto_id,))
    else:
        cursor.execute('INSERT INTO carrinho (id_produto, quantidade) VALUES (?, ?)', (produto_id, 1))
    conn.commit()
    conn.close()

def listar_carrinho():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT p.id, p.nome, p.preco, p.tipo, p.detalhe, c.quantidade 
        FROM carrinho c 
        JOIN produtos p ON c.id_produto = p.id
    ''')
    dados = cursor.fetchall()
    conn.close()
    return dados

def limpar_carrinho():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM carrinho')
    conn.commit()
    conn.close()
