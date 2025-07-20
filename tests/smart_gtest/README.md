# Smart GTest Agent

Simple AI assistant for DonutBuffer testing using LangGraph.

## Features

- 🤖 **LangGraph-powered AI agent** for testing assistance
- 💬 **Interactive dialogue** with specialized C++ testing knowledge
- 🎯 **DonutBuffer focus** - ring buffer and performance testing expertise

## Installation

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Set up environment:**
```bash
# Copy example and edit with your API key
cp env_example.txt .env
# Add: OPENAI_API_KEY=your_key_here
```

## Usage

Run the agent:
```bash
python test_agent.py
```

Example conversation:
```
👤 You: How can I test ring buffer performance?
🤖 Agent: For ring buffer performance testing, I recommend:
1. Throughput benchmarks with varying thread counts
2. Latency measurements under different loads  
3. Memory usage analysis
4. Comparison between mutex and lockfree implementations
```

## Configuration

- **OPENAI_API_KEY**: Your OpenAI API key (required)
- **OPENAI_MODEL**: Model to use (default: gpt-3.5-turbo) 