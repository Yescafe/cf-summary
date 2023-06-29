import json

tokens = None

def get_tokens():
    global tokens
    if not tokens is None:
        return tokens
    # get handles from tokens.json
    with open('tokens.json', 'r+') as fp:
        raw = fp.read()
    tokens = json.loads(raw)
    return tokens
