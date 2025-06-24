from models.produto import Produto

class ItemVenda(Produto):
    def __init__(self, produto: Produto, quantidade: int):
        super().__init__(produto.nome, produto.preco)
        self.__quantidade = quantidade

    @property
    def quantidade(self):
        return self.__quantidade

    def __str__(self):
        return f'{super().__str__()} | Quantidade: {self.__quantidade}'
