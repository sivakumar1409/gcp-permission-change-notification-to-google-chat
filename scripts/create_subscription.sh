#!/bin/bash


. config.sh


if gcloud pubsub subscriptions describe "$PUBSUB_SUBSCRIPTION_NAME" --project="$PROJECT_ID" > /dev/null 2>&1; then
 echo "Subscription $PUBSUB_SUBSCRIPTION_NAME already exists."
else


# Create the subscription with the Cloud Function as the push endpoint
   gcloud pubsub subscriptions create "$PUBSUB_SUBSCRIPTION_NAME" \
   --topic="$PUBSUB_TOPIC_NAME" \
   --push-endpoint="https://${REGION}-${PROJECT_ID}.cloudfunctions.net/${HANDLER_GCF_FUNCTION_NAME}" \
   --ack-deadline=10 \
   --push-auth-service-account="$SERVICE_ACCOUNT" \
   --project="$PROJECT_ID"


   echo "Subscription $PUBSUB_SUBSCRIPTION_NAME created with push endpoint to Cloud Function $HANDLER_GCF_FUNCTION_NAME."
fi

