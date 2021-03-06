import global_variable


def error(s):
    print('ERROR:  ' + s)

    print()
    text.output()
    print()
    table.output()
    print()
    code.output()
    exit()


def test(s0, s1):
    if s0 != s1:
        error('test,' + s0 + ',' + s1)
    pass


# 处理单个元素 常数 变量
def factor():
    sym = get_sym()
    # print(sym)
    if sym.isdigit():  # 是数字
        code.add('lit', 0, int(sym))  # 数字直接扔上去
    else:  # 否则是标识符
        item = table.get(sym)

        if item['kind'] == 'const':  # 是常量的话
            value = item['value']
            code.add('lit', 0, value)  # 常量的层数留空
        elif item['kind'] == 'var':
            the_level = item['level']
            the_addr = item['address']
            code.add('lod', level - the_level, the_addr)
        else:
            error("factor wrong")


# 处理乘法除法
def term():
    factor()
    while get_next_sym() in ['*', '/']:
        sym = get_sym()
        factor()
        if sym == '*':
            code.add('opr', 0, 4)
        else:
            code.add('opr', 0, 5)


# 表达式解析
def expression():
    # print('exp')
    if get_next_sym() in ['+', '-']:
        sym = get_sym()
        term()  # 处理 term
        if sym == '-':
            code.add('opr', '0', '1')
    else:
        term()

    while get_next_sym() in ['+', '-']:
        sym = get_sym()
        term()
        if sym == '+':
            code.add('opr', 0, 2)  # + 2
        elif sym == '-':
            code.add('opr', 0, 3)  # - 3
        else:
            error('express error')


# 判断语句
def condition():
    if get_next_sym() == 'odd':  # 一元运算符 奇偶判断
        get_sym()
        expression()
        code.add('opr', 0, 6)  # 6 对应 odd
    else:
        expression()
        sym = get_sym()
        expression()
        if sym == '=':
            code.add('opr', 0, 8)
        elif sym == '#':
            code.add('opr', 0, 9)
        elif sym == '<':
            code.add('opr', 0, 10)
        elif sym == '<=':
            code.add('opr', 0, 13)
        elif sym == '>':
            code.add('opr', 0, 12)
        elif sym == '>=':
            code.add('opr', 0, 11)


# 从 begin 到 end （不包括 end 后面的符号）
def statement():
    if get_next_sym() == 'begin':
        test(get_sym(), 'begin')
        statement()
        while get_next_sym() == ';':
            test(get_sym(), ';')
            statement()
        test(get_sym(), 'end')
    elif get_next_sym() == 'if':
        test(get_sym(), 'if')
        condition()
        addr = code.add('jpc', 0, 0)
        test(get_sym(), 'then')
        statement()
        code.set(addr, code.length())
    elif get_next_sym() == 'while':
        test(get_sym(), 'while')
        addr0 = code.length()
        condition()
        addr1 = code.add('jpc', 0, '-')
        test(get_sym(), 'do')
        statement()
        code.add('jmp', 0, addr0)
        code.set(addr1, code.length())
    elif get_next_sym() == 'call':
        test(get_sym(), 'call')
        name = get_sym()
        code.add(
            'cal',
            level - table.get(name)['level'],
            table.get(name)['address']
        )
    elif get_next_sym() == 'write':
        test(get_sym(), 'write')
        test(get_sym(), '(')
        while True:
            expression()
            code.add('opr', 0, 14)  # write
            code.add('opr', 0, 15)  # 换行

            if get_next_sym() != ',':
                break
            test(get_sym(), ',')
        test(get_sym(), ')')
    elif get_next_sym() == 'read':
        test(get_sym(), 'read')
        test(get_sym(), '(')
        while True:
            name = get_sym()
            code.add('opr', 0, 16)  # read bnhr55
            code.add(  # sto
                'sto',
                level - table.get(name)['level'],
                table.get(name)['address']
            )
            if get_next_sym() != ',':
                break
            test(get_sym(), ',')
        test(get_sym(), ')')
    elif table.is_ident(get_next_sym()):
        name = get_sym()
        test(get_sym(), ':=')
        expression()  # 解析语句
        # test(get_sym(), ';')  # 解析完成后应该是分号
        code.add(
            'sto',
            level - table.get(name)['level'],
            table.get(name)['address']
        )


def block():
    global level
    relative_addr = 2  # 相对地址，从 3 开始  0 1 2 被占用
    jmp_addr = code.add('jmp', 0, '-')  # 上来先塞上一个 jmp

    while get_next_sym() in ['const', 'var', 'procedure']:  # 是声明
        sym = get_sym()
        if sym == 'const':
            while True:
                name = get_sym()
                test(get_sym(), '=')
                value = get_sym()
                value = int(value)
                table.add('const', name, value, '-', '-')
                if get_sym() == ';':
                    break
        elif sym == 'var':
            while True:
                name = get_sym()
                relative_addr += 1
                table.add('var', name, '-', level, relative_addr)
                if get_sym() == ';':
                    break
        elif sym == 'procedure':
            name = get_sym()
            test(get_sym(), ';')
            table.add('procedure', name, '-', level, code.length())
            level += 1
            block()
            level -= 1
            test(get_sym(), ';')

    code.set(jmp_addr, code.length())  # 反填跳转地址
    code.add('int', 0, relative_addr + 1)
    statement()
    code.add('opr', 0, 0)  # return


if __name__ == '__main__':
    text = global_variable.Text('./学长_in.txt')  # 读入的文本
    get_sym = text.get_sym
    get_next_sym = text.get_next_sym
    table = global_variable.Table()  # 符号表
    code = global_variable.Code()  # 目标代码表

    level = 0
    block()
    test(get_sym(), '.')  # 吞掉 '.'

    print()
    text.output()
    print()
    table.output()
    print()
    code.output()
