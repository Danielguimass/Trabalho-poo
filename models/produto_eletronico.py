from models.produto import Produto

class ProdutoEletronico(Produto):
    def __init__(self, nome: str, preco: float, garantia_meses: int):
        super().__init__(nome, preco)
        self.__garantia_meses = garantia_meses

    def exibir_garantia(self) -> str:
        return f"{self.nome} tem {self.__garantia_meses} meses de garantia."

    def __str__(self) -> str:
        return f"{super().__str__()} - Garantia: {self.__garantia_meses} meses"
