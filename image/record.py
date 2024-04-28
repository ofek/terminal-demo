from __future__ import annotations

import json
import os
import re
import sys
import time

import pexpect

COMMANDS_FILE = '/record/commands.txt'
RECORDING_FILE = '/record/record.cast'
OUTPUT_FILE = '/record/record.gif'
SETUP_COMMAND = 'set -e'
PROMPT = b'\x1b[0;32m\xe2\x9d\xaf \x1b[0m'


def main():
    args = sys.argv[1:]
    if '-h' in args or '--help' in args:
        return os.execvp('agg', ['agg', '--help'])

    shell_commands = []
    with open(COMMANDS_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                shell_commands.append(line.rstrip())

    env_vars = dict(os.environ)
    for arg, env_var, default in (('--rows', 'LINES', 24), ('--cols', 'COLUMNS', 80)):
        try:
            value = int(args[args.index(arg) + 1])
        except (ValueError, IndexError):
            value = os.getenv(env_var, default)
        env_vars[env_var] = str(value)

    shell = pexpect.spawn(
        'asciinema',
        ['rec', RECORDING_FILE, '--overwrite', '-c', os.environ['SHELL']],
        env=env_vars,
        timeout=None,
    )
    shell.setwinsize(int(env_vars['LINES']), int(env_vars['COLUMNS']))

    prompt_pattern = re.escape(PROMPT.decode('utf-8')).encode('utf-8')
    shell.expect(prompt_pattern)
    shell.sendline(SETUP_COMMAND)
    shell.expect(prompt_pattern)

    num_commands = len(shell_commands)
    inside_command = False
    for i, shell_command in enumerate(shell_commands, 1):
        # Best effort attempt at detecting multi-line commands
        continuation_line = (
            # Explicit continuation line
            shell_command.endswith('\\')
            # Next line starts with a space
            or (i != num_commands and shell_commands[i].startswith(' '))
        )
        if continuation_line or inside_command:
            print(shell_command)
        else:
            print(f'{shell_command} ... ', end='', flush=True)

        for char in shell_command:
            shell.send(char.encode('utf-8'))
            time.sleep(0.03)

        shell.send(b'\n')
        time.sleep(0.05)

        if continuation_line:
            inside_command = True
            continue

        try:
            shell.expect(prompt_pattern)
        except pexpect.EOF:
            print('Shell closed unexpectedly')
            return 1

        if not inside_command:
            print('done')

        inside_command = False

    shell.close()

    with open(RECORDING_FILE, 'r', encoding='utf-8') as f:
        recording_lines = f.readlines()

    for i, line in enumerate(recording_lines[1:], 1):
        _, _, text = json.loads(line)
        if text.startswith(SETUP_COMMAND):
            # Remove setup command and prompt
            for _ in range(2):
                del recording_lines[i]

            break

    with open(RECORDING_FILE, 'w', encoding='utf-8') as f:
        f.writelines(recording_lines)

    return os.execvp('agg', ['agg', RECORDING_FILE, OUTPUT_FILE, *args])


if __name__ == '__main__':
    sys.exit(main())
