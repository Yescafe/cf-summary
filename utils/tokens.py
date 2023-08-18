import json

def get_tokens():
    # get handles from tokens.json
    with open('tokens.json', 'r+') as fp:
        raw = fp.read()
    tokens = json.loads(raw)
    return tokens
