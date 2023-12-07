import json

def get_tokens():
    # get handles from tokens.json
    with open('tokens.json', 'r+') as fp:
        tokens = json.load(fp)
    return tokens
