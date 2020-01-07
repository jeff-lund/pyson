import string
from sys import argv

WHITESPACE = " \n\t\v"
SYNTAX = '[]{},:'
QUOTES = '"\''
NUMERICS = '-.0123456789'
BOOLS = 'nft'


def lex_string(i, s):
    # TODO add escape characters
    initial = s[i]
    i += 1
    while i < len(s):
        if s[i] == initial and s[i - 1] != '\\':
                return i
        i += 1
    return None

def lex_number(i, s):
    period = False
    exp = False
    
    if s[i] == '-':
        i += 1
        if i < len(s) and not s[i].isdigit():
            return None
    
    if s[i] == '0':
        if i + 1 < len(s) and s[i + 1] not in 'eE.':
            return i
        i += 1

    while i < len(s):
        if s[i].isdigit():
            i += 1
        elif s[i] == '.' and not period:
            period = True
            i += 1
        elif (s[i] == 'e' or s[i] == 'E') and not exp:
            exp = True
            i += 1
            if s[i] in '-+':
                i += 1
            if not s[i].isdigit():
                # and exponent must be followed by a digit
                # raise a parsing exception here
                return None
        else:
            break
    return i - 1

def lex_bool(i, s):
    diff = len(s) - i
    if diff >= 4:
        if s[i:i+4] == 'true':
            return i + 3
        elif s[i:i+4] == 'null':
            return i + 3
    if diff >= 5:
        if s[i:i+5] == 'false':
            return i + 4
    return None

def lex(s):
    tokens = []
    i = 0
    while i < len(s):
        if s[i] in WHITESPACE:
            i += 1
            continue
        
        if s[i] in QUOTES:
            j = lex_string(i, s)
            if j is not None:
                tokens.append(s[i:j+1])
                i = j + 1
                continue
        
        if s[i].isdigit() or s[i] in NUMERICS:
            j = lex_number(i, s)
            if j is not None:
                t = s[i:j+1]
                if '.' in t or 'e' in t or 'E' in t:
                    t = float(t)
                else:
                    t = int(t)
                tokens.append(t)
                i = j + 1
                continue
        
        if s[i] in SYNTAX:
            tokens.append(s[i])
            i += 1
            continue

        if s[i] in BOOLS:
            j = lex_bool(i, s)
            if j is not None:
                tokens.append(s[i:j+1])
                i = j + 1
                continue
        # no matching tokens found
        raise Exception("Unexpected character at position {}: {}".format(i, s[i]))

    return tokens

def validate_tokens(tokens):
    if not tokens:
        raise Exception("Left curly brace found without matching right curly brace")

def parse_obj(tokens):
    obj = {}
    validate_tokens(tokens)
    t = tokens[0]
    if t == '}':
        return obj, tokens[1:]
    
    while True:
        # get key
        key = t
        if type(key) != str:
            raise Exception("Invalid key value : {}".format(t))
        tokens = tokens[1:]
        validate_tokens(tokens)
        
        # validate delimiter
        t = tokens[0]
        if t != ':':
            raise Exception("Invalid object syntax, missing ':' delimiter between key : value in object. Found: {}".format(t))
        tokens = tokens[1:]
        validate_tokens(tokens)
        
        # get value
        t = tokens[0]
        val, tokens = parse(tokens)
        
        # insert k-v pair into object
        obj[key] = val
        validate_tokens(tokens)
        
        # check for comma for next pair or brace to end object
        t = tokens[0]
        if t == '}':
            return obj, tokens[1:]
        elif t != ',':
            raise Exception("Parsing error. Key-value pairs in object must be comma delimited. Found: {}".format(t))
        else:
            tokens = tokens[1:]

        validate_tokens(tokens)
        t = tokens[0]

def parse_array(tokens):
    arr = []
    if not tokens:
        raise Exception("Left bracket found without matching right bracket: {}".format(tokens))
    
    t = tokens[0]
    if t == ']':
        return arr, tokens[1:]
    
    while True:
        val, tokens = parse(tokens)
        arr.append(val)
        if not tokens:
            raise Exception("Left bracket found without matching right bracket")
        t = tokens[0]
        if t == ']':
            return arr, tokens[1:]
        elif t != ',':
            raise Exception("Expected comma delimited between objects in array, found: {}".format(t))
        else:
            tokens = tokens[1:]
    raise Exception("How did you get here??")

def parse(tokens):
    if not tokens:
        return []
    t = tokens[0]
    if t == '[':
        return parse_array(tokens[1:])
    elif t == '{':
        return parse_obj(tokens[1:])
    else:
        return t, tokens[1:]

def pyson(s):
    tokens = lex(s)
    obj, leftover = parse(tokens)
    return obj, leftover

if __name__ == '__main__':
    s = argv[1]
    print(parse(s))
