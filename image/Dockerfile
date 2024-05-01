FROM rust:1.77-slim-bookworm AS build

ARG recorder
ARG converter
ARG nf_version=3.2.1
ARG cascadia_code_version=2404.23

RUN cargo install --git https://github.com/asciinema/asciinema --rev $recorder
RUN cargo install --git https://github.com/asciinema/agg --rev $converter

RUN apt update && apt install -y curl unzip
RUN mkdir /fonts

RUN curl -LO https://github.com/googlefonts/noto-emoji/files/15046272/Noto_Emoji.zip \
 && unzip Noto_Emoji.zip -d /NotoEmoji \
 && mv /NotoEmoji/static/* /fonts \
 && rm -rf /NotoEmoji Noto_Emoji.zip

RUN curl -LO https://github.com/microsoft/cascadia-code/releases/download/v$cascadia_code_version/CascadiaCode-$cascadia_code_version.zip \
 && unzip CascadiaCode-$cascadia_code_version.zip -d /CascadiaCode \
 && mv /CascadiaCode/ttf/static/CascadiaMonoNF-*.ttf /fonts \
 && rm -rf /CascadiaCode CascadiaCode-$cascadia_code_version.zip

RUN curl -LO https://github.com/ryanoasis/nerd-fonts/releases/download/v$nf_version/JetBrainsMono.zip \
 && unzip JetBrainsMono.zip -d /JetBrainsMono \
 && mv /JetBrainsMono/JetBrainsMonoNerdFont-*.ttf /fonts \
 && rm -rf /JetBrainsMono JetBrainsMono.zip

RUN curl -LO https://github.com/ryanoasis/nerd-fonts/releases/download/v$nf_version/FiraCode.zip \
 && unzip FiraCode.zip -d /FiraCode \
 && mv /FiraCode/FiraCodeNerdFont-*.ttf /fonts \
 && mv /FiraCode/FiraCodeNerdFontMono-*.ttf /fonts \
 && rm -rf /FiraCode FiraCode.zip

 RUN curl -LO https://github.com/ryanoasis/nerd-fonts/releases/download/v$nf_version/FiraMono.zip \
  && unzip FiraMono.zip -d /FiraMono \
  && mv /FiraMono/FiraMonoNerdFont-*.otf /fonts \
  && rm -rf /FiraMono FiraMono.zip

FROM buildpack-deps:bookworm

COPY --from=build /usr/local/cargo/bin/asciinema /usr/local/bin/asciinema
COPY --from=build /usr/local/cargo/bin/agg /usr/local/bin/agg
COPY --from=build /fonts /root/.local/share/fonts

WORKDIR /root
ENV HOME /root
ENV SHELL /bin/bash
ENV TERM xterm-256color
# https://github.com/termstandard/colors#truecolor-detection
ENV COLORTERM truecolor

RUN apt update && apt install --no-install-recommends -y python3-venv ttf-*

RUN python3 -m venv /root/.internal/venv
RUN /root/.internal/venv/bin/pip install pexpect "tomli; python_version < '3.11'"

COPY record.py /root/.internal/record.py

ENTRYPOINT ["/root/.internal/venv/bin/python", "-u", "/root/.internal/record.py"]
