PROJECT_ID=
CHAT_WEBHOOK_URL=""
MONITORED_PROJECT_IDS=()
REGION=""

#pls don't modify
SERVICE_ACCOUNT=gcp-perm-chge-not-sa
PUBSUB_TOPIC_NAME="gcp_permission_change_logs"
LOG_SINK_NAME="permission_change_logs_to_chat_message"
PUBSUB_SUBSCRIPTION_NAME="permission_change_logs_to_chat_subscription"
HANDLER_GCF_FUNCTION_NAME="permission_change_alerts_to_google_chat"
PUBSUB_TOPIC_ID="pubsub.googleapis.com/projects/$PROJECT_ID/topics/$PUBSUB_TOPIC_NAME"

