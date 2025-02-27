gcloud iam service-accounts create $SERVICE_ACCOUNT --display-name="GCP Permission Change Notification Service Account" --project="$PROJECT_ID"

echo "Service account created. SA email: $SERVICE_ACCOUNT@$PROJECT_ID.iam.gserviceaccount.com"

export SERVICE_ACCOUNT_EMAIL=$SERVICE_ACCOUNT@$PROJECT_ID.iam.gserviceaccount.com


