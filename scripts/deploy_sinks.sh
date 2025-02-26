
#!/bin/bash


. config.sh
chmod +x ./scripts/create_log_sink.sh
# List of project IDs
# Loop through each project ID and call the create_log_sink.sh script
for project_id in "${MONITORED_PROJECT_IDS[@]}"; do
 create_log_sink.sh "$project_id"
done
