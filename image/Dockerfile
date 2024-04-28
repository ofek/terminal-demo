FROM rust:1.77-slim-bookworm AS build

ARG recorder
ARG converter

RUN cargo install --git https://github.com/asciinema/asciinema --rev $recorder
RUN cargo install --git https://github.com/asciinema/agg --rev $converter

FROM buildpack-deps:bookworm

COPY --from=build /usr/local/cargo/bin/asciinema /usr/local/bin/asciinema
COPY --from=build /usr/local/cargo/bin/agg /usr/local/bin/agg

WORKDIR /root
ENV HOME /root
ENV SHELL /bin/bash
ENV TERM xterm-256color
# https://github.com/termstandard/colors#truecolor-detection
ENV COLORTERM truecolor

RUN apt update && apt install -y python3-venv ttf*
RUN echo 'PS1="\\e[0;32m❯ \\e[0m"' >> /root/.bashrc

RUN python3 -m venv /root/.internal/venv
RUN /root/.internal/venv/bin/pip install pexpect

COPY record.py /root/.internal/record.py

ENTRYPOINT ["/root/.internal/venv/bin/python", "-u", "/root/.internal/record.py"]
