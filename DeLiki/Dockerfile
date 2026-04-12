FROM python:3.14-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /builder
COPY pyproject.toml ./

RUN uv pip install -r pyproject.toml --system --compile-bytecode

FROM python:3.14-slim
COPY --from=builder /usr/local /usr/local

WORKDIR /app

COPY ./src ./src
COPY ./start.sh ./start.sh

RUN chmod +x ./start.sh
ENTRYPOINT ["./start.sh"]

