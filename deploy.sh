#!/usr/bin/env bash
# ============================================================
# deploy.sh — One-command deploy of CrisisAI to Cloud Run
# Usage: bash deploy.sh <YOUR_GCP_PROJECT_ID>
# ============================================================
set -euo pipefail

PROJECT_ID="${1:-}"
if [[ -z "$PROJECT_ID" ]]; then
  echo "Usage: bash deploy.sh <YOUR_GCP_PROJECT_ID>"
  exit 1
fi

REGION="us-central1"
SERVICE="crisis-ai-api"
REPO="crisis-ai"
SA_NAME="crisis-ai-sa"
SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO}/${SERVICE}:latest"

echo "==> [1/7] Setting project: $PROJECT_ID"
gcloud config set project "$PROJECT_ID"

echo "==> [2/7] Enabling required APIs"
gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  aiplatform.googleapis.com \
  --quiet

echo "==> [3/7] Creating Artifact Registry repository (if not exists)"
gcloud artifacts repositories create "$REPO" \
  --repository-format=docker \
  --location="$REGION" \
  --description="CrisisAI container images" \
  --quiet 2>/dev/null || true

echo "==> [4/7] Creating service account (if not exists)"
gcloud iam service-accounts create "$SA_NAME" \
  --display-name="CrisisAI Cloud Run SA" \
  --quiet 2>/dev/null || true

# Grant Vertex AI user role so the SA can call Gemma 4
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/aiplatform.user" \
  --quiet

echo "==> [5/7] Building and pushing Docker image"
gcloud builds submit \
  --tag "$IMAGE" \
  --project "$PROJECT_ID" \
  .

echo "==> [6/7] Deploying to Cloud Run"
gcloud run deploy "$SERVICE" \
  --image="$IMAGE" \
  --region="$REGION" \
  --platform=managed \
  --allow-unauthenticated \
  --memory=512Mi \
  --cpu=1 \
  --min-instances=0 \
  --max-instances=10 \
  --concurrency=80 \
  --port=8080 \
  --set-env-vars="GOOGLE_CLOUD_PROJECT=${PROJECT_ID},GOOGLE_CLOUD_LOCATION=${REGION}" \
  --service-account="$SA_EMAIL" \
  --quiet

echo "==> [7/7] Done!"
SERVICE_URL=$(gcloud run services describe "$SERVICE" \
  --region="$REGION" --format="value(status.url)")
echo ""
echo "  CrisisAI API is live at: $SERVICE_URL"
echo "  Health check:            $SERVICE_URL/health"
echo "  Dashboard endpoint:      $SERVICE_URL/api/dashboard"
echo "  Interactive docs:        $SERVICE_URL/docs"
echo ""
