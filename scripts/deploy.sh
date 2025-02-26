#!/bin/bash


export PATH=$(pwd)/scripts:$PATH


. config.sh


if [ "$1" == "--only-sink" ]; then
 . deploy_sinks.sh
else
 . enable_apis.sh
 . deploy_function.sh
 . create_pubsub_topic.sh
 . create_subscription.sh
# . create_bigquery_subscription.sh
 . deploy_sinks.sh
fi
