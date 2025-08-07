#include <iostream>
#include <type_traits>
#include <cassert>

// ✅ Способ #1: Классическая рекурсивная специализация (C++98)
template<int N>
struct factorial {
    static constexpr int value = N * factorial<N-1>::value;
};

// Специализация для остановки рекурсии
template<>
struct factorial<0> {
    static constexpr int value = 1;
};

// ✅ Способ #2: Constexpr функция (C++11+) - РЕКОМЕНДУЕТСЯ
template<typename T>
constexpr T factorial_func(T n) {
    return (n <= 1) ? 1 : n * factorial_func(n - 1);
}

// ✅ Способ #3: Fold expression (C++17) - для больших значений
template<int N>
constexpr int factorial_fold() {
    if constexpr (N <= 1) {
        return 1;
    } else {
        return N * factorial_fold<N-1>();
    }
}

// ✅ Способ #4: Итеративный constexpr (самый эффективный)
template<typename T>
constexpr T factorial_iterative(T n) {
    T result = 1;
    for (T i = 2; i <= n; ++i) {
        result *= i;
    }
    return result;
}

// ✅ Способ #5: Variable template (C++14)
template<int N>
constexpr int factorial_v = N * factorial_v<N-1>;

template<>
constexpr int factorial_v<0> = 1;

// ✅ Способ #6: SFINAE + enable_if для type safety
template<typename T, typename = std::enable_if_t<std::is_integral_v<T>>>
constexpr T factorial_safe(T n) {
    static_assert(std::is_integral_v<T>, "Factorial requires integral type");
    return (n <= 1) ? 1 : n * factorial_safe(n - 1);
}

// 🚀 Способ #7: Современный C++20 с concepts
#if __cpp_concepts >= 201907L
#include <concepts>

template<std::integral T>
constexpr T factorial_concept(T n) {
    return (n <= 1) ? 1 : n * factorial_concept(n - 1);
}
#endif

// 🎯 Способ #8: Compile-time lookup table для максимальной производительности
template<int N>
struct factorial_lut {
    static constexpr int table[] = {
        1, 1, 2, 6, 24, 120, 720, 5040, 40320, 362880, 3628800,
        39916800, 479001600 // до 12!
    };
    static constexpr int value = (N < sizeof(table)/sizeof(table[0])) ? table[N] : -1;
};

// 🔥 Способ #9: Consteval (C++20) - гарантированное вычисление на compile-time
#if __cpp_consteval >= 201811L
template<typename T>
consteval T factorial_consteval(T n) {
    return (n <= 1) ? 1 : n * factorial_consteval(n - 1);
}
#endif

// Тестирование и демонстрация
int main() {
    std::cout << "=== Template Factorial Demonstrations ===\n\n";
    
    // Тестируем все варианты
    std::cout << "1. Classic template struct:\n";
    static_assert(factorial<4>::value == 24, "bad factorial");
    std::cout << "   factorial<4>::value = " << factorial<4>::value << "\n";
    std::cout << "   factorial<5>::value = " << factorial<5>::value << "\n\n";
    
    std::cout << "2. Constexpr function:\n";
    static_assert(factorial_func(4) == 24, "bad factorial_func");
    std::cout << "   factorial_func(4) = " << factorial_func(4) << "\n";
    std::cout << "   factorial_func(6) = " << factorial_func(6) << "\n\n";
    
    std::cout << "3. Fold expression (C++17):\n";
    static_assert(factorial_fold<4>() == 24, "bad factorial_fold");
    std::cout << "   factorial_fold<4>() = " << factorial_fold<4>() << "\n";
    std::cout << "   factorial_fold<7>() = " << factorial_fold<7>() << "\n\n";
    
    std::cout << "4. Iterative constexpr:\n";
    static_assert(factorial_iterative(4) == 24, "bad factorial_iterative");
    std::cout << "   factorial_iterative(4) = " << factorial_iterative(4) << "\n";
    std::cout << "   factorial_iterative(8) = " << factorial_iterative(8) << "\n\n";
    
    std::cout << "5. Variable template:\n";
    static_assert(factorial_v<4> == 24, "bad factorial_v");
    std::cout << "   factorial_v<4> = " << factorial_v<4> << "\n";
    std::cout << "   factorial_v<5> = " << factorial_v<5> << "\n\n";
    
    std::cout << "6. SFINAE type-safe:\n";
    static_assert(factorial_safe(4) == 24, "bad factorial_safe");
    std::cout << "   factorial_safe(4) = " << factorial_safe(4) << "\n";
    std::cout << "   factorial_safe(9) = " << factorial_safe(9) << "\n\n";
    
#if __cpp_concepts >= 201907L
    std::cout << "7. C++20 concepts:\n";
    static_assert(factorial_concept(4) == 24, "bad factorial_concept");
    std::cout << "   factorial_concept(4) = " << factorial_concept(4) << "\n\n";
#endif
    
    std::cout << "8. Lookup table:\n";
    static_assert(factorial_lut<4>::value == 24, "bad factorial_lut");
    std::cout << "   factorial_lut<4>::value = " << factorial_lut<4>::value << "\n";
    std::cout << "   factorial_lut<10>::value = " << factorial_lut<10>::value << "\n\n";
    
#if __cpp_consteval >= 201811L
    std::cout << "9. Consteval (C++20):\n";
    static_assert(factorial_consteval(4) == 24, "bad factorial_consteval");
    std::cout << "   factorial_consteval(4) = " << factorial_consteval(4) << "\n\n";
#endif
    
    // Демонстрация compile-time вычислений
    std::cout << "🚀 All computations happen at compile-time!\n";
    std::cout << "   No runtime calculations for constant expressions.\n\n";
    
    // Runtime вычисления для переменных значений
    std::cout << "=== Runtime calculations ===\n";
    int n = 5;
    std::cout << "Runtime factorial_func(" << n << ") = " << factorial_func(n) << "\n";
    std::cout << "Runtime factorial_iterative(" << n << ") = " << factorial_iterative(n) << "\n";
    
    return 0;
}

// Дополнительные static_assert для проверки корректности
static_assert(factorial<0>::value == 1);
static_assert(factorial<1>::value == 1);
static_assert(factorial<2>::value == 2);
static_assert(factorial<3>::value == 6);
static_assert(factorial<4>::value == 24);
static_assert(factorial<5>::value == 120);

static_assert(factorial_func(0) == 1);
static_assert(factorial_func(1) == 1);
static_assert(factorial_func(4) == 24);
static_assert(factorial_func(5) == 120);

static_assert(factorial_v<0> == 1);
static_assert(factorial_v<4> == 24);
static_assert(factorial_v<5> == 120); 