#!/usr/bin/env bash
set -euo pipefail
# EXPERIMENTAL. Not run without explicit DEPLOY_ENABLED and operator setup.
: "${GCP_PROJECT_ID:?Set GCP_PROJECT_ID}"
: "${GCP_REGION:?Set GCP_REGION}"
: "${GCP_WIF_PROVIDER:?Set GCP_WIF_PROVIDER}"
: "${GCP_SERVICE_ACCOUNT:?Set GCP_SERVICE_ACCOUNT}"
: "${GCP_ARTIFACT_REPOSITORY:?Set GCP_ARTIFACT_REPOSITORY}"
: "${GCP_CLOUDSQL_DATABASE_URL_SECRET:?Set Cloud SQL DATABASE_URL secret name}"
: "${GCP_JWT_SECRET_NAME:?Set JWT_SECRET secret name}"
: "${GCP_OIDC_TOKEN:?GitLab CI id_token not provided}"
# Explicitly pin to the current tested SHA and avoid direct deployment of GitLab
# registry images which Cloud Run might not be allowed to pull.
printf '%s' "$GCP_OIDC_TOKEN" > /tmp/gcp_credential_subject.jwt
chmod 600 /tmp/gcp_credential_subject.jwt
gcloud iam workload-identity-pools create-cred-config "$GCP_WIF_PROVIDER"   --service-account="$GCP_SERVICE_ACCOUNT"   --output-file=/tmp/gcp_wif.json   --credential-source-file=/tmp/gcp_credential_subject.jwt
export GOOGLE_APPLICATION_CREDENTIALS=/tmp/gcp_wif.json
gcloud auth login --cred-file="$GOOGLE_APPLICATION_CREDENTIALS" --quiet
IMAGE="${GCP_REGION}-docker.pkg.dev/${GCP_PROJECT_ID}/${GCP_ARTIFACT_REPOSITORY}/tenantproof:${CI_COMMIT_SHA}"
gcloud builds submit --project="$GCP_PROJECT_ID" --tag="$IMAGE" .
gcloud run deploy tenantproof --project="$GCP_PROJECT_ID" --region="$GCP_REGION"   --image="$IMAGE" --platform=managed --quiet   --set-env-vars="APP_ENV=production,DEMO_SEED=true"   --set-secrets="DATABASE_URL=${GCP_CLOUDSQL_DATABASE_URL_SECRET}:latest,JWT_SECRET=${GCP_JWT_SECRET_NAME}:latest"
# Service IAM access, Cloud SQL networking, and audience configuration must be
# configured by an operator separately; do not make test secrets public.
