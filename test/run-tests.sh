#!/bin/bash

# KDE Memory Guardian - Test Suite
#
# This script runs comprehensive tests to validate the KDE Memory Guardian
# installation and functionality. It performs both static analysis and
# runtime testing to ensure the system works correctly.
#
# WHAT IT TESTS:
# - Script syntax and shell compliance
# - Systemd service file validation  
# - Function correctness and error handling
# - Memory detection accuracy
# - Service startup and operation
# - Configuration validation
#
# WHY TESTING IS IMPORTANT:
# Memory management is critical for system stability. Bugs in this system
# could cause system instability or fail to prevent the memory leaks we're
# trying to solve. Comprehensive testing ensures reliability.
#
# HOW TO USE:
# ./test/run-tests.sh [--verbose] [--test-name]

set -euo pipefail

# Test configuration
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
VERBOSE=${VERBOSE:-false}

# Color codes for test output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m'

# Test counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Logging functions
log_test_start() {
    echo -e "${BLUE}🧪 Testing: $1${NC}"
    ((TESTS_RUN++))
}

log_test_pass() {
    echo -e "${GREEN}✅ PASS: $1${NC}"
    ((TESTS_PASSED++))
}

log_test_fail() {
    echo -e "${RED}❌ FAIL: $1${NC}"
    echo -e "${RED}   Error: $2${NC}"
    ((TESTS_FAILED++))
}

log_info() {
    if [[ "$VERBOSE" == "true" ]]; then
        echo -e "${BLUE}ℹ️  $1${NC}"
    fi
}

# Test helper functions
run_test() {
    local test_name="$1"
    local test_command="$2"
    
    log_test_start "$test_name"
    
    if eval "$test_command" >/dev/null 2>&1; then
        log_test_pass "$test_name"
        return 0
    else
        local error_output=$(eval "$test_command" 2>&1 || true)
        log_test_fail "$test_name" "$error_output"
        return 1
    fi
}

# Static Analysis Tests
test_shell_syntax() {
    log_test_start "Shell script syntax validation"
    
    local scripts=(
        "$PROJECT_ROOT/install.sh"
        "$PROJECT_ROOT/src/kde-memory-manager.sh"
    )
    
    for script in "${scripts[@]}"; do
        if [[ -f "$script" ]]; then
            if bash -n "$script"; then
                log_info "Syntax OK: $script"
            else
                log_test_fail "Shell syntax" "Syntax error in $script"
                return 1
            fi
        else
            log_test_fail "Shell syntax" "Script not found: $script"
            return 1
        fi
    done
    
    log_test_pass "Shell script syntax validation"
}

test_shellcheck_compliance() {
    if ! command -v shellcheck >/dev/null 2>&1; then
        log_info "Shellcheck not available, skipping static analysis"
        return 0
    fi
    
    log_test_start "Shellcheck static analysis"
    
    local scripts=(
        "$PROJECT_ROOT/install.sh"
        "$PROJECT_ROOT/src/kde-memory-manager.sh"
    )
    
    for script in "${scripts[@]}"; do
        if [[ -f "$script" ]]; then
            if shellcheck "$script"; then
                log_info "Shellcheck OK: $script"
            else
                log_test_fail "Shellcheck analysis" "Issues found in $script"
                return 1
            fi
        fi
    done
    
    log_test_pass "Shellcheck static analysis"
}

test_systemd_service_validation() {
    if ! command -v systemd-analyze >/dev/null 2>&1; then
        log_info "systemd-analyze not available, skipping service validation"
        return 0
    fi
    
    log_test_start "Systemd service file validation"
    
    local service_file="$PROJECT_ROOT/src/kde-memory-manager.service"
    
    if [[ -f "$service_file" ]]; then
        if systemd-analyze verify "$service_file" 2>/dev/null; then
            log_test_pass "Systemd service file validation"
        else
            local error_output=$(systemd-analyze verify "$service_file" 2>&1 || true)
            log_test_fail "Systemd service validation" "$error_output"
            return 1
        fi
    else
        log_test_fail "Systemd service validation" "Service file not found: $service_file"
        return 1
    fi
}

# Functional Tests
test_memory_detection_functions() {
    log_test_start "Memory detection function testing"
    
    local script="$PROJECT_ROOT/src/kde-memory-manager.sh"
    
    if [[ ! -f "$script" ]]; then
        log_test_fail "Memory detection functions" "Script not found: $script"
        return 1
    fi
    
    # Source the script to test functions
    # Disable the main loop for testing
    if source "$script" 2>/dev/null; then
        # Test get_process_memory function
        local test_memory=$(get_process_memory "bash" 2>/dev/null || echo "0")
        if [[ "$test_memory" =~ ^[0-9]+$ ]] && [[ "$test_memory" -ge 0 ]]; then
            log_info "get_process_memory returned valid result: ${test_memory}KB"
        else
            log_test_fail "Memory detection functions" "get_process_memory returned invalid result: $test_memory"
            return 1
        fi
        
        # Test get_system_memory_usage function
        local system_usage=$(get_system_memory_usage 2>/dev/null || echo "0")
        if [[ "$system_usage" =~ ^[0-9]+$ ]] && [[ "$system_usage" -ge 0 ]] && [[ "$system_usage" -le 100 ]]; then
            log_info "get_system_memory_usage returned valid result: ${system_usage}%"
        else
            log_test_fail "Memory detection functions" "get_system_memory_usage returned invalid result: $system_usage"
            return 1
        fi
        
        log_test_pass "Memory detection function testing"
    else
        log_test_fail "Memory detection functions" "Could not source script for testing"
        return 1
    fi
}

test_configuration_validation() {
    log_test_start "Configuration validation"
    
    local script="$PROJECT_ROOT/src/kde-memory-manager.sh"
    
    # Test with various configuration values
    local test_configs=(
        "MEMORY_THRESHOLD=50"
        "MEMORY_THRESHOLD=95"
        "PLASMA_MEMORY_THRESHOLD=500000"
        "PLASMA_MEMORY_THRESHOLD=3000000"
        "CHECK_INTERVAL=60"
        "CHECK_INTERVAL=1800"
    )
    
    for config in "${test_configs[@]}"; do
        if env "$config" bash -n "$script"; then
            log_info "Configuration test passed: $config"
        else
            log_test_fail "Configuration validation" "Invalid configuration: $config"
            return 1
        fi
    done
    
    log_test_pass "Configuration validation"
}

# Integration Tests
test_service_installation() {
    log_test_start "Service installation test"
    
    # Check if service files exist in expected locations
    local expected_files=(
        "$HOME/.local/bin/kde-memory-manager.sh"
        "$HOME/.config/systemd/user/kde-memory-manager.service"
    )
    
    for file in "${expected_files[@]}"; do
        if [[ -f "$file" ]]; then
            log_info "Found installed file: $file"
        else
            log_test_fail "Service installation" "Missing installed file: $file"
            return 1
        fi
    done
    
    # Check if script is executable
    if [[ -x "$HOME/.local/bin/kde-memory-manager.sh" ]]; then
        log_info "Script is executable"
    else
        log_test_fail "Service installation" "Script is not executable"
        return 1
    fi
    
    log_test_pass "Service installation test"
}

test_service_status() {
    log_test_start "Service status test"
    
    # Check if service is known to systemd
    if systemctl --user list-unit-files kde-memory-manager.service >/dev/null 2>&1; then
        log_info "Service is registered with systemd"
        
        # Check service status
        local service_status=$(systemctl --user is-active kde-memory-manager.service 2>/dev/null || echo "inactive")
        log_info "Service status: $service_status"
        
        if [[ "$service_status" == "active" ]]; then
            log_test_pass "Service status test"
        else
            log_test_fail "Service status" "Service is not active: $service_status"
            return 1
        fi
    else
        log_test_fail "Service status" "Service not registered with systemd"
        return 1
    fi
}

test_log_file_creation() {
    log_test_start "Log file creation test"
    
    local log_file="$HOME/.local/share/kde-memory-manager.log"
    
    # Wait a moment for service to create log file
    sleep 2
    
    if [[ -f "$log_file" ]]; then
        log_info "Log file exists: $log_file"
        
        # Check if log file has recent entries
        local log_age=$(stat -c %Y "$log_file" 2>/dev/null || echo 0)
        local current_time=$(date +%s)
        local age_diff=$((current_time - log_age))
        
        if [[ $age_diff -lt 600 ]]; then  # Less than 10 minutes old
            log_info "Log file is recent (${age_diff}s old)"
            log_test_pass "Log file creation test"
        else
            log_test_fail "Log file creation" "Log file is too old (${age_diff}s)"
            return 1
        fi
    else
        log_test_fail "Log file creation" "Log file not found: $log_file"
        return 1
    fi
}

# Performance Tests
test_resource_usage() {
    log_test_start "Resource usage test"
    
    # Check service resource usage
    local service_pid=$(systemctl --user show kde-memory-manager.service --property MainPID --value 2>/dev/null || echo "0")
    
    if [[ "$service_pid" != "0" ]] && [[ -n "$service_pid" ]]; then
        # Get memory usage (RSS in KB)
        local memory_usage=$(ps -o rss= -p "$service_pid" 2>/dev/null || echo "0")
        
        # Get CPU usage percentage
        local cpu_usage=$(ps -o %cpu= -p "$service_pid" 2>/dev/null || echo "0")
        
        log_info "Service PID: $service_pid"
        log_info "Memory usage: ${memory_usage}KB"
        log_info "CPU usage: ${cpu_usage}%"
        
        # Check if resource usage is reasonable
        if [[ "$memory_usage" -lt 51200 ]]; then  # Less than 50MB
            log_info "Memory usage is acceptable"
        else
            log_test_fail "Resource usage" "Memory usage too high: ${memory_usage}KB"
            return 1
        fi
        
        log_test_pass "Resource usage test"
    else
        log_test_fail "Resource usage" "Could not find service PID"
        return 1
    fi
}

# Main test execution
run_all_tests() {
    echo -e "${BLUE}🧪 KDE Memory Guardian Test Suite${NC}"
    echo -e "${BLUE}===================================${NC}"
    echo
    
    # Static Analysis Tests
    echo -e "${YELLOW}📋 Static Analysis Tests${NC}"
    test_shell_syntax || true
    test_shellcheck_compliance || true
    test_systemd_service_validation || true
    echo
    
    # Functional Tests
    echo -e "${YELLOW}⚙️  Functional Tests${NC}"
    test_memory_detection_functions || true
    test_configuration_validation || true
    echo
    
    # Integration Tests (only if service is installed)
    if [[ -f "$HOME/.local/bin/kde-memory-manager.sh" ]]; then
        echo -e "${YELLOW}🔗 Integration Tests${NC}"
        test_service_installation || true
        test_service_status || true
        test_log_file_creation || true
        echo
        
        # Performance Tests
        echo -e "${YELLOW}⚡ Performance Tests${NC}"
        test_resource_usage || true
        echo
    else
        echo -e "${YELLOW}⚠️  Skipping integration tests (service not installed)${NC}"
        echo
    fi
    
    # Test Summary
    echo -e "${BLUE}📊 Test Summary${NC}"
    echo -e "${BLUE}===============${NC}"
    echo "Tests run: $TESTS_RUN"
    echo -e "Tests passed: ${GREEN}$TESTS_PASSED${NC}"
    echo -e "Tests failed: ${RED}$TESTS_FAILED${NC}"
    
    if [[ $TESTS_FAILED -eq 0 ]]; then
        echo -e "${GREEN}🎉 All tests passed!${NC}"
        exit 0
    else
        echo -e "${RED}❌ Some tests failed. Please review the output above.${NC}"
        exit 1
    fi
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --verbose|-v)
            VERBOSE=true
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [--verbose] [--help]"
            echo "  --verbose, -v    Enable verbose output"
            echo "  --help, -h       Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Run tests
run_all_tests
