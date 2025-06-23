from models.produto import Produto

class ProdutoBeleza(Produto):
    def __init__(self, nome: str, preco: float, tipo_pele: str):
        super().__init__(nome, preco)
        self.__tipo_pele = tipo_pele

    def __str__(self) -> str:
        return f"{super().__str__()} - Indicado para pele: {self.__tipo_pele}"
