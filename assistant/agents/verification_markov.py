# assistant/agents/verification_markov.py
"""
Lightweight token-based verifier.
Not a full Markov model due to small scope — it scores sequences by permitted vocabulary.
Return positive score if tokens look normal, negative if anomalous.
"""
import re

ALLOWED_TOKENS = set([
    "apt-get", "install", "apt", "dpkg", "systemctl", "start", "stop", "restart",
    "service", "firefox", "curl", "wget", "ls", "df", "free", "ps", "kill",
    ".", "/", "-", "_", ":", "@"
])

def tokenize(s: str):
    return re.findall(r'[\w\-\./:@]+', s.lower())

class MarkovVerifier:
    def __init__(self):
        pass

    def score_sequence(self, s: str) -> float:
        tokens = tokenize(s)
        if not tokens:
            return 1.0
        bad = 0
        for t in tokens:
            if t not in ALLOWED_TOKENS and not re.match(r'^[\d]+$', t):
                bad += 1
        # If too many unknown tokens relative to length -> negative
        ratio = bad / max(1, len(tokens))
        if ratio > 0.4:
            return -1.0
        return 1.0 - ratio
