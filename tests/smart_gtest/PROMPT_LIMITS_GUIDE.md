# 📏 Руководство по лимитам System Prompt

## 📊 **Текущий размер нашего промпта**

```
📝 Символы: 2,661
📄 Строки: 60  
📖 Слова: 295
🪙 Токены: ~665
```

## 🚦 **Лимиты OpenAI API**

### **GPT-4o / GPT-4**
- **Общий контекст**: 128,000 токенов
- **System prompt**: до ~60,000 токенов (практически)
- **Наш промпт использует**: 0.5% от лимита ✅
- **Можно добавить**: ~59,335 токенов

### **GPT-3.5-turbo**
- **Общий контекст**: 16,385 токенов
- **System prompt**: до ~8,000 токенов (практически)
- **Наш промпт использует**: 4.1% от лимита ✅
- **Можно добавить**: ~7,335 токенов

## 📐 **Что такое токены?**

### **Определение**
- **Токен** - базовая единица обработки текста в LLM
- **1 токен** ≈ 4 символа (для английского)
- **1 токен** ≈ 0.75 слова (в среднем)

### **Примеры токенизации**
```
"Hello" → 1 токен
"Hello world" → 2 токена
"AI Test Planner" → 3 токена
"{"id": "test"}" → 5 токенов
```

## 🎯 **Практические лимиты**

### ✅ **Размеры промптов**
| Размер | Токены | Оценка | Рекомендация |
|--------|---------|---------|---------------|
| Маленький | < 1,000 | ✅ Отлично | Можно расширять |
| Средний | 1,000-5,000 | ✅ Хорошо | Место есть |
| Большой | 5,000-10,000 | ⚠️ Средне | Следить за ростом |
| Очень большой | > 10,000 | ❌ Много | Нужна оптимизация |

### 📈 **Наш статус**: ОТЛИЧНЫЙ (665 токенов)

## 🚀 **Возможности расширения**

### **Что можно добавить в промпт:**

#### 🔧 **Новые типы узлов** (~100-300 токенов за узел)
```
7. FileRead - Read file contents
params: {"path": "file.txt", "lines": "1-10"}
- Use for: reading logs, configs, code files
- Supports line ranges and encoding detection
```

#### 📊 **Расширенная схема БД** (~200-500 токенов)
```
Extended database schema:
- performance_metrics: benchmark_id, test_name, cpu_usage, memory_mb, duration_ms
- test_history: run_id, test_suite, timestamp, environment, git_commit
- failure_analysis: failure_id, test_name, error_type, stack_trace, fix_suggestion
```

#### 🎯 **Больше примеров** (~150-300 токенов за пример)
```
Example with multiple nodes:
{
  "nodes": [
    {"id": "logs", "type": "FileRead", "params": {"path": "test.log"}},
    {"id": "analysis", "type": "LLMFormat", "params": {"prompt": "Analyze errors"}}
  ],
  "edges": [{"source": "logs", "target": "analysis"}]
}
```

#### 📝 **Детальные инструкции** (~100-500 токенов)
```
Planning guidelines:
- Use Chat for simple Q&A and conversations
- Use TestDB for data queries and analysis  
- Use Shell for file operations and system commands
- Chain nodes with LLMFormat for human-readable output
```

## ⚠️ **Когда нужна оптимизация**

### **Сигналы что промпт слишком большой:**
1. **Медленные ответы** - большой промпт = больше обработки
2. **Высокая стоимость** - каждый токен стоит денег
3. **Ошибки API** - превышение лимитов
4. **Плохое качество** - слишком много информации = путаница

### **Техники оптимизации:**

#### 🔄 **Вынос в отдельные файлы**
```python
# Вместо длинного промпта в коде
with open('prompts/node_descriptions.txt', 'r') as f:
    node_descriptions = f.read()

system_prompt = f"""
You are AI Test Assistant.
{node_descriptions}
Return only JSON.
"""
```

#### 📦 **Модульные промпты**
```python
def build_system_prompt(include_examples=True, include_extended_schema=False):
    prompt = BASE_PROMPT
    
    if include_examples:
        prompt += EXAMPLES_SECTION
    
    if include_extended_schema:
        prompt += EXTENDED_SCHEMA
    
    return prompt
```

#### 🎯 **Условная загрузка**
```python
# Загружать детали только когда нужно
if task_requires_database:
    system_prompt += DATABASE_SCHEMA
    
if task_requires_files:
    system_prompt += FILE_OPERATIONS
```

## 💰 **Стоимость токенов**

### **Цены (примерные)**
- **GPT-4o**: $5/1M input токенов
- **GPT-3.5**: $0.5/1M input токенов

### **Наш промпт**
- **GPT-4o**: $0.003 за запрос
- **GPT-3.5**: $0.0003 за запрос

**Экономия**: наш маленький промпт = низкая стоимость! 💰

## 📋 **Рекомендации**

### ✅ **Что делать сейчас**
1. **Промпт отличного размера** - можно смело расширять
2. **Добавлять новые узлы** по мере необходимости
3. **Больше примеров** для лучшего планирования
4. **Детальные инструкции** для edge cases

### 🚀 **Планы расширения**
1. **FileRead узел** для работы с файлами
2. **Performance узел** для бенчмарков  
3. **Git узел** для работы с репозиторием
4. **Docker узел** для контейнеров

### 📊 **Мониторинг**
- Периодически запускать `analyze_prompt_size.py`
- Следить за качеством планирования
- Измерять время ответа
- Контролировать стоимость

## 🎯 **Итог**

**Наш system_prompt имеет ОТЛИЧНЫЙ размер!**

- ✅ Маленький и эффективный (665 токенов)
- ✅ Быстрые ответы
- ✅ Низкая стоимость  
- ✅ Высокое качество планирования
- ✅ Огромный запас для расширения

**Можно смело добавлять новую функциональность!** 🚀 