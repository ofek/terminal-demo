# terminal-demo

Produce GIFs from shell commands using [asciinema](https://github.com/asciinema/asciinema) and [agg](https://github.com/asciinema/agg).

***Table of contents:***

- [Image creation](#image-creation)
- [Usage](#usage)
- [Extra arguments](#extra-arguments)
- [Configuration](#configuration)
  - [Commands](#commands)
  - [Prompt](#prompt)
- [Fonts](#fonts)

## Image creation

Create your own Dockerfile, for example:

```dockerfile
# Preferably set up your environment in a separate layer
FROM ubuntu as setup

RUN <<EOL
cat <<'EOF' > /script.sh
#!/bin/bash
awk 'BEGIN{
  s="/\\/\\/\\/\\/\\"; s=s s s s s s s s;
  for (colnum = 0; colnum<77; colnum++) {
    r = 255-(colnum*255/76);
    g = (colnum*510/76);
    b = (colnum*255/76);
    if (g>255) g = 510-g;
    printf "\033[48;2;%d;%d;%dm", r,g,b;
    printf "\033[38;2;%d;%d;%dm", 255-r,255-g,255-b;
    printf "%s\033[0m", substr(s,colnum+1,1);
  }
  printf "\n";
}'
EOF
EOL
RUN chmod +x /script.sh

FROM ofekmeister/terminal-demo

# Then copy what is necessary from previous layers
COPY --from=setup /script.sh /script.sh
```

Then build the image:

```console
$ docker build . -t demo
```

> [!TIP]
> Although it's recommended to use `ofekmeister/terminal-demo` as the final layer, the image is based on [buildpack-deps](https://hub.docker.com/_/buildpack-deps) so if you want to use it directly as the base layer it should already contain most of the necessary tools and development headers.

## Usage

You'll need to mount a directory to `/record` in the container that contains a TOML file named `config.toml` with the commands you want to run. For example:

```toml
commands = """
# We are about to test for truecolor support
. /script.sh
"""
```

The serialized recording and output GIF will be saved in this directory as well.

```console
$ docker run --rm -v $PWD:/record demo
```

<img src="https://raw.githubusercontent.com/ofek/terminal-demo/master/example.gif" alt="Example recording" role="img">

## Extra arguments

The image entrypoint is a script that will forward all arguments to [agg](https://github.com/asciinema/agg). For example, to see the available options run:

```console
$ docker run --rm -v $PWD:/record demo --help
```

## Configuration

### Commands

You can specify the commands to run as a multi-line string in the `commands` field of the TOML file. For example:

```toml
commands = """
echo "Hello, world!"
echo "Goodbye, world!"
"""
```

If any commands must span multiple lines or you want extra control, you can use an array of command tables with a required `text` field. For example:

```toml
[[command]]
text = "echo 'Hello, world!'"
[[command]]
text = '''
echo How \
    are \
    you, world?
'''
[[command]]
text = "echo 'Goodbye, world!'"
```

Commands have the following optional fields:

Field | Default | Description
--- | --- | ---
`delay` | `0.03` | Seconds between each keypress; set to `0` to disable.
`wait` | `0.1` | Seconds to wait before running the next command. If there is no delay, then the default will instead be `0.25`.

### Prompt

You can change the shell prompt by setting the top-level `prompt` field. The following is the default:

```toml
prompt = "\u001b[0;32m❯ \u001b[0m"
```

If the prompt uses characters that represent placeholders, like the hostname, the session will hang looking for the prompt in order to know when to proceed with the next command. In this case, you can set the `prompt-pattern` field to a regular expression that matches the prompt.

For more information about ANSI escape codes, see [this guide](https://gist.github.com/fnky/458719343aabd01cfb17a3a4f7296797).

## Fonts

The image provides the following fonts that you can use in the `--font-family` [agg](https://github.com/asciinema/agg) option:

- `Cascadia Mono NF` from Cascadia Code [v2404.23](https://github.com/microsoft/cascadia-code/releases/tag/v2404.23)
- `FiraCode Nerd Font Mono` from Nerd Fonts [v3.2.1](https://github.com/ryanoasis/nerd-fonts/releases/tag/v3.2.1)
- `FiraMono Nerd Font` from Nerd Fonts [v3.2.1](https://github.com/ryanoasis/nerd-fonts/releases/tag/v3.2.1)
- `JetBrainsMono NF` from Nerd Fonts [v3.2.1](https://github.com/ryanoasis/nerd-fonts/releases/tag/v3.2.1)

[Monochrome-only](https://github.com/asciinema/agg/tree/89c957608f44d3450335120f89222ac138929f91#emoji) emoji support comes from Google's Noto Emoji [v15.1](https://github.com/googlefonts/noto-emoji/releases/tag/v2.042).
