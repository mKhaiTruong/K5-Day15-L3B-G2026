"""Test nhánh OpenAI trong codebase/ai.py, giả lập API (không gọi mạng, không tốn token).

Chạy: python -m pytest tests/test_ai.py
"""
import io
import json
import os
import sys
import urllib.error

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "codebase"))

import ai


def _fake_response(content="{}", prompt_tokens=120, completion_tokens=30):
    return {"choices": [{"message": {"content": content}}],
            "usage": {"prompt_tokens": prompt_tokens, "completion_tokens": completion_tokens}}


@pytest.fixture
def openai_mode(monkeypatch):
    """Bật MODEL_PROVIDER=openai với key giả, ghi lại request đã gửi."""
    monkeypatch.setattr(ai, "MODEL_PROVIDER", "openai")
    monkeypatch.setattr(ai, "MODEL_NAME", "gpt-test")
    monkeypatch.setattr(ai, "API_KEY", "sk-test")
    sent = {}

    def fake_post(url, headers, body, timeout=60):
        sent.update(url=url, headers=headers, body=body)
        return sent.get("response", _fake_response('{"khai_niem": []}'))

    monkeypatch.setattr(ai, "post_json", fake_post)
    return sent


def test_openai_tra_du_4_khoa_va_token_tu_usage(openai_mode):
    r = ai.call_model("Trả về JSON.", "Lab Day13 CP1")
    assert r == {"text": '{"khai_niem": []}', "model": "gpt-test", "tokens_in": 120, "tokens_out": 30}


def test_openai_gui_dung_request(openai_mode):
    ai.call_model("SYS", "USER")
    body = openai_mode["body"]
    assert openai_mode["url"] == ai.URL_OPENAI
    assert openai_mode["headers"]["Authorization"] == "Bearer sk-test"
    assert body["model"] == "gpt-test"
    assert body["response_format"] == {"type": "json_object"}
    assert body["messages"] == [{"role": "system", "content": "SYS"}, {"role": "user", "content": "USER"}]


def test_openai_content_none_thanh_chuoi_rong(openai_mode):
    openai_mode["response"] = _fake_response(content=None)
    assert ai.call_model("SYS", "USER")["text"] == ""


def test_provider_chua_ho_tro_bao_loi(monkeypatch):
    monkeypatch.setattr(ai, "MODEL_PROVIDER", "gemini")
    with pytest.raises(NotImplementedError):
        ai.call_model("SYS", "USER")


def test_post_json_http_loi_thanh_runtime_error(monkeypatch):
    def raise_http(req, timeout):
        raise urllib.error.HTTPError(req.full_url, 401, "Unauthorized", {}, io.BytesIO(b'{"error": "bad key"}'))

    monkeypatch.setattr(ai.urllib.request, "urlopen", raise_http)
    with pytest.raises(RuntimeError, match="HTTP 401"):
        ai.post_json(ai.URL_OPENAI, {}, {"x": 1})


def test_post_json_doc_phan_hoi(monkeypatch):
    class Resp(io.BytesIO):
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    monkeypatch.setattr(ai.urllib.request, "urlopen",
                        lambda req, timeout: Resp(json.dumps({"ok": 1}).encode("utf-8")))
    assert ai.post_json(ai.URL_OPENAI, {}, {}) == {"ok": 1}
