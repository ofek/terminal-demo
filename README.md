# terminal-demo

Produce GIFs from shell commands.

## Image creation

Make sure the `terminal-demo` layer comes last in the Dockerfile.

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

```console
$ docker build . -t demo
```

## Usage

You'll need to mount a directory to `/record` in the container that contains a file named `commands.txt` with the commands you want to run. For example:

```
# We are about to test for truecolor support
. /script.sh
```

The serialized recording and output GIF will be saved in this directory as well.

```console
$ docker run --rm -v $(pwd):/record demo
```

<img src="https://raw.githubusercontent.com/ofek/terminal-demo/master/example.gif" alt="Example recording" role="img">
