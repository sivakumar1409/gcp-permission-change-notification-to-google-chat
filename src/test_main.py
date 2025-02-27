import unittest
import json
from unittest.mock import patch, MagicMock
import main  # Assuming your code is in main.py


class TestMain(unittest.TestCase):
    @patch('main.Http')
    def test_send_to_chat(self, mock_http):
        """Test sending a message to Google Chat."""
        mock_response = MagicMock()
        mock_response.status = 200
        mock_http.return_value.request.return_value = (mock_response, b'{}')

        result = main.send_to_chat("Test message")

        mock_http.return_value.request.assert_called_once_with(
            uri=main.CHAT_WEBHOOK_URL,
            method="POST",
            headers={"Content-Type": "application/json; charset=UTF-8"},
            body=json.dumps({"text": "Test message"}),
        )
        self.assertEqual(result[0], mock_response)
        self.assertEqual(result[1], b'{}')

    def test_process_log_project(self):
        """Test processing a project-level log."""
        log = {
            "protoPayload": {
                "authenticationInfo": {"principalEmail": "test@example.com"},
                "serviceData": {"policyDelta": {"bindingDeltas": [
                    {"action": "ADD", "role": "roles/viewer", "member": "user:testuser@example.com"}]}},
            },
            "insertId": "test-insert-id",
            "resource": {"type": "project", "labels": {"project_id": "test-project"}},
        }
        expected_result = {
            'changed_by': 'test@example.com',
            'insert_id': 'test-insert-id',
            'type': 'project',
            'project_id': 'test-project',
            'changes': [{'action': 'ADD', 'role': 'roles/viewer', 'member': 'user:testuser@example.com'}]
        }

        result = main.process_log(log)
        self.assertEqual(result, expected_result)

    def test_process_log_bigquery_dataset(self):
        """Test processing a BigQuery dataset log."""
        log = {
            "protoPayload": {
                "authenticationInfo": {"principalEmail": "test@example.com"},
                "resourceName": "project/test-project/dataset/test-dataset",
                "metadata": {"datasetChange": {"bindingDeltas": [
                    {"action": "ADD", "role": "roles/viewer", "member": "user:testuser@example.com"}]}},
            },
            "insertId": "test-insert-id",
            "resource": {"type": "bigquery_dataset", "labels": {"project_id": "test-project"}},
        }
        expected_result = {
            'changed_by': 'test@example.com',
            'insert_id': 'test-insert-id',
            'type': 'bigquery_resource',
            'project_id': 'test-project',
            'resource_name': 'project/test-project/dataset/test-dataset',
            'changes': [{'action': 'ADD', 'role': 'roles/viewer', 'member': 'user:testuser@example.com'}],
            'resource_type': 'bigquery_dataset'
        }

        result = main.process_log(log)
        self.assertEqual(result, expected_result)

    def test_process_log_bigquery_table(self):
        """Test processing a BigQuery table log."""
        log = {
            "protoPayload": {
                "authenticationInfo": {"principalEmail": "test@example.com"},
                "resourceName": "project/test-project/dataset/test-dataset",
                "metadata": {"tableChange": {"bindingDeltas": [
                    {"action": "ADD", "role": "roles/viewer", "member": "user:testuser@example.com"}]}},
            },
            "insertId": "test-insert-id",
            "resource": {"type": "bigquery_dataset", "labels": {"project_id": "test-project"}},
        }
        expected_result = {
            'changed_by': 'test@example.com',
            'insert_id': 'test-insert-id',
            'type': 'bigquery_resource',
            'project_id': 'test-project',
            'resource_name': 'project/test-project/dataset/test-dataset',
            'changes': [{'action': 'ADD', 'role': 'roles/viewer', 'member': 'user:testuser@example.com'}],
            'resource_type': 'bigquery_table'
        }

        result = main.process_log(log)
        self.assertEqual(result, expected_result)

    def test_process_log_resource(self):
        """Test processing a generic resource log."""
        log = {
            "protoPayload": {
                "authenticationInfo": {"principalEmail": "test@example.com"},
                "request": {"policy": {"bindings": [{"role": "roles/test", "members": ["user:test@example.com"]}]}},
                "resourceName": "project/test-project/resource/test-resource"
            },
            "insertId": "test-insert-id",
            "resource": {"type": "test_resource", "labels": {"project_id": "test-project"}},
        }
        expected_result = {
            'changed_by': 'test@example.com',
            'insert_id': 'test-insert-id',
            'type': 'resource',
            'project_id': 'test-project',
            'resource_type': 'test_resource',
            'resource_name': 'project/test-project/resource/test-resource',
            'updated_policy': [{'role': 'roles/test', 'members': ['user:test@example.com']}],
        }

        result = main.process_log(log)
        self.assertEqual(result, expected_result)

    def test_process_log_unknown_bigquery_resource(self):
        """Test processing an unknown BigQuery resource type log."""
        log = {
            "protoPayload": {
                "authenticationInfo": {"principalEmail": "test@example.com"},
                "resourceName": "project/test-project/resource/test-resource",
                "metadata": {},
            },
            "insertId": "test-insert-id",
            "resource": {"type": "bigquery_dataset", "labels": {"project_id": "test-project"}},
        }

        with self.assertRaises(ValueError) as context:
            main.process_log(log)
        self.assertEqual(str(context.exception), "Unknown bigquery resource type")

    def test_construct_chat_message_project(self):
        """Test constructing a chat message for a project-level event."""
        info = {
            'type': 'project',
            'project_id': 'test-project',
            'changed_by': 'test@example.com',
            'insert_id': 'test-insert-id',
            'changes': [
                {'action': 'ADD', 'role': 'roles/viewer', 'member': 'user:testuser@example.com'},
                {'action': 'REMOVE', 'role': 'roles/editor', 'member': 'user:olduser@example.com'}
            ]
        }
        expected_message = """*Project Level Permissions Updated*
Project: `test-project`
Updated By: `test@example.com`

*Changes:*
  - Action: `ADD`
  - Role: `roles/viewer`
  - Members: `user:testuser@example.com`
  - Action: `REMOVE`
  - Role: `roles/editor`
  - Members: `user:olduser@example.com`

[View Log](https://console.cloud.google.com/logs/query;query=%0AinsertId%3D%22test-insert-id%22?project=test-project)"""

        result = main.construct_chat_message(info)
        self.assertEqual(result, expected_message)

    def test_construct_chat_message_bigquery(self):
        """Test constructing a chat message for a BigQuery resource event."""
        info = {
            'type': 'bigquery_resource',
            'project_id': 'test-project',
            'changed_by': 'test@example.com',
            'insert_id': 'test-insert-id',
            'resource_type': 'bigquery_dataset',
            'resource_name': 'project/test-project/dataset/test-dataset',
            'changes': [
                {'action': 'ADD', 'role': 'roles/viewer', 'member': 'user:testuser@example.com'},
                {'action': 'REMOVE', 'role': 'roles/editor', 'member': 'user:olduser@example.com'}
            ]
        }
        expected_message = """*BigQuery Resource Level Permissions Updated*
Project: `test-project`
Updated By: `test@example.com`
Resource Type: `bigquery_dataset`
Resource Name: `project/test-project/dataset/test-dataset`

*Changes:*
  - Action: `ADD`
  - Role: `roles/viewer`
  - Members: `user:testuser@example.com`
  - Action: `REMOVE`
  - Role: `roles/editor`
  - Members: `user:olduser@example.com`

[View Log](https://console.cloud.google.com/logs/query;query=%0AinsertId%3D%22test-insert-id%22?project=test-project)"""

        result = main.construct_chat_message(info)
        self.assertEqual(result, expected_message)

    def test_construct_chat_message_resource(self):
        """Test constructing a chat message for a generic resource event."""
        info = {
            'type': 'resource',
            'project_id': 'test-project',
            'changed_by': 'test@example.com',
            'insert_id': 'test-insert-id',
            'resource_type': 'test_resource',
            'resource_name': 'project/test-project/resource/test-resource',
            'updated_policy': [
                {'role': 'roles/viewer', 'members': ['user:testuser@example.com', 'user:testuser2@example.com']},
                {'role': 'roles/editor', 'members': ['user:olduser@example.com']}
            ]
        }
        expected_message = """*Resource Level Permissions Updated*
Project: `test-project`
Updated By: `test@example.com`
Resource Type: `test_resource`
Resource Name: `project/test-project/resource/test-resource`

*Latest Permissions After Update:*
  - Role: `roles/viewer`
  - Members: `user:testuser@example.com, user:testuser2@example.com`
  - Role: `roles/editor`
  - Members: `user:olduser@example.com`

[View Log](https://console.cloud.google.com/logs/query;query=%0AinsertId%3D%22test-insert-id%22?project=test-project)"""
        result = main.construct_chat_message(info)
        self.assertEqual(result, expected_message)


    @patch('main.send_to_chat')
    @patch('main.json.loads')
    @patch('main.b64decode')
    def test_redirect_notification_json_error(self, mock_b64decode, mock_json_loads, mock_send_to_chat):
        """Test redirect notification with a JSON decoding error."""
        mock_request = MagicMock()
        mock_request.get_json.return_value = {'message': {'data': 'test-data'}}
        mock_b64decode.return_value = b'invalid json'
        mock_json_loads.side_effect = json.JSONDecodeError("Test error", 'invalid json', 0)

        result, status_code = main.redirect_notification(mock_request)

        self.assertEqual(result, "Error processing message")
        self.assertEqual(status_code, 500)

        mock_send_to_chat.assert_called_once()

    @patch('main.send_to_chat')
    def test_redirect_notification_no_data(self, mock_send_to_chat):
        """Test redirect notification with no data."""
        mock_request = MagicMock()
        mock_request.get_json.return_value = {'message': {}}

        result, status_code = main.redirect_notification(mock_request)

        self.assertEqual(result, "No data in message")
        self.assertEqual(status_code, 200)
        mock_send_to_chat.assert_not_called()

    @patch('main.send_to_chat')
    @patch('main.process_log')
    @patch('main.json.loads')
    @patch('main.b64decode')
    def test_redirect_notification_general_error(self, mock_b64decode, mock_json_loads, mock_process_log,
                                                 mock_send_to_chat):
        """Test redirect notification with a general error."""
        mock_request = MagicMock()
        mock_request.get_json.return_value = {'message': {'data': 'test-data'}}
        mock_b64decode.return_value = b'{"test":"log"}'
        mock_json_loads.return_value = {"test": "log"}
        mock_process_log.side_effect = Exception("Generic error")

        result, status_code = main.redirect_notification(mock_request)

        self.assertEqual(result, "Error processing message")
        self.assertEqual(status_code, 500)
        mock_send_to_chat.assert_called_once()


if __name__ == '__main__':
    unittest.main()
