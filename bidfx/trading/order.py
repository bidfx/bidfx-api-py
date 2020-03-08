__all__ = [
    "DealTypes",
    "AssetClasses",
    "Order",
    "OrderFields",
]

from enum import Enum
from typing import Any


class DealTypes(Enum):
    SPOT = "SPOT"
    FORWARD = "FWD"
    SWAP = "SWAP"
    NDF = "NDF"
    NDS = "NDS"


class AssetClasses(Enum):
    EQUITY = "EQUITY"
    FUTURE = "FUTURE"
    OPTION = "OPTION"
    STRATEGY = "STRATEGY"
    FIXED_INCOME = "FIXED_INCOME"


class OrderFields(Enum):
    ASSET_CLASS = "asset_class"
    DEAL_TYPE = "deal_type"
    ORDER_TS_ID = "order_ts_id"


class OrderError:
    def __init__(self, field: str, message: str, value: Any = None):
        self.field = field
        self.message = message
        self.value = value

    def __repr__(self):
        return (
            f'<OrderError field="{self.field}" message="{self.message}" '
            f'{f"value = {self.value}" if self.value else ""}>'
        )

    def __str__(self):
        return (
            f'field="{self.field}" message="{self.message}" '
            f'{f"value = {self.value}" if self.value else ""}'
        )


class cached_property:
    def __init__(self, func):
        self.func = func

    def __get__(self, instance, cls=None):
        result = instance.__dict__[self.func.__name__] = self.func(instance)
        return result


class Order:
    def __init__(self, parameters: dict):
        if not isinstance(parameters, dict):
            raise ValueError("order parameters should be provided as a dictionary")
        self.parameters = parameters or {}
        self._errors = []

    def update_parameter(self, name, value):
        self.parameters[name] = value

    def update_parameters(self, params):
        self.parameters.update(params)

    @cached_property
    def errors(self):
        errors = self.parameters.get("errors", [])
        for error in errors:
            field = error.get("field")
            message = error.get("message")
            value = error.get("value")
            self._errors.extend([OrderError(field, message, value)])
        return self._errors

    @property
    def deal_type(self):
        return self.parameters.get(OrderFields.DEAL_TYPE.value)

    @property
    def asset_class(self):
        return self.parameters.get(OrderFields.ASSET_CLASS.value)

    @property
    def order_ts_id(self):
        return self.parameters.get(OrderFields.ORDER_TS_ID.value)

    # def spot(self):
    #     return self.update_parameter(OrderFields.DEAL_TYPE, DealTypes.SPOT.value)
    #
    # def forward(self):
    #     self.update_parameter(OrderFields.DEAL_TYPE.value, DealTypes.FORWARD.value)
    #     return self
    #
    # def swap(self):
    #     self.update_parameter(OrderFields.DEAL_TYPE.value, DealTypes.SWAP.value)
    #     return self
    #
    # def ndf(self):
    #     self.update_parameter(OrderFields.DEAL_TYPE.value, DealTypes.NDF.value)
    #     return self
    #
    # def nds(self):
    #     self.update_parameter(OrderFields.DEAL_TYPE.value, DealTypes.NDS.value)
    #     return self
    #
    # def equity(self):
    #     self.update_parameter(OrderFields.ASSET_CLASS.value, AssetClasses.EQUITY.value)
    #     return self
    #
    # def future(self):
    #     self.update_parameter(OrderFields.ASSET_CLASS.value, AssetClasses.FUTURE.value)
    #     return self
    #
    # def option(self):
    #     self.update_parameter(OrderFields.ASSET_CLASS.value, AssetClasses.OPTION.value)
    #     return self
    #
    # def strategy(self):
    #     self.update_parameter(OrderFields.ASSET_CLASS.value, AssetClasses.STRATEGY.value)
    #     return self
    #
    # def fixed_income(self):
    #     self.update_parameter(OrderFields.ASSET_CLASS.value, AssetClasses.FIXED_INCOME.value)
    #     return self

    def __str__(self):
        return f"<Order parameters: {str(self.parameters)}>"
