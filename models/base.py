from abc import ABC, abstractmethod

class ProdutoBase(ABC):
    @abstractmethod
    def exibir_detalhes(self) -> str:
        pass
