import logging
import os
from autogen import ConversableAgent, LLMConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load LLM configuration
llm_config = LLMConfig.from_json(path="OAI_CONFIG_LIST.json")

# Define agents
coder = ConversableAgent(
    name="coder",
    system_message="You are a Python developer. Write clear, efficient Python code.",
    llm_config=llm_config,
)

reviewer = ConversableAgent(
    name="reviewer",
    system_message=(
        "You are a code reviewer. Analyze provided code and suggest improvements. "
        "Be constructive and specific in your feedback."
    ),
    llm_config=llm_config,
)

# Start a conversation - max_turns counts TOTAL messages (both agents)
# So max_turns=6 means: reviewer->coder, coder->reviewer, reviewer->coder (3 exchanges)
logger.info("Starting conversation between reviewer and coder...")

response = reviewer.run(
    recipient=coder,
    message="Write a Python function that computes Fibonacci numbers.",
    max_turns=3  # Allow for proper back-and-forth conversation
)

logger.info("Conversation completed. Processing results...")

# Process and summarize the conversation
response.process()
final_output = response.summary
logger.info("Final output:\n%s", final_output)

# --- Save code to a file ---
import re

code_blocks = re.findall(r"```(?:python)?\n([\s\S]*?)```", final_output)

if code_blocks:
    code_to_save = "\n\n".join(code_blocks)
    save_path = os.path.join(os.getcwd(), "generated_code.py")
    with open(save_path, "w", encoding="utf-8") as f:
        f.write(code_to_save)
    logger.info("✅ Code saved to %s", save_path)
else:
    logger.warning("⚠️ No code block found in the final output.")