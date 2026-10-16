"""Check insider probe guardrails without connecting to the plant."""

import unittest
from unittest.mock import MagicMock, patch

import attack_a_insider


class InsiderProbeTests(unittest.TestCase):
    def run_probe(self, arguments, reads):
        client = MagicMock()
        client.read_holding_registers.side_effect = [
            MagicMock(registers=[value], isError=lambda: False) for value in reads
        ]
        client.write_register.return_value.isError.return_value = False
        with patch("sys.argv", ["attack_a_insider.py", *arguments]):
            with patch.object(attack_a_insider, "ModbusTcpClient", return_value=client):
                with patch("builtins.print"):
                    try:
                        attack_a_insider.main()
                    finally:
                        self.client = client

    def test_default_is_read_only(self):
        self.run_probe([], [250])
        self.client.write_register.assert_not_called()
        self.client.close.assert_called_once()

    def test_unexpected_baseline_prevents_writes(self):
        with self.assertRaisesRegex(RuntimeError, "Expected baseline"):
            self.run_probe(["--execute"], [249])
        self.client.write_register.assert_not_called()

    def test_both_cycles_restore_original(self):
        self.run_probe(["--execute"], [250, 250, 300, 250, 250, 301, 250])
        self.assertEqual(
            [call.kwargs["value"] for call in self.client.write_register.call_args_list],
            [300, 250, 301, 250],
        )

    def test_failed_readback_still_restores(self):
        with self.assertRaisesRegex(RuntimeError, "expected readback"):
            self.run_probe(["--execute"], [250, 250, 299, 250])
        self.assertEqual(
            [call.kwargs["value"] for call in self.client.write_register.call_args_list],
            [300, 250],
        )
        self.client.close.assert_called_once()


if __name__ == "__main__":
    unittest.main()
