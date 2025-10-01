#!/usr/bin/env bash
# Create/Update a Cloud Run Job and run it once
# Usage: ./scripts/create_job.sh <PROJECT_ID> <REGION> <REPO> <IMAGE> [TASKS]
set -euo pipefail
PROJECT_ID=${1:?PROJECT_ID}
REGION=${2:-asia-northeast1}
REPO=${3:-jobs-lab}
IMAGE=${4:-prime-lab}
TASKS=${5:-4}

IMAGE_URI="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO}/${IMAGE}:latest"

echo "Using ${IMAGE_URI} (tasks=${TASKS})"

# Create (or update) the job
if gcloud run jobs describe prime-counter --region "${REGION}" >/dev/null 2>&1; then
  gcloud run jobs update prime-counter     --image "${IMAGE_URI}"     --tasks "${TASKS}"     --max-retries 1     --set-env-vars RANGE_MAX=50000,PAUSE_SEC=0.5     --region "${REGION}"
else
  gcloud run jobs create prime-counter     --image "${IMAGE_URI}"     --tasks "${TASKS}"     --max-retries 1     --set-env-vars RANGE_MAX=50000,PAUSE_SEC=0.5     --region "${REGION}"
fi

# Execute once (on-demand)
gcloud run jobs execute prime-counter --region "${REGION}"
echo "Submitted. Check Logs Explorer for 'prime-counter' entries."
