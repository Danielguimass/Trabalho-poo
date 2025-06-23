from models.produto import Produto

class ProdutoModa(Produto):
    def __init__(self, nome: str, preco: float, tamanho: str):
        super().__init__(nome, preco)
        self.__tamanho = tamanho

    def __str__(self) -> str:
        return f"{super().__str__()} - Tamanho: {self.__tamanho}"
