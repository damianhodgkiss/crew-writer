FORMATTING_RULES = """IMPORTANT FORMATTING RULES:
    - Start the article directly with the main heading
    - Do not include any commentary or notes about the process
    - Do not include phrases like "Based on..." or "I've made..."
    - Do not use placeholders like "[Update this...]" or "[Add more...]"
    - Do not reference previous sections or future content
    - Use proper Markdown headings starting with #
    - Always write complete, self-contained sections"""

CRITICAL_RULES = """CRITICAL RULES:
    - NEVER use placeholders or references like "Continue with..." or "As mentioned above..."
    - NEVER mention previous parts or sections
    - NEVER use phrases that refer to previous or future content
    - NEVER use square brackets to indicate content continuation
    - NEVER use ellipsis (...) to indicate skipped content
    - ALWAYS write complete, self-contained content
    - ALWAYS include full implementation details
    - ALWAYS write every section in full, even if unchanged
    - ALWAYS write the entire content as if it's the first and only version
    - ALWAYS ensure the entire content is coherent and complete
    - ALWAYS repeat all content when continuing or revising"""

CONTINUATION_RULES = """For long content:
    - If you need to continue, end your message with exactly:
      TO BE CONTINUED...
    
    - When finished, end with exactly:
      {completion_marker}
      {completion_message}"""
