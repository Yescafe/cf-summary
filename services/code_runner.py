import os

EXEC = [('cpp', 'test.cpp', 'clang++ -std=c++20 -o runner test.cpp 2> ce.txt && ./runner > output.txt && rm -f runner')]

def run_code(source: str, lang: str):
    exec = None
    for e in EXEC:
        if e[0] == lang:
            exec = e
            break
    with open(e[1], 'w+') as fp:
        fp.write(source)
    os.system(exec[2])
    with open('ce.txt', 'r') as ce_txt:
        ret = ce_txt.read()
        if len(ret) > 0:
            return ret, False
    with open('output.txt', 'r') as output_txt:
        ret = output_txt.read()
    os.system('rm -f ce.txt output.txt test.cpp')
    return ret, True
