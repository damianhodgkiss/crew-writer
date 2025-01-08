import dotenv
from pathlib import Path
from typing import Optional
import os
from ..common.content_manager import ContentManager
from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager
from .PROMPTS import (
    EDITOR_SYSTEM_PROMPT,
    USER_PROXY_SYSTEM_PROMPT,
    MODIFICATION_PROMPT,
)

config_list = [
    {
        "model": "claude-3-5-sonnet-latest",
        "api_key": os.getenv("ANTHROPIC_API_KEY"),
        "api_type": "anthropic",
    }
]

editor = AssistantAgent(
    name="editor",
    description="You are a content editor.",
    system_message=EDITOR_SYSTEM_PROMPT,
    llm_config={"config_list": config_list},
)


def modify_article(filepath: Path, instructions: str) -> str:
    """Modify an existing article according to instructions"""
    content_manager = ContentManager()
    user_proxy = UserProxyAgent(
        name="user_proxy",
        human_input_mode="TERMINATE",
        code_execution_config=False,
        system_message=USER_PROXY_SYSTEM_PROMPT,
    )

    # Read the original content
    with open(filepath, "r", encoding="utf-8") as f:
        original_content = f.read()

    content_manager.reset()

    def message_handler(message):
        content = message.get("content", "")
        name = message.get("name", "")

        if name == "editor":
            # Handle parts the same way as writer
            if "PART" in content and "OF" in content:
                content_manager.append_content(content)
                if not content_manager.is_complete():
                    return False
                # Replace content with complete modifications when all parts received
                message["content"] = content_manager.get_full_content()
            else:
                # For non-part responses, still process them
                content_manager.append_content(content)

        return "MODIFICATIONS COMPLETE" in content

    allowed_transitions = {
        user_proxy: [editor],
        editor: [user_proxy],
    }

    groupchat = GroupChat(
        agents=[user_proxy, editor],
        messages=[],
        max_round=10,
        allowed_or_disallowed_speaker_transitions=allowed_transitions,
        speaker_transitions_type="allowed",
    )

    manager = GroupChatManager(groupchat=groupchat, is_termination_msg=message_handler)

    user_proxy.initiate_chat(
        manager,
        message=MODIFICATION_PROMPT.format(
            instructions=instructions,
            original_content=original_content,
        ),
    )

    return content_manager.get_full_content()
