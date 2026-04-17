"""Unit tests for token_counter."""

from __future__ import annotations

from wikibench.runtime.token_counter import count_messages_tokens, count_tokens


class TestCountTokens:
    def test_empty_string(self) -> None:
        assert count_tokens("") == 0

    def test_nonempty_returns_positive(self) -> None:
        assert count_tokens("Hello, world!") > 0

    def test_longer_text_more_tokens(self) -> None:
        short = count_tokens("Hi")
        long = count_tokens("Hi " * 100)
        assert long > short

    def test_gpt4o_mini(self) -> None:
        # "Hello" should be 1 token for most OpenAI models
        result = count_tokens("Hello", model="gpt-4o-mini")
        assert 1 <= result <= 5

    def test_unknown_model_fallback(self) -> None:
        # Should not raise; falls back to char estimate
        result = count_tokens("Hello world", model="unknown-model-xyz")
        assert result > 0

    def test_bytes_like_content(self) -> None:
        text = "a" * 400
        tokens = count_tokens(text, model="gpt-4o-mini")
        # rough expectation: ~100 tokens for 400 chars
        assert tokens > 0


class TestCountMessagesTokens:
    def test_single_user_message(self) -> None:
        msgs = [{"role": "user", "content": "What is X?"}]
        total = count_messages_tokens(msgs, model="gpt-4o-mini")
        assert total > 0

    def test_system_plus_user(self) -> None:
        msgs = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello!"},
        ]
        total = count_messages_tokens(msgs)
        assert total > count_messages_tokens([msgs[1]])

    def test_empty_messages(self) -> None:
        assert count_messages_tokens([]) == 3  # just the priming tokens
