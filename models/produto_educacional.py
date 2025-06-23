from models.produto import Produto

class ProdutoEducacional(Produto):
    def __init__(self, nome: str, preco: float, plataforma: str):
        super().__init__(nome, preco)
        self.__plataforma = plataforma

    def __str__(self) -> str:
        return f"{super().__str__()} - Plataforma: {self.__plataforma}"
