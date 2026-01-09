import TOKENIZER
import PARSER
from NODE import NL, NUM, STR, BL, ARR, FUN
from DEPENDENCIES import *
from ERROR import *

lexer = TOKENIZER.TOKENIZER()
parser = PARSER.PARSER()


class RUNTIME:
    def exec(self, ast):
        last_condition_state = None
        for c in ast.tree:

            if c.my_type != N_INSTRUCAO_CONDICIONAL and last_condition_state is not None:
                last_condition_state = None
            elif c.my_type == N_INSTRUCAO_CONDICIONAL:
                if c.layer == 'se' and last_condition_state is not None:
                    last_condition_state = None

            if c.my_type == N_DECLARACAO:
                if c.get_key() is None:
                    ERROR.throw_error('(ErroDeSintaxe) Tentou criar uma variável sem nome.')
                if c.get_reserve() == 'multiple':
                    DADOS_SOLIDOS[c.get_key()] = ARR()
                else:
                    DADOS_SOLIDOS[c.get_key()] = NL()

            elif c.my_type == N_EXCLUSAO:
                key = c.get_value()

                if key.my_type == N_CHAVE:
                    k = key.syn_obj
                    if DADOS_SOLIDOS.get(k) is not None:
                        DADOS_SOLIDOS.pop(k)
                    else:
                        ERROR.throw_error(f'(ErroDeMemória) Tentou acessar um endereço inexistente: {k}, declare this '
                                          f'declare essa variável primeiro!')

                elif key.my_type == N_VETOR_ACESSO:
                    k = key.get_key()
                    indexes = key.get_indexes()
                    address_pointer = DADOS_SOLIDOS[k]
                    mod = None
                    for i in range(len(indexes)):
                        if i == len(indexes) - 1:
                            mod = 'del'
                        address_pointer = self.scarve_array(address_pointer, indexes[i], mod)
                else:
                    ERROR.throw_error('O comando "del" só aceita um endereço de memória como parâmetro. ')

            elif c.my_type == N_ATRIBUICAO:
                key = c.get_key()          # returns expread / arraccess
                value = c.get_value()

                ac_key = key.get_key()
                memory_address = DADOS_SOLIDOS.get(ac_key)
                if memory_address is not None:
                    resolved_v = self.solve_exp(value)

                    if key.my_type == N_LEITURA_EXP:
                        if DADOS_SOLIDOS[ac_key].my_type == N_VETOR:
                            if resolved_v.my_type == N_VETOR:
                                DADOS_SOLIDOS[ac_key] = resolved_v
                            else:
                                ERROR.throw_error(f'(ErroDeAtribuição) Tentou atribuir um valor "{ac_key}" '
                                                  f'a um endereço de memória do tipo vetor. ')

                        elif DADOS_SOLIDOS[ac_key].my_type == N_FUN:
                            if resolved_v.my_type == N_FUN:
                                DADOS_SOLIDOS[ac_key] = resolved_v
                            else:
                                ERROR.throw_error(f'(ErroDeAtribuição) Tentou atribuir um valor de tipo {resolved_v.my_type} "{ac_key}" '
                                                  f'a um endereço de função.')
                        else:
                            if resolved_v.my_type in N_NUM + N_TEXTO + N_BOOL + N_NULO:
                                DADOS_SOLIDOS[ac_key] = resolved_v
                            else:
                                ERROR.throw_error(f'(ErroDeAtribuição) Tentou atribuir um vetor "{ac_key}" '
                                                  f'a um endereço de memória de valor simples.')

                    elif key.my_type == N_VETOR_ACESSO:
                        indexes = key.get_indexes()
                        address_pointer = DADOS_SOLIDOS[ac_key]
                        mod = None
                        for i in range(len(indexes)):
                            if i == len(indexes)-1:
                                mod = 'add'
                            address_pointer = self.scarve_array(address_pointer, indexes[i], mod, resolved_v)

                else:
                    ERROR.throw_error(f'(ErroDeMemória) Tentou acessar um endereço inexistente: {ac_key}, declare essa '
                                      f'variável primeiro!')

            elif c.my_type == N_C_ESCREVA:
                value = c.get_value()
                res = self.solve_exp(value)
                res.write_to_console()
                print()

            elif c.my_type == N_INSTRUCAO_CONDICIONAL:
                if last_condition_state is None:
                    if c.layer == 'se':
                        value = c.get_value()
                        last_condition_state = False
                        if self.solve_exp(value).syn_obj == 'verdadeiro':
                            self.exec(parser.parse(c.get_exeblock().get_block()))  # rever a necessidade de um node codeblock
                            last_condition_state = True
                    else:
                        ERROR.throw_error(f'Era esperado um "se" antes de "{c.layer}".')

                elif last_condition_state is False:
                    if c.layer == 'senaose':
                        value = c.get_value()
                        if self.solve_exp(value).syn_obj == 'verdadeiro':
                            self.exec(parser.parse(c.get_exeblock().get_block()))
                            last_condition_state = True
                    else:
                        self.exec(parser.parse(c.get_exeblock().get_block()))
                        last_condition_state = True

            elif c.my_type == N_LOOP_ENQUANTO:
                value = c.get_value()
                if c.get_exeblock() is None:
                    ERROR.throw_error('(ErroDeSintaxe) O loop enquanto requer um bloco ({...}).')
                while self.solve_exp(value).syn_obj == 'verdadeiro':
                    self.exec(parser.parse(c.get_exeblock().get_block()))

            elif c.my_type == N_LOOP_POR:
                from_op = c.get_value()
                block = c.get_exeblock()

                if from_op is not None:
                    dec = from_op.get_v1()
                    arr = from_op.get_v2()

                    key = None
                    if dec.my_type == N_DECLARACAO:
                        key = dec.get_key()
                        if dec.get_reserve() == 'multiple':
                            DADOS_SOLIDOS[key] = ARR()
                        else:
                            DADOS_SOLIDOS[key] = NL()
                    else:
                        ERROR.throw_error(f'(ErroDeTipo) O for precisa de uma declaração de variável como primeiro parâmetro, mas recebeu '
                                          f'"{dec.my_type}".')

                    if arr.my_type == N_PARA_OP:
                        arr = self.solve_exp(arr)

                    elif arr.my_type == N_CHAVE:
                        if DADOS_SOLIDOS.get(arr.syn_obj) is not None:
                            arr = DADOS_SOLIDOS[arr.syn_obj]
                        else:
                            ERROR.throw_error(f'(ErroDeMemória) Tentou acessar um endereço inexistente: {arr.syn_obj}, declare essa '
                                              f'variável primeiro!')

                    if arr.my_type != N_VETOR:
                        ERROR.throw_error(f'(ErroDeTipo) O for precisa de um vetor como segundo parâmetro, mas recebeu '
                                          f'"{arr.my_type}".')

                    for each in arr.get_node_list():
                        DADOS_SOLIDOS[key] = each
                        if block is None:
                            ERROR.throw_error('(ErroDeSintaxe) O loop por requer um bloco ({...}).')
                        self.exec(parser.parse(block.get_block()))
                else:
                    ERROR.throw_error('(ErroDeAtribuição) O loop por não possui declaração associada a ele.')

            elif c.my_type == N_DEC_FUNCAO:
                key = c.get_key()

                if key is None:
                    ERROR.throw_error('(ErroDeSintaxe) Tentou criar uma função sem nome.')
                if c.get_exeblock() is None:
                    ERROR.throw_error('(ErroDeSintaxe) A função requer um bloco ({...}).')

                parameter_labels = []
                if DADOS_SOLIDOS.get(key) is None:
                    if c.get_parameters() is None:
                        ERROR.throw_error('(ErroDeAtribuição) A declaração da função requer parênteses.')
                    for parameter in c.get_parameters().get_node_array():
                        if parameter.my_type == 'AST':
                            for n in parameter.tree:
                                if n.my_type == N_DECLARACAO:
                                    parameter_labels.append(n.get_key())
                                if n.my_type != N_DECLARACAO:
                                    ERROR.throw_error(f'(ErroDeTipo) Você só pode definir declarações como '
                                                      f'parâmetros de função, mas foi recebido {n.my_type}.')

                            self.exec(parameter)
                        elif parameter.my_type == N_NULO:
                            parameter_labels.append(parameter.syn_obj)
                        else:
                            ERROR.throw_error(f'(ErroDeTipo) Você só pode definir declarações como '
                                              f'parâmetros de função, mas foi recebido {parameter.my_type}.')
                    DADOS_SOLIDOS[key] = FUN(parameter_labels, c.get_exeblock())

                else:
                    ERROR.throw_error(f"(ErroDeAtribuição) O identificador {key} já está em uso, escolha outro nome para a "
                                      f'função.')

            elif c.my_type == N_CHAMADA_FUNCAO:
                key = c.get_key()
                pars = c.get_parameters().get_node_array()

                memory_address = DADOS_SOLIDOS.get(key)
                if memory_address is not None:
                    memory_address = DADOS_SOLIDOS[key]
                    if memory_address.my_type == N_FUN:
                        mother_pars = memory_address.get_parameters()

                        m_counts = 0
                        p_counts = 0

                        for each in mother_pars:
                            if each != 'nulo':
                                m_counts += 1

                        for each in pars:
                            if each.my_type != N_NULO:
                                p_counts += 1

                        if p_counts > m_counts:
                            ERROR.throw_error(f'(ErroDeAcesso) Excesso de parâmetros ({p_counts-m_counts}) '
                                              f'na função "{key}"')
                        if p_counts < m_counts:
                            ERROR.throw_error(f'(ErroDeAcesso) Parâmetros insuficientes ({m_counts-p_counts}) '
                                              f'na função "{key}"')

                        if len(mother_pars) <= len(pars):
                            for i in range(0, len(mother_pars)):
                                DADOS_SOLIDOS[mother_pars[i]] = self.solve_icognite(pars[i])
                    else:
                        ERROR.throw_error(f'(ErroDeChamada) Tentou chamar "{key}", que não é uma função. '
                                          f'Apenas funções podem ser chamadas.')

                    self.exec(parser.parse(memory_address.get_exeblock().get_block()))

                else:
                    ERROR.throw_error(f'(ErroDeMemória) Tentou acessar uma memória inexistente: {key}, declare essa '
                                      f'variável primeiro!')

            # print(DADOS_SOLIDOS)

    def solve_exp(self, operation):
        res = NL()
        n_res = None
        s_res = ''

        if operation is None:
            ERROR.throw_error('(ErroDeOperação) Expressão não resolvida. Você esqueceu de fechar alguma estrutura?')

        if operation.my_type == N_BINAROOP:
            i1 = operation.get_v1()
            i2 = operation.get_v2()

            i1 = self.solve_icognite(i1)
            i2 = self.solve_icognite(i2)

            if i1.my_type == i2.my_type:
                if i1.my_type == N_NUM and i2.my_type == N_NUM:
                    i1 = int(i1.syn_obj) if '.' not in i1.syn_obj else float(i1.syn_obj)
                    i2 = int(i2.syn_obj) if '.' not in i2.syn_obj else float(i2.syn_obj)
                    if operation.op == SOMA:
                        n_res = i1 + i2
                    elif operation.op == SUBTRACAO:
                        n_res = i1 - i2
                    elif operation.op == MULTIPLICACAO:
                        n_res = i1 * i2
                    elif operation.op == DIVISAO:
                        if i2 != 0:
                            n_res = i1 / i2
                        else:
                            ERROR.throw_error(f'(ErroDeDivisãoPorZero) Tentou dividir por zero!')
                elif i1.my_type == N_TEXTO and i2.my_type == N_TEXTO:
                    if operation.op == SOMA:
                        i1 = i1.syn_obj
                        i2 = i2.syn_obj
                        s_res = i1 + i2
                    else:
                        ERROR.throw_error(f'(ErroDeOperação) Só é permitido realizar a operação {operation.op} '
                                          f'entre números.')
            else:
                ERROR.throw_error(f'(ErroDeOperação) Não é possível operar entre tipos DIFERENTES '
                                  f'({i1.my_type}, {i2.my_type}).')

            if n_res is not None:
                if 0 < n_res < 1:
                    res = NUM(T_V, str(n_res))
                else:
                    res = NUM(T_INTEIRO, str(n_res))
            else:
                res = STR(s_res)

            return res

        elif operation.my_type == N_COMPOP:
            o1 = operation.get_v1()
            o2 = operation.get_v2()

            o1 = self.solve_icognite(o1)
            o2 = self.solve_icognite(o2)

            i1 = o1.syn_obj
            i2 = o2.syn_obj

            if o1.my_type == N_NUM and o2.my_type == N_NUM:
                i1 = int(i1) if o1.syn_class == T_INTEIRO else float(i1)
                i2 = int(i2) if o2.syn_class == T_INTEIRO else float(i2)

                if operation.op == MAIOR:
                    if i1 > i2:
                        return BL('true')
                    else:
                        return BL('false')

                elif operation.op == MENOR:
                    if i1 < i2:
                        return BL('true')
                    else:
                        return BL('false')

                elif operation.op == MA_OU_IGUAL:
                    if i1 >= i2:
                        return BL('true')
                    else:
                        return BL('false')

                elif operation.op == ME_OU_IGUAL:
                    if i1 <= i2:
                        return BL('true')
                    else:
                        return BL('false')

            if operation.op == IGUAL:
                if i1 == i2:
                    return BL('true')
                else:
                    return BL('false')

            elif operation.op == DIFERENTE:
                if i1 != i2:
                    return BL('true')
                else:
                    return BL('false')

            else:
                ERROR.throw_error(f'(ErroDeOperação) Não é possível realizar esse tipo de comparação. '
                                  f'{o1.my_type} e {o2.my_type}. Apenas valores inteiros são permitidos.')

        elif operation.my_type == N_LOGICABINARIA:
            o1 = operation.get_v1()
            o2 = operation.get_v2()

            o1 = self.solve_icognite(o1)
            o2 = self.solve_icognite(o2)

            i1 = o1.syn_obj
            i2 = o2.syn_obj

            if o1.my_type == N_BOOL and o2.my_type == N_BOOL:
                if operation.op == E:
                    if i1 == 'verdadeiro' and i2 == 'verdadeiro':
                        return BL('verdadeiro')
                    else:
                        return BL('falso')

                elif operation.op == OU:
                    if i1 == 'verdadeiro' or i2 == 'verdadeiro':
                        return BL('verdadeiro')
                    else:
                        return BL('falso')
            else:
                ERROR.throw_error(f'(ErroDeOperação) Só é possível realizar operações lógicas entre booleanos. '
                                  f'Tipos recebidos: ({o1.my_type}, {o2.my_type})')

        elif operation.my_type == N_VETOR_ACESSO:
            ac_key = operation.get_key()
            memory_address = DADOS_SOLIDOS.get(ac_key)
            if memory_address is not None:
                indexes = operation.get_indexes()
                address_pointer = DADOS_SOLIDOS[ac_key]
                for i in indexes:
                    address_pointer = self.scarve_array(address_pointer, i)

                if address_pointer.my_type == N_VETOR:
                    return self.generate_clone(address_pointer)
                return address_pointer
            else:
                ERROR.throw_error(f'(Erro de Memória) Tentou acessar uma memória inexistente: {ac_key}, declare essa '
                                  f'variável primeiro!')

        elif operation.my_type == N_PARA_OP:
            o1 = operation.get_v1()
            o2 = operation.get_v2()

            o1 = self.solve_icognite(o1)
            o2 = self.solve_icognite(o2)

            if o1.my_type == N_NUM and o2.my_type == N_NUM:
                if o1.syn_class == T_INTEIRO and o2.syn_class == T_INTEIRO:
                    i1 = int(o1.syn_obj)
                    i2 = int(o2.syn_obj)
                    arr = ARR()
                    for i in range(i1, i2+1):
                        arr.add_to_node_list(NUM(T_INTEIRO, str(i)))
                    return arr
                else:
                    ERROR.throw_error(f'(ErroDeOperação) A operação para só aceita INTEIRO e INTEIRO como parâmetros. Tente '
                                      f'{o1.my_type} e {o2.my_type}.')
            else:
                ERROR.throw_error(f'(ErroDeOperação) A operação para só aceita INTEIRO e INTEIRO como parâmetros. Tente'
                                  f'{o1.my_type} e {o2.my_type}.')

        elif operation.my_type == N_OP_NAO:
            i2 = operation.get_v2()
            i2 = self.solve_icognite(i2)

            if i2.my_type == N_BOOL:
                i2 = i2.syn_obj
                if i2 == 'verdadeiro':
                    res = 'falso'
                elif i2 == 'falso':
                    res = 'verdadeiro'

                res = lexer.set_tokens(lexer.lexate(res))[0]
                return res
            else:
                ERROR.throw_error(f'(ErroDeOperação) Não é possível negar valores que não são booleanos. {i2.my_type})')

        elif operation.my_type == N_VETOR_TAMANHO:
            ad_type = operation.get_v2()
            if ad_type.my_type == N_CHAVE:
                ac_key = ad_type.syn_obj
                memory_address = DADOS_SOLIDOS.get(ac_key)
                if memory_address is not None:
                    if memory_address.my_type == N_VETOR:
                        return NUM(T_INTEIRO, str(len(memory_address.get_node_list())))
                    else:
                        ERROR.throw_error(f'(ErroDeOperação) O operador de tamanho só aceita vetores como parâmetro. Tente '
                                          f'{memory_address.my_type}.')
                else:
                    ERROR.throw_error(f'(Erro de Memória) Tentou acessar uma memória inexistente: {ac_key}, declare essa '
                                      f'variável primeiro!')

            elif ad_type.my_type == N_VETOR_ACESSO:
                ac_key = ad_type.get_key()
                memory_address = DADOS_SOLIDOS.get(ac_key)
                if memory_address is not None:
                    indexes = ad_type.get_indexes()
                    address_pointer = DADOS_SOLIDOS[ac_key]
                    for i in indexes:
                        address_pointer = self.scarve_array(address_pointer, i)

                    if address_pointer.my_type == N_VETOR:
                        return NUM(T_INTEIRO, str(len(address_pointer.get_node_list())))
                    else:
                        ERROR.throw_error(f'(ErroDeOperação) O operador de tamanho só aceita VETORES como parâmetro. Recebeu '
                                          f'{memory_address.my_type}.')
                else:
                    ERROR.throw_error(f'(ErroDeMemória) Tentou acessar uma memória inexistente: {ac_key}, Declare essa '
                                      f'variável primeiro!')
            else:
                ERROR.throw_error(f'(ErroDeOperação) O operador de tamanho só aceita VETORES como parâmetro. Recebeu '
                                  f'{ad_type.my_type}.')

        elif operation.my_type == N_C_LEIA:
            i1 = self.solve_icognite(operation.get_v2())
            return STR(input(i1.syn_obj))

        elif operation.my_type == N_PARA_TEXTO:
            i1 = self.solve_icognite(operation.get_v2())
            return STR(i1.syn_obj)

        elif operation.my_type == N_PARA_NUMERO:
            i1 = self.solve_icognite(operation.get_v2())
            if i1.my_type == N_TEXTO:
                obj = i1.syn_obj
                if obj.isnumeric():
                    return NUM(T_INTEIRO, obj)
                else:
                    ERROR.throw_error(f'(ErroDeTipo) O operador "inteiro" exige strings apenas numéricas como parâmetro, mas você forneceu '
                                      f'"{obj}".')
            else:
                ERROR.throw_error(f'(ErroDeOperação) O operador "inteiro" aceita apenas strings como parâmetro. '
                                  f'Recebeu {i1.my_type}.')

        elif operation.my_type == N_PARBLOCO:
            for each in operation.get_node_array():
                res = self.solve_exp(each)  # REVER DEPOIS PARA A IMPLEMENTAÇÃO DE FN()
                return res

        elif operation.my_type in N_TEXTO + N_NUM + N_BOOL + N_VETOR + N_NULO:
            return operation

        elif operation.my_type == N_CHAVE:
            key = operation.syn_obj
            if DADOS_SOLIDOS.get(key) is not None:
                if DADOS_SOLIDOS[key].my_type == N_VETOR:
                    return self.generate_clone(DADOS_SOLIDOS[key])
                else:
                    return DADOS_SOLIDOS[key]
            else:
                ERROR.throw_error(f'(ErroDeMemória) Tentou acessar uma memória inexistente: {operation.syn_obj}, Declare essa '
                                  f'variável primeiro!')

    def solve_icognite(self, i):
        if i.my_type == N_CHAVE:
            if DADOS_SOLIDOS.get(i.syn_obj) is not None:
                return DADOS_SOLIDOS[i.syn_obj]
            else:
                ERROR.throw_error(
                    f'(ErroDeMemória) Tentou acessar uma memória inexistente: {i.syn_obj}, Declare essa '
                    f'variável primeiro!')

        elif i.my_type == N_LOGICABINARIA or i.my_type == N_COMPOP or i.my_type == N_PARBLOCO or i.my_type == N_OP_NAO or \
                i.my_type == N_VETOR_TAMANHO or i.my_type == N_VETOR_ACESSO or i.my_type == N_C_LEIA or \
                i.my_type == N_PARA_TEXTO or i.my_type == N_LOGICABINARIA:
            return self.solve_exp(i)
        else:
            return i

    def scarve_array(self, array, index, mod=None, element=None):
        if array.my_type == N_VETOR:
            c_list = array.get_node_list()
            index = self.solve_icognite(index)
            if index.my_type == N_NUM and index.syn_class == T_INTEIRO:
                index = int(index.syn_obj)
                max_index = len(c_list)-1
                if mod == 'add':
                    if -1 < index <= max_index:
                        c_list[index] = element
                    elif index > max_index:
                        it = index - max_index
                        for i in range(it):
                            if i == it-1:
                                c_list.append(element)
                            else:
                                c_list.append(NL())
                    else:
                        ERROR.throw_error(f'(ErroDeAcesso) Índice fora dos limites do VETOR! Apenas valores positivos '
                                          f'são aceitos em atribuição.')

                elif mod == 'del':
                    if -1 < index <= max_index:
                        c_list.pop(index)
                    else:
                        ERROR.throw_error(f'(ErroDeAcesso) Índice fora dos limites do VETOR! Apenas valores de '
                                          f'0 até o tamanho do vetor -1 são aceitos para leitura.')
                else:
                    if -1 < index <= max_index:
                        return c_list[index]
                    else:
                        ERROR.throw_error(f'(ErroDeAcesso) Índice fora dos limites do VETOR! Apenas valores de '
                                          f'0 até o tamanho do vetor -1 são aceitos para leitura.')
            else:
                ERROR.throw_error(f'(ErroDeTipo) Arrays exigem valores inteiros como índice, mas você forneceu '
                                  f'"{index.syn_class}".')
        else:
            ERROR.throw_error(f'(ErroDeTipo) Tentou acessar índice de um objeto que não é vetor ({array.my_type}).')

    def generate_clone(self, n_array):
        node_list = n_array.get_node_list()
        clone = ARR()
        for each in node_list:
            if each.my_type == N_VETOR:
                s_clone = ARR()
                s_clone.set_node_list(each.get_node_list().copy())
                clone.add_to_node_list(self.generate_clone(s_clone))
            else:
                clone.add_to_node_list(each)
        return clone
