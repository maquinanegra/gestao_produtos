"""
Programa para gestão do catálogo de produtos. Este programa permite:
    - Lista o catálogo
    - Pesquisar por alguns campos 
    - Eliminar um registo do catálogo
    - Guardar o catálogo em ficheiro
"""

from decimal import Decimal as dec
from hashlib import new
import subprocess
import sys
from typing import TextIO

CSV_DEFAULT_DELIM = ','
DEFAULT_INDENTATION = 3

################################################################################
##
##       PRODUTOS E CATÁLOGO
##
################################################################################

PRODUCT_TYPES = {
    'AL': 'Alimentação',
    'DL': 'Detergente p/ Loiça',
    'FRL': 'Frutas e Legumes'
}

class Produto:
    def __init__(
            self, 
            id_: int, 
            nome: str, 
            tipo: str, 
            quantidade: int,
            preco: dec
    ):
        if id_ < 0 or len(str(id_)) != 5:
            raise InvalidProdAttribute(f'{id_=} inválido (deve ser > 0 e ter 5 dígitos)')
        if not nome:
            raise InvalidProdAttribute('Nome vazio')
        if tipo.upper() not in PRODUCT_TYPES:
            raise InvalidProdAttribute(f'Tipo de produto ({tipo}) desconhecido')
        if quantidade < 0:
            raise InvalidProdAttribute('Quantidade deve ser >= 0')
        if preco < 0:
            raise InvalidProdAttribute('Preço deve ser >= 0')

        self.id = id_
        self.nome = nome
        self.tipo = tipo.upper()
        self.quantidade = quantidade
        self.preco = preco
    #:

    @classmethod
    def from_csv(cls, txt_csv: str) -> 'Produto':
        # '40001,morangos da escócia,FRL,100,1.5'
        attrs = txt_csv.split(',')
        return cls(
            id_ = int(attrs[0]),
            nome = attrs[1].strip(),
            tipo = attrs[2].strip(),
            quantidade = int(attrs[3]),
            preco = dec(attrs[4]),
        )
    #

    @property
    def nome_tipo(self) -> str:
        return PRODUCT_TYPES[self.tipo]
    #:

    def __str__(self):
        cls_name = self.__class__.__name__
        return f'{cls_name}[id_= {self.id}  nome = "{self.nome}" tipo = "{self.tipo}"]'
    #:

    def __repr__(self):
        cls_name = self.__class__.__name__
        return f'{cls_name}({self.id}, "{self.nome}", "{self.tipo}", {self.quantidade}, etc...)'
    #:
#:

class InvalidProdAttribute(ValueError):
    pass
#:

class ProductCollection:
    def __init__(self):
        self._prods = {}
    #:
    
    def append(self, prod: Produto):
        if prod.id in self._prods:
            raise DuplicateValue(f'Já existe produto com id {prod.id} na colecção')
        self._prods[prod.id] = prod
    #:

    def pesquisa_por_id(self, id_):
        return self._prods.get(id_)
    #:

    def pesquisa(self, criterio):
        encontrados = ProductCollection()
        for prod in self._prods.values():
            if criterio(prod):
                encontrados.append(prod)
        return encontrados
    #:

    def __iter__(self):
        for prod in self._prods.values():
            yield prod
        #:
    #:

    def __str__(self):
        return f'{self.__class__.__name__}[#produtos = {len(self._prods)}]'
    #:

    def _dump(self):
        for prod in self._prods.values():
            print(prod)
    #:
#:

class DuplicateValue(Exception):
    pass
#:

produtos = ProductCollection()

################################################################################
##
##       LEITURA DOS FICHEIROS
##
################################################################################

def le_produtos(caminho_fich_produtos: str):
    with open(caminho_fich_produtos, 'rt') as fich:
        for linha in linhas_relevantes(fich):
            prod = Produto.from_csv(linha)
            produtos.append(prod)
#:

def escreve_produtos(caminho_fich_produtos: str, new_prod):
    with open(caminho_fich_produtos, 'wt') as fich:
        fich.write(new_prod)
#:

def linhas_relevantes(fich: TextIO) -> list:
    for linha in fich:
        if not linha.strip():
            continue
        if linha[0] == '#':
            continue
        yield linha
#:

################################################################################
##
##       MENU, OPÇÕES E INTERACÇÃO COM UTILIZADOR
##
################################################################################

def exibe_msg(*args, indent = DEFAULT_INDENTATION, **kargs):
    print(' ' * (indent - 1), *args, **kargs)
#:

def cls():
    if sys.platform == 'win32':
        subprocess.run(['cls'], shell=True, check=True)
    elif sys.platform in ('darwin', 'linux', 'bsd', 'unix'):
        subprocess.run(['clear'], check=True)
    #:
#:

def pause(msg: str="Pressione ENTER para continuar...", indent = DEFAULT_INDENTATION):
    input(f"{' ' * indent}{msg}")
#:

def exec_menu():
    """
    - Lista o catálogo
    - Pesquisar por alguns campos 
    - Eliminar um registo do catálogo
    - Guardar o catálogo em ficheiro
    """

    while True:
        cls()
        exibe_msg("*******************************************")
        exibe_msg("* L - Listar catálogo                     *")
        exibe_msg("* P - Pesquisar por id                    *")
        exibe_msg("* A - Acrescentar produto                 *")
        exibe_msg("* E - Eliminar produto                    *")
        exibe_msg("* G - Guardar catálogo em ficheiro        *")
        exibe_msg("*                                         *")
        exibe_msg("* T - Terminar programa                   *")
        exibe_msg("*******************************************")

        print()
        opcao = input("   OPCAO> ").strip().upper()

        if opcao in ('L', 'LISTAR'):
            exec_listar()
        elif opcao in ('P', 'PESQUISAR'):
            exec_pesquisar()
        elif opcao in ('A', 'ADICIONAR'):
            exec_adicionar()
        elif opcao in ('E', 'ELIMINAR'):
            exibe_msg("ELIMINAR")
        elif opcao in ('G', 'GUARDAR'):
            exibe_msg("GUARDAR")
        elif opcao in ('T', 'TERMINAR'):
            exibe_msg("O programa vai encerrar")
            # return
            sys.exit(0)
        else:
            exibe_msg(f"Opção {opcao} inválida ou ainda não implementada")
        #:
    #:
#:

def exec_listar():
    for prod in produtos:
        exibe_msg(prod)
    #:
    pause()
#:
def exec_pesquisar():
    id = int(input(" "*DEFAULT_INDENTATION+"ID a pesquisar: "))
    x = produtos.pesquisa_por_id(id)
    exibe_msg(x)
    #:
    pause()
#:

def exec_adicionar():
    def new_prod_func():
        new_prod1 = input("Insira a referência do produto: ")
        new_prod2 = input("Insira a descrição do produto: ") 
        new_prod3 = input("insira o tipo de produto: ")
        new_prod4 = input("Insira a quantidade de produto: ")
        new_prod5 = input("Insira o preço do produto:")
        while not new_prod1 and not new_prod2 and not new_prod3 and not new_prod4 and not new_prod5:
            new_prod_func()

        return new_prod1, new_prod2, new_prod3, new_prod4, new_prod5
    
    new_prod1, new_prod2, new_prod3, new_prod4, new_prod5 = new_prod_func()
    new_prod_csv = f'{new_prod1}, {new_prod2}, {new_prod3}, {new_prod4}, {new_prod5}'
    try:
        new_prod = Produto.from_csv(new_prod_csv)
        produtos.append(new_prod)
    except InvalidProdAttribute as err:
        print (err)
    #escreve_produtos('produtos.csv',new_prod_csv)
    #:
    pause()

def main():
    le_produtos('produtos.csv')
    exec_menu()
#:

if __name__ == '__main__':
    main()
#:
