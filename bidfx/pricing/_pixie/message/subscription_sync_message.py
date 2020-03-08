from .pixie_message_type import PixieMessageType
from ..util.compression import Compressor
from ..util.varint import encode_varint, encode_strings_list


class SubscriptionSyncMessage:
    msg_type = PixieMessageType.SubscriptionSyncMessage

    def __init__(
        self,
        edition,
        subjects,
        is_compressed=False,
        is_controls=False,
        is_unchanged=False,
        sids=None,
    ):
        self.compressor = Compressor()
        self.is_compressed = is_compressed
        self.is_controls = is_controls
        self.is_unchanged = is_unchanged
        self.option = 0
        self.edition = edition
        self.subjects = subjects
        self.size = len(self.subjects)
        if sids:
            self.sid_list = sorted(
                [(sid, operation) for sid, operation in sids.items()],
                key=lambda x: x[0],
            )  # sorted based on sid

        if is_compressed:
            self.option = int(self.option ^ 1)  # set compression bit
        if is_controls:
            self.option = int(self.option ^ 2)  # set control bit
        if is_unchanged:
            self.option = int(self.option ^ 4)  # set unchanged bit

    def to_bytes(self):
        subject_sync_message = self.msg_type
        subject_sync_message += encode_varint(self.option)
        subject_sync_message += encode_varint(self.edition)

        if self.subjects:
            subject_sync_message += encode_varint(self.size)
            for subject in self.subjects:
                encoded_subject = encode_strings_list(subject.flatten())
                if self.is_compressed:
                    encoded_subject = self.compressor.compress(encoded_subject)
                subject_sync_message += encoded_subject
        else:
            subject_sync_message += encode_varint(self.size)

        if self.is_controls:
            control_part = b""
            control_part += encode_varint(len(self.sid_list))
            for sid, operation in self.sid_list:
                control_part += encode_varint(sid)
                control_part += operation
            if self.is_compressed:
                subject_sync_message += self.compressor.compress(control_part)
            else:
                subject_sync_message += control_part
        subject_sync_message_bytes = encode_varint(len(subject_sync_message))
        subject_sync_message_bytes += subject_sync_message
        return subject_sync_message_bytes

    def __str__(self):
        return (
            f"SubscriptionSyncMessage Option:{self.option} Size:{self.size} "
            f"Edition:{self.edition} Subjects:{self._subject_list()}"
        )

    def _subject_list(self):
        return "\n   " + ("\n   ".join(str(s) for s in self.subjects))
