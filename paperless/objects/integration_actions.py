import types
import urllib.parse as urlparse
from typing import Optional
from urllib.parse import parse_qs

import attr
import dateutil.parser

from paperless.api_mappers import BaseMapper
from paperless.client import PaperlessClient
from paperless.json_encoders.integration_actions import (
    IntegrationActionEncoder,
    ManagedIntegrationEncoder,
)
from paperless.mixins import (
    CreateMixin,
    FromJSONMixin,
    ListMixin,
    ReadMixin,
    ToJSONMixin,
    UpdateMixin,
)
from paperless.objects.utils import NO_UPDATE


@attr.s(frozen=False)
class IntegrationAction(FromJSONMixin, ToJSONMixin, ReadMixin, UpdateMixin):
    _primary_key = 'uuid'
    _list_mapper = BaseMapper
    _list_object_representation = None
    _json_encoder = IntegrationActionEncoder
    type = attr.ib(validator=attr.validators.instance_of(str))
    entity_id = attr.ib(validator=attr.validators.instance_of(str))
    created = attr.ib(
        default=NO_UPDATE,
        validator=attr.validators.optional(attr.validators.instance_of((str, object))),
    )
    updated = attr.ib(
        default=NO_UPDATE,
        validator=attr.validators.optional(attr.validators.instance_of((str, object))),
    )
    uuid: Optional[str] = attr.ib(
        default=NO_UPDATE,
        validator=attr.validators.optional(attr.validators.instance_of((str, object))),
    )
    status: Optional[str] = attr.ib(
        default=NO_UPDATE,
        validator=attr.validators.optional(attr.validators.instance_of((str, object))),
    )
    status_message: Optional[str] = attr.ib(
        default=NO_UPDATE, validator=attr.validators.instance_of((str, object))
    )

    @property
    def created_dt(self):
        return (
            dateutil.parser.parse(self.created)
            if isinstance(self.created, str)
            else None
        )

    @property
    def updated_dt(self):
        return (
            dateutil.parser.parse(self.updated)
            if isinstance(self.updated, str)
            else None
        )

    @classmethod
    def construct_post_url(cls, managed_integration_uuid):
        return 'managed_integrations/public/{}/integration_actions'.format(
            managed_integration_uuid
        )

    @classmethod
    def construct_list_url(cls, managed_integration_uuid):
        return 'managed_integrations/public/{}/integration_actions'.format(
            managed_integration_uuid
        )

    def create(self, managed_integration_uuid):
        """
        Persist new version of self to Paperless Parts and updates instance with any new data from the creation.
        """
        client = PaperlessClient.get_instance()
        data = self.to_json()
        resp = client.create_resource(
            self.construct_post_url(managed_integration_uuid), data=data
        )
        resp_obj = self.from_json(resp)
        keys = filter(
            lambda x: not x.startswith('__')
            and not x.startswith('_')
            and type(getattr(resp_obj, x)) != types.MethodType
            and (
                not isinstance(getattr(resp_obj.__class__, x), property)
                if x in dir(resp_obj.__class__)
                else True
            ),
            dir(resp_obj),
        )
        for key in keys:
            setattr(self, key, getattr(resp_obj, key))

    @classmethod
    def parse_list_response(cls, results):
        """
        An optional overridable method in case your list resources come back in a format other than a json list representation of itself.

        For instance, maybe your list endpoint returns an object including pagination instructions as well as the resource list. You would use this method to strip down to just the resource list.

        :return: json list of your resource
        """
        return results['results']

    @classmethod
    def list(cls, managed_integration_uuid, params=None, pages=None):
        """
        Returns a list of (1) either the minimal representation of this resource as defined by _list_object_representation or (2) a list of this resource.

        :param params: dict of params for your list request
        :param pages: iterable of ints describing the indices of the pages you want (starting from 1)
        :return: [resource]
        """
        client = PaperlessClient.get_instance()
        response = client.get_resource_list(
            cls.construct_list_url(managed_integration_uuid=managed_integration_uuid),
            params=params,
        )
        resource_list = cls.parse_list_response(response)
        while response['next'] is not None:
            next_url = response['next']
            next_query_params = parse_qs(urlparse.urlparse(next_url).query)
            if params is not None:
                next_query_params = {**next_query_params, **params}
            response = client.get_resource_list(
                cls.construct_list_url(
                    managed_integration_uuid=managed_integration_uuid
                ),
                params=next_query_params,
            )
            resource_list.extend(cls.parse_list_response(response))
        if cls._list_object_representation:
            return [
                cls._list_object_representation.from_json(resource)
                for resource in resource_list
            ]
        else:
            return [cls.from_json(resource) for resource in resource_list]

    @classmethod
    def construct_get_url(cls):
        return 'integration_actions/public'

    @classmethod
    def construct_patch_url(cls):
        return 'integration_actions/public'

    @classmethod
    def filter(
        cls,
        managed_integration_uuid: uuid,
        status: Optional[str] = None,
        type: Optional[str] = None,
    ):
        return cls.list(
            managed_integration_uuid=managed_integration_uuid,
            params={'status': status, "type": type},
        )

    @classmethod
    def construct_get_params(cls):
        """
        Optional method to define query params to send along GET request

        :return None or params dict
        """
        return None


@attr.s(frozen=False)
class IntegrationActionDefinition(FromJSONMixin, ToJSONMixin):
    _primary_key = 'uuid'
    _list_object_representation = None
    name = attr.ib(validator=attr.validators.instance_of(str))
    type = attr.ib(validator=attr.validators.instance_of(str))
    uuid: str = attr.ib(
        default=NO_UPDATE, validator=attr.validators.instance_of((str, object))
    )
    related_object_type: Optional[str] = attr.ib(
        default=NO_UPDATE,
        validator=attr.validators.optional(attr.validators.instance_of((str, object))),
    )

    @classmethod
    def list(cls, managed_integration_uuid, params=None, pages=None):
        """
        Returns a list of (1) either the minimal representation of this resource as defined by _list_object_representation or (2) a list of this resource.

        :param params: dict of params for your list request
        :param pages: iterable of ints describing the indices of the pages you want (starting from 1)
        :return: [resource]
        """
        client = PaperlessClient.get_instance()
        response = client.get_resource_list(
            cls.construct_list_url(managed_integration_uuid=managed_integration_uuid),
            params=params,
        )
        resource_list = cls.parse_list_response(response)
        while response['next'] is not None:
            next_url = response['next']
            next_query_params = parse_qs(urlparse.urlparse(next_url).query)
            if params is not None:
                next_query_params = {**next_query_params, **params}
            response = client.get_resource_list(
                cls.construct_list_url(
                    managed_integration_uuid=managed_integration_uuid
                ),
                params=next_query_params,
            )
            resource_list.extend(cls.parse_list_response(response))
        if cls._list_object_representation:
            return [
                cls._list_object_representation.from_json(resource)
                for resource in resource_list
            ]
        else:
            return [cls.from_json(resource) for resource in resource_list]

    @classmethod
    def construct_list_url(cls, managed_integration_uuid):
        return 'managed_integrations/public/{}/integration_action_definitions'.format(
            managed_integration_uuid
        )

    @classmethod
    def parse_list_response(cls, results):
        """
        An optional overridable method in case your list resources come back in a format other than a json list representation of itself.

        For instance, maybe your list endpoint returns an object including pagination instructions as well as the resource list. You would use this method to strip down to just the resource list.

        :return: json list of your resource
        """
        return results['results']


@attr.s(frozen=False)
class ManagedIntegration(
    FromJSONMixin, ToJSONMixin, ReadMixin, CreateMixin, ListMixin, UpdateMixin
):
    _primary_key = 'uuid'
    _json_encoder = ManagedIntegrationEncoder
    erp_name = attr.ib(validator=attr.validators.instance_of(str))
    is_active: bool = attr.ib(validator=attr.validators.instance_of((bool, object)))
    erp_version: Optional[str] = attr.ib(
        default=NO_UPDATE,
        validator=attr.validators.optional(attr.validators.instance_of((str, object))),
    )
    integration_version: Optional[str] = attr.ib(
        default=NO_UPDATE,
        validator=attr.validators.optional(attr.validators.instance_of((str, object))),
    )
    uuid: str = attr.ib(
        default=NO_UPDATE, validator=attr.validators.instance_of((str, object))
    )

    @classmethod
    def construct_list_url(cls):
        return 'managed_integrations/public'

    @classmethod
    def construct_post_url(cls):
        return 'managed_integrations/public'

    @classmethod
    def construct_get_url(cls):
        return f'managed_integrations/public'

    @classmethod
    def construct_patch_url(cls):
        return f'managed_integrations/public'
