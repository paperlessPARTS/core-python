import attr
import types
from typing import Optional
from paperless.client import PaperlessClient
from paperless.mixins import (
    CreateMixin,
    FromJSONMixin,
    ReadMixin,
    ToJSONMixin,
    PaginatedListMixin,
    ListMixin
)
from paperless.objects.utils import NO_UPDATE
from paperless.json_encoders.integration_actions import IntegrationActionEncoder, ManagedIntegrationEncoder


@attr.s(frozen=False)
class IntegrationAction(FromJSONMixin, ToJSONMixin, ReadMixin, CreateMixin, PaginatedListMixin):
    _json_encoder = IntegrationActionEncoder
    action_type = attr.ib(
        validator=attr.validators.instance_of(str)
    )
    entity_id = attr.ib(
        validator=attr.validators.instance_of(str)
    )
    action_uuid: Optional[str] = attr.ib(
        default=NO_UPDATE,
        validator=attr.validators.optional(attr.validators.instance_of((str, object)))
    )
    status: Optional[str] = attr.ib(
        default=NO_UPDATE,
        validator=attr.validators.optional(attr.validators.instance_of((str, object)))
    )
    status_message: Optional[str] = attr.ib(
        default=NO_UPDATE,
        validator=attr.validators.instance_of((str, object))
    )

    @classmethod
    def construct_list_url(cls):
        return 'integration_actions/public'

    @classmethod
    def construct_create_url(cls):
        return 'integration_actions/public'

    @classmethod
    def construct_get_url(cls):
        return f'integration_actions/public'

    @classmethod
    def construct_patch_url(cls):
        return f'integration_actions/public'

    @classmethod
    def filter(cls, status: Optional[str] = None, action_type: Optional[str] = None):
        return cls.list(params={'status': status, "action_type": action_type})

    def create(self):
        """
        Persist new version of self to Paperless Parts and updates instance with any new data from the creation.
        """
        client = PaperlessClient.get_instance()
        data = self.to_json()
        resp = client.create_resource(self.construct_create_url(), data=data)
        resp_obj = self.from_json(resp)
        keys = filter(
            lambda x: not x.startswith('__') and not x.startswith('_'), dir(resp_obj)
        )
        for key in keys:attr.ib(
            setattr(self, key, getattr(resp_obj, key)))

    def update(self):
        """
        Persists local changes of an existing Paperless Parts resource to Paperless.
        """
        client = PaperlessClient.get_instance()
        data = self.to_json()
        resp = client.update_resource(
            self.construct_patch_url(), self.action_uuid, data=data
        )
        resp_obj = self.from_json(resp)
        # This filter is designed to remove methods, properties, and private data members and only let through the
        # fields explicitly defined in the class definition
        keys = filter(
            lambda x: not x.startswith('__')
            and not x.startswith('_')
            and type(getattr(resp_obj, x)) != types.MethodType
            and (not isinstance(getattr(resp_obj.__class__, x), property) if x in dir(resp_obj.__class__) else True),
            dir(resp_obj),
        )
        for key in keys:
            setattr(self, key, getattr(resp_obj, key))


@attr.s(frozen=False)
class ManagedIntegration(FromJSONMixin, ToJSONMixin, ReadMixin, CreateMixin, ListMixin):
    _json_encoder = ManagedIntegrationEncoder
    erp_name = attr.ib(
        validator=attr.validators.instance_of(str)
    )
    is_active: bool = attr.ib(
        validator=attr.validators.instance_of((bool, object))
    )
    erp_version: Optional[str] = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of((str, object)))
    )
    integrations_version: Optional[str] = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of((str, object)))
    )
    integrations_project_subcommit: Optional[str] = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of((str, object)))
    )
    create_integration_action_after_creating_new_order: Optional[str] = attr.ib(
        validator=attr.validators.instance_of((bool, object))
    )
    id: int = attr.ib(
        default=NO_UPDATE,
        validator=attr.validators.instance_of(int)
    )

    @classmethod
    def construct_list_url(cls):
        return 'managed_integration/public'

    @classmethod
    def construct_create_url(cls):
        return 'managed_integration/public'

    @classmethod
    def construct_get_url(cls):
        return f'managed_integration/public'

    @classmethod
    def construct_patch_url(cls):
        return f'managed_integration/public'

    def create(self):
        """
        Persist new version of self to Paperless Parts and updates instance with any new data from the creation.
        """
        client = PaperlessClient.get_instance()
        data = self.to_json()
        resp = client.create_resource(self.construct_create_url(), data=data)
        resp_obj = self.from_json(resp)
        keys = filter(
            lambda x: not x.startswith('__') and not x.startswith('_'), dir(resp_obj)
        )
        for key in keys:attr.ib(
            setattr(self, key, getattr(resp_obj, key)))

    def update(self):
        """
        Persists local changes of an existing Paperless Parts resource to Paperless.
        """
        client = PaperlessClient.get_instance()
        data = self.to_json()
        resp = client.update_resource(
            self.construct_patch_url(), self.action_uuid, data=data
        )
        resp_obj = self.from_json(resp)
        # This filter is designed to remove methods, properties, and private data members and only let through the
        # fields explicitly defined in the class definition
        keys = filter(
            lambda x: not x.startswith('__')
            and not x.startswith('_')
            and type(getattr(resp_obj, x)) != types.MethodType
            and (not isinstance(getattr(resp_obj.__class__, x), property) if x in dir(resp_obj.__class__) else True),
            dir(resp_obj),
        )
        for key in keys:
            setattr(self, key, getattr(resp_obj, key))