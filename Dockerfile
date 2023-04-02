FROM python:3.11 as install_deps

RUN mkdir /app
WORKDIR /app

COPY pyproject.toml poetry.lock  /app/

RUN pip install --upgrade pip==23.0.1 setuptools && \
   curl -sSL https://install.python-poetry.org | python - && \
   export PATH="/root/.local/bin:$PATH" && \
   poetry config virtualenvs.create false --local && \
   poetry install && \
   pip list

COPY . /app

FROM python:3.11-slim

EXPOSE 8080

COPY --from=install_deps /usr/local/bin/ /usr/local/bin/
COPY --from=install_deps /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/

WORKDIR /app
COPY .  /app/

RUN chmod +x /app/entrypoint.sh

CMD ["api"]
ENTRYPOINT ["/app/entrypoint.sh"]
