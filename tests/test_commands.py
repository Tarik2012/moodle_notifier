import pytest

from django.core.management import call_command


@pytest.mark.django_db
def test_sync_courses_command_runs(monkeypatch):
    from core.management.commands.sync_courses import Command

    monkeypatch.setattr(Command, "call_moodle", lambda self, func, params=None: [])

    call_command("sync_courses")


@pytest.mark.django_db
def test_send_medical_alerts_command_dispatches(monkeypatch):
    from medical_alerts.management.commands import send_medical_alerts as command_module

    class DummyTask:
        def __init__(self):
            self.called = False

        def delay(self):
            self.called = True

    dummy = DummyTask()
    monkeypatch.setattr(command_module, "send_medical_alerts_15_days", dummy)

    call_command("send_medical_alerts")
    assert dummy.called
