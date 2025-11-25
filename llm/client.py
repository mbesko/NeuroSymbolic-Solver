import os
from openai import OpenAI
from dotenv import load_dotenv
from .prompts import PROMPT_FORMALIZE, PROMPT_EXPLAIN


class LLMClient:
    def __init__(self):
        load_dotenv()

        api_key = os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("OPENAI_BASE_URL", "https://openrouter.ai/api/v1")
        self.model = os.getenv("MODEL_NAME", "google/gemini-2.0-flash-exp:free")

        if not api_key:
            print("⚠️ ПРЕДУПРЕЖДЕНИЕ: Не найден API ключ в .env")

        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url,
            default_headers={
                "HTTP-Referer": "https://localhost:8000",
                "X-Title": "NeuroSymbolic Solver"
            }
        )

    def formalize(self, text: str) -> str:
        """
        Пытается получить JSON от модели.
        Сначала пробует строгий режим json_object.
        Если модель его не поддерживает (ошибка 400), пробует обычный режим.
        """
        messages = [
            {"role": "system", "content": PROMPT_FORMALIZE},
            {"role": "user", "content": text}
        ]

        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            return completion.choices[0].message.content

        except Exception:
            try:
                completion = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.1
                )
                return completion.choices[0].message.content
            except Exception as e:
                return f"Error: {str(e)}"

    def explain(self, task: str, logs: list) -> str:
        log_str = "\n".join(logs[-40:])
        if len(logs) > 40:
            log_str = f"...(начало пропущено, показаны последние 40 шагов)...\n{log_str}"

        content = f"Задача: {task}\n\nЛог решателя:\n{log_str}"

        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": PROMPT_EXPLAIN},
                    {"role": "user", "content": content}
                ],
                temperature=0.7
            )
            return completion.choices[0].message.content
        except Exception as e:
            return f"Не удалось сгенерировать объяснение. Ошибка: {e}"