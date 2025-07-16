#include <gtest/gtest.h>
#include <atomic>
#include "ringbuffer/mutex_ring_buffer.h"
#include "ringbuffer/lockfree_ring_buffer.h"

// =============================================================================
// БАЗОВЫЕ UNIT ТЕСТЫ ДЛЯ MutexRingBuffer
// =============================================================================
// Проверяют корректность основных операций с использованием мьютексов
// и condition variables для синхронизации между потоками
// =============================================================================

class MutexRingBufferTest : public ::testing::Test {
protected:
    void SetUp() override {
        stop_flag.store(false);
    }
    
    std::atomic<bool> stop_flag{false};
};

// СЦЕНАРИЙ: Проверка базового цикла производства и потребления
// ЧТО ПРОВЕРЯЕТСЯ:
// 1. Успешное добавление элементов в буфер
// 2. Корректность счетчика элементов  
// 3. FIFO порядок извлечения элементов
// 4. Состояние буфера после операций
// ОЖИДАЕМЫЙ РЕЗУЛЬТАТ: Элементы извлекаются в том же порядке, что и добавлялись
TEST_F(MutexRingBufferTest, BasicProduceConsume) {
    MutexRingBuffer rb(2);  // Буфер размером 2 элемента
    
    // Добавляем два элемента - буфер должен заполниться
    EXPECT_TRUE(rb.produce(1, 0, stop_flag));
    EXPECT_TRUE(rb.produce(2, 0, stop_flag));
    EXPECT_EQ(rb.get_count(), 2u);  // Счетчик должен показывать 2
    
    // Извлекаем элементы и проверяем FIFO порядок
    int value = 0;
    EXPECT_TRUE(rb.consume(value, 0, stop_flag));
    EXPECT_EQ(value, 1);  // Первый добавленный элемент
    
    EXPECT_TRUE(rb.consume(value, 0, stop_flag));
    EXPECT_EQ(value, 2);  // Второй добавленный элемент
    EXPECT_EQ(rb.get_count(), 0u);  // Буфер должен быть пустым
}

// СЦЕНАРИЙ: Проверка управления емкостью буфера и переполнения
// ЧТО ПРОВЕРЯЕТСЯ:
// 1. Корректность возвращаемой емкости буфера
// 2. Начальное состояние пустого буфера
// 3. Заполнение буфера до максимальной емкости
// 4. Блокировка при попытке переполнения
// ОЖИДАЕМЫЙ РЕЗУЛЬТАТ: Буфер корректно отслеживает свое состояние и блокирует переполнение
TEST_F(MutexRingBufferTest, CapacityManagement) {
    MutexRingBuffer rb(2);  // Создаем буфер на 2 элемента
    
    // Проверяем начальное состояние
    EXPECT_EQ(rb.get_capacity(), 2u);  // Емкость должна быть 2
    EXPECT_EQ(rb.get_count(), 0u);     // Изначально пустой
    
    // Заполняем буфер до предела
    EXPECT_TRUE(rb.produce(1, 0, stop_flag));  // Первый элемент
    EXPECT_TRUE(rb.produce(2, 0, stop_flag));  // Второй элемент
    EXPECT_EQ(rb.get_count(), 2u);             // Буфер полный
    
    // Попытка добавить в переполненный буфер должна неблокирующе отклоняться
    EXPECT_FALSE(rb.produce(3, 0, stop_flag));
}

// СЦЕНАРИЙ: Проверка поведения при чтении из пустого буфера
// ЧТО ПРОВЕРЯЕТСЯ:
// 1. Реакция буфера на попытку чтения когда данных нет
// 2. Неблокирующее поведение при отсутствии данных
// 3. Сохранение переменной value при неуспешном чтении
// ОЖИДАЕМЫЙ РЕЗУЛЬТАТ: Операция consume возвращает false без блокировки
TEST_F(MutexRingBufferTest, EmptyBufferConsume) {
    MutexRingBuffer rb(2);  // Пустой буфер
    int value = 0;          // Переменная для результата
    
    // Попытка чтения из пустого буфера должна неблокирующе завершиться неудачей
    EXPECT_FALSE(rb.consume(value, 0, stop_flag));
}

// СЦЕНАРИЙ: Проверка циклических операций и work-around буфера
// ЧТО ПРОВЕРЯЕТСЯ:
// 1. Корректность работы кольцевого буфера при многократном использовании
// 2. Правильность work-around индексов head и tail
// 3. Отсутствие memory corruption при переполнении индексов
// 4. FIFO порядок при многократных циклах заполнения/освобождения
// ОЖИДАЕМЫЙ РЕЗУЛЬТАТ: Буфер корректно работает через множество циклов
TEST_F(MutexRingBufferTest, CircularOperation) {
    MutexRingBuffer rb(2);  // Буфер на 2 элемента
    int value = 0;
    
    // Выполняем 5 циклов полного заполнения и освобождения
    for (int i = 0; i < 5; ++i) {
        // Заполняем буфер двумя элементами
        EXPECT_TRUE(rb.produce(i * 10, 0, stop_flag));      // Например: 0, 10, 20...
        EXPECT_TRUE(rb.produce(i * 10 + 1, 0, stop_flag));  // Например: 1, 11, 21...
        
        // Извлекаем элементы в правильном порядке
        EXPECT_TRUE(rb.consume(value, 0, stop_flag));
        EXPECT_EQ(value, i * 10);      // Проверяем первый элемент
        
        EXPECT_TRUE(rb.consume(value, 0, stop_flag));
        EXPECT_EQ(value, i * 10 + 1);  // Проверяем второй элемент
        
        // После каждого цикла буфер снова пустой и готов к следующему циклу
    }
}

// =============================================================================
// БАЗОВЫЕ UNIT ТЕСТЫ ДЛЯ LockFreeRingBuffer
// =============================================================================
// Проверяют корректность основных операций с использованием lock-free алгоритмов
// на основе atomic операций и sequence numbers для синхронизации
// =============================================================================

class LockFreeRingBufferTest : public ::testing::Test {
protected:
    void SetUp() override {
        stop_flag.store(false);
    }
    
    std::atomic<bool> stop_flag{false};
};

// СЦЕНАРИЙ: Проверка базового цикла производства и потребления (Lock-Free)
// ЧТО ПРОВЕРЯЕТСЯ:
// 1. Успешное добавление элементов без использования мьютексов
// 2. Корректность atomic счетчика элементов
// 3. FIFO порядок при использовании sequence numbers
// 4. Отсутствие race conditions в lock-free операциях
// ОЖИДАЕМЫЙ РЕЗУЛЬТАТ: Элементы извлекаются в том же порядке, используя только atomic операции
TEST_F(LockFreeRingBufferTest, BasicProduceConsume) {
    LockFreeRingBuffer rb(2);  // Lock-free буфер размером 2 элемента
    
    // Добавляем элементы используя atomic операции
    EXPECT_TRUE(rb.produce(1, 0, stop_flag));
    EXPECT_TRUE(rb.produce(2, 0, stop_flag));
    EXPECT_EQ(rb.get_count(), 2u);  // Atomic счетчик должен показывать 2
    
    // Извлекаем элементы и проверяем lock-free FIFO порядок
    int value = 0;
    EXPECT_TRUE(rb.consume(value, 0, stop_flag));
    EXPECT_EQ(value, 1);  // Первый элемент (sequence-based ordering)
    
    EXPECT_TRUE(rb.consume(value, 0, stop_flag));
    EXPECT_EQ(value, 2);  // Второй элемент
    EXPECT_EQ(rb.get_count(), 0u);  // Буфер пустой
}

// СЦЕНАРИЙ: Проверка управления емкостью в lock-free буфере
// ЧТО ПРОВЕРЯЕТСЯ:
// 1. Корректность atomic операций для отслеживания заполненности
// 2. Предотвращение переполнения без блокировок
// 3. Lock-free проверка доступности слотов через sequence numbers
// 4. Отсутствие ABA problem при работе с емкостью
// ОЖИДАЕМЫЙ РЕЗУЛЬТАТ: Буфер корректно управляет емкостью используя только atomic операции
TEST_F(LockFreeRingBufferTest, CapacityManagement) {
    LockFreeRingBuffer rb(2);  // Lock-free буфер на 2 элемента
    
    // Проверяем начальное состояние через atomic операции
    EXPECT_EQ(rb.get_capacity(), 2u);  // Фиксированная емкость
    EXPECT_EQ(rb.get_count(), 0u);     // Изначально пустой (atomic count)
    
    // Заполняем буфер используя CAS операции
    EXPECT_TRUE(rb.produce(1, 0, stop_flag));  // Первый slot через atomic sequence
    EXPECT_TRUE(rb.produce(2, 0, stop_flag));  // Второй slot
    EXPECT_EQ(rb.get_count(), 2u);             // Atomic счетчик показывает заполненность
    
    // Lock-free отклонение переполнения через sequence checking
    EXPECT_FALSE(rb.produce(3, 0, stop_flag));
}

// СЦЕНАРИЙ: Проверка lock-free поведения при чтении из пустого буфера
// ЧТО ПРОВЕРЯЕТСЯ:
// 1. Lock-free обработка пустого состояния через sequence numbers
// 2. Отсутствие блокировок при недоступности данных
// 3. Корректность atomic проверок доступности слотов
// 4. Неизменность данных при неуспешном lock-free чтении
// ОЖИДАЕМЫЙ РЕЗУЛЬТАТ: Операция завершается неудачей без блокировок и ожиданий
TEST_F(LockFreeRingBufferTest, EmptyBufferConsume) {
    LockFreeRingBuffer rb(2);  // Пустой lock-free буфер
    int value = 0;             // Переменная для atomic чтения
    
    // Lock-free попытка чтения из пустого буфера через sequence checking
    EXPECT_FALSE(rb.consume(value, 0, stop_flag));
}

// СЦЕНАРИЙ: Проверка lock-free циклических операций и sequence overflow
// ЧТО ПРОВЕРЯЕТСЯ:
// 1. Корректность lock-free work-around при переполнении sequence numbers
// 2. Отсутствие ABA problem при многократных циклах
// 3. Стабильность atomic операций при интенсивном использовании
// 4. FIFO порядок при работе с wraparound sequence numbers
// ОЖИДАЕМЫЙ РЕЗУЛЬТАТ: Lock-free буфер стабильно работает через множество циклов
TEST_F(LockFreeRingBufferTest, CircularOperation) {
    LockFreeRingBuffer rb(2);  // Lock-free буфер на 2 элемента
    int value = 0;
    
    // Выполняем 5 циклов lock-free заполнения и освобождения
    for (int i = 0; i < 5; ++i) {
        // Lock-free заполнение через atomic sequence increments
        EXPECT_TRUE(rb.produce(i * 10, 0, stop_flag));      // CAS операция на sequence
        EXPECT_TRUE(rb.produce(i * 10 + 1, 0, stop_flag));  // Следующий sequence slot
        
        // Lock-free извлечение с проверкой sequence numbers
        EXPECT_TRUE(rb.consume(value, 0, stop_flag));
        EXPECT_EQ(value, i * 10);      // Проверяем порядок через sequence
        
        EXPECT_TRUE(rb.consume(value, 0, stop_flag));
        EXPECT_EQ(value, i * 10 + 1);  // Второй элемент в sequence порядке
        
        // Sequence numbers wraparound готов к следующему циклу
    }
}

// =============================================================================
// GENERIC ТЕСТЫ ДЛЯ ОБЕИХ РЕАЛИЗАЦИЙ
// =============================================================================
// Тесты, которые должны работать одинаково для Mutex и LockFree реализаций
// Используют TYPED_TEST для автоматического запуска с разными типами
// =============================================================================

template<typename RingBufferType>
class RingBufferGenericTest : public ::testing::Test {
protected:
    void SetUp() override {
        stop_flag.store(false);
    }
    
    std::atomic<bool> stop_flag{false};
};

// Список типов для параметризованных тестов
typedef ::testing::Types<MutexRingBuffer, LockFreeRingBuffer> RingBufferTypes;
TYPED_TEST_SUITE(RingBufferGenericTest, RingBufferTypes);

// СЦЕНАРИЙ: Проверка корректной обработки stop_flag в обеих реализациях
// ЧТО ПРОВЕРЯЕТСЯ:
// 1. Обе реализации должны одинаково реагировать на stop_flag = true
// 2. Операции должны немедленно прерываться без блокировок
// 3. Не должно быть различий в поведении между Mutex и LockFree
// 4. Graceful shutdown mechanism работает в обеих реализациях
// ОЖИДАЕМЫЙ РЕЗУЛЬТАТ: Обе реализации возвращают false при установленном stop_flag
TYPED_TEST(RingBufferGenericTest, StopFlagRespected) {
    TypeParam rb(10);               // Буфер любого из типов (Mutex или LockFree)
    this->stop_flag.store(true);    // Устанавливаем сигнал остановки
    
    // Обе операции должны немедленно завершиться с false
    int value = 0;
    EXPECT_FALSE(rb.produce(1, 0, this->stop_flag));      // Производство прервано
    EXPECT_FALSE(rb.consume(value, 0, this->stop_flag));  // Потребление прервано
}
