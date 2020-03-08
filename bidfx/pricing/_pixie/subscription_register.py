import threading

from bidfx.exceptions import PricingError
from bidfx.pricing._pixie.message.subscription_sync_message import (
    SubscriptionSyncMessage,
)
from bidfx.pricing.subject import Subject


def _subscribe_op(subscription_set: set, subject: Subject):
    subscription_set.add(subject)


def _unsubscribe_op(subscription_set: set, subject: Subject):
    subscription_set.discard(subject)


def _subject_order():
    return (
        lambda subject: subject.get(Subject.CURRENCY_PAIR, "")
        + subject.get(Subject.QUANTITY, "")
        + str(subject)
    )


class SubscriptionRegister:
    def __init__(self):
        self._lock = threading.Lock()
        self._edition = 1
        self._subject_editions = {self._edition: []}
        self._pending_ops = []

    def subscribe(self, subject: Subject):
        with self._lock:
            self._pending_ops.append((_subscribe_op, subject))

    def unsubscribe(self, subject: Subject):
        with self._lock:
            self._pending_ops.append((_unsubscribe_op, subject))

    def subscription_sync(self):
        with self._lock:
            if len(self._pending_ops) == 0:
                return None
            subject_set, is_unchanged = self._active_subject_set()
            if is_unchanged:
                return None
            subjects = sorted(subject_set, key=_subject_order())
            self._edition += 1
            self._subject_editions[self._edition] = subjects
            return SubscriptionSyncMessage(self._edition, subjects, is_compressed=True)

    def _active_subject_set(self):
        previous_subject_set = set(self._subject_editions[self._edition])
        subject_set = previous_subject_set.copy()
        for operation_fn, subject in self._pending_ops:
            operation_fn(subject_set, subject)
        self._pending_ops.clear()
        is_unchanged = subject_set == previous_subject_set
        return subject_set, is_unchanged

    def purge_editions_before(self, edition):
        with self._lock:
            purged = {
                ed: v for (ed, v) in self._subject_editions.items() if ed >= edition
            }
            self._subject_editions = purged

    def subjects_for_edition(self, edition):
        with self._lock:
            subjects = self._subject_editions.get(edition)
            if subjects is None:
                raise PricingError(f"no subject set registered for edition {edition}")
            return subjects

    def reset_and_get_subjects(self):
        with self._lock:
            subject_set, _ = self._active_subject_set()
            subjects = sorted(subject_set, key=_subject_order())
            for subject in subjects:
                self._pending_ops.append((_subscribe_op, subject))
            self._edition = 1
            self._subject_editions = {self._edition: []}
            return subjects
