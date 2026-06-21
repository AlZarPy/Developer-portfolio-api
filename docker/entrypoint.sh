#!/bin/sh
set -eu

mkdir -p /app/logs /app/data

if [ "${RUN_MIGRATIONS_ON_STARTUP:-false}" = "true" ]; then
  alembic upgrade head
fi

exec "$@"
