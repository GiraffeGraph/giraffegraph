import json
from dataclasses import dataclass, field
from json import JSONDecodeError
from typing import Any, Protocol
from urllib import error, request

from app.application.errors import ExternalServiceError, RuleViolationError


class OpenAITransport(Protocol):
    def __call__(
        self,
        *,
        url: str,
        headers: dict[str, str],
        payload: dict[str, object],
        timeout_seconds: float,
    ) -> dict[str, Any]: ...


def _default_openai_transport(
    *,
    url: str,
    headers: dict[str, str],
    payload: dict[str, object],
    timeout_seconds: float,
) -> dict[str, Any]:
    body = json.dumps(payload).encode("utf-8")
    http_request = request.Request(
        url,
        data=body,
        headers=headers,
        method="POST",
    )
    try:
        with request.urlopen(http_request, timeout=timeout_seconds) as response:
            raw_response = response.read().decode("utf-8")
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace").strip()
        if detail:
            raise ExternalServiceError(
                f"OpenAI provider request failed with status {exc.code}: {detail}"
            ) from exc
        raise ExternalServiceError(
            f"OpenAI provider request failed with status {exc.code}."
        ) from exc
    except error.URLError as exc:
        raise ExternalServiceError(
            f"OpenAI provider request failed: {exc.reason}."
        ) from exc
    except OSError as exc:
        raise ExternalServiceError(
            f"OpenAI provider request failed: {exc}."
        ) from exc

    try:
        parsed = json.loads(raw_response)
    except JSONDecodeError as exc:
        raise ExternalServiceError("OpenAI provider returned invalid JSON.") from exc
    if not isinstance(parsed, dict):
        raise ExternalServiceError("OpenAI provider returned a non-object response.")
    return parsed


@dataclass(slots=True)
class OpenAILLMProvider:
    api_key: str
    base_url: str = "https://api.openai.com/v1"
    timeout_seconds: float = 30.0
    transport: OpenAITransport = field(default=_default_openai_transport)
    provider_name: str = "openai"

    def generate_structured(
        self,
        *,
        prompt: str,
        schema_name: str,
        payload: dict[str, Any],
        model: str | None = None,
    ) -> dict[str, Any]:
        normalized_model = self._normalize_optional(model)
        if normalized_model is None:
            raise RuleViolationError(
                "OpenAI extraction provider requires a configured model."
            )

        response = self.transport(
            url=f"{self.base_url.rstrip('/')}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            payload={
                "model": normalized_model,
                "temperature": 0,
                "response_format": {"type": "json_object"},
                "messages": [
                    {
                        "role": "system",
                        "content": prompt,
                    },
                    {
                        "role": "user",
                        "content": json.dumps(
                            {
                                "schema_name": schema_name,
                                "payload": payload,
                            }
                        ),
                    },
                ],
            },
            timeout_seconds=self.timeout_seconds,
        )
        content = self._extract_content(response)
        parsed_output = self._parse_output(content)
        if not isinstance(parsed_output, dict):
            raise ExternalServiceError(
                "OpenAI provider returned a non-object structured output."
            )
        return parsed_output

    def _extract_content(self, response: dict[str, Any]) -> str:
        choices = response.get("choices")
        if not isinstance(choices, list) or len(choices) == 0:
            raise ExternalServiceError("OpenAI provider response did not include choices.")

        first_choice = choices[0]
        if not isinstance(first_choice, dict):
            raise ExternalServiceError("OpenAI provider returned an invalid choice payload.")

        message = first_choice.get("message")
        if not isinstance(message, dict):
            raise ExternalServiceError("OpenAI provider response did not include a message.")

        content = message.get("content")
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            text_parts: list[str] = []
            for item in content:
                if not isinstance(item, dict):
                    continue
                text_value = item.get("text")
                if isinstance(text_value, str):
                    text_parts.append(text_value)
                    continue
                if isinstance(text_value, dict):
                    nested_text = text_value.get("value")
                    if isinstance(nested_text, str):
                        text_parts.append(nested_text)
            if text_parts:
                return "".join(text_parts)

        raise ExternalServiceError(
            "OpenAI provider response did not include textual message content."
        )

    def _parse_output(self, content: str) -> object:
        normalized_content = content.strip()
        if normalized_content.startswith("```"):
            normalized_content = self._strip_code_fence(normalized_content)
        try:
            return json.loads(normalized_content)
        except JSONDecodeError as exc:
            raise ExternalServiceError(
                "OpenAI provider returned a non-JSON structured output."
            ) from exc

    def _strip_code_fence(self, content: str) -> str:
        lines = content.splitlines()
        if len(lines) >= 2 and lines[0].startswith("```") and lines[-1].strip() == "```":
            return "\n".join(lines[1:-1]).strip()
        return content

    def _normalize_optional(self, value: str | None) -> str | None:
        if value is None:
            return None
        normalized_value = value.strip()
        if normalized_value == "":
            return None
        return normalized_value
