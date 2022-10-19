import datetime
import json
import unittest
from unittest.mock import MagicMock

from paperless.client import PaperlessClient
from paperless.objects.integration_actions import (
    IntegrationAction,
    IntegrationActionDefinition,
    ManagedIntegration,
)


class TestIntegrationAction(unittest.TestCase):
    def setUp(self):
        self.client = PaperlessClient()
        with open(
            'tests/unit/mock_data/managed_integration.json'
        ) as single_integration_data:
            self.mock_managed_integration_json = json.load(single_integration_data)
        with open(
            'tests/unit/mock_data/managed_integration_list.json'
        ) as list_integration_data:
            self.mock_managed_integration_list_json = json.load(list_integration_data)
        with open('tests/unit/mock_data/integration_action.json') as single_action_data:
            self.mock_integration_action_json = json.load(single_action_data)
        with open(
            'tests/unit/mock_data/integration_action_list.json'
        ) as list_actions_data:
            self.mock_integration_action_list_json = json.load(list_actions_data)
        with open(
            'tests/unit/mock_data/integration_action_definition_list.json'
        ) as list_action_definition_data:
            self.mock_integration_action_definition_list = json.load(
                list_action_definition_data
            )
        with open(
            'tests/unit/mock_data/integration_action_list_unwrapped.json'
        ) as list_actions_data:
            self.mock_integration_action_list_unwrapped_json = json.load(
                list_actions_data
            )

    def test_get_managed_integration(self):
        self.client.get_resource = MagicMock(
            return_value=self.mock_managed_integration_json
        )
        managed_integration = ManagedIntegration.get(
            id="712f4343-a29c-4263-be38-3c1694f53439"
        )
        self.assertEqual(
            managed_integration.uuid, "712f4343-a29c-4263-be38-3c1694f53439"
        )
        self.assertEqual(managed_integration.erp_name, "jobboss")
        self.assertEqual(managed_integration.is_active, True)
        self.assertEqual(managed_integration.integration_version, "2.0")

    def test_list_managed_integrations(self):
        self.client.get_resource_list = MagicMock(
            return_value=self.mock_managed_integration_list_json
        )
        managed_integration_list = ManagedIntegration.list()
        self.assertEqual(len(managed_integration_list), 3)
        integration_1 = managed_integration_list[0]
        print(integration_1)
        self.assertEqual(integration_1.uuid, "60e310e2-dfbe-49d1-b406-6726be6516d3")
        self.assertEqual(integration_1.erp_name, "e2")
        self.assertEqual(integration_1.erp_version, "1.5")
        self.assertEqual(integration_1.is_active, False)
        integration_1 = managed_integration_list[-1]
        print(integration_1)
        self.assertEqual(integration_1.uuid, "abcef968-7903-44eb-9037-2033573c6c3e")
        self.assertEqual(integration_1.erp_name, "jobboss")
        self.assertEqual(integration_1.erp_version, "1.0")
        self.assertEqual(integration_1.is_active, True)

    def test_get_integration_action(self):
        self.client.get_resource = MagicMock(
            return_value=self.mock_integration_action_json
        )
        int_act = IntegrationAction.get(id="abc-123")
        self.assertEqual(int_act.type, "export_order")
        self.assertEqual(int_act.uuid, "abc-123")
        self.assertEqual(int_act.status, "queued")
        self.assertEqual(int_act.status_message, None)
        self.assertEqual(int_act.entity_id, "1")
        self.assertIsInstance(int_act.created_dt, datetime.date)
        self.assertIsInstance(int_act.updated_dt, datetime.date)

    def test_list_integration_actions(self):
        self.client.get_resource_list = MagicMock(
            return_value=self.mock_integration_action_list_json
        )
        action_list = IntegrationAction.list(
            managed_integration_uuid=self.mock_managed_integration_json['uuid']
        )
        self.assertEqual(len(action_list), 8)
        action_1 = action_list[0]
        self.assertEqual(action_1.type, "export_order")
        self.assertEqual(action_1.uuid, "20bf3744-625a-49d3-b6a8-5293334e9476")
        self.assertEqual(action_1.status, "completed")
        self.assertEqual(action_1.status_message, None)
        self.assertEqual(action_1.entity_id, "1")
        self.assertIsInstance(action_1.created_dt, datetime.date)
        self.assertIsInstance(action_1.updated_dt, datetime.date)
        action_8 = action_list[-1]
        self.assertEqual(action_8.type, "export_order")
        self.assertEqual(action_8.uuid, "f9e8b33c-2361-47b2-ad23-c9390d488619")
        self.assertEqual(action_8.status, "queued")
        self.assertEqual(action_8.status_message, None)
        self.assertEqual(action_8.entity_id, "99")
        self.assertIsInstance(action_8.created_dt, datetime.date)
        self.assertIsInstance(action_8.updated_dt, datetime.date)

    def test_list_integration_action_definitions(self):
        self.client.get_resource_list = MagicMock(
            return_value=self.mock_integration_action_definition_list
        )
        definition_list = IntegrationActionDefinition.list(
            managed_integration_uuid=self.mock_managed_integration_json['uuid']
        )
        self.assertEqual(len(definition_list), 2)
        definition_1 = definition_list[0]
        self.assertEqual(definition_1.uuid, "82587760-94af-40be-8fdb-4ffa348da001")
        self.assertEqual(definition_1.name, "Export Order")
        self.assertEqual(definition_1.type, "export_order")
        self.assertEqual(definition_1.related_object_type, "order")
        definition_2 = definition_list[-1]
        self.assertEqual(definition_2.uuid, "72587760-94af-40be-8fdb-4ffa348da001")
        self.assertEqual(definition_2.name, "Export Quote")
        self.assertEqual(definition_2.type, "export_quote")
        self.assertEqual(definition_2.related_object_type, None)

    def test_batch_create_integration_actions(self):
        self.client.create_resource = MagicMock(
            return_value=self.mock_integration_action_list_unwrapped_json
        )
        integration_action_list = IntegrationAction.create_many(
            [
                IntegrationAction(type="test_type", entity_id="test_entity_id"),
                IntegrationAction(type="test_type_2", entity_id="test_entity_id_2"),
            ]
        )
        self.assertEqual(integration_action_list, None)

    def test_batch_update_integration_actions(self):
        self.client.patch_resource = MagicMock(
            return_value=self.mock_integration_action_list_unwrapped_json
        )
        integration_action_list = IntegrationAction.update_many(
            [
                IntegrationAction(type="test_type", entity_id="test_entity_id"),
                IntegrationAction(type="test_type_2", entity_id="test_entity_id_2"),
            ]
        )
        self.assertEqual(integration_action_list, None)
