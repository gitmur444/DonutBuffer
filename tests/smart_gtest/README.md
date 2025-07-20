# Smart GTest Agent

AI-powered testing assistant for DonutBuffer project using LangGraph. This agent integrates with the testing system to provide intelligent analysis and recommendations for C++ ring buffer performance testing.

## Features

- 🤖 **LangGraph-powered AI agent** for intelligent test analysis
- 🧪 **Testing context awareness** - recognizes test-related queries
- ⚡ **Performance analysis** - specialized in ring buffer benchmarks
- 🔄 **Interactive dialogue** - conversational interface for testing insights
- 🎯 **DonutBuffer integration** - tailored for mutex vs lockfree comparisons

## Installation

1. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

2. **Set up environment variables:**
```bash
# Copy the example file
cp env_example.txt .env

# Edit .env with your OpenAI API key
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-3.5-turbo
```

## Usage

### Basic Agent Interaction

Run the interactive agent:
```bash
python test_agent.py
```

The agent will start an interactive session where you can:
- Ask questions about test results
- Get performance analysis recommendations  
- Receive suggestions for optimization
- Discuss C++ testing strategies

### Example Conversations

**Performance Analysis:**
```
👤 You: How can I improve ring buffer performance?
🤖 Agent: 🧪 Smart GTest Analysis

For ring buffer performance improvements, consider these strategies:
1. Lockfree implementation using atomic operations
2. Memory alignment and cache optimization
3. Batch operations to reduce contention
4. NUMA-aware memory allocation

*Detected keywords: performance, ring buffer*
```

**Test Strategy:**
```
👤 You: What tests should I run for mutex vs lockfree comparison?
🤖 Agent: 🧪 Smart GTest Analysis

For comprehensive mutex vs lockfree comparison:
1. Throughput benchmarks under varying load
2. Latency measurements (min/max/avg)
3. CPU utilization analysis
4. Memory usage patterns
5. Scalability tests with different thread counts

*Detected keywords: test, mutex, lockfree*
```

## Integration with GTest System

The agent integrates with the existing Smart GTest logging system:

- **Context awareness**: Automatically detects test-related queries
- **Keyword detection**: Recognizes performance, benchmark, ring buffer terms
- **Specialized responses**: Provides DonutBuffer-specific recommendations
- **Future integration**: Can be extended to analyze actual test results

## Architecture

The agent uses LangGraph with a simple workflow:

```
User Input → Analyze Input → Generate Response → Format Output
```

### Components:

1. **AgentState**: Manages conversation state and context
2. **SmartGTestAgent**: Main agent class with LangGraph workflow
3. **Analysis nodes**: Input analysis, LLM generation, output formatting
4. **Context detection**: Identifies test-related vs general queries

## Development

### Extending the Agent

To add new functionality:

1. **Add new nodes** to the LangGraph workflow
2. **Extend AgentState** with additional fields
3. **Create specialized prompts** for different contexts
4. **Integrate with test data** sources

### Example Extension - Test Result Analysis:

```python
async def _analyze_test_results(self, state: AgentState) -> AgentState:
    """Analyze recent test results from the database"""
    # Read from PostgreSQL Smart GTest results
    # Provide insights based on test outcomes
    pass
```

## Configuration

- **OPENAI_API_KEY**: Your OpenAI API key (required)
- **OPENAI_MODEL**: Model to use (default: gpt-3.5-turbo)
- **LANGCHAIN_TRACING_V2**: Enable LangSmith tracing (optional)
- **LANGCHAIN_PROJECT**: LangSmith project name (optional)

## Future Enhancements

- [ ] Direct integration with PostgreSQL test results
- [ ] Automated test report generation
- [ ] Performance trend analysis
- [ ] Integration with CI/CD pipelines
- [ ] Voice interface for hands-free testing
- [ ] Test case generation suggestions 