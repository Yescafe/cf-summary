import services.code_runner as code_runner

def instruction_run(params: str):
    lines = params.split('\n')
    source, lang = '', ''
    for line in lines:
        if line.startswith(r'```'):
            line = line[len(r'```'):]
            if len(line) > 0:
                lang = line
            continue
        source += line + '\n'
    result, compilation_error = code_runner.run_code(source=source, lang=lang)
    if not compilation_error:
        result = 'Compilation error:\n' + result
    ret = f'''Source code (lang: {lang}):
```{lang}
{source}
```
Result:
```
{result}
```
'''
    return ret
