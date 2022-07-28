from decimal import Decimal
from types import MethodType, SimpleNamespace
from typing import Dict, List, Optional, Union

import attr

from paperless.api_mappers.quotes import QuoteDetailsMapper
from paperless.client import PaperlessClient
from paperless.json_encoders.quotes import QuoteEncoder
from paperless.manager import BaseManager, GetManagerMixin
from paperless.mixins import (
    FromJSONMixin,
    ListMixin,
    ToDictMixin,
    ToJSONMixin,
    UpdateMixin,
)
from paperless.objects.components import BaseOperation
from paperless.objects.utils import NO_UPDATE

from .common import Money, Salesperson
from .components import AssemblyMixin, BaseComponent
from .utils import (
    convert_cls,
    convert_dictionary,
    convert_iterable,
    numeric_validator,
    optional_convert,
)


@attr.s(frozen=True)
class CostingVariablePayload:
    value: Optional[Union[float, int, str, bool]] = attr.ib()
    # NOTE: row will only not be None if parent QuoteCostingVariable.variable_class == 'drop_down'
    row: Optional[Dict[str, Union[float, int, str, bool]]] = attr.ib()
    # NOTE: options will only not be None if parent QuoteCostingVariable.variable_class == 'drop_down'
    options: Optional[List[Union[float, int, str]]] = attr.ib()


@attr.s(frozen=True)
class QuoteCostingVariable:
    value = attr.ib()
    label: str = attr.ib(validator=attr.validators.instance_of(str))
    quantity_specific: bool = attr.ib()
    quantities: Dict[int, CostingVariablePayload] = attr.ib(
        converter=convert_dictionary(CostingVariablePayload)
    )
    variable_class: str = attr.ib(attr.validators.instance_of(str))
    value_type: str = attr.ib(attr.validators.instance_of(str))


@attr.s(frozen=True)
class QuoteOperation(BaseOperation):
    costing_variables: List[QuoteCostingVariable] = attr.ib(
        converter=convert_iterable(QuoteCostingVariable)
    )

    def get_variable_for_qty(
        self, label: str, qty: int
    ) -> Optional[CostingVariablePayload]:
        """Return the value of the variable with the specified label for the given quantity or None if
        that variable does not exist."""
        return (
            {cv.label: cv.quantities for cv in self.costing_variables}
            .get(label, dict())
            .get(qty, None)
        )

    # TODO: deprecate this
    def get_variable(self, label):
        """Return the value of the variable with the specified label or None if
        that variable does not exist."""
        return {cv.label: cv.value for cv in self.costing_variables}.get(label, None)


@attr.s(frozen=False)
class AddOnQuantity:
    price: Optional[Money] = attr.ib(
        converter=optional_convert(Money),
        validator=attr.validators.optional(attr.validators.instance_of(Money)),
    )
    manual_price: Optional[Money] = attr.ib(
        converter=optional_convert(Money),
        validator=attr.validators.optional(attr.validators.instance_of(Money)),
    )
    quantity: int = attr.ib(validator=attr.validators.instance_of(int))


@attr.s(frozen=False)
class AddOn:
    is_required: bool = attr.ib(validator=attr.validators.instance_of(bool))
    name: str = attr.ib(validator=attr.validators.instance_of(str))
    notes: Optional[str] = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of(str))
    )
    quantities: List[AddOnQuantity] = attr.ib(converter=convert_iterable(AddOnQuantity))
    costing_variables: List[QuoteCostingVariable] = attr.ib(
        converter=convert_iterable(QuoteCostingVariable)
    )

    def get_variable_for_qty(
        self, label: str, qty: int
    ) -> Optional[CostingVariablePayload]:
        """Return the value of the variable with the specified label for the given quantity or None if
        that variable does not exist."""
        return (
            {cv.label: cv.quantities for cv in self.costing_variables}
            .get(label, dict())
            .get(qty, None)
        )


@attr.s(frozen=False)
class Expedite:
    id: int = attr.ib(validator=attr.validators.instance_of(int))
    lead_time: int = attr.ib(validator=attr.validators.instance_of(int))
    markup: float = attr.ib(validator=numeric_validator)
    unit_price: Money = attr.ib(
        converter=Money, validator=attr.validators.instance_of(Money)
    )
    total_price: Money = attr.ib(
        converter=Money, validator=attr.validators.instance_of(Money)
    )


@attr.s(frozen=False)
class Quantity:
    id: int = attr.ib(validator=attr.validators.instance_of(int))
    quantity: int = attr.ib(validator=attr.validators.instance_of(int))
    markup_1_price: Optional[Money] = attr.ib(
        converter=optional_convert(Money),
        validator=attr.validators.optional(attr.validators.instance_of(Money)),
    )
    markup_1_name: Optional[str] = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of(str))
    )
    markup_2_price: Optional[Money] = attr.ib(
        converter=optional_convert(Money),
        validator=attr.validators.optional(attr.validators.instance_of(Money)),
    )
    markup_2_name: Optional[str] = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of(str))
    )
    unit_price: Money = attr.ib(
        converter=Money, validator=attr.validators.instance_of(Money)
    )
    total_price: Money = attr.ib(
        converter=Money, validator=attr.validators.instance_of(Money)
    )
    total_price_with_required_add_ons: Money = attr.ib(
        converter=Money, validator=attr.validators.instance_of(Money)
    )
    lead_time: int = attr.ib(validator=attr.validators.instance_of(int))
    expedites: List[Expedite] = attr.ib(converter=convert_iterable(Expedite))
    is_most_likely_won_quantity: bool = attr.ib(
        validator=attr.validators.instance_of(bool)
    )
    most_likely_won_quantity_percent: Optional[int] = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of(int))
    )


@attr.s(frozen=False)
class QuoteComponent(BaseComponent):
    add_ons: List[AddOn] = attr.ib(converter=convert_iterable(AddOn))
    material_operations: List[QuoteOperation] = attr.ib(
        converter=convert_iterable(QuoteOperation)
    )
    shop_operations: List[QuoteOperation] = attr.ib(
        converter=convert_iterable(QuoteOperation)
    )
    quantities: List[Quantity] = attr.ib(converter=convert_iterable(Quantity))


@attr.s(frozen=False)
class Metrics:
    order_revenue_all_time: Money = attr.ib(
        converter=Money, validator=attr.validators.instance_of(Money)
    )
    order_revenue_last_thirty_days: Money = attr.ib(
        converter=Money, validator=attr.validators.instance_of(Money)
    )
    quotes_sent_all_time: int = attr.ib(validator=attr.validators.instance_of(int))
    quotes_sent_last_thirty_days: int = attr.ib(
        validator=attr.validators.instance_of(int)
    )


@attr.s(frozen=False)
class Company:
    id: Optional[int] = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of(int))
    )
    notes: Optional[str] = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of(str))
    )
    metrics: Metrics = attr.ib(converter=convert_cls(Metrics))
    business_name: str = attr.ib(validator=attr.validators.instance_of(str))
    erp_code: str = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of(str))
    )


@attr.s(frozen=False)
class Account:
    id: int = attr.ib(validator=attr.validators.instance_of(int))
    notes: Optional[str] = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of(str))
    )
    name: str = attr.ib(validator=attr.validators.instance_of(str))
    erp_code: str = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of(str))
    )


@attr.s(frozen=False)
class Customer:
    id: Optional[int] = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of(int))
    )
    first_name: str = attr.ib(validator=attr.validators.instance_of(str))
    last_name: str = attr.ib(validator=attr.validators.instance_of(str))
    email: str = attr.ib(validator=attr.validators.instance_of(str))
    notes: Optional[str] = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of(str))
    )
    company: Company = attr.ib(converter=convert_cls(Company))


@attr.s(frozen=False)
class Contact:
    id: int = attr.ib(validator=attr.validators.instance_of(int))
    first_name: str = attr.ib(validator=attr.validators.instance_of(str))
    last_name: str = attr.ib(validator=attr.validators.instance_of(str))
    email: str = attr.ib(validator=attr.validators.instance_of(str))
    notes: Optional[str] = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of(str))
    )
    phone: Optional[str] = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of(str))
    )
    phone_ext: Optional[str] = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of(str))
    )
    account: Account = attr.ib(converter=convert_cls(Account))


@attr.s(frozen=False)
class QuoteItem(AssemblyMixin):
    id: int = attr.ib(validator=attr.validators.instance_of(int))
    components: List[QuoteComponent] = attr.ib(
        converter=convert_iterable(QuoteComponent)
    )
    type: str = attr.ib(validator=attr.validators.instance_of(str))
    position: int = attr.ib(validator=attr.validators.instance_of(int))
    export_controlled: bool = attr.ib(validator=attr.validators.instance_of(bool))
    component_ids: List[int] = attr.ib(validator=attr.validators.instance_of(list))
    private_notes: Optional[str] = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of(str))
    )
    public_notes: Optional[str] = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of(str))
    )

    @property
    def root_component(self):
        try:
            return [c for c in self.components if c.is_root_component][0]
        except IndexError:
            raise ValueError('Order item has no root component')

    def get_component(self, component_id: int) -> QuoteComponent:
        for component in self.components:
            if component.id == component_id:
                return component


@attr.s(frozen=False)
class ParentQuote:
    id: int = attr.ib(validator=attr.validators.instance_of(int))
    number: int = attr.ib(validator=attr.validators.instance_of(int))
    status: str = attr.ib(validator=attr.validators.instance_of(str))


@attr.s(frozen=False)
class ParentSupplierOrder:
    id: int = attr.ib(validator=attr.validators.instance_of(int))
    number: int = attr.ib(validator=attr.validators.instance_of(int))
    status: str = attr.ib(validator=attr.validators.instance_of(str))


@attr.s(frozen=False)
class RequestForQuote:
    id: int = attr.ib(validator=attr.validators.instance_of(int))
    email: str = attr.ib(validator=attr.validators.instance_of(str))
    first_name: str = attr.ib(validator=attr.validators.instance_of(str))
    last_name: str = attr.ib(validator=attr.validators.instance_of(str))
    business_name: str = attr.ib(validator=attr.validators.instance_of(str))
    phone: Optional[str] = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of(str))
    )
    phone_ext: Optional[str] = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of(str))
    )
    requested_delivery_date: Optional[str] = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of(str))
    )
    contact_info_conflict: bool = attr.ib(validator=attr.validators.instance_of(bool))


@attr.s(frozen=False)
class Quote(
    FromJSONMixin, ListMixin, ToDictMixin, UpdateMixin, ToJSONMixin
):  # We don't use ReadMixin here because quotes are identified uniquely by (number, revision) pairs
    STATUSES = SimpleNamespace(
        OUTSTANDING='outstanding', CANCELLED='cancelled', TRASH='trash', LOST='lost'
    )
    _primary_key = 'number'

    _mapper = QuoteDetailsMapper
    _json_encoder = QuoteEncoder

    id: int = attr.ib(validator=attr.validators.instance_of(int))
    number: int = attr.ib(validator=attr.validators.instance_of(int))
    revision_number: Optional[int] = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of(int))
    )
    sales_person: Salesperson = attr.ib(converter=convert_cls(Salesperson))
    salesperson: Salesperson = attr.ib(converter=convert_cls(Salesperson))
    estimator: Salesperson = attr.ib(converter=convert_cls(Salesperson))
    contact: Contact = attr.ib(converter=convert_cls(Contact))
    customer: Customer = attr.ib(converter=convert_cls(Customer))
    tax_rate: Optional[Decimal] = attr.ib(
        converter=optional_convert(Decimal),
        validator=attr.validators.optional(attr.validators.instance_of(Decimal)),
    )
    tax_cost: Optional[Money] = attr.ib(
        converter=optional_convert(Money),
        validator=attr.validators.optional(attr.validators.instance_of(Money)),
    )
    private_notes: Optional[str] = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of(str))
    )
    quote_items: List[QuoteItem] = attr.ib(converter=convert_iterable(QuoteItem))
    status: Optional[str] = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of(str))
    )
    sent_date: Optional[str] = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of(str))
    )
    expired_date: str = attr.ib(validator=attr.validators.instance_of(str))
    quote_notes: Optional[str] = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of(str))
    )
    export_controlled: bool = attr.ib(validator=attr.validators.instance_of(bool))
    digital_last_viewed_on: Optional[str] = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of(str))
    )
    expired: bool = attr.ib(validator=attr.validators.instance_of(bool))
    request_for_quote: Optional[RequestForQuote] = attr.ib(
        converter=convert_cls(RequestForQuote),
        validator=attr.validators.optional(
            attr.validators.instance_of(RequestForQuote)
        ),
    )
    parent_quote: Optional[ParentQuote] = attr.ib(
        converter=convert_cls(ParentQuote),
        validator=attr.validators.optional(attr.validators.instance_of(ParentQuote)),
    )
    parent_supplier_order: Optional[ParentSupplierOrder] = attr.ib(
        converter=convert_cls(ParentSupplierOrder),
        validator=attr.validators.optional(
            attr.validators.instance_of(ParentSupplierOrder)
        ),
    )
    authenticated_pdf_quote_url: Optional[str] = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of(str))
    )
    is_unviewed_drafted_rfq: bool = attr.ib(validator=attr.validators.instance_of(bool))
    created: str = attr.ib(validator=attr.validators.instance_of(str))
    erp_code = attr.ib(
        default=NO_UPDATE,
        validator=attr.validators.optional(attr.validators.instance_of((str, object))),
    )

    @classmethod
    def construct_get_url(cls):
        return 'quotes/public'

    @classmethod
    def construct_get_params(cls, revision):
        """
        Optional method to define query params to send along GET request

        :return None or params dict
        """
        return {'revision': revision}

    @classmethod
    def construct_get_new_resources_url(cls):
        return 'quotes/public/new'

    # id is the quote number
    @classmethod
    def construct_get_new_params(cls, id, revision):
        return {'last_quote': id, 'revision': revision}

    @classmethod
    def construct_patch_url(cls):
        return 'quotes/public'


class QuoteManager(GetManagerMixin, BaseManager):
    _base_object = Quote

    def set_status(self, obj, status):
        client = self._client
        params = None
        if obj.revision_number is not None:
            params = {'revision': obj.revision_number}
        resp_json = client.request(
            url=f'quotes/public/{obj.number}/status_change',
            method=PaperlessClient.METHODS.PATCH,
            data={"status": status},
            params=params,
        )
        resp_obj = self._base_object.from_json(resp_json)
        keys = filter(
            lambda x: not x.startswith('__') and not x.startswith('_'), dir(resp_obj)
        )
        for key in keys:
            setattr(obj, key, getattr(resp_obj, key))

    def update(self, obj):
        """
        Persists local changes of an existing Paperless Parts resource to Paperless.
        """

        client = self._client
        primary_key = getattr(self, obj._primary_key)
        data = obj.to_json()

        # Include the revision number as a query parameter, if applicable
        params = None
        if obj.revision_number is not None:
            params = {'revision': obj.revision_number}

        resp = client.update_resource(
            self._base_object.construct_patch_url(),
            primary_key,
            data=data,
            params=params,
        )
        resp_obj = self._base_object.from_json(resp)
        # This filter is designed to remove methods, properties, and private data members and only let through the
        # fields explicitly defined in the class definition
        keys = filter(
            lambda x: not x.startswith('__')
            and not x.startswith('_')
            and type(getattr(resp_obj, x)) != MethodType
            and (
                not isinstance(getattr(resp_obj.__class__, x), property)
                if x in dir(resp_obj.__class__)
                else True
            ),
            dir(resp_obj),
        )
        for key in keys:
            setattr(obj, key, getattr(resp_obj, key))

    def get_new(self, id=None, revision=None):
        client = self._client

        return client.get_new_resources(
            self._base_object.construct_get_new_resources_url(),
            params=self._base_object.construct_get_new_params(id, revision)
            if id
            else None,
        )
