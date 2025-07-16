#!/bin/bash

# Скрипт для запуска тестов DonutBuffer из корня проекта
# Использование: ./run-tests.sh [опции]

set -e  # Останавливаться при ошибках

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Определяем директории
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_DIR="$PROJECT_ROOT/build"

echo -e "${BLUE}🎯 DonutBuffer Test Runner${NC}"
echo -e "${BLUE}================================${NC}"
echo "Project root: $PROJECT_ROOT"
echo "Build directory: $BUILD_DIR"
echo ""

# Проверяем, что build директория существует
if [ ! -d "$BUILD_DIR" ]; then
    echo -e "${RED}❌ Build directory not found: $BUILD_DIR${NC}"
    echo -e "${YELLOW}💡 Run the following commands first:${NC}"
    echo "   mkdir build && cd build"
    echo "   cmake .."
    echo "   make -j4"
    exit 1
fi

# Проверяем, что исполняемые файлы существуют
if [ ! -f "$BUILD_DIR/tests/ringbuffer_tests" ]; then
    echo -e "${RED}❌ Unit tests not found. Please build the project first.${NC}"
    exit 1
fi

if [ ! -f "$BUILD_DIR/tests/e2e_buffer_tests" ]; then
    echo -e "${RED}❌ E2E tests not found. Please build the project first.${NC}"
    exit 1
fi

if [ ! -f "$BUILD_DIR/BufferRunner" ]; then
    echo -e "${RED}❌ BufferRunner not found. Please build the project first.${NC}"
    exit 1
fi

# Функция для запуска всех тестов
run_all_tests() {
    echo -e "${BLUE}🚀 Running all tests via CTest...${NC}"
    cd "$BUILD_DIR"
    if [ "$1" = "--verbose" ] || [ "$1" = "-v" ]; then
        ctest -V
    else
        ctest
    fi
    cd "$PROJECT_ROOT"
}

# Функция для запуска unit тестов
run_unit_tests() {
    echo -e "${BLUE}🔧 Running Unit Tests...${NC}"
    "$BUILD_DIR/tests/ringbuffer_tests"
}

# Функция для запуска e2e тестов
run_e2e_tests() {
    echo -e "${BLUE}🌐 Running E2E Tests...${NC}"
    "$BUILD_DIR/tests/e2e_buffer_tests" "$BUILD_DIR/BufferRunner"
}

# Функция для запуска CLI тестов
run_cli_tests() {
    echo -e "${BLUE}⚡ Running CLI Performance Tests...${NC}"
    echo ""
    
    echo -e "${YELLOW}1. Default (mutex, 1P+1C):${NC}"
    "$BUILD_DIR/BufferRunner"
    echo ""
    
    echo -e "${YELLOW}2. Lockfree (1P+1C):${NC}"
    "$BUILD_DIR/BufferRunner" --type=lockfree
    echo ""
    
    echo -e "${YELLOW}3. Lockfree multi-threaded (4P+2C):${NC}"
    "$BUILD_DIR/BufferRunner" --type=lockfree --producers=4 --consumers=2
    echo ""
    
    echo -e "${YELLOW}4. Stress test (8P+8C):${NC}"
    "$BUILD_DIR/BufferRunner" --type=lockfree --producers=8 --consumers=8
    echo ""
}

# Функция показа помощи
show_help() {
    echo "Usage: $0 [command] [options]"
    echo ""
    echo "Commands:"
    echo "  all, test          - Run all tests (default)"
    echo "  unit              - Run only unit tests"
    echo "  e2e               - Run only E2E tests"
    echo "  cli               - Run CLI performance tests"
    echo "  help, -h, --help  - Show this help"
    echo ""
    echo "Options:"
    echo "  -v, --verbose     - Verbose output (for 'all' command)"
    echo ""
    echo "Examples:"
    echo "  $0                - Run all tests"
    echo "  $0 all -v         - Run all tests with verbose output"
    echo "  $0 unit           - Run only unit tests"
    echo "  $0 e2e            - Run only E2E tests"
    echo "  $0 cli            - Run CLI performance benchmarks"
}

# Разбор аргументов
case "${1:-all}" in
    "all"|"test"|"")
        run_all_tests "$2"
        ;;
    "unit")
        run_unit_tests
        ;;
    "e2e")
        run_e2e_tests
        ;;
    "cli")
        run_cli_tests
        ;;
    "help"|"-h"|"--help")
        show_help
        exit 0
        ;;
    *)
        echo -e "${RED}❌ Unknown command: $1${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}✅ Test execution completed!${NC}" 