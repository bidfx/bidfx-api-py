#!/usr/bin/env python

import logging
import time
from typing import List

import requests

from bidfx.session import Session
from bidfx.trading.order import Order
from bidfx.trading.trade_error import TradeError
import json
from collections import namedtuple


def _json_object_hook(d):
    return namedtuple("X", d.keys())(*d.values())


def json2obj(data):
    return json.loads(data, object_hook=_json_object_hook)


class FxOrder:
    def __init__(
        self,
        *initial_data,
        account=None,
        aggregation_level_1=None,
        aggregation_level_2=None,
        aggregation_level_3=None,
        algo=None,
        all_in_price=None,
        allocation_data=None,
        allocation_template=None,
        alternate_owner=None,
        asset_class=None,
        best_value=None,
        ccy_pair=None,
        client_order_id=None,
        competitive_rates=None,
        correlation_id=None,
        creation_date=None,
        custom_fields=None,
        deal_type=None,
        dealt_ccy=None,
        disable_instrument_lookup=None,
        excluded_executing_brokers=None,
        executing_broker=None,
        expiry_date=None,
        far_dealt_ccy=None,
        far_fixing_date=None,
        far_quantity=None,
        far_settlement_date=None,
        far_side=None,
        far_tenor=None,
        fixing_date=None,
        handling_comment=None,
        handling_type=None,
        included_executing_brokers=None,
        internal_comment=None,
        leg_index=None,
        order_instruction=None,
        order_type=None,
        owner=None,
        price=None,
        price_offset=None,
        quantity=None,
        reference1=None,
        reference2=None,
        settlement_date=None,
        side=None,
        solicitation_type=None,
        source_id=None,
        source_intent=None,
        tenor=None,
        tep=None,
        tep_type=None,
        time_in_force_type=None,
        trigger_price=None,
    ):
        self.account = account
        self.aggregation_level_1 = aggregation_level_1
        self.aggregation_level_2 = aggregation_level_2
        self.aggregation_level_3 = aggregation_level_3
        self.algo = algo
        self.all_in_price = all_in_price
        self.allocation_data = allocation_data
        self.allocation_template = allocation_template
        self.alternate_owner = alternate_owner
        self.asset_class = asset_class
        self.best_value = best_value
        self.ccy_pair = ccy_pair
        self.client_order_id = client_order_id
        self.competitive_rates = competitive_rates
        self.correlation_id = correlation_id
        self.creation_date = creation_date
        self.custom_fields = custom_fields
        self.deal_type = deal_type
        self.dealt_ccy = dealt_ccy
        self.disable_instrument_lookup = disable_instrument_lookup
        self.excluded_executing_brokers = excluded_executing_brokers
        self.executing_broker = executing_broker
        self.expiry_date = expiry_date
        self.far_dealt_ccy = far_dealt_ccy
        self.far_fixing_date = far_fixing_date
        self.far_quantity = far_quantity
        self.far_settlement_date = far_settlement_date
        self.far_side = far_side
        self.far_tenor = far_tenor
        self.fixing_date = fixing_date
        self.handling_comment = handling_comment
        self.handling_type = handling_type
        self.included_executing_brokers = included_executing_brokers
        self.internal_comment = internal_comment
        self.leg_index = leg_index
        self.order_instruction = order_instruction
        self.order_type = order_type
        self.owner = owner
        self.price = price
        self.price_offset = price_offset
        self.quantity = quantity
        self.reference1 = reference1
        self.reference2 = reference2
        self.settlement_date = settlement_date
        self.side = side
        self.solicitation_type = solicitation_type
        self.source_id = source_id
        self.source_intent = source_intent
        self.tenor = tenor
        self.tep = tep
        self.tep_type = tep_type
        self.time_in_force_type = time_in_force_type
        self.trigger_price = trigger_price
        self.broker_order_id = None
        self.cancel_response_time = None
        self.cancel_time = None
        self.children = None
        self.client_lei = None
        self.description = None
        self.executing_broker_name = None
        self.executions = None
        self.far_all_in_price = None
        self.forward_points = None
        self.instructions = None
        self.leg_ratio = None
        self.limit_violations = None
        self.line_handler_order_id = None
        self.order_manager_state = None
        self.order_ts_id = None
        self.parent_order_ts_id = None
        self.partition_id = None
        self.spot_rate = None
        self.state = None
        self.strategy_parent_order_ts_id = None
        self.submit_response_time = None
        self.submit_time = None
        self.swap_points = None
        self.unexecuted_quantity = None
        self.uuid = None

    @staticmethod
    def from_dict(dictionary):
        order = FxOrder()
        for key in dictionary:
            setattr(order, key, dictionary[key])
        return order


def main():
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(levelname)-7s %(threadName)-12s %(message)s",
    )
    logging.info("making request")

    session = Session.create_from_ini_file()
    fx_order1 = FxOrder(
        asset_class="FX",
        account="FX_ACCT",
        ccy_pair="EURGBP",
        deal_type="SPOT",
        tenor="SPOT",
        dealt_ccy="GBP",
        handling_type="AUTOMATIC",
        order_type="MARKET",
        price="0.886865",
        quantity="500000",
        reference1="SFPRef1",
        reference2="SFPRef2",
        side="SELL",
    )
    response = session.trading.rest.fx().create_order(fx_order1)

    json_ = response.json()[0]
    order = FxOrder.from_dict(json_)

    print(order.order_ts_id)
    # print(session.trading.rest.fx().get_order('20200301-133911-3625828480-280-API').json())
    # print(session.trading.rest.fx().get_order('20200301-133911-3625828480-280-API').json())
    # print(session.trading.rest.fx().get_order('20200301-133911-3625828480-280-API').json())


if __name__ == "__main__":
    main()
