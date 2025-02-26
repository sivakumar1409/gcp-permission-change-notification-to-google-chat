#!/bin/bash


. config.sh


TOPIC_NAME=$PUBSUB_TOPIC_NAME


# Check if the topic exists, if exists delete it and create new one
if gcloud pubsub topics describe "$TOPIC_NAME" --project="$PROJECT_ID" > /dev/null 2>&1; then
 echo "Topic $TOPIC_NAME already exists, deleting it"
 gcloud pubsub topics delete "$TOPIC_NAME" --project="$PROJECT_ID"
fi
  gcloud pubsub topics create "$TOPIC_NAME" --project="$PROJECT_ID"
  echo "Topic $TOPIC_NAME created."

