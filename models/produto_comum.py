from models.produto import Produto

class ProdutoComum(Produto):
    def __init__(self, nome: str, preco: float):
        super().__init__(nome, preco)
