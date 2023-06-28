import apis.hello, apis.cf, apis.code_runner

class Binder:
    def __init__(self, auto_prefix: str = '$'):
        self.auto_prefix = auto_prefix
        self.maps = [('help', self.instruction_help, 'get help')]
    def bind(self, instruction, func, tips: str = ''):
        self.maps.append((instruction, func, tips))
        self.maps.sort(reverse=True, key=lambda x: x[0])
    def compile(self, message_content: str):
        for instruction, func, _ in self.maps:
            if message_content.startswith(self.auto_prefix + instruction):
                param_str = message_content[len(self.auto_prefix) + len(instruction):].strip()
                return func(param_str)
        return None
    def instruction_help(self, _params):
        instructions = reversed(self.maps)
        ret = ''
        for instr in instructions:
            ret += f'{self.auto_prefix}{instr[0]}'
            if len(instr[2]) == 0:
                ret += '\n'
            else:
                ret += f': {instr[2]}\n'
        if len(ret) == 0:
            return 'No instruction is available.'
        return ret

def make_binder() -> Binder:
    binder = Binder()

    binder.bind('hello', apis.hello.instruction_hello, 'echo hello')
    binder.bind('cf', apis.cf.instruction_cf, 'fetch coming soon CF contests')
    binder.bind('cf1', apis.cf.instruction_cf1, 'fetch one coming soon CF contest')
    binder.bind('cfr', apis.cf.instruction_cfr, 'get CF rating ranks')
    binder.bind('cfc', apis.cf.instruction_cfc, 'get the recent contest participants ranking change')
    binder.bind('run', apis.code_runner.instruction_run, 'run source code')

    return binder

if __name__ == '__main__':
    message_content = input()

    binder = make_binder()

    ret = binder.compile(message_content)

    print(ret)
