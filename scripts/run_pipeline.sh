#!/usr/bin/env bash
# Automated end-to-end execution of the pipeline.
# Fails fast: any stage error aborts the script with a non-zero exit code.
set -euo pipefail

JDBC_URL="${JDBC_URL:-jdbc:postgresql://postgres:5432/asset_db}"
DB_USER="${DB_USER:-asset_user}"
DB_PASSWORD="${DB_PASSWORD:-asset_pass}"
DATA_DIR="${DATA_DIR:-./data}"
OUTPUT_DIR="${OUTPUT_DIR:-./data/export}"
FILENAME="${FILENAME:-consolidated_positions.csv}"

echo "Running full pipeline -> output: ${OUTPUT_DIR}/${FILENAME}"
python -m src.pipeline \
  --jdbc-url "${JDBC_URL}" \
  --user "${DB_USER}" \
  --password "${DB_PASSWORD}" \
  --data-dir "${DATA_DIR}" \
  --output-dir "${OUTPUT_DIR}" \
  --filename "${FILENAME}"
