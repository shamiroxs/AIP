# assistant/tests/test_llm_integration.py
import pytest
from assistant.agents.llm_agent import LLMAgent, MockLLM
from assistant.agents.nl_router import NLRouter
from assistant.security.llm_safety import LLMSafety
from assistant.agents.context_memory import ContextMemory
from assistant.config.settings import settings

def test_mock_llm_answer():
    llm = LLMAgent()
    # Ensure mock is used by default
    settings.LLM_ENABLED = False
    resp = llm.answer_query("How do I check disk usage?", context="")
    assert "disk" in resp.text.lower() or "help" in resp.text.lower()

def test_suggest_command_mock():
    llm = LLMAgent()
    settings.LLM_ENABLED = False
    resp = llm.suggest_command("Install firefox", context="")
    # Mock may return JSON or empty dict text
    assert isinstance(resp.text, str)

def test_nl_router_with_no_proposal(tmp_path, monkeypatch):
    settings.LLM_ENABLED = False
    router = NLRouter()
    out = router.handle_unknown("How to view memory?")
    assert "reply" in out
    assert out["proposed_intent"] is None

def test_llm_safety_rejects_dangerous():
    safety = LLMSafety()
    bad = {"action": "install_package", "args": ["rm -rf /"], "explanation": "delete", "confidence": 0.9}
    ok, san, reasons = safety.verify_and_sanitize_suggestion(bad)
    assert not ok
    assert reasons

def test_markov_verifier():
    from assistant.agents.verification_markov import MarkovVerifier
    v = MarkovVerifier()
    assert v.score_sequence("apt-get install firefox") > 0
    assert v.score_sequence("gibberish $$ ### ???") < 0
