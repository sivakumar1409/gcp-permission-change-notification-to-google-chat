import os
import json
from base64 import b64decode

from httplib2 import Http

CHAT_WEBHOOK_URL = os.environ.get('CHAT_WEBHOOK_URL')


def redirect_notification(request):
    """
    Handles Pub/Sub message, processes log, constructs a chat message, and sends it.

    Args:
        request: The HTTP request object from Cloud Functions.

    Returns:
        A tuple: (status message, HTTP status code).
    """
    try:
        pubsub_message = request.get_json().get('message')
        if not pubsub_message or 'data' not in pubsub_message:
            return "No data in message", 200

        data = b64decode(pubsub_message['data']).decode('utf-8')
        print(f"Received data: {data}")

        log = json.loads(data)
        result = process_log(log)
        message = construct_chat_message(result)
        response = send_to_chat(message)
        print(f"Processing result: {result}")
        print(f"Chat response: {response}")
        return "Notification sent to Google Chat", 200

    except json.JSONDecodeError as json_err:
        error_message = f"Error decoding JSON: {json_err}\nReceived message: {data}"
        print(error_message)
        send_to_chat(error_message)
        return "Error processing message", 500
    except Exception as e:
        error_message = f"An unexpected error occurred: {e}\nReceived message: {data}"
        print(error_message)
        send_to_chat(error_message)
        return "Error processing message", 500


def send_to_chat(message):
    """
    Sends a message to the Google Chat webhook.

    Args:
        message: The message string to send.

    Returns:
        The HTTP response object from the POST request.
    """
    message_headers = {"Content-Type": "application/json; charset=UTF-8"}
    http_obj = Http()
    response = http_obj.request(
        uri=CHAT_WEBHOOK_URL,
        method="POST",
        headers=message_headers,
        body=json.dumps({"text": message}),
    )
    return response


def process_log(log):
    """
    Processes the log message to extract relevant information.

    Args:
        log: The parsed log data (dictionary).

    Returns:
        A dictionary containing the extracted information.
    """
    result = {
        'changed_by': log['protoPayload']['authenticationInfo']['principalEmail'],
        'insert_id': log['insertId']
    }
    resource_type = log['resource']['type']

    if resource_type == 'project':
        result['type'] = 'project'
        result['project_id'] = log['resource']['labels']['project_id']
        result['changes'] = log['protoPayload']['serviceData']['policyDelta']['bindingDeltas']

    elif resource_type == 'bigquery_dataset':
        result['type'] = 'bigquery_resource'
        result['project_id'] = log['resource']['labels']['project_id']
        result['resource_name'] = log['protoPayload']['resourceName']

        if 'tableChange' in log['protoPayload']['metadata']:
            result['changes'] = log['protoPayload']['metadata']['tableChange']['bindingDeltas']
            result['resource_type'] = 'bigquery_table'
        elif 'datasetChange' in log['protoPayload']['metadata']:
            result['changes'] = log['protoPayload']['metadata']['datasetChange']['bindingDeltas']
            result['resource_type'] = 'bigquery_dataset'
        else:
            raise ValueError("Unknown bigquery resource type")

    else:
        result['type'] = 'resource'
        result['project_id'] = log['resource']['labels']['project_id']
        result['resource_type'] = resource_type
        result['resource_name'] = log['protoPayload']['resourceName']
        result['updated_policy'] = log['protoPayload']['request']['policy']['bindings']

    return result


def construct_chat_message(info):
    """
    Constructs a Google Chat message with improved formatting.

    Args:
        info: The processed log information (dictionary).

    Returns:
        The formatted Google Chat message string.
    """
    message_parts = []

    if info['type'] == 'project':
        message_parts.append(f"*Project Level Permissions Updated*")
        message_parts.append(f"Project: `{info['project_id']}`")
        message_parts.append(f"Updated By: `{info['changed_by']}`")
        message_parts.append("\n*Changes:*")
        for change in info['changes']:
            message_parts.append(f"  - Action: `{change['action']}`")
            message_parts.append(f"  - Role: `{change['role']}`")
            message_parts.append(f"  - Members: `{change['member']}`")

    elif info['type'] == 'bigquery_resource':
        message_parts.append(f"*BigQuery Resource Level Permissions Updated*")
        message_parts.append(f"Project: `{info['project_id']}`")
        message_parts.append(f"Updated By: `{info['changed_by']}`")
        message_parts.append(f"Resource Type: `{info['resource_type']}`")
        message_parts.append(f"Resource Name: `{info['resource_name']}`")
        message_parts.append("\n*Changes:*")
        for binding in info['changes']:
            message_parts.append(f"  - Action: `{binding['action']}`")
            message_parts.append(f"  - Role: `{binding['role']}`")
            message_parts.append(f"  - Members: `{binding['member']}`")

    else:
        message_parts.append(f"*Resource Level Permissions Updated*")
        message_parts.append(f"Project: `{info['project_id']}`")
        message_parts.append(f"Updated By: `{info['changed_by']}`")
        message_parts.append(f"Resource Type: `{info['resource_type']}`")
        message_parts.append(f"Resource Name: `{info['resource_name']}`")
        message_parts.append("\n*Latest Permissions After Update:*")
        for binding in info['updated_policy']:
            message_parts.append(f"  - Role: `{binding['role']}`")
            message_parts.append(f"  - Members: `{', '.join(binding['members'])}`")

    message_parts.append(
        f"\n[View Log](https://console.cloud.google.com/logs/query;query=%0AinsertId%3D%22{info['insert_id']}%22?project={info['project_id']})"
    )

    return "\n".join(message_parts)