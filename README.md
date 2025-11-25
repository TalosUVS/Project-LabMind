# AG2 Framework with Gemini API

A powerful integration that combines Microsoft's AG2 (AutoGen) framework with Google's Gemini API to create and orchestrate intelligent AI agents.

## 🌟 Overview

This project demonstrates how to leverage the AG2 framework alongside Google's Gemini models to build multi-agent systems capable of collaborative problem-solving, complex task execution, and autonomous workflows.

## ✨ Features

- **Multi-Agent Orchestration**: Create and manage multiple AI agents with distinct roles
- **Gemini Integration**: Utilize Google's latest Gemini models for advanced reasoning
- **Flexible Architecture**: Easy configuration and customization of agent behaviors
- **Collaborative Problem Solving**: Agents can work together to solve complex tasks
- **Code Execution**: Built-in support for executing and testing generated code

## 📋 Prerequisites

- Python 3.10 or higher
- Google Cloud account with Gemini API access
- AG2 framework installed

## 🚀 Installation

1. Clone the repository:
```bash
git clone https://github.com/TalosUVS/Project-LabMind.git
cd Project-LabMind
```

2. Install required dependencies:
```bash
pip install ag2[gemini]
```

3. Create your configuration file `OAI_CONFIG_LIST.json`:
```json
{
  "model": "gemini-1.5-pro",
  "api_key": "${GEMINI_API_KEY}",
  "api_type": "google"
}
```

4. Set up:

## 🔧 Configuration File

Create an `OAI_CONFIG_LIST.json` file in your project root:

```json
{
  "model": "gemini-1.5-pro",
  "api_key": "${GEMINI_API_KEY}",
  "api_type": "google"
}
```

## 💡 Quick Start

```python
import logging
from autogen import ConversableAgent, LLMConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load LLM configuration from JSON file
llm_config = LLMConfig.from_json(path="OAI_CONFIG_LIST.json")

# Create agents with Gemini
assistant = ConversableAgent(
    name="assistant",
    system_message="You are a helpful AI assistant.",
    llm_config=llm_config,
)

user_proxy = ConversableAgent(
    name="user_proxy",
    system_message="You represent the user and execute code.",
    llm_config=llm_config,
)

# Start conversation
response = user_proxy.run(
    recipient=assistant,
    message="Help me analyze this dataset and create visualizations",
    max_turns=5
)

# Process and get results
response.process()
final_output = response.summary
logger.info("Final output:\n%s", final_output)
```

## 🔧 Configuration

### Agent Setup

You can customize agents with different configurations:

```python
config_list = [
    {
        "model": "gemini-1.5-pro",
        "api_key": os.getenv("GEMINI_API_KEY"),
        "temperature": 0.7,
        "max_tokens": 2048
    }
]

agent = ConversableAgent(
    name="DataAnalyst",
    system_message="You are a data analysis expert.",
    llm_config={"config_list": config_list}
)
```

## 📖 Usage Examples

### Example 1: Code Generation and Review
```python
import logging
from autogen import ConversableAgent, LLMConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load configuration
llm_config = LLMConfig.from_json(path="OAI_CONFIG_LIST.json")

# Define agents
coder = ConversableAgent(
    name="coder",
    system_message="You are a Python developer. Write short Python scripts.",
    llm_config=llm_config,
)

reviewer = ConversableAgent(
    name="reviewer",
    system_message=(
        "You are a code reviewer. Analyze provided code and suggest improvements. "
        "Do not generate code, only suggest improvements."
    ),
    llm_config=llm_config,
)

# Start conversation
response = reviewer.run(
    recipient=coder,
    message="Write a Python function that computes Fibonacci numbers.",
    max_turns=3
)

# Process results
response.process()
final_output = response.summary
logger.info("Final output:\n%s", final_output)
```

### Example 2: Data Analysis Agent
```python
data_analyst = ConversableAgent(
    name="data_analyst",
    system_message="You analyze data and provide insights.",
    llm_config=llm_config,
)

researcher = ConversableAgent(
    name="researcher",
    system_message="You ask questions and interpret results.",
    llm_config=llm_config,
)

response = researcher.run(
    recipient=data_analyst,
    message="Analyze the sales trends for Q4 2024.",
    max_turns=5
)

response.process()
logger.info("Analysis complete:\n%s", response.summary)
```

### Example 3: Multi-Turn Conversation
```python
teacher = ConversableAgent(
    name="teacher",
    system_message="You explain complex topics simply.",
    llm_config=llm_config,
)

student = ConversableAgent(
    name="student",
    system_message="You ask follow-up questions to understand better.",
    llm_config=llm_config,
)

response = student.run(
    recipient=teacher,
    message="Explain how machine learning works.",
    max_turns=10
)

response.process()
print(response.summary)
```

## 🎯 Use Cases

- **Software Development**: Collaborative coding with multiple specialized agents
- **Data Analysis**: Automated data exploration and visualization
- **Research Assistant**: Literature review and summary generation
- **Content Creation**: Multi-stage content generation and editing
- **Problem Solving**: Complex multi-step reasoning tasks

## 🛠️ Advanced Features

### Response Processing
Every conversation returns a response object that can be processed:

```python
response = agent1.run(
    recipient=agent2,
    message="Your task here",
    max_turns=5
)

# Process the conversation
response.process()

# Access the summary
summary = response.summary
logger.info("Summary: %s", summary)
```

### Logging and Debugging
Enable detailed logging to track agent conversations:

```python
import logging

# Set logging level
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
```

### Custom System Messages
Tailor agent behavior with specific instructions:

```python
specialized_agent = ConversableAgent(
    name="specialist",
    system_message=(
        "You are an expert in X. "
        "Always provide detailed explanations. "
        "Use examples when possible."
    ),
    llm_config=llm_config,
)
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request


## ⚠️ Troubleshooting

### Common Issues

**Configuration File Not Found**: Ensure `OAI_CONFIG_LIST.json` is in your project root directory

**API Key Error**: Verify your Gemini API key is properly set in environment variables or the config file

**Import Error**: Make sure you've installed the correct package with `pip install ag2[gemini]`

**Max Turns Reached**: Increase the `max_turns` parameter in the `run()` method if conversations are cut short

**Response Processing Error**: Always call `response.process()` before accessing `response.summary`
