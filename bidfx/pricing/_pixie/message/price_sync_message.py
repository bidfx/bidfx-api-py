import logging

from bidfx.pricing.events import SubscriptionEvent, PriceEvent, SubscriptionStatus
from ..util.buffer_reads import read_byte
from ..util.varint import decode_varint, decode_string

log = logging.getLogger("bidfx.pricing.pixie.message")

ERROR_FID = int.from_bytes(b"\x7f\xff\xff\xff", byteorder="big")

FULL_MAP = b"f"
PARTIAL_MAP = b"p"
STATUS = b"s"

STATUSES = {
    b"O": SubscriptionStatus.OK,
    b"P": SubscriptionStatus.PENDING,
    b"S": SubscriptionStatus.STALE,
    b"C": SubscriptionStatus.CANCELLED,
    b"D": SubscriptionStatus.DISCONTINUED,
    b"H": SubscriptionStatus.PROHIBITED,
    b"U": SubscriptionStatus.UNAVAILABLE,
    b"R": SubscriptionStatus.REJECTED,
    b"T": SubscriptionStatus.TIMEOUT,
    b"I": SubscriptionStatus.INACTIVE,
    b"E": SubscriptionStatus.EXHAUSTED,
    b"L": SubscriptionStatus.CLOSED,
}


class PriceSyncMessage:
    def __init__(self, input_stream, decompressor):
        self.is_compressed = True if decode_varint(input_stream) == 1 else False
        self.revision = decode_varint(input_stream)
        self.revision_time = decode_varint(input_stream)
        self.conflation_latency = decode_varint(input_stream)
        self.edition = decode_varint(input_stream)
        self.size = decode_varint(input_stream)
        self._buffer = (
            decompressor.decompress(input_stream)
            if self.is_compressed
            else input_stream
        )
        log.debug(f"Price Sync edition:{self.edition} revision:{self.revision}")

    def visit_updates(self, subjects, data_dictionary, callbacks):
        for i in range(self.size):
            self._visit_next_update(subjects, data_dictionary, callbacks)

    def _visit_next_update(self, subjects, data_dictionary, callbacks):
        type_of_update = read_byte(self._buffer)
        if type_of_update == PARTIAL_MAP:
            self._price_update(subjects, data_dictionary, callbacks, full=False)
        if type_of_update == FULL_MAP:
            self._price_update(subjects, data_dictionary, callbacks, full=True)
        elif type_of_update == STATUS:
            self._status_update(subjects, callbacks)

    def _price_update(self, subjects, data_dictionary, callbacks, full):
        sid = decode_varint(self._buffer)
        subject = subjects[sid]
        field_count = decode_varint(self._buffer)
        price = self._extract_price(data_dictionary, field_count)
        event = PriceEvent(subject, price, full)
        callbacks.price_event_fn(event)

    def _extract_price(self, data_dictionary, field_count):
        price = {}
        for _ in range(field_count):
            self._visit_field(data_dictionary, price)
        return price

    def _status_update(self, subjects, callbacks):
        sid = decode_varint(self._buffer)
        subject = subjects[sid]
        status = STATUSES[read_byte(self._buffer)]
        explanation = decode_string(self._buffer)
        event = SubscriptionEvent(subject, status, explanation)
        callbacks.subscription_event_fn(event)

    def _visit_field(self, data_dictionary, price):
        fid = decode_varint(self._buffer)
        if fid != ERROR_FID:
            definition = data_dictionary[fid]
            value = definition.parse_value(self._buffer)
            if definition.enabled:
                price[definition.name] = value

    def __str__(self):
        return (
            f"PriceSync revision:{self.revision} revision time:{self.revision_time} "
            f"conflation latency:{self.conflation_latency} edition:{self.edition} "
            f"size:{self.size}"
        )
