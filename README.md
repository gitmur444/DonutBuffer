# DonutBuffer: Ring Buffer Visualizer

## LinkedIn — Experience (Project)
**AI-Driven Test Assistant • Personal R&D Project**  
*Jan 2025 – Present • Remote*

Designed and built an intelligent assistant that helps C++ engineers work with the company's test-automation stack.

**LLM-driven planning**: the system lets a large-language model dynamically design and refine LangChain/LangGraph workflows on the fly, selecting only the resources I expose (LLM, SQL test-metadata DB, shell & CI tools).

**Hybrid architecture**:
- classical Hierarchical Task Network logic for safe execution paths;
- LLM nodes for reasoning, summarising failures, prioritising flaky tests;
- custom SQL & Shell nodes (read-only guards, whitelists).

**Iterative self-improvement loop**: the agent captures execution errors, feeds them back to the LLM, and regenerates/optimises the graph until the pipeline converges.

**Technologies**: Python 3.12, LangChain / LangGraph, OpenAI GPT-4o, SQLAlchemy (SQLite), FAISS, Docker, GitHub MCP server, Bash tooling.

**Outcomes**:
- cut average "locate-and-rerun failed tests" time from 25 min to under 5 min in internal benchmarks;
- demonstrated safe, read-only SQL generation by LLM using schema-+-example prompting and regex validation;
- prepared a plug-and-play template for integrating additional tools (e.g., Jira, Slack, GitHub Actions).

**Goal**: explore next-gen multi-agent patterns and prove that LLMs can act as adaptive test-orchestration planners while keeping execution secure and auditable.

---

## Project Build

```sh
make
```
- Build is performed from the project root. Makefile automatically creates the build folder, calls cmake and builds the project.
- To clean the build use:
```sh
make clean
```

## Running the Application

On macOS the binary is located inside .app:
```sh
./build/DonutBufferApp.app/Contents/MacOS/DonutBufferApp [options]
```

## Smart GTest System

The project includes an integrated Smart GTest system with PostgreSQL logging:

```sh
# Quick start Smart GTest
cd tests/smart_gtest
./quick_start.sh

# Manual test execution
make build
./build/test_example

# CLI database management
./build/smart_test_cli status
./build/smart_test_cli recent
```

For more details see `tests/smart_gtest/README.md`

## Examples of running with parameters:
```sh
# Example: mutex buffer, 3 producers, 2 consumers, 8 MB buffer, 32 MB data
./build/DonutBufferApp.app/Contents/MacOS/DonutBufferApp --buffer-type mutex --producers 3 --consumers 2 --buffer-size_mb 8 --total-transfer_mb 32

# Example: lockfree buffer, 1 producer, 1 consumer, 4 MB buffer, 16 MB data
./build/DonutBufferApp.app/Contents/MacOS/DonutBufferApp --buffer-type lockfree --producers 1 --consumers 1 --buffer-size_mb 4 --total-transfer_mb 16

# Example: concurrent_queue, run without GUI
./build/DonutBufferApp.app/Contents/MacOS/DonutBufferApp --nogui --buffer-type concurrent_queue --producers 2 --consumers 2 --buffer-size_mb 2 --total-transfer_mb 8
```

## Command Line Options

### C++ Entry Point (`DonutBufferApp`)
- `--nogui` &mdash; run without graphical interface. Default value is `true`.
- `--mutex-vs-lockfree` &mdash; execute comparison test between `MutexRingBuffer` and `LockFreeRingBuffer` and exit.
- `--concurrent-vs-lockfree` &mdash; execute test of `ConcurrentQueue` against `LockFreeRingBuffer` and exit.
- `--buffer-type {lockfree, mutex, concurrent_queue}` &mdash; type of buffer used.
- `--producers N` &mdash; number of producer threads.
- `--consumers N` &mdash; number of consumer threads.
- `--buffer-size_mb N` &mdash; buffer size in megabytes.
- `--total-transfer_mb N` &mdash; total amount of data transferred through the ring buffer in megabytes.

