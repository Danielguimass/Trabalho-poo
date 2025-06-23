from models.base import ProdutoBase

class Produto(ProdutoBase):
    _codigo_atual = 1

    def __init__(self, nome: str, preco: float):
        self.__codigo = Produto._codigo_atual
        self.__nome = nome
        self.__preco = preco
        Produto._codigo_atual += 1

    @property
    def codigo(self):
        return self.__codigo

    @property
    def nome(self):
        return self.__nome

    @property
    def preco(self):
        return self.__preco

    def exibir_detalhes(self) -> str:
        return f'Código: {self.__codigo} | Nome: {self.__nome} | Preço: R$ {self.__preco:.2f}'

    def __str__(self):
        return self.exibir_detalhes()
