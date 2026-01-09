from NODE import *
from ERROR import *


class PARSER:
    def parse(self, nodes):
        _ast = AST()
        _exp_holder = []
        inst_buffer = ''
        _block_holder = []
        _par_holder = []
        _arr_holder = []
        _node_holder = None
        open_block_count = 0
        open_par_count = 0
        open_arr_count = 0
        ln_tracker = 1
        cl_tracker = 0

        for i in range(len(nodes)):
            node = nodes[i]

            cl_tracker += 1
            if node.syn_obj == '\n':
                ln_tracker += 1
                cl_tracker = 0

            if node.syn_obj == '(':
                _par_holder.append(node)
                open_par_count += 1
                continue

            elif node.syn_obj == ')':
                open_par_count -= 1

            if open_par_count > 0:
                if open_arr_count == 0:
                    if node.syn_obj not in '[]':
                        _par_holder.append(node)
                        continue

            else:
                if len(_par_holder) > 0:
                    _par_holder.append(SYM(')'))
                    node = self.stop_for_par(_par_holder)
                    _par_holder.clear()

            if node.syn_obj == '[':
                _arr_holder.append(node)
                open_arr_count += 1
                continue

            elif node.syn_obj == ']':
                open_arr_count -= 1

            if open_arr_count > 0:
                _arr_holder.append(node)
                continue

            else:
                if len(_arr_holder) > 0:
                    _arr_holder.append(SYM(']'))
                    if open_par_count > 0:
                        _par_holder.append(self.stop_for_bra(_arr_holder))
                        continue
                    else:
                        node = self.stop_for_bra(_arr_holder)
                    _arr_holder.clear()

            if (node.syn_obj == ';' or node.syn_obj == '\n' or node.syn_obj == '{') and \
                    inst_buffer != 'create_block':
                if len(_exp_holder) > 0:
                    parsed_exp = self.parse_exp(_exp_holder.copy())
                    _exp_holder.clear()

                    if len(parsed_exp) == 1:
                        if len(_ast.tree) > 0:
                            _ast.tree[-1].set_value(parsed_exp[0])
                        else:
                            ERROR.throw_error(f'(ErroDeOperação) Uso incorreto do operador: '
                                              f'{parsed_exp[0].my_type}.', ln_tracker, cl_tracker)
                    else:
                        ERROR.throw_error('(ErroDeOperação) Você esqueceu algum operador?', ln_tracker, cl_tracker)
                else:
                    if inst_buffer == 'assignment':
                        ERROR.throw_error(f'(ErroDeSintaxe) Era esperada uma expressão após {_ast.tree[-1].my_type}.',
                                          ln_tracker, cl_tracker)
                if node.syn_obj == '{':
                    open_block_count += 1
                    inst_buffer = 'create_block'
                    continue
                else:
                    inst_buffer = ''
                continue

            # print(f'{inst_buffer} with {node.self_write()}')
            if inst_buffer == '':
                if node.my_type == N_CHAVE:
                    if node.syn_obj == 'var':
                        inst_buffer = 'declaracao'
                        _ast.tree.append(DECLARATION('single'))

                    elif node.syn_obj == 'vet':
                        inst_buffer = 'declaracao'
                        _ast.tree.append(DECLARATION('multiple'))

                    elif node.syn_obj == 'del':
                        inst_buffer = 'atribuicao'
                        _ast.tree.append(DELETATION())

                    elif node.syn_obj == 'escreva':
                        inst_buffer = 'atribuicao'
                        _ast.tree.append(CONSOLEWRITE())

                    elif node.syn_obj == 'se':
                        inst_buffer = 'atribuicao'
                        _ast.tree.append(CONDSTATEMENT(node.syn_obj))

                    elif node.syn_obj == 'senaose':
                        inst_buffer = 'atribuicao'
                        _ast.tree.append(CONDSTATEMENT(node.syn_obj))

                    elif node.syn_obj == 'senao':
                        _ast.tree.append(CONDSTATEMENT(node.syn_obj))

                    elif node.syn_obj == 'enquanto':
                        inst_buffer = 'atribuicao'
                        _ast.tree.append(WLOOP())

                    elif node.syn_obj == 'por':
                        inst_buffer = ''
                        _ast.tree.append(FLOOP())
                        continue

                    elif node.syn_obj == 'funcao':
                        inst_buffer = 'declaracao'
                        _ast.tree.append(FUNDEC())

                    else:
                        _node_holder = EXPREAD(node.syn_obj)
                        inst_buffer = 'call'

                else:
                    ERROR.throw_error(f'(ElementoInesperado) O elemento {node.syn_obj} não era esperado nesta posição.',
                                      ln_tracker, cl_tracker)

            elif inst_buffer == 'declaracao':
                if node.my_type == N_CHAVE and node.syn_obj not in palavras_chave:
                    _ast.tree[-1].set_key(node.syn_obj)

                elif node.syn_obj == '=':
                    _ast.tree.append(ASSIGNMENT(EXPREAD(_ast.tree[-1].get_key())))
                    inst_buffer = 'atribuicao'

                elif node.syn_obj == 'de':
                    _exp_holder.append(_ast.tree[-1])
                    _ast.tree.pop()
                    _exp_holder.append(node)
                    inst_buffer = 'atribuicao'

                elif node.my_type == N_PARBLOCO:
                    if _ast.tree[-1].my_type == N_DEC_FUNCAO:
                        _ast.tree[-1].set_parameters(node)
                    else:
                        ERROR.throw_error(f'(ErroDeTipo) Você não pode definir parâmetros para tipos que não são funções.',
                                          ln_tracker, cl_tracker)
                else:
                    ERROR.throw_error(f'(ErroDeNome) Declaração mal nomeada, palavras/caracteres especiais como {node.syn_obj} '
                                      f'não podem fazer parte do nome de variáveis/funções.', ln_tracker, cl_tracker)

            elif inst_buffer == 'call':
                if node.syn_obj == '=':
                    _ast.tree.append(ASSIGNMENT(_node_holder))
                    inst_buffer = 'atribuicao'
                elif node.my_type == N_VETOR:
                    _node_holder = ARRACCESS(_node_holder.get_key(), node)
                elif node.my_type == N_PARBLOCO:
                    _ast.tree.append(FUNCALL(_node_holder.get_key(), node))

            elif inst_buffer == 'create_block':
                if node.syn_obj == '{':
                    open_block_count += 1
                    if open_block_count > 1:
                        _block_holder.append(node)

                elif node.syn_obj == '}':
                    open_block_count -= 1
                    if open_block_count == 0:
                        _block_holder.append(SYM('\n'))
                        block = CODEBLOCK()
                        block.set_block(_block_holder.copy())
                        if len(_ast.tree) > 0 and (_ast.tree[-1].my_type in N_INSTRUCAO_CONDICIONAL + N_LOOP_ENQUANTO +
                                                   N_LOOP_POR + N_DEC_FUNCAO):
                            _ast.tree[-1].set_exeblock(block)
                        else:
                            ERROR.throw_error('(ElementoInesperado) Nenhuma palavra-chave requer um bloco antes de "{".',
                                              ln_tracker, cl_tracker)
                        _block_holder.clear()
                        inst_buffer = ''
                    else:
                        _block_holder.append(node)
                else:
                    _block_holder.append(node)

            elif inst_buffer == 'atribuicao':
                _exp_holder.append(node)

        if len(_block_holder) > 0:
            ERROR.throw_error('(ErroDeSintaxe) Bloco de código não fechado.', ln_tracker, cl_tracker)
        return _ast

    def stop_for_par(self, par_exp):
        parblock = PARBLOCK()  # -((-4 + 3) * (-5))
        par_group = []
        sec_par_hold = []
        open_par_count = 0

        for e in par_exp:
            if e.my_type == N_SIM:
                if e.syn_obj == '(':
                    open_par_count += 1
                    if open_par_count > 1:
                        sec_par_hold.append(e)
                    continue

                elif e.syn_obj == ')':
                    if open_par_count > 1:
                        sec_par_hold.append(e)
                    open_par_count -= 1

                if e.syn_obj in ',)':
                    if open_par_count == 1:
                        if len(sec_par_hold) == 0:
                            c = self.parse_exp(par_group.copy())
                            if len(c) > 1:
                                c.append(SYM(';'))
                                c = self.parse(c)
                            else:
                                c = c[0]
                            parblock.add_to_node_array(c)
                            par_group.clear()
                        else:
                            c_ = self.stop_for_par(sec_par_hold.copy())
                            par_group.append(c_)
                            sec_par_hold.clear()
                        continue

            if open_par_count == 1:
                par_group.append(e)

            elif open_par_count > 1:
                sec_par_hold.append(e)

            else:
                if len(par_group) > 0:
                    c = self.parse_exp(par_group.copy())
                    if len(c) > 1:
                        c.append(SYM(';'))
                        c = self.parse(c)
                    else:
                        c = c[0]
                    parblock.add_to_node_array(c)
                    par_group.clear()
                elif len(sec_par_hold) > 0:
                    parblock.add_to_node_array(self.stop_for_par(sec_par_hold.copy()))
                    sec_par_hold.clear()
                else:
                    parblock.add_to_node_array(NL())
            #  print(parblock.self_write())

        return parblock

    def stop_for_bra(self, arr_exp):
        array = ARR()  # [1, 2, [3, 4], 5, [6]] (nodes)
        arr_group = []
        sec_arr_hold = []
        open_bra_count = 0

        for e in arr_exp:
            if e.my_type == N_SIM:
                if e.syn_obj == '[':
                    open_bra_count += 1
                    if open_bra_count > 1:
                        sec_arr_hold.append(e)
                    continue

                elif e.syn_obj == ']':
                    if open_bra_count > 1:
                        sec_arr_hold.append(e)
                        open_bra_count -= 1
                        continue
                    open_bra_count -= 1

                elif e.syn_obj == ',':
                    if open_bra_count == 1:
                        if len(sec_arr_hold) == 0:
                            c = self.parse_exp(arr_group.copy())[0]
                            array.add_to_node_list(c)
                            arr_group.clear()
                        else:
                            c_ = self.stop_for_bra(sec_arr_hold.copy())
                            array.add_to_node_list(c_)
                            sec_arr_hold.clear()
                        continue

            if open_bra_count == 1:
                arr_group.append(e)

            elif open_bra_count > 1:
                sec_arr_hold.append(e)

            else:
                if len(arr_group) > 0:
                    array.add_to_node_list(self.parse_exp(arr_group.copy())[0])
                    arr_group.clear()
                elif len(sec_arr_hold) > 0:
                    array.add_to_node_list(self.stop_for_bra(sec_arr_hold.copy()))
                    sec_arr_hold.clear()
                else:
                    array.add_to_node_list(NL())

        return array

    @staticmethod
    def parse_exp(node_exp):
        solve = node_exp
        op_groups = ['ler', 'tamanho', 'texto int', '* /', '+ -', '!', '> < == != >= <=', '&& ||', 'para', 'de']
        in_op = False

        holder = []
        for op in op_groups:
            for i in range(len(solve)):
                each = solve[i]
                if each.my_type == N_OPER:
                    if each.syn_obj in op.split(' '):
                        in_op = True
                        bop = None
                        if each.syn_obj == '*':
                            bop = BYNARYOP(MULTIPLICACAO)
                        elif each.syn_obj == '/':
                            bop = BYNARYOP(DIVISAO)
                        elif each.syn_obj == '+':
                            bop = BYNARYOP(SOMA)
                        elif each.syn_obj == '-':
                            if len(holder) == 0:
                                holder.append(NUM(T_INTEIRO, '0'))
                            bop = BYNARYOP(SUBTRACAO)
                        elif each.syn_obj == '==':
                            bop = COMPOP(IGUAL)
                        elif each.syn_obj == '!=':
                            bop = COMPOP(DIFERENTE)
                        elif each.syn_obj == '>':
                            bop = COMPOP(MAIOR)
                        elif each.syn_obj == '<':
                            bop = COMPOP(MENOR)
                        elif each.syn_obj == '>=':
                            bop = COMPOP(MA_OU_IGUAL)
                        elif each.syn_obj == '<=':
                            bop = COMPOP(ME_OU_IGUAL)
                        elif each.syn_obj == '&&':
                            bop = BYNARYLOGIC(E)
                        elif each.syn_obj == '||':
                            bop = BYNARYLOGIC(OU)
                        elif each.syn_obj == 'de':
                            bop = FROMOP()
                        elif each.syn_obj == 'para':
                            bop = TOOP()
                        elif each.syn_obj == '!':
                            bop = NOTOP()
                            holder.append(bop)
                            continue
                        elif each.syn_obj == 'texto':
                            bop = STRINGFY()
                            holder.append(bop)
                            continue
                        elif each.syn_obj == 'inteiro':
                            bop = NUMFY()
                            holder.append(bop)
                            continue
                        elif each.syn_obj == 'tamanho':
                            bop = ARRSIZE()
                            holder.append(bop)
                            continue
                        elif each.syn_obj == 'ler':
                            bop = CONSOLEREAD()
                            holder.append(bop)
                            continue

                        if len(holder) > 0:
                            bop.set_v1(holder[-1])
                            holder[-1] = bop
                        else:
                            ERROR.throw_error(f'(ErroDeOperação) O elemento do lado esquerdo está faltando para {each.syn_obj}.')
                    else:
                        holder.append(each)

                else:
                    if each.my_type == N_VETOR:
                        if len(holder) > 0:
                            if holder[-1].my_type == N_CHAVE:
                                holder[-1] = ARRACCESS(holder[-1].syn_obj, each)
                                continue

                    if in_op:
                        if i < len(solve) and len(holder) > 0:
                            holder[-1].set_v2(each)
                            in_op = False
                        else:
                            ERROR.throw_error(f'(ErroDeOperação) O elemento do lado direito está faltando para {each.syn_obj}.')

                    else:
                        holder.append(each)

            solve = holder.copy()
            holder.clear()

        return solve
