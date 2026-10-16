"""Validate scoped dependency transformation without network or plant access."""

import unittest
from unittest.mock import Mock

from attack_b_supply_chain import staged_dependency


class SupplyChainProbeTests(unittest.TestCase):
    def setUp(self):
        self.original = Mock()
        self.module = {"emit": self.original}
        exec(staged_dependency("", "unit-test"), self.module)

    def test_startup_report_changed_but_input_not_mutated(self):
        details = {"state": "active", "bind": "127.0.0.1:5063"}
        self.module["emit"]("service.state", "Started", details=details)
        call = self.original.call_args
        self.assertIn("reported_state=inactive", call.args[1])
        self.assertEqual(call.kwargs["severity"], "warning")
        self.assertEqual(call.kwargs["details"]["state"], "inactive")
        self.assertEqual(call.kwargs["details"]["w4_test"], "unit-test")
        self.assertEqual(details["state"], "active")

    def test_nonstartup_events_forwarded_unchanged(self):
        for event_type, details in (("protocol.read", {"offset": 3}),
                                    ("service.state", {"state": "inactive"})):
            with self.subTest(event_type=event_type):
                self.module["emit"](event_type, "Original", details=details)
                self.original.assert_called_with(
                    event_type, "Original", severity="info", details=details
                )

    def test_marker_cannot_inject_python(self):
        marker = "test'\nraise RuntimeError('unexpected')\n#"
        module = {"emit": self.original}
        exec(staged_dependency("", marker), module)
        module["emit"]("service.state", "Started", details={"state": "active"})
        self.assertEqual(self.original.call_args.kwargs["details"]["w4_test"], marker)


if __name__ == "__main__":
    unittest.main()
