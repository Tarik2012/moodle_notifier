import logging

from .models import ExternalSyncLog

logger = logging.getLogger(__name__)


def log_external_sync(
    service,
    action,
    entity_type,
    entity_id,
    status,
    message=None,
):
    """
    Store a non-blocking audit record for external sync operations.
    Any internal error is swallowed to avoid impacting the caller.
    """
    try:
        ExternalSyncLog.objects.create(
            service=service,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            status=status,
            message=message,
        )
    except Exception:
        logger.exception("Failed to persist external sync log")
