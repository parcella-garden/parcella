#!/bin/bash
# Führt die automatisierten Tests aus. Kapselt den kompletten Ablauf,
# damit man sich keine Docker-Befehle merken muss: einfach ausführen mit
#
#   ./run_tests.sh
#
# Startet eine Wegwerf-Testdatenbank, installiert Testabhängigkeiten
# (einmalig, danach gecached), führt pytest im web-Container aus,
# räumt die Testdatenbank IMMER wieder auf – auch wenn Tests fehlschlagen.
set -e

echo "Starte Test-Datenbank..."
docker compose -f docker-compose.dev.yml --profile test up -d db_test

echo "Warte, bis die Test-Datenbank bereit ist..."
until docker compose -f docker-compose.dev.yml exec -T db_test pg_isready -U parcella > /dev/null 2>&1; do
    sleep 1
done

echo "Führe Tests aus..."
set +e  # ab hier: Fehler selbst behandeln, nicht das Skript abbrechen lassen
docker compose -f docker-compose.dev.yml run --rm \
    -e DATABASE_URL=postgresql+asyncpg://parcella:test@db_test:5432/parcella_test \
    web sh -c "pip install -r requirements-dev.txt --break-system-packages --quiet && python -m pytest -v"
TEST_EXIT_CODE=$?
set -e

echo "Räume Test-Datenbank auf..."
docker compose -f docker-compose.dev.yml --profile test down

exit $TEST_EXIT_CODE
