"""
Node usage examples for AI Test Planner system prompt
"""

def get_examples_text():
    """Get node usage examples for system prompt"""
    
    return """
        Node Usage Examples:

        Chat node (for conversations and simple questions):
        {"id": "chat1", "type": "Chat", "params": {"style": "friendly"}}
        {"id": "chat2", "type": "Chat", "params": {"style": "technical", "context": "additional info"}}

        TestDB node (for database queries using Smart SQL - ONLY intent allowed):
        {"id": "query1", "type": "TestDB", "params": {"intent": "показать все актуальные тесты с результатами"}}
        {"id": "query2", "type": "TestDB", "params": {"intent": "найти неудачные тесты", "context": "нужен анализ проблем"}}
        {"id": "query3", "type": "TestDB", "params": {"intent": "статистика по тестам по статусам"}}
        {"id": "query4", "type": "TestDB", "params": {"intent": "показать последние 10 запусков тестов"}}

        Shell node (for system commands):
        {"id": "shell1", "type": "Shell", "params": {"command": "ls -la logs/"}}
        {"id": "shell2", "type": "Shell", "params": {"command": "cat test.log | grep ERROR"}}

        LLMFormat node (for formatting data):
        {"id": "format1", "type": "LLMFormat", "params": {"prompt": "Summarize test results", "format": "summary"}}
        {"id": "format2", "type": "LLMFormat", "params": {"prompt": "Create detailed report", "format": "report"}}

        Join node (for combining multiple inputs):
        {"id": "join1", "type": "Join", "params": {"mode": "all", "separator": "\\n---\\n"}}
        {"id": "join2", "type": "Join", "params": {"mode": "any"}}

        UserTask node (for accessing original user request):
        {"id": "task1", "type": "UserTask", "params": {}}

        Plan Structure Examples (IMPORTANT - TestDB must use "intent", never "sql"):
        Single node: {"nodes": [{"id": "chat1", "type": "Chat", "params": {"style": "friendly"}}], "edges": []}
        Two nodes: {"nodes": [{"id": "query", "type": "TestDB", "params": {"intent": "показать все тесты"}}, {"id": "format", "type": "LLMFormat", "params": {"prompt": "создать таблицу тестов", "format": "report"}}], "edges": [{"source": "query", "target": "format"}]}
    """ 