# ---- OPEN FILE ----

mat_op = ['=', '+', '-', '/', '*']
logi_op = ['!', '>', '<', '!=', '==', '>=', '<=', '&&', '||']
operadores = mat_op + logi_op + ['texto', 'inteiro', 'de', 'para', 'temanho', 'ler']

pontuacoes = [',', ';', ':', '.', '?']
grupos = ['(', ')', '[', ']', '{', '}']

simbolos = pontuacoes + grupos + ['\n']

specialChars = operadores + simbolos

palavras_chave = ('var', 'vet', 'del', 'se', 'senao', 'senaose', 'funcao', 'por',
             'enquanto', 'escreva', 'verdadeiro', 'falso', 'texto', 'de', 'para', 'tamanho',
             'ler', 'texto')

DADOS_SOLIDOS = {}

# ---- TOKEN TYPES ----

T_CHAVE = 'chave'
T_SIMBOLO = 'simbolo'
T_TEXTO = 'texto'
T_INTEIRO = 'inteiro'
T_V = 'virgula'
T_OPERADOR = 'operador'
T_BOOLEANO = 'booleano'
T_NULO = 'nulo'

# ---- OPERATION TYPES ----

SOMA = 'soma'
SUBTRACAO = 'subtracao'
MULTIPLICACAO = 'multiplicacao'
DIVISAO = 'divisao'

IGUAL = 'igual'
DIFERENTE = 'diferente'
MAIOR = 'maior'
MENOR = 'menor'
MA_OU_IGUAL = 'ma_ou_igual'
ME_OU_IGUAL = 'me_ou_igual'
NAO = 'nao'

E = 'e'
OU = 'ou'

# ---- NODE TYPES ----

N_NUM = 'NUM'
N_TEXTO = 'texto'
N_BOOL = 'BOOL'
N_OPER = 'OPER'
N_SIM = 'SIMBOLO'
N_CHAVE = 'CHAVE'
N_NULO = 'NULO'
N_VETOR = 'VETOR'
N_FUN = 'FUNCAO'
N_DECLARACAO = 'declaracao'
N_ATRIBUICAO = 'atribuicao'
N_C_ESCREVA = 'console-escreva'
N_C_LEIA = 'console-leia'
N_PARBLOCO = "n_parbloco"
N_BINAROOP = "n_binaroop"
N_COMPOP = "n_compop"
N_LOGICABINARIA = 'n_peloregis'
N_EXCLUSAO = 'n_exclusao'
N_LEITURA_EXP = 'n_exp_leitura'
N_VETOR_ACESSO = 'n_vetor_acesso'
N_OP_NAO = 'n_nao_op'
N_VETOR_TAMANHO = 'n_vetor_tamanho'
N_INSTRUCAO_CONDICIONAL = 'instrucao-condicional'
N_LOOP_ENQUANTO = 'loop-enquanto'
N_LOOP_POR = 'loop-por'
N_DEC_FUNCAO = 'n_dec_funcao'
N_CHAMADA_FUNCAO = 'n_chamada_funcao'
N_PARA_TEXTO = 'n_para_texto'
N_PARA_NUMERO = 'n_para_numero'
N_PARA_OP = 'n_para-op'
