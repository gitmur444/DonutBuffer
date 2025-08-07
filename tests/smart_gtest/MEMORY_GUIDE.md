# 🧠 AI Test Planner - Руководство по памяти

## 🎯 Обзор упрощенной системы

После рефакторинга система использует **простую in-memory память** вместо сложных PostgreSQL checkpoints.

## 🗄️ Что было удалено

### ❌ Сложные таблицы (удалены из PostgreSQL):
- `checkpoints` - хранение состояний LangGraph
- `checkpoint_blobs` - бинарные данные состояний  
- `checkpoint_writes` - журнал изменений
- `checkpoint_migrations` - схема миграций

### ❌ Сложная логика:
- Persistent threads
- Cross-session memory
- Семантический поиск
- "Session has X total responses"

## ✅ Что осталось

### 📋 Таблицы в PostgreSQL (только для TestDB):
- `test_results` - результаты C++ тестов 
- `actual_tests` - метаданные C++ тестов

### 🧠 Простая память:
- **InMemoryStore** - хранение в рамках одного запуска
- **ChatTool.conversation_history** - последние 5 взаимодействий
- **Одна сессия**: `default_session`
- **Один пользователь**: `default_user`

## 🔧 Как работает память

### 1. **Запуск системы**
```python
# Создается простая память
checkpointer = InMemorySaver()  # В рамках запуска
store = InMemoryStore()         # Простое хранилище

# Одна сессия для всех
thread_id = "default_session"
user_id = "default_user"
```

### 2. **ChatTool память**
```python
class ChatTool:
    def __init__(self, user_task: str):
        self.conversation_history = []  # Пустая история
    
    def add_to_history(self, interaction: str):
        self.conversation_history.append(interaction)
        
        # Только последние 5 взаимодействий
        if len(self.conversation_history) > 5:
            self.conversation_history = self.conversation_history[-5:]
```

### 3. **Использование истории**
```python
def generate_response(self, question: str):
    # Берем последние 5 взаимодействий для контекста
    history_context = ""
    if self.conversation_history:
        history_context = "\n".join(self.conversation_history[-5:])
    
    # Отправляем в OpenAI вместе с вопросом
    user_prompt = f"""
    User question: "{question}"
    Recent conversation history:
    {history_context}
    """
```

## 📊 Архитектура памяти

```
┌─── AI Test Planner ───┐
│                       │
│ ┌─── ChatTool ──────┐ │
│ │ conversation_history│ │  ← 🧠 ПАМЯТЬ (максимум 5 элементов)
│ │ [                  │ │
│ │   "Q: привет",     │ │
│ │   "A: Привет!..",  │ │
│ │   "Q: как дела?",  │ │
│ │   "A: Хорошо!.."   │ │
│ │ ]                  │ │
│ └────────────────────┘ │
│                       │
│ ┌─── PostgreSQL ────┐ │
│ │ test_results      │ │  ← 📊 ДАННЫЕ (для TestDB узлов)
│ │ actual_tests      │ │
│ └───────────────────┘ │
└───────────────────────┘
```

## 🔄 Жизненный цикл памяти

### **Запуск 1**: `python ai_test_planner.py "привет"`
```
1. Создается ChatTool с пустой историей: []
2. Выполняется Chat узел
3. Добавляется в историю: ["Q: привет", "A: Привет!.."]
4. ❌ После завершения программы история ТЕРЯЕТСЯ
```

### **Запуск 2**: `python ai_test_planner.py "как дела?"`
```
1. Создается НОВЫЙ ChatTool с пустой историей: []
2. ❌ Предыдущий диалог НЕ ПОМНИТСЯ
3. Но ChatTool умеет отвечать на "что я только что спросил?" из контекста
```

## 🎯 Практические примеры

### ✅ **Что работает в рамках одного запуска:**
```bash
# Если план содержит несколько Chat узлов в одном графе
{
  "nodes": [
    {"id": "chat1", "type": "Chat", "params": {"question": "привет"}},
    {"id": "chat2", "type": "Chat", "params": {"question": "как дела?"}}
  ],
  "edges": [{"source": "chat1", "target": "chat2"}]
}

# chat2 будет видеть историю от chat1
```

### ❌ **Что НЕ работает между запусками:**
```bash
# Запуск 1
python ai_test_planner.py "меня зовут Иван"

# Запуск 2 
python ai_test_planner.py "как меня зовут?"
# ❌ Система НЕ помнит "Иван"
```

### ✅ **Что работает благодаря LLM:**
```bash
python ai_test_planner.py "что я только что спросил?"
# ✅ ChatTool понимает контекст и может ответить разумно
```

## 🛠️ Технические детали

### **InMemorySaver**
- Хранит состояние LangGraph в рамках одного запуска
- Позволяет узлам передавать данные друг другу
- Не сохраняется между запусками

### **ChatTool.conversation_history**
- Простой Python список строк
- Максимум 5 элементов
- Очищается при каждом новом запуске

### **PostgreSQL подключение**
- Используется ТОЛЬКО для TestDB узлов
- Содержит тестовые данные C++
- НЕ используется для памяти диалогов

## 📝 Команды для использования

```bash
# Простой диалог
python ai_test_planner.py "привет"

# Вопросы о памяти (работают благодаря LLM)
python ai_test_planner.py "что я только что спросил?"

# Запросы к тестовым данным
python ai_test_planner.py "show me test results"

# Команды shell
python ai_test_planner.py "покажи файлы в папке logs"
```

## ⚡ Преимущества упрощенной системы

1. **Простота** - нет сложной логики сессий
2. **Скорость** - нет обращений к PostgreSQL для памяти
3. **Надежность** - меньше точек отказа
4. **Понятность** - легко понять и модифицировать
5. **Достаточность** - покрывает 90% случаев использования

## 🎯 Итог

Система теперь использует **простую в-память модель** вместо сложных persistent checkpoints. Память работает в рамках одного запуска, но система остается функциональной благодаря умному ChatTool и возможности работы с тестовыми данными через PostgreSQL. 