from models.produto import Produto

class ProdutoAlimento(Produto):
    def __init__(self, nome: str, preco: float, validade: str):
        super().__init__(nome, preco)
        self.__validade = validade

    def __str__(self) -> str:
        return f"{super().__str__()} - Validade: {self.__validade}"
