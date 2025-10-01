#!/usr/bin/env bash
# Create a Cloud Scheduler cron to trigger the job every weekday at 21:00 KST
# Usage: ./scripts/schedule_job.sh <PROJECT_ID> <REGION>
set -euo pipefail
PROJECT_ID=${1:?PROJECT_ID}
REGION=${2:-asia-northeast1}

# Use default compute engine service account for OIDC
SVC_ACCOUNT="$(gcloud iam service-accounts list --format='value(email)' --filter='Compute Engine default service account' --project="${PROJECT_ID}" | head -n1)"

JOB="prime-counter"

gcloud scheduler jobs create http run-${JOB}-cron   --schedule="0 21 * * 1-5"   --time-zone="Asia/Seoul"   --uri="https://run.googleapis.com/apis/run.googleapis.com/v1/namespaces/${PROJECT_ID}/jobs/${JOB}:run"   --oauth-service-account-email="${SVC_ACCOUNT}"   --http-method=POST   --location="${REGION}"
