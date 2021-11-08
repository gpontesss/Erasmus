FROM python:3.9-alpine AS deps

WORKDIR /deps

RUN apk add --no-cache curl && \
    curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py \
    | python -

COPY pyproject.toml poetry.lock ./
RUN $HOME/.poetry/bin/poetry export --without-hashes -f requirements.txt > requirements.txt


FROM python:3.9-alpine

WORKDIR /src

RUN apk add --no-cache build-base musl-dev postgresql-dev git libffi-dev

COPY --from=deps /deps/requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENTRYPOINT [ "sh", "-c" ]
CMD [ "./envtmpl config-template.toml -o config.toml && python -m erasmus" ]
