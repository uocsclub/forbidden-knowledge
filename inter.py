# goes from text formed of s-exprs to tokens
def tokenize(text):
    return text.replace('(', ' ( ')\
               .replace(')', ' ) ')\
               .replace("'", " ' ")\
               .split()


def treeify(tokens):
    return treeify_aux(tokens)[1]

# goes from tokens to a python list
def treeify_aux(tokens, i=0, sublist=False):
    done = False
    acc = []
    while i < len(tokens):
        if tokens[i] == '(':
            i, res = treeify_aux(tokens, i + 1, True)
            acc.append(res)
        elif tokens[i] == ')':
            if not sublist:
                raise Exception(f"unmatched close-paren at token index {i}")
            else:
                return (i + 1, acc)
        else:
            acc.append(sym(tokens[i]))
            i += 1

    if not sublist:
        return (i, acc)
    else:
        raise Exception(f"unbalanced open-paren")

def sym(s):
    try:
        return int(s)
    except ValueError:
        try:
            return float(s)
        except ValueError:
            return s

import operator as op
import math
# an Environment is nothing but a mapping from keys to values which
# has an outer sccope
class Env(dict):
    def __init__(self, init={}, outer=None):
        self.update(init)
        self.outer = outer
    # return the env which contains this key
    def find(self, key):
        return self if (key in self) else\
            (self.outer.find(key) if self.outer else None)


global_env = Env({
    '+': op.add, '-':op.sub, '*':op.mul, '/':op.truediv,
    '>':op.gt, '<':op.lt, '>=':op.ge, '<=':op.le, '=':op.eq,
    'abs':     abs,
    'append':  op.add,
    'apply':   lambda f, args: f(*args),
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
global_env.update(filter(lambda x: x[0].find('__') == -1, vars(math).items()))

def trace(name):
    def trace_aux(func):
        def fun(*args, **kwargs):
            val = func(*args, **kwargs)
            print(f"trace [{name}][{args}][{kwargs}]:", val)
            return val
        return fun
    return trace_aux

class Proc(object):
    def __init__(self, args, body, env, name="lambda"):
        self.args = args
        self.body = body
        self.env = env # This is for closures
        self.__name__ = name
    def __call__(self, *args):
        if len(args) != len(self.args):
            raise Exception("Bad # of arguments passed to ")
        e = Env(dict(zip(self.args, args)), self.env)
        print('body', self.body)
        return [tar(x, e) for x in self.body][-1]

def tar(form, env=global_env):
    if isinstance(form, str): # symbol
        e = env.find(form)
        if e:
            return e[form]
        else:
            raise Exception(f"Unbound symbol {form}")
    elif not isinstance(form, list): # literal
        return form
    # special forms
    elif form[0] == 'if':
        return form[2] if tar(form[1], env) else form[3]
    elif form[0] == 'lambda':
        return Proc(form[1], form[2:], env)
    elif form[0] == 'set!':
        e = env.find(form[1])
        if e:
            e[form[1]] = tar(form[2], env)
        else:
            raise Exception("set! to unbound value")
    elif form[0] == 'define':
        # function definition
        if isinstance(form[1], list):
            raise Exception("not implemented yet")
        elif isinstance(form[1], str):
            env[form[1]] = tar(form[2], env)
            return env[form[1]]
        else:
            raise Exception("trying to define a literal form")
    elif form[0] == 'quote':
        return form[1]
    else:
        proc = tar(form[0], env)
        args = [tar(x, env) for x in form[1:]]
        return proc(*args)

def interp(text):
    vals = [tar(t) for t in treeify(tokenize(text))]
    print('vals', vals)
    return vals[-1]
            
def repl(prompt="sscm> "):
    while True:
        vals = [tar(t) for t in treeify(tokenize(input(prompt)))]
        print("vals", vals)
        print("=>", vals[-1])
