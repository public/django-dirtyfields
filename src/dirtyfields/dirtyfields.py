# Adapted from http://stackoverflow.com/questions/110803/dirty-fields-in-django

import copy

from django.db.models.signals import post_save
import django.dispatch


def _iter_fields(obj):
    for field in obj._meta.local_fields:
        if not field.rel:
            yield field, field.to_python(getattr(obj, field.name))


def _to_dict(obj):
    return {
        field.name: copy.copy(value)
        for field, value in _iter_fields(obj)
    }


def _changes(obj, new_state):
    return {
        key: value
        for key, value in obj._original_state.iteritems()
        if new_state[key] != value
    }


dirty_save = django.dispatch.Signal(
    providing_args=["instance", "original_data", "changes"])


def _reset_state(sender, instance, **kwargs):
    new_state = _to_dict(instance)
    changes = _changes(instance, new_state)

    if changes:
        dirty_save.send(
            sender=sender,
            original_data=instance._original_state,
            changes=changes
        )

    instance._original_state = new_state


class DirtyFieldsMixin(object):
    def __init__(self, *args, **kwargs):
        super(DirtyFieldsMixin, self).__init__(*args, **kwargs)

        self._original_state = _to_dict(self)

        post_save.connect(
            _reset_state,
            sender=self.__class__,
            dispatch_uid='{0}-DirtyFieldsMixin-sweeper'.format(
                self.__class__.__name__
            )
        )
        _reset_state(sender=self.__class__, instance=self)
