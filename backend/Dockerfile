ARG PYTHON_VERSION=3.9.10
FROM python:${PYTHON_VERSION}-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV STATIC_URL=/sa/

WORKDIR /app

ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    foodgram

RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

COPY foodgram .

RUN mkdir -p /app/media && chown -R foodgram:foodgram /app/media
RUN python manage.py collectstatic --noinput

USER foodgram

EXPOSE 8000

ENTRYPOINT ["gunicorn"]
CMD ["config.wsgi:application", "--bind=0.0.0.0:8000", "--log-level", "info"]
