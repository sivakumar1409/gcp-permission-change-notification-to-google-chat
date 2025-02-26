#!/bin/bash


. config.sh


TOPIC_NAME=$PUBSUB_TOPIC_NAME


# Check if the topic exists
if gcloud pubsub topics describe "$TOPIC_NAME" --project="$PROJECT_ID" > /dev/null 2>&1; then
 echo "Topic $TOPIC_NAME already exists."
else
 # Create the topic if it does not exist
 gcloud pubsub topics create "$TOPIC_NAME" --project="$PROJECT_ID"
 echo "Topic $TOPIC_NAME created."
fi


# gcloud pubsub topics create access_change_logs
