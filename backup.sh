#!/bin/bash

# ========== ADVAITAM — POSTGRESQL BACKUP SCRIPT ==========
# Dumps the PostgreSQL database, compresses it, uploads to S3, and rotates old backups.
#
# Usage:
#   bash backup.sh                     # manual run
#   sudo -u advaitam bash backup.sh    # run as app user
#
# Cron setup (run daily at 2:00 AM):
#   sudo crontab -u advaitam -e
#   Add: 0 2 * * * /home/advaitam/app/backup.sh >> /home/advaitam/app/logs/backup.log 2>&1
#
# Restore a backup:
#   aws s3 cp s3://<bucket>/backups/advaitam_db_2026-03-01_02-00-00.sql.gz /tmp/restore.sql.gz
#   gunzip /tmp/restore.sql.gz
#   sudo -u postgres psql advaitam_db < /tmp/restore.sql
#
# Requirements:
#   - aws CLI installed and configured (or EC2 IAM instance role with s3:PutObject on the bucket)
#   - PGPASSWORD set via .env or environment

set -euo pipefail

# ── Colors ────────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# ── Configuration — edit these or pass as environment variables ───────────────
APP_DIR="${APP_DIR:-/home/advaitam/app}"
ENV_FILE="${APP_DIR}/.env"

# Load .env if it exists (to get DB_* and AWS_* variables)
if [ -f "$ENV_FILE" ]; then
    # Export only the variables we need (avoid exporting everything)
    # mapfile reads each key=value line safely; export handles the rest
    while IFS= read -r line; do
        [[ "$line" =~ ^(DB_NAME|DB_USER|DB_PASSWORD|DB_HOST|DB_PORT|AWS_STORAGE_BUCKET_NAME|AWS_S3_REGION_NAME)= ]] && export "$line"
    done < <(grep -E "^(DB_NAME|DB_USER|DB_PASSWORD|DB_HOST|DB_PORT|AWS_STORAGE_BUCKET_NAME|AWS_S3_REGION_NAME)=" "$ENV_FILE")
fi

DB_NAME="${DB_NAME:-advaitam_db}"
DB_USER="${DB_USER:-advaitam_user}"
DB_PASSWORD="${DB_PASSWORD:-}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
S3_BUCKET="${AWS_STORAGE_BUCKET_NAME:-advaitam-assets}"
S3_REGION="${AWS_S3_REGION_NAME:-us-east-1}"
S3_PREFIX="backups"
BACKUP_DIR="/tmp/advaitam_backups"
RETENTION_DAYS=30   # Keep backups for 30 days in S3
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
BACKUP_FILENAME="${DB_NAME}_${TIMESTAMP}.sql.gz"
BACKUP_PATH="${BACKUP_DIR}/${BACKUP_FILENAME}"
LOG_PREFIX="[BACKUP][$(date '+%Y-%m-%d %H:%M:%S')]"

echo -e "${YELLOW}${LOG_PREFIX} Starting PostgreSQL backup...${NC}"
echo "${LOG_PREFIX} Database: ${DB_NAME} @ ${DB_HOST}:${DB_PORT}"
echo "${LOG_PREFIX} Destination: s3://${S3_BUCKET}/${S3_PREFIX}/${BACKUP_FILENAME}"

# ── Pre-flight checks ─────────────────────────────────────────────────────────
if ! command -v pg_dump &>/dev/null; then
    echo -e "${RED}${LOG_PREFIX} ERROR: pg_dump not found. Install postgresql-client.${NC}"
    exit 1
fi

if ! command -v aws &>/dev/null; then
    echo -e "${RED}${LOG_PREFIX} ERROR: aws CLI not found. Install it: sudo apt install awscli${NC}"
    exit 1
fi

if [ -z "$DB_PASSWORD" ]; then
    echo -e "${RED}${LOG_PREFIX} ERROR: DB_PASSWORD is empty. Set it in .env or environment.${NC}"
    exit 1
fi

# ── Create backup directory ───────────────────────────────────────────────────
mkdir -p "$BACKUP_DIR"

# ── Run pg_dump ───────────────────────────────────────────────────────────────
echo "${LOG_PREFIX} Running pg_dump..."
PGPASSWORD="$DB_PASSWORD" pg_dump \
    --host="$DB_HOST" \
    --port="$DB_PORT" \
    --username="$DB_USER" \
    --dbname="$DB_NAME" \
    --format=plain \
    --no-password \
    --verbose \
    2>>"${APP_DIR}/logs/backup.log" \
  | gzip > "$BACKUP_PATH"

BACKUP_SIZE=$(du -sh "$BACKUP_PATH" | cut -f1)
echo -e "${GREEN}${LOG_PREFIX} Backup created: ${BACKUP_PATH} (${BACKUP_SIZE})${NC}"

# ── Upload to S3 ──────────────────────────────────────────────────────────────
echo "${LOG_PREFIX} Uploading to S3..."
aws s3 cp \
    "$BACKUP_PATH" \
    "s3://${S3_BUCKET}/${S3_PREFIX}/${BACKUP_FILENAME}" \
    --region "$S3_REGION" \
    --storage-class STANDARD_IA \
    --only-show-errors

echo -e "${GREEN}${LOG_PREFIX} Upload complete: s3://${S3_BUCKET}/${S3_PREFIX}/${BACKUP_FILENAME}${NC}"

# ── Remove local temp file ────────────────────────────────────────────────────
rm -f "$BACKUP_PATH"
echo "${LOG_PREFIX} Local temp file removed."

# ── Rotate old S3 backups (delete files older than RETENTION_DAYS) ────────────
echo "${LOG_PREFIX} Rotating backups older than ${RETENTION_DAYS} days from S3..."
CUTOFF_DATE=$(date -d "${RETENTION_DAYS} days ago" +%Y-%m-%d)

aws s3 ls "s3://${S3_BUCKET}/${S3_PREFIX}/" --region "$S3_REGION" | while read -r line; do
    FILE_DATE=$(echo "$line" | awk '{print $1}')
    FILE_NAME=$(echo "$line" | awk '{print $4}')

    if [[ "$FILE_DATE" < "$CUTOFF_DATE" ]] && [[ -n "$FILE_NAME" ]]; then
        echo "${LOG_PREFIX} Deleting old backup: ${FILE_NAME} (dated ${FILE_DATE})"
        aws s3 rm "s3://${S3_BUCKET}/${S3_PREFIX}/${FILE_NAME}" --region "$S3_REGION"
    fi
done

echo -e "${GREEN}${LOG_PREFIX} Backup rotation complete.${NC}"

# ── Verify the latest backup exists in S3 ────────────────────────────────────
LATEST=$(aws s3 ls "s3://${S3_BUCKET}/${S3_PREFIX}/" --region "$S3_REGION" | sort | tail -1 | awk '{print $4}')
echo -e "${GREEN}${LOG_PREFIX} ✅ Latest backup in S3: ${LATEST}${NC}"

echo -e "${GREEN}${LOG_PREFIX} ✅ Backup completed successfully.${NC}"


