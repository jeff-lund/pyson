import string
from sys import argv

WHITESPACE = " \n\t\v"
SYNTAX = '[]{},:'
QUOTES = '"\''
NUMERICS = '-.0123456789'
FLOAT_CHARACTERS = '.eE'
BOOLS = 'ft'
NULLS = 'n'
ESCAPES = 'bfnrtu\\/\'"'
HEX_DIGITS = '0123456789abcdefABCDEF'
HEX_COUNT = 4
TRUE_LEN = 4
FALSE_LEN = 5
NULL_LEN = 4

def lex_string(s):
    initial = s[0]
    escaped = False
    hexed = 0
    for i in range(1, len(s)):
        if escaped:
            if s[i] in ESCAPES:
                escaped = False
                if s[i] == 'u':
                    hexed = HEX_COUNT
            else:
                break
        elif hexed:
            if s[i] not in HEX_DIGITS:
                break
            else:
                hexed -= 1
        elif s[i] == initial:
            return s[1:i], s[i+1:]
        elif s[i] == '\\':
            escaped = True

    return None, s

def lex_number(s):
    # Keep working on this, need to parse floats correctly
    '''
    period = False
    exponent = False
    i = 0
    # can lead with a negative sign
    if s[i] == '-':
        i += 1
    # can only lead with 1 zero
    if s[i] == '0':
        i += 1
        if i < len(s):
            if s[i] == '.':
                period = True
            elif s[i] in 'eE':
                exponent = True
        else:
            return 0, s[1:]
    '''
    i = 0
    while i < len(s):
        if s[i] not in NUMERICS:
            break
        i += 1

    #if period or exponent:
    if '.' in s[:i] or 'e' in s[:i] or 'E' in s[:i]:
        return float(s[:i]), s[i:]
    else:
        return int(s[:i]), s[i:]

def lex_bool(s):
    if len(s) >= TRUE_LEN and s[:TRUE_LEN] == 'true':
        return True, s[TRUE_LEN:]
    if len(s) >= FALSE_LEN and s[:FALSE_LEN] == 'false':
        return False, s[FALSE_LEN:]
    return None, s

def lex_null(s):
        if len(s) >= NULL_LEN and s[:NULL_LEN] == 'null':
            return True, s[NULL_LEN:]
        return None, s

def lex(s):
    tokens = []
    i = 0
    while s:
        char = s[0]
        if char in WHITESPACE:
            s = s[1:]
            continue

        if char in QUOTES:
            t, s = lex_string(s)
            if t is not None:
                tokens.append(t)
                continue

        if char.isdigit() or char in NUMERICS:
            t, s = lex_number(s)
            if t is not None:
                tokens.append(t)
                continue

        if char in SYNTAX:
            tokens.append(char)
            s = s[1:]
            continue

        if char in BOOLS:
            t, s = lex_bool(s)
            if t is not None:
                tokens.append(t)
                continue

        if char in NULLS:
            t, s = lex_null(s)
            if t is not None:
                tokens.append(None)
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
    if leftover:
        raise Exception("Excess data after parsing")
    return obj

if __name__ == '__main__':
    s = argv[1]
    print(pyson(s))
