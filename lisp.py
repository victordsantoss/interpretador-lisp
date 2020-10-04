from __future__ import division
import math
import operator as op

# Tipos de variáveis

Symbol = str
List = list
Number = (int, float)

# Análise Sintática e Léxica: parse, tokenize e read_from_tokes 

def tokenize(string):
    '''
        A função tokenize recebe como entrada uma string de caracteres; ela adiciona espaços ao redor de cada parênteses e,
        em seguida, chama str.split() para obter uma lista de tokens.
    '''
    return string.replace('(',' ( ').replace(')',' ) ').split()

def atom(token):
    '''
        Responsável por transformar números em números e qualquer outra coisa em um símbolo token.
    '''
    try: 
        return int(token)
    except ValueError:
        try: 
            return float(token)
        except ValueError:
            return Symbol(token)

def read_from_tokens(tokens):
    '''
        Lê uma expressão na forma de sequência de tokens e realiza sua análise
    '''
    if len (tokens) == 0:
        raise SyntaxError('Unexpected EOF reading')
    token = tokens.pop(0)
    if '(' == token:
        L = []
        while tokens[0] != ')':
            L.append(read_from_tokens(tokens))
        tokens.pop(0)
        return L
    elif ')' == token:
        raise SyntaxError('Unexpected')
    else:
        return atom (token)

def parse (program):
    '''
        Lê uma expressão na forma de string e chama as funçõe resposáveis por realizar a análise Léxica e Sintática
    '''
    return read_from_tokens(tokenize(program))

# Ambiente de interpretação Lisp

def standard_env():
    '''
        Um ambiente com alguns procedimentos padrão do Scheme.
    '''
    env = Env()
    env.update(vars(math)) # sin, cos, sqrt, pi, ...
    env.update({
        '+':op.add, 
        '-':op.sub,
        '*':op.mul,
        '/':op.truediv, 
        '>':op.gt,
        '<':op.lt,
        '>=':op.ge,
        '<=':op.le,
        '=':op.eq, 
        'abs':     abs,
        'append':  op.add,  
        'begin':   lambda *x: x[-1],
        'car':     lambda x: x[0],
        'cdr':     lambda x: x[1:], 
        'cons':    lambda x,y: [x] + y,
        'eq?':     op.is_, 
        'equal?':  op.eq, 
        'length':  len, 
        'list':    lambda *x: list(x), 
        'list?':   lambda x: isinstance(x,list), 
        'map':     map,
        'max':     max,
        'min':     min,
        'not':     op.not_,
        'null?':   lambda x: x == [], 
        'number?': lambda x: isinstance(x, Number),   
        'procedure?': callable,
        'round':   round,
        'symbol?': lambda x: isinstance(x, Symbol),
    })

    return env

class Env(dict):
    '''
        Definição de dicionários: estrutura do tipo chave e valor.
    '''
    def __init__(self, parms = (), args = (), outer = None):
        self.update(zip(parms, args))
        self.outer = outer
    def find(self, var):
        "Busca a chave específica dentro do dicionário"
        return self if (var in self) else self.outer.find(var)

global_env = standard_env()

# Interação com o usuário 

def lispstr(exp):
    '''
        Converte um objeto python de volta em uma expressão legível interpretada por Lisp.
    '''
    if isinstance(exp, List):
        return '(' + ' '.join(map(lispstr, exp)) + ')' 
    else:
        return str(exp)

def repl(prompt = 'lis.py> '):
    '''
        Cria um loop para a iserção de expressões no terminal.
    '''
    while True:
        val = eval(parse(input(prompt)))
        if val is not None: 
            print(lispstr(val))

# Procedimentos 

class Procedure(object):
    '''
        Interpreta o procedimento definico pelo usuário.
    '''
    def __init__(self, parms, body, env):
        self.parms, self.body, self.env = parms, body, env
    def __call__(self, *args): 
        return eval(self.body, Env(self.parms, args, self.env))

# Avaliações 

def eval(x, env=global_env):
    '''
        Avalia o tipo da expressão em um determinado ambiente.
    '''
    if isinstance(x, Symbol):      
        return env.find(x)[x]
    elif not isinstance(x, List):  
        return x                
    elif x[0] == 'quote':          
        (_, exp) = x
        return exp
    elif x[0] == 'if':            
        (_, test, conseq, alt) = x
        exp = (conseq if eval(test, env) else alt)
        return eval(exp, env)
    elif x[0] == 'define':         
        (_, var, exp) = x
        env[var] = eval(exp, env)
    elif x[0] == 'set!':          
        (_, var, exp) = x
        env.find(var)[var] = eval(exp, env)
    elif x[0] == 'lambda':        
        (_, parms, body) = x
        return Procedure(parms, body, env)
    else:                         
        proc = eval(x[0], env)
        args = [eval(exp, env) for exp in x[1:]]
        return proc(*args)


if __name__ == "__main__":
    '''
        Inicializa o programa
    '''
    repl ()
