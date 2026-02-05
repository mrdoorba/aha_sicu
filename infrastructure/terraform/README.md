# Store ICU Infrastructure - Terraform

This directory contains Terraform configuration for GCP resources.

## Prerequisites

1. [Terraform](https://www.terraform.io/downloads) >= 1.0
2. GCP account with billing enabled
3. `gcloud` CLI authenticated

## Setup

### 1. Create a `terraform.tfvars` file

```hcl
project_id = "your-gcp-project-id"
region     = "asia-southeast1"  # or your preferred region
```

### 2. Initialize Terraform

```bash
cd infrastructure/terraform
terraform init
```

### 3. Apply the configuration

```bash
terraform plan    # Review changes
terraform apply   # Apply changes
```

## Resources Created

| Resource | Purpose |
|----------|---------|
| Google Sheets API | Enables API access for brand sync |
| Service Account (`store-icu-gsheets-sync`) | Identity for accessing Google Sheets |
| Service Account Key | Credentials for local development |

## After Terraform Apply

### 1. Get the Service Account email

```bash
terraform output gsheets_service_account_email
```

**Share this email with your Google Sheet** (Viewer access is sufficient).

### 2. Save the Service Account key

```bash
# Create credentials directory
mkdir -p ../../backend/credentials

# Decode and save the key
terraform output -raw gsheets_service_account_key | base64 -d > ../../backend/credentials/gsheets-service-account.json

# Secure the file
chmod 600 ../../backend/credentials/gsheets-service-account.json
```

### 3. Update backend `.env`

```env
GSHEETS_CREDENTIALS_PATH=./credentials/gsheets-service-account.json
GSHEETS_SPREADSHEET_ID=your-spreadsheet-id-from-url
GSHEETS_RANGE=Sheet1!A:Z
```

## Security Notes

- **Never commit** `terraform.tfvars` or `*.tfstate` files
- **Never commit** service account key files
- For production, use [Workload Identity](https://cloud.google.com/kubernetes-engine/docs/how-to/workload-identity) instead of key files
- The `.gitignore` should already exclude these files

## Outputs

| Output | Description |
|--------|-------------|
| `gsheets_service_account_email` | Email to share with Google Sheet |
| `gsheets_service_account_key` | Base64-encoded JSON key (sensitive) |
