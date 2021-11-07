from sys import argv, stdout
from time import time
start = time()

SEPAEATORS = {
    '(', ')', '[', ']', '{', '}', ',', '\n', ' ', '+', '-', '*', '/', '%', '^', '='
}
DIGITS = {
    '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.'
}

# Keywords
KW_PRINT = 'print'
KW_VAR   = 'store'
KW_DEF   = 'define'
KW_IF    = 'if'
KW_WHEN  = 'when'
KW_END   = 'end'

INSTRUCTIONS = {
    KW_PRINT,
    KW_VAR,
    KW_DEF,
    KW_IF,
    KW_WHEN,
    KW_END
}

# Operators
OP_IS  = 'is'
OP_NOT = 'not'
OPERATORS = {
    OP_IS,
    OP_NOT,
    '<',
    '>'
}


# Tokens
TT_INSTRUCTION = 'INSTRUCTION'
TT_OPERATORS   = 'OPERATORS'
TT_STRING      = 'STRING'
TT_NUM         = 'NUMBER'
TT_IDENTIFYER  = 'IDENTIFYER'
TT_SEPARATOR   = 'SEPARATOR'

variables = {}

def typeof(string=''):
    if string == '': return None
    if string[0] == '"' and string[-1] == '"':
        return 'string'

    for i in string:
        if i not in DIGITS:
            return None
    if string.count('.') <= 1:
        return 'number'


def precedence(op):
    if op == '+' or op == '-':
        return 1
    if op == '*' or op == '/':
        return 2
    return 0

def applyOp(a, b, op):
    if op == '+': return a + b
    if op == '-': return a - b
    if op == '*': return a * b
    if op == '/': return a // b
    if op == OP_IS and a == b or op == OP_NOT and a != b or op == '<' and a < b or op == '>' and a > b:
        return 'true'
    return 'false'

def evaluate(tokens, types):
    values = []
    ops = []

    for i in range(len(tokens)):
        if tokens[i] == '(':
            ops.append(tokens[i])

        elif tokens[i].isdigit():
            values.append(int(tokens[i]))

        elif types[i] == TT_IDENTIFYER:
            var_value = str(variables[tokens[i]])
            values.append(int(var_value) if var_value.isdigit() else var_value)

        elif tokens[i][0] == '"' and tokens[i][-1] == '"':
            values.append(tokens[i][1: -1])


        elif tokens[i] == ')':
            while len(ops) != 0 and ops[-1] != '(':
                val2 = values.pop()
                val1 = values.pop()
                op = ops.pop()
                values.append(applyOp(val1, val2, op))

            ops.pop()

        # Current tok is an operator
        else:
            while len(ops) != 0 and precedence(ops[-1]) >= precedence(tokens[i]):
                val2 = values.pop()
                val1 = values.pop()
                op = ops.pop()
                values.append(applyOp(val1, val2, op))

            ops.append(tokens[i])


    while len(ops) != 0:
        val2 = values.pop()
        val1 = values.pop()
        op = ops.pop()
        values.append(applyOp(val1, val2, op))

    return values[-1]

class Instruction:
    def __init__(self, name='', connectors=[]):
        self.name = name
        self.connectors = connectors

    def __repr__(self):
        return f'{self.name}'


##################################################################################################

def read_file(file_name):
    with open(file_name, 'r', encoding='utf-8') as src:
        content = src.readlines()
        content[-1] += '\n'
        return content

def tokenize(stmt):
    current_tok = ''
    quote_count = 0
    tokens = []
    for i in stmt:

        if i == '"': quote_count += 1
        if i == '#': break

        if i in SEPAEATORS and quote_count % 2 == 0:
            if current_tok != '':
                tokens.append(current_tok)
            if i != ' ' and i != '\n':
                tokens.append(i)

            current_tok = ''
        else: current_tok += i

    return tokens

def parse(tokens):
    types = []
    for i in tokens:
        if i in INSTRUCTIONS:
            types.append(TT_INSTRUCTION)
        elif i in OPERATORS:
            types.append(TT_OPERATORS)
        elif i in SEPAEATORS:
            types.append(TT_SEPARATOR)
        elif typeof(i) == 'string':
            types.append(TT_STRING)
        elif typeof(i) == 'number':
            types.append(TT_NUM)
        else:
            types.append(TT_IDENTIFYER)

    return types

current_line = 0

current_code_level = 0
executing_code_level = 0

def PRINT(object):
    if '\\n' in object:
        for i in object.split("\\n")[:-1]:
            stdout.write(f'{i}\n')
        return
    stdout.write(f'{object}')

def DEFINE(name, connectors):
    pass

def interpret(tokens, types):
    if not types or types[0] != TT_INSTRUCTION:
        return

    global current_code_level, executing_code_level
    if tokens[0] == KW_END:
        if executing_code_level == current_code_level:
            executing_code_level -= 1

        current_code_level -= 1
        return

    if current_code_level != executing_code_level:
        return

    if tokens[0] == KW_PRINT:
        "print EXPR"
        EXPR = str(evaluate(tokens[1:], types[1:]))
        PRINT(EXPR)
        return

    if tokens[0] == KW_VAR:
        "store EXPR VAR"
        EXPR = tokens[1:len(tokens) - 1]
        VAR = tokens[-1]
        variables.update({VAR: evaluate(EXPR, types[1:len(tokens) - 1])})
        return

    if tokens[0] == KW_DEF:
        "define NAME CONNECTORS"

    if tokens[0] == KW_IF:
        "if CONDI"
        CONDI = evaluate(tokens[1:], types[1:])
        current_code_level += 1
        if CONDI == 'true':
            executing_code_level += 1
        return
    if tokens[0] == KW_WHEN:
        "when CONDI"
        CONDI = evaluate(tokens[1:], types[1:])
        current_code_level += 1
        if CONDI == 'true':
            executing_code_level += 1
        return

def main():
    global current_line
    text = read_file(file_name=argv[-1])
    for stmt in text:
        current_line += 1
        tokens = tokenize(stmt)
        try:
            interpret(tokens=tokens, types=parse(tokens))
        except Exception as e:
            stdout.write(f"Exception in line {current_line}: {e}\n")

if __name__ == '__main__':
    main()
    stdout.write(f'\nExecution time: {time() - start} sec')