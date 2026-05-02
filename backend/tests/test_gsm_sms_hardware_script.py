"""Tests for GSM SMS hardware helper parsing and command flow."""
import importlib.util
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[2] / "scripts" / "test_gsm_sms_hardware.py"
SPEC = importlib.util.spec_from_file_location("test_gsm_sms_hardware", SCRIPT_PATH)
gsm_sms = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(gsm_sms)


class FakeSerial:
    def __init__(self, responses):
        self.responses = list(responses)
        self.writes = []
        self._buffer = b""

    def reset_input_buffer(self):
        self._buffer = b""

    def write(self, payload):
        self.writes.append(payload)
        if self.responses:
            self._buffer += self.responses.pop(0).encode("utf-8")

    @property
    def in_waiting(self):
        return len(self._buffer)

    def read(self, size):
        chunk = self._buffer[:size]
        self._buffer = self._buffer[size:]
        return chunk


def test_parse_cmgl_messages_extracts_sender_and_content():
    raw = '''
    +CMGL: 1,"REC UNREAD","+15551234567","","26/05/02,12:34:56-20"
    EVY inbound test water
    OK
    '''

    messages = gsm_sms.parse_cmgl_messages(raw)

    assert messages == [
        {
            "index": 1,
            "status": "REC UNREAD",
            "sender": "+15551234567",
            "timestamp": "26/05/02",
            "content": "EVY inbound test water",
        }
    ]


def test_send_sms_uses_text_mode_cmgs_and_ctrl_z():
    fake = FakeSerial(
        [
            "\r\nOK\r\n",
            "\r\n> ",
            "\r\n+CMGS: 12\r\nOK\r\n",
        ]
    )

    result = gsm_sms.send_sms(fake, "555-123-4567", "EVY test", timeout_s=1)

    assert result["pass"] is True
    assert fake.writes[0] == b"AT+CMGF=1\r\n"
    assert fake.writes[1] == b'AT+CMGS="+15551234567"\r\n'
    assert fake.writes[2] == b"EVY test\x1a"


def test_normalize_phone_number_defaults_us_country_code():
    assert gsm_sms.normalize_phone_number("(555) 123-4567") == "+15551234567"
    assert gsm_sms.normalize_phone_number("+15559876543") == "+15559876543"
