#!/bin/bash


if [ -z "$1" ]; then
 echo "Usage: $0 <PROJECT_ID>"
 exit 1
fi


PROJECT_ID=$1


. config.sh


# Check if the sink exists
if gcloud logging sinks describe "$LOG_SINK_NAME" --project="$PROJECT_ID" > /dev/null 2>&1; then
 echo "Sink $LOG_SINK_NAME already exists. Deleting it..."
 gcloud logging sinks delete "$LOG_SINK_NAME" --project="$PROJECT_ID" --quiet
 echo "Sink $LOG_SINK_NAME deleted."
fi


# Create the sink
gcloud logging sinks create "$LOG_SINK_NAME" "$PUBSUB_TOPIC_ID" --log-filter='protoPayload.methodName=~"setIam" OR protoPayload.methodName=~"SetIam"' --project="$PROJECT_ID"
echo "Sink $LOG_SINK_NAME created."


# Get the writer_identity of the sink
writer_identity=$(gcloud logging sinks describe "$LOG_SINK_NAME" --project="$PROJECT_ID" --format="value(writerIdentity)")


# Grant permission to the writer_identity on the topic
gcloud pubsub topics add-iam-policy-binding "$PUBSUB_TOPIC_NAME" \
 --member="$writer_identity" \
 --project="$PROJECT_ID" \
 --role="roles/pubsub.publisher"


echo "Granted pubsub.publisher role to $writer_identity on topic $PUBSUB_TOPIC_ID."