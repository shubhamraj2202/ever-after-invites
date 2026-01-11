#!/bin/bash
set -e

# --- Step 1: Load Configuration from .env ---
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
else
    echo "Error: .env file not found."
    exit 1
fi

echo "Configuration loaded from .env:"
echo "Project ID: ${PROJECT_ID}"
echo "GitHub Repo: ${GITHUB_REPO}"
echo "GCS Bucket: ${BUCKET_NAME}"
echo "Service Account: ${SERVICE_ACCOUNT}"
echo "Region: ${REGION}"


# --- Step 2: Create the Service Account ---
echo "\nChecking for Service Account..."
if ! gcloud iam service-accounts describe ${SERVICE_ACCOUNT}@${PROJECT_ID}.iam.gserviceaccount.com --project=${PROJECT_ID} --quiet &>/dev/null; then
  echo "Creating Service Account..."
  gcloud iam service-accounts create ${SERVICE_ACCOUNT} \
    --project=${PROJECT_ID} \
    --description="Service Account for GitHub Actions" \
    --display-name="GitHub Actions Runner"
else
  echo "Service Account '${SERVICE_ACCOUNT}' already exists."
fi


# --- Step 3: Create Resources ---
echo "\nChecking for Artifact Registry repository..."
if ! gcloud artifacts repositories describe gatherly-app-repo --project=${PROJECT_ID} --location=${REGION} --quiet &>/dev/null; then
  echo "Creating Artifact Registry repository..."
  gcloud artifacts repositories create gatherly-app-repo \
    --repository-format=docker \
    --location=${REGION} \
    --description="Docker repository for Gatherly app" \
    --project=${PROJECT_ID}
else
  echo "Artifact Registry repository 'gatherly-app-repo' already exists."
fi

echo "\nChecking for Google Cloud Storage bucket..."
if ! gsutil ls -b gs://${BUCKET_NAME} &>/dev/null; then
  echo "Creating Google Cloud Storage bucket..."
  gsutil mb -p ${PROJECT_ID} -l ${REGION} gs://${BUCKET_NAME}
  echo "Making bucket public for website hosting..."
  gsutil iam ch allUsers:objectViewer gs://${BUCKET_NAME}
else
  echo "GCS bucket 'gs://${BUCKET_NAME}' already exists."
fi


# --- Step 4: Grant Permissions to the Service Account ---
echo "\nGranting permissions (these commands are additive and safe to re-run)..."
# Allow pushing to Artifact Registry
gcloud artifacts repositories add-iam-policy-binding gatherly-app-repo \
    --project=${PROJECT_ID} \
    --location=${REGION} \
    --member="serviceAccount:${SERVICE_ACCOUNT}@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/artifactregistry.writer"

# Allow deploying to Cloud Run
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${SERVICE_ACCOUNT}@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/run.admin"

# Allow writing to the GCS bucket
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${SERVICE_ACCOUNT}@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/storage.objectAdmin"

# Allow the service account to be impersonated by the Workload Identity
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${SERVICE_ACCOUNT}@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/iam.serviceAccountUser"


# --- Step 5: Set up Workload Identity Federation ---
echo "\nSetting up Workload Identity Federation..."

# Create the Workload Identity Pool if it doesn't exist
if ! gcloud iam workload-identity-pools describe "github-pool" --project=${PROJECT_ID} --location="global" --quiet &>/dev/null; then
  echo "Creating Workload Identity Pool..."
  gcloud iam workload-identity-pools create "github-pool" \
    --project=${PROJECT_ID} \
    --location="global" \
    --display-name="GitHub Actions Pool"
else
  echo "Workload Identity Pool 'github-pool' already exists."
fi

# Create the Workload Identity Provider if it doesn't exist
if ! gcloud iam workload-identity-pools providers describe "github-provider" --project=${PROJECT_ID} --location="global" --workload-identity-pool="github-pool" --quiet &>/dev/null; then
  echo "Creating Workload Identity Provider..."
  gcloud iam workload-identity-pools providers create-oidc "github-provider" \
    --project=${PROJECT_ID} \
    --location="global" \
    --workload-identity-pool="github-pool" \
    --display-name="GitHub Actions Provider" \
    --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository,attribute.repository_owner=assertion.repository_owner" \
    --issuer-uri="https://token.actions.githubusercontent.com" \
    --attribute-condition="attribute.repository_owner=='shubhamraj2202'"
else
    echo "Workload Identity Provider 'github-provider' already exists."
fi

# Get the full ID of the pool
WORKLOAD_IDENTITY_POOL=$(gcloud iam workload-identity-pools describe "github-pool" \
  --project=${PROJECT_ID} \
  --location="global" \
  --format="value(name)")

# Allow authentications from your GitHub repo to impersonate the Service Account
echo "Binding Service Account to GitHub repository..."
gcloud iam service-accounts add-iam-policy-binding "${SERVICE_ACCOUNT}@${PROJECT_ID}.iam.gserviceaccount.com" \
  --project=${PROJECT_ID} \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/${WORKLOAD_IDENTITY_POOL}/attribute.repository/${GITHUB_REPO}"

echo "\n✅ GCP configuration complete!"