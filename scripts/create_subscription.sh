#!/bin/bash


. config.sh


if gcloud pubsub subscriptions describe "$PUBSUB_SUBSCRIPTION_NAME" --project="$PROJECT_ID" > /dev/null 2>&1; then
  echo "Subscription $PUBSUB_SUBSCRIPTION_NAME already exists. Deleting and recreating..."
  gcloud pubsub subscriptions delete "$PUBSUB_SUBSCRIPTION_NAME" --project="$PROJECT_ID" --quiet
  echo "Subscription $PUBSUB_SUBSCRIPTION_NAME deleted."
fi

# Create the subscription with the Cloud Function as the push endpoint
   gcloud pubsub subscriptions create "$PUBSUB_SUBSCRIPTION_NAME" \
   --topic="$PUBSUB_TOPIC_NAME" \
   --push-endpoint="https://${REGION}-${PROJECT_ID}.cloudfunctions.net/${HANDLER_GCF_FUNCTION_NAME}" \
   --ack-deadline=10 \
   --push-auth-service-account="$SERVICE_ACCOUNT_EMAIL" \
   --project="$PROJECT_ID"

   echo "Subscription $PUBSUB_SUBSCRIPTION_NAME created with push endpoint to Cloud Function $HANDLER_GCF_FUNCTION_NAME."

