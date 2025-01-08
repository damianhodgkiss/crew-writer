import os
import json
from ..common.content_manager import ContentManager
from ..common.seo_tools import SEOTools
from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager
from autogen.agentchat.contrib.capabilities import transform_messages, transforms
from .PROMPTS import (
    RESEARCHER_SYSTEM_PROMPT,
    KEYWORD_SPECIALIST_SYSTEM_PROMPT,
    WRITER_SYSTEM_PROMPT,
    EDITOR_SYSTEM_PROMPT,
    USER_PROXY_SYSTEM_PROMPT,
    INITIAL_PROMPT,
)

context_handling = transform_messages.TransformMessages(
    transforms=[
        # transforms.MessageHistoryLimiter(max_messages=10, keep_first_message=True),
        transforms.MessageTokenLimiter(
            max_tokens=40000,
            max_tokens_per_message=15000,
            model="gpt-4-32k",
        ),
    ]
)

config_list = [
    {
        "model": "claude-3-5-sonnet-latest",
        "api_key": os.getenv("ANTHROPIC_API_KEY"),
        "api_type": "anthropic",
        "api_rate_limit": 1,
        "max_retries": 3,
    }
]

researcher = AssistantAgent(
    name="researcher",
    description="You are a competitive research specialist.",
    system_message=RESEARCHER_SYSTEM_PROMPT,
    llm_config={"config_list": config_list},
)
context_handling.add_to_agent(researcher)

keyword_specialist = AssistantAgent(
    name="keyword_specialist",
    description="You are an SEO keyword specialist.",
    system_message=KEYWORD_SPECIALIST_SYSTEM_PROMPT,
    llm_config={"config_list": config_list},
)
context_handling.add_to_agent(keyword_specialist)

writer = AssistantAgent(
    name="writer",
    description="You are a professional content writer.",
    system_message=WRITER_SYSTEM_PROMPT,
    llm_config={"config_list": config_list},
)
context_handling.add_to_agent(writer)

editor = AssistantAgent(
    name="editor",
    description="You are a content editor.",
    system_message=EDITOR_SYSTEM_PROMPT,
    llm_config={"config_list": config_list},
)
context_handling.add_to_agent(editor)


def create_article(topic: str, content_guidelines: list[str] = None) -> str:
    """Create an article about the given topic"""
    content_manager = ContentManager()
    seo_tools = SEOTools()
    user_proxy = UserProxyAgent(
        name="user_proxy",
        human_input_mode="TERMINATE",
        code_execution_config=False,
        system_message=USER_PROXY_SYSTEM_PROMPT,
    )

    research_data = seo_tools.analyze_competition(topic)
    content_manager.reset()

    # Format content guidelines as a string, or use empty string if None
    content_guidelines = (
        "\n".join(f"- {guideline}" for guideline in content_guidelines)
        if content_guidelines
        else "No specific content guidelines"
    )

    def message_handler(message):
        content = message.get("content", "")
        name = message.get("name", "")

        if name == "writer":
            content_manager.append_content(content)
            if not content_manager.is_complete():
                return False
            # Replace content with complete article when all parts received
            message["content"] = content_manager.get_full_content()

        return "ARTICLE COMPLETE" in content

    allowed_transitions = {
        user_proxy: [researcher],
        researcher: [keyword_specialist],
        keyword_specialist: [writer],
        writer: [editor],
        editor: [writer],
    }

    groupchat = GroupChat(
        agents=[user_proxy, researcher, keyword_specialist, writer, editor],
        messages=[],
        max_round=30,
        allowed_or_disallowed_speaker_transitions=allowed_transitions,
        speaker_transitions_type="allowed",
    )

    manager = GroupChatManager(groupchat=groupchat, is_termination_msg=message_handler)

    user_proxy.initiate_chat(
        manager,
        message=INITIAL_PROMPT.format(
            topic=topic,
            content_guidelines=content_guidelines,
            research_data=json.dumps(research_data, indent=2),
        ),
    )

    return content_manager.get_full_content()
