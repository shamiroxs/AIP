import torch
from pathlib import Path
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from assistant.utils.logger import get_logger

log = get_logger(__name__)


class LocalLLM:
    _model = None
    _tokenizer = None

    @classmethod
    def load(cls, model_path: str):
        if cls._model is not None:
            return

        model_path = Path(model_path).expanduser().resolve()

        if not model_path.exists():
            raise FileNotFoundError(f"Model path does not exist: {model_path}")

        log.info("Loading local T5 fine-tuned model from %s", model_path)

        cls._tokenizer = AutoTokenizer.from_pretrained(
            model_path,
            local_files_only=True
        )

        cls._model = AutoModelForSeq2SeqLM.from_pretrained(
            model_path,
            dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map="auto",
            local_files_only=True
        )

        cls._model.eval()

    @classmethod
    def generate(cls, prompt: str, max_new_tokens: int = 256) -> str:
        inputs = cls._tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True
        ).to(cls._model.device)

        with torch.no_grad():
            outputs = cls._model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=False
            )

        return cls._tokenizer.decode(outputs[0], skip_special_tokens=True)
