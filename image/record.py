from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path

import pexpect

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

HOME_DIR = Path.home()
DATA_DIR = Path('/record')
CONFIG_FILE = DATA_DIR / 'config.toml'
RECORDING_FILE = DATA_DIR / 'record.cast'
OUTPUT_FILE = DATA_DIR / 'record.gif'

# Ensure that the shell exits if any command fails
SETUP_COMMAND = 'set -e'

# This appears to be the lowest perceptible keypress delay, any lower doesn't seem to have any effect
DEFAULT_KEYPRESS_DELAY = 0.03

# The time to wait after typing the final character in a command
DEFAULT_COMMAND_WAIT_WITH_KEYPRESS_DELAY = 0.1
DEFAULT_COMMAND_WAIT_WITHOUT_KEYPRESS_DELAY = 0.25

# https://gist.github.com/fnky/458719343aabd01cfb17a3a4f7296797
# The user types: \u001b
# We get: \x1b
# Bash requires: \e
DEFAULT_PROMPT = '\x1b[0;32m❯ \x1b[0m'
BASH_PROMPT_REPLACEMENTS = {'\x1b': '\\e'}


def main():
    args = sys.argv[1:]
    if '-h' in args or '--help' in args:
        return os.execvp('agg', ['agg', '--help'])

    env_vars = dict(os.environ)
    for arg, env_var, default in (('--rows', 'LINES', 24), ('--cols', 'COLUMNS', 80)):
        try:
            value = int(args[args.index(arg) + 1])
        except (ValueError, IndexError):
            value = os.getenv(env_var, default)
        env_vars[env_var] = str(value)

    with CONFIG_FILE.open(encoding='utf-8') as f:
        config = tomllib.loads(f.read())

    prompt = bash_prompt = config.get('prompt', DEFAULT_PROMPT)
    for seq, replacement in BASH_PROMPT_REPLACEMENTS.items():
        bash_prompt = bash_prompt.replace(seq, replacement)

    with (HOME_DIR / '.bashrc').open('a', encoding='utf-8') as f:
        f.write(f'\nPS1="{bash_prompt}"\n')

    shell = pexpect.spawn(
        'asciinema',
        ['rec', str(RECORDING_FILE), '--overwrite', '-c', os.environ['SHELL']],
        env=env_vars,
        timeout=None,
    )
    shell.setwinsize(int(env_vars['LINES']), int(env_vars['COLUMNS']))

    prompt_pattern = re.compile(config.get('prompt-pattern') or re.escape(prompt))
    shell.expect(prompt_pattern)

    # Set up the shell
    shell.sendline(SETUP_COMMAND)
    time.sleep(DEFAULT_COMMAND_WAIT_WITHOUT_KEYPRESS_DELAY)
    shell.expect(prompt_pattern)

    # Allow for a multi-line string or an array of command structures
    commands = (
        [{'text': commands} for commands in config['commands'].splitlines()]
        if 'commands' in config
        else config['command']
    )
    error = False
    for command in commands:
        text = command['text'].strip()
        delay = float(command.get('delay', DEFAULT_KEYPRESS_DELAY))
        if delay:
            for char in text:
                print(char, end='')
                shell.send(char.encode('utf-8'))
                time.sleep(delay)

            wait = float(command.get('wait', DEFAULT_COMMAND_WAIT_WITH_KEYPRESS_DELAY))
        else:
            print(text, end='')
            shell.send(text.encode('utf-8'))
            wait = float(command.get('wait', DEFAULT_COMMAND_WAIT_WITHOUT_KEYPRESS_DELAY))

        print()
        shell.send(b'\n')
        time.sleep(wait)

        try:
            shell.expect(prompt_pattern)
        except pexpect.EOF:
            error = True
            print('Shell exited unexpectedly')
            break

    shell.close()

    with RECORDING_FILE.open(encoding='utf-8') as f:
        recording_lines = f.readlines()

    for i, line in enumerate(recording_lines[1:], 1):
        _, _, contents = json.loads(line)
        if contents.startswith(SETUP_COMMAND):
            # Remove setup command and prompt
            for _ in range(2):
                del recording_lines[i]

            break

    with RECORDING_FILE.open('w', encoding='utf-8') as f:
        f.writelines(recording_lines)

    if not error:
        return os.execvp('agg', ['agg', str(RECORDING_FILE), str(OUTPUT_FILE), *args])

    import subprocess

    subprocess.run(['agg', str(RECORDING_FILE), str(OUTPUT_FILE), *args])
    return 1


if __name__ == '__main__':
    sys.exit(main())
