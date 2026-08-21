from django.db import transaction
from django.utils import timezone

from api.utils.hashing import compute_data_hash
from api.utils.validators import (
    validate_boolean_optional,
    validate_coordinate,
    validate_decimal,
    validate_event_date,
    validate_event_datetime,
    validate_int_optional,
    validate_required,
)


class BaseImportAdapter:
    model = None
    key_field = "dataID"
    hash_fields = []
    payload_builder = None

    def __init__(self, hash_fields=None):
        self.hash_fields = hash_fields or list(self.hash_fields)
        self.validators = {
            "required": validate_required,
            "coordinate": validate_coordinate,
            "decimal": validate_decimal,
            "int_optional": validate_int_optional,
            "boolean_optional": validate_boolean_optional,
            "event_date": validate_event_date,
            "event_datetime": validate_event_datetime,
        }

    def build_payload(self, record):
        return self.payload_builder(record, self.validators)

    def compute_hash(self, payload):
        hash_payload = {}
        for f in self.hash_fields:
            hash_payload[f] = payload.get(f)
        return compute_data_hash(hash_payload)

    def fetch_existing_hash_map(self, keys):
        if not keys:
            return {}

        return {
            key: {"id": pk, "data_hash": data_hash}
            for key, pk, data_hash in self.model.objects.filter(
                **{f"{self.key_field}__in": keys}
            ).values_list(self.key_field, "id", "data_hash")
        }

    def make_instance(self, payload):
        return self.model(**payload)

    def write(self, to_create, to_update):
        now = timezone.now()

        for obj in to_update:
            obj.updated_at = now

        with transaction.atomic():
            if to_create:
                self.model.objects.bulk_create(to_create, batch_size=1000)

            if to_update:
                self.model.objects.bulk_update(
                    to_update,
                    fields=self.hash_fields + ["data_hash", "updated_at"],
                    batch_size=1000,
                )
