import re

# Função principal que gerencia o escopo do programa
def gerenciamento_escopo(arquivo):
    pilha = [[]]  # Inicializa uma pilha de escopos, começa com um escopo vazio
    tabela_simbolos = []  # Inicializa uma lista para armazenar todas as variáveis declaradas
    contador = 1  # Inicializa um contador para controlar o número da linha
    comandos = lista_comandos(arquivo)  # Obtém a lista de comandos do arquivo de entrada

    # Percorre cada linha de comando
    for linha in comandos:
        partes = linha.split()  # Divide a linha em partes separadas por espaços
        if len(partes) == 0:
            contador += 1  # Incrementa o contador de linha se a linha estiver vazia
        else:
            # Verifica o tipo de comando na primeira parte da linha
            match partes[0]:
                # Se for um comando "BLOCO", cria um novo escopo vazio
                case "BLOCO":
                    bloco = partes[1]
                    pilha.append([])
                # Se for um comando "NUMERO", faz a declaração de uma variável numérica
                case "NUMERO":
                    var = "".join(partes[1:])
                    lex, valores = declaracao(var)
                    tabela = []
                    for lexema, valor in zip(lex, valores):
                        try:
                            if (tipo(valor) == "NUMERO" or valor == None):
                                tabela.append({
                                    "lexema": lexema,
                                    "valor": valor,
                                    "tipo": "NUMERO",
                                    "bloco": bloco
                                })
                        except Exception as ex:
                            print(f" Erro: valor não numérico")
                            break
                    if criar_escopo(tabela, pilha):
                        pilha[len(pilha) - 1].extend(tabela)
                        tabela_simbolos.extend(tabela)
                    else:
                        print(f" Erro: variável já declarada")
                # Se for um comando "CADEIA", faz a declaração de uma variável de cadeia de caracteres
                case "CADEIA":
                    var = "".join(partes[1:])
                    lex, valores = declaracao(var)
                    tabela = []
                    for lexema, valor in zip(lex, valores):
                        if (tipo(valor) == "CADEIA" or valor == None):
                            tabela.append({
                                "lexema": lexema,
                                "valor": valor,
                                "tipo": "CADEIA",
                                "bloco": bloco
                            })
                        else:
                            print(
                                f" {contador} Erro: valor não é cadeia")
                            break
                    if criar_escopo(tabela, pilha):
                        pilha[len(pilha) - 1].extend(tabela)
                        tabela_simbolos.extend(tabela)
                    else:
                        print(f" {contador} Erro: variável já declarada")
                # Se for um comando "PRINT", imprime o valor da variável
                case "PRINT":
                    var = partes[1]
                    try:
                        valor = busca_de_variavel(var, pilha, contador)
                        print(f" {valor}")
                    except Exception as ex:
                        print(str(ex))
                # Se for um comando "FIM", remove o escopo atual da pilha
                case "FIM":
                    pilha.pop()
                # Para outros casos, trata-se de uma atribuição de valor a uma variável
                case _:
                    try:
                        var, valor = linha.split("=")
                        atribuicao(var.strip(), valor.strip(), pilha,
                                   contador)
                    except Exception as ex:
                        print(str(ex))
            contador += 1


# Função para obter a lista de comandos a partir de um arquivo
def lista_comandos(arquivo):
    arquivo = open(arquivo, 'r')
    lista = []
    for linha in arquivo:
        lista.append(linha.strip())
    arquivo.close()
    return lista

# Função para processar a declaração de variáveis
def declaracao(var):
    lex = []  # Lista para armazenar os lexemas das variáveis
    valores = []  # Lista para armazenar os valores das variáveis
    declaracoes = re.findall(
        "[a-zA-Z][0-9a-zA-Z_]*=[^,]+|[a-zA-Z][0-9a-zA-Z_]*[^,]?", var)
    for i in declaracoes:
        separado = i.split("=")
        if len(separado) == 2:
            lex.append(separado[0])
            valores.append(separado[1])
        else:
            lex.append(separado[0])
            valores.append(None)
    return lex, valores

# Função para verificar se é possível criar um novo escopo
def criar_escopo(tabela, pilha):
    for i in pilha[len(pilha) - 1]:
        for j in tabela:
            if i["lexema"] == j["lexema"]:
                return False
    return True

# Função para buscar o valor de uma variável na pilha de escopos
def busca_de_variavel(variavel, pilha, linha):
    for i in pilha[len(pilha) - 1:0:-1]:
        for tabela in i:
            if tabela["lexema"] == variavel:
                return tabela["valor"]
    raise Exception(
        f" Erro linha {linha:>2}: variável não declarada")

'''
    Atualiza o valor de uma variável na pilha de tabelas. Caso a variável não exista, cria um nova.
    Se o tipo do valor for diferente do tipo da variável, lança uma exceção.
    Se for uma atribuição de uma variavel a outra uma execeção é lançada.
'''
def atribuicao(variavel, valor, pilha, linha):

    def obter_valor_e_tipo(valor, pilha):
        # Verifica se o valor é um identificador de variável
        for i in pilha[::-1]:  # Percorre a pilha de escopos de cima para baixo
            for tabela in i:
                if tabela["lexema"] == valor:
                    return tabela["valor"], tabela["tipo"]
        # Se não for identificador, trata como valor literal
        tipo_valor = tipo(valor)
        return valor, tipo_valor

    def verifica_declaracao(variavel, pilha):
        for i in pilha[::-1]:
            for tabela in i:
                if tabela["lexema"] == variavel:
                    return True
        return False

    if not verifica_declaracao(variavel, pilha):
        raise Exception(
            f" Erro: linha {linha:>2} variável não declarada")

    try:
        valor_resolvido, tipo_var = obter_valor_e_tipo(valor, pilha)
    except Exception as ex:
        raise Exception(f" Erro linha {linha:>2}: tipos não compatíveis")

    for i in pilha[::-1]:  # Percorre a pilha de escopos de cima para baixo
        for tabela in i:
            if tabela["lexema"] == variavel:
                if tabela["tipo"] == tipo_var:
                    tabela["valor"] = valor_resolvido
                    return
                else:
                    raise Exception(
                        f" Erro linha {linha:>2}: tipos não compatíveis"
                    )
    pilha[-1].append({
        "lexema": variavel,
        "valor": valor_resolvido,
        "tipo": tipo_var,
        "bloco": "global"
    })

'''
    Verifica o tipo de um valor e retorna "NUMERO" se for um número, "CADEIA" se for uma cadeia de caracteres ou None se for uma variável não inicializada. Se o tipo não estiver entre os previstos, uma exceção será lançada. 
'''
def tipo(valor):
    if valor is None:
        return None
    if valor[0] == '"' and valor[-1] == '"':
        return "CADEIA"
    try:
        float(valor)
        return "NUMERO"
    except ValueError:
        raise Exception()

def print_tabela(tabela):
    ''' Funcao auxiliar para imprimir uma tabela '''
    print(f"{tabela['tipo']} {tabela['lexema']} = {tabela['valor']} | {tabela['bloco']}")


def print_pilha(pilha):
    ''' Imprime a pilha de tabelas '''

    print("PILHA:")
    for i in pilha:
        for j in i:
            print_tabela(j)
    print("FIM PILHA)
def main():
    aquivo = "exemplo.txt"
    gerenciamento_escopo(aquivo)


if __name__ == "__main__":
    main()
