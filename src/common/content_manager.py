class ContentManager:
    def __init__(self):
        self._full_content = []
        self._is_complete = False

    def _clean_content_lines(
        self, content_lines: list[str], phrases_to_check: list[str]
    ) -> list[str]:
        """Helper method to clean content lines by removing lines that start with specified phrases"""
        # Remove empty lines from start and end
        while content_lines and not content_lines[0].strip():
            content_lines.pop(0)
        while content_lines and not content_lines[-1].strip():
            content_lines.pop()

        # Remove lines that start with any of the phrases or match PART X OF Y pattern
        cleaned_lines = [
            line
            for line in content_lines
            if not (
                any(
                    line.strip().startswith(phrase) or phrase in line
                    for phrase in phrases_to_check
                )
                or line.strip().startswith(
                    "PART "
                )  # Explicit check for PART X OF Y pattern
            )
        ]

        return cleaned_lines

    def append_content(self, content: str) -> None:
        content_lines = content.split("\n")

        # Define phrases to check and remove
        phrases_to_check = [
            "MODIFICATIONS COMPLETE",
            "TO BE CONTINUED",
            "END OF MODIFICATIONS",
            "END OF ARTICLE",
            "DRAFT COMPLETE",
            "Here's the modified",
            "I've made these changes",
            "I have made",
            "Here is the",
            "The modified article",
            "@user_proxy",
        ]
        content_lines = self._clean_content_lines(content_lines, phrases_to_check)

        # Set completion status based on the original message
        self._is_complete = any(
            marker in content for marker in ["END OF ARTICLE", "END OF MODIFICATIONS"]
        )

        # Only extend if we have content
        if content_lines:
            if self._full_content and self._full_content[-1].strip():
                self._full_content.append("")  # Add separator line between parts
            self._full_content.extend(content_lines)

    def get_full_content(self) -> str:
        # Clean up any extra newlines
        content = "\n".join(self._full_content).strip()
        # Ensure exactly one newline at the end
        return content + "\n"

    def is_complete(self) -> bool:
        return self._is_complete

    def reset(self) -> None:
        self._full_content = []
        self._is_complete = False
