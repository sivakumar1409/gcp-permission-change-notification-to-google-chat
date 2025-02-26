. config.sh




 CHAT_WEBHOOK_URL=$CHAT_WEBHOOK_URL




 gcloud functions deploy ${HANDLER_GCF_FUNCTION_NAME} \
   --runtime=python39 --REGION=${REGION} --trigger-http --project=${PROJECT_ID} \
   --source=./src/. --entry-point=redirect_notification --timeout=1800 --memory=256M \
   --min-instances=0 --max-instances=1 \
   --no-allow-unauthenticated \
   --gen2 \
   --set-env-vars "CHAT_WEBHOOK_URL=${CHAT_WEBHOOK_URL}"






   gcloud functions add-invoker-policy-binding ${HANDLER_GCF_FUNCTION_NAME} \
   --project=${PROJECT_ID} --REGION=${REGION} --member=serviceAccount:$SERVICE_ACCOUNT