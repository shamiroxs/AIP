# assistant/utils/response_formatter.py
def format_for_speech(text: str, max_words: int = 60) -> str:
    # Keep a short speech-friendly summary
    words = text.split()
    if len(words) <= max_words:
        return text
    short = " ".join(words[:max_words]) + " ... I provided more details to the console."
    return short

def format_for_gui(text: str) -> str:
    # Return full text (or truncated at 5000 chars)
    if len(text) > 5000:
        return text[:5000] + "\n\n[truncated]"
    return text
