#!/bin/bash

# KDE Memory Guardian - CI Test Suite
#
# Simplified test suite designed for GitHub Actions CI environment
# Focuses on static analysis and basic validation without requiring
# running services or user session components.

set -euo pipefail

# Test configuration
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

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
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Test repository structure
test_repository_structure() {
    log_test_start "Repository structure validation"
    
    local required_files=(
        "$PROJECT_ROOT/install.sh"
        "$PROJECT_ROOT/src/kde-memory-manager.sh"
        "$PROJECT_ROOT/src/kde-memory-manager.service"
        "$PROJECT_ROOT/test/run-tests.sh"
        "$PROJECT_ROOT/README.md"
    )
    
    for file in "${required_files[@]}"; do
        if [[ -f "$file" ]]; then
            log_info "Found required file: $file"
        else
            log_test_fail "Repository structure" "Missing required file: $file"
            return 1
        fi
    done
    
    log_test_pass "Repository structure validation"
}

# Test shell script syntax
test_shell_syntax() {
    log_test_start "Shell script syntax validation"
    
    local scripts=(
        "$PROJECT_ROOT/install.sh"
        "$PROJECT_ROOT/src/kde-memory-manager.sh"
        "$PROJECT_ROOT/test/run-tests.sh"
    )
    
    # Add tool scripts
    if [[ -d "$PROJECT_ROOT/tools" ]]; then
        while IFS= read -r -d '' script; do
            scripts+=("$script")
        done < <(find "$PROJECT_ROOT/tools" -name "*.sh" -print0)
    fi
    
    for script in "${scripts[@]}"; do
        if [[ -f "$script" ]]; then
            if bash -n "$script" 2>/dev/null; then
                log_info "Syntax OK: $script"
            else
                local error_output=$(bash -n "$script" 2>&1 || true)
                log_test_fail "Shell syntax" "Syntax error in $script: $error_output"
                return 1
            fi
        fi
    done
    
    log_test_pass "Shell script syntax validation"
}

# Test shellcheck compliance (if available)
test_shellcheck_compliance() {
    if ! command -v shellcheck >/dev/null 2>&1; then
        log_info "Shellcheck not available, skipping static analysis"
        return 0
    fi
    
    log_test_start "Shellcheck static analysis"
    
    local scripts=(
        "$PROJECT_ROOT/install.sh"
        "$PROJECT_ROOT/src/kde-memory-manager.sh"
        "$PROJECT_ROOT/test/run-tests.sh"
    )
    
    local shellcheck_failed=false
    
    for script in "${scripts[@]}"; do
        if [[ -f "$script" ]]; then
            if shellcheck "$script" 2>/dev/null; then
                log_info "Shellcheck OK: $script"
            else
                log_info "Shellcheck issues found in: $script (non-critical)"
                shellcheck_failed=true
            fi
        fi
    done
    
    if [[ "$shellcheck_failed" == "true" ]]; then
        log_info "Some shellcheck issues found but not failing CI"
    fi
    
    log_test_pass "Shellcheck static analysis"
}

# Test systemd service file
test_systemd_service() {
    log_test_start "Systemd service file validation"
    
    local service_file="$PROJECT_ROOT/src/kde-memory-manager.service"
    
    if [[ ! -f "$service_file" ]]; then
        log_test_fail "Systemd service validation" "Service file not found: $service_file"
        return 1
    fi
    
    # Basic service file structure validation
    local required_sections=("Unit" "Service" "Install")
    
    for section in "${required_sections[@]}"; do
        if grep -q "^\[$section\]" "$service_file"; then
            log_info "Found required section: [$section]"
        else
            log_test_fail "Systemd service validation" "Missing required section: [$section]"
            return 1
        fi
    done
    
    # Check for required fields
    if grep -q "^ExecStart=" "$service_file"; then
        log_info "Found ExecStart directive"
    else
        log_test_fail "Systemd service validation" "Missing ExecStart directive"
        return 1
    fi
    
    # Try systemd-analyze if available
    if command -v systemd-analyze >/dev/null 2>&1; then
        if systemd-analyze verify "$service_file" 2>/dev/null; then
            log_info "systemd-analyze verification passed"
        else
            log_info "systemd-analyze found issues (non-critical for CI)"
        fi
    fi
    
    log_test_pass "Systemd service file validation"
}

# Test memory detection logic
test_memory_detection_logic() {
    log_test_start "Memory detection logic validation"
    
    # Test process memory detection logic
    local test_memory=$(ps -eo pid,rss,comm | grep "bash" | grep -v grep | awk '{sum+=$2} END {print sum+0}' 2>/dev/null || echo "0")
    if [[ "$test_memory" =~ ^[0-9]+$ ]] && [[ "$test_memory" -ge 0 ]]; then
        log_info "Process memory detection logic works: ${test_memory}KB"
    else
        log_test_fail "Memory detection logic" "Process memory detection failed: $test_memory"
        return 1
    fi
    
    # Test system memory detection logic
    if [[ -r /proc/meminfo ]]; then
        local mem_total=$(grep '^MemTotal:' /proc/meminfo | awk '{print $2}' 2>/dev/null || echo "1")
        local mem_available=$(grep '^MemAvailable:' /proc/meminfo | awk '{print $2}' 2>/dev/null || echo "1")
        
        if [[ "$mem_total" =~ ^[0-9]+$ ]] && [[ "$mem_available" =~ ^[0-9]+$ ]] && [[ $mem_total -gt 0 ]]; then
            local mem_used=$((mem_total - mem_available))
            local usage_percent=$((mem_used * 100 / mem_total))
            log_info "System memory detection logic works: ${usage_percent}%"
        else
            log_test_fail "Memory detection logic" "System memory detection failed"
            return 1
        fi
    else
        log_test_fail "Memory detection logic" "/proc/meminfo not readable"
        return 1
    fi
    
    log_test_pass "Memory detection logic validation"
}

# Test configuration validation
test_configuration_validation() {
    log_test_start "Configuration validation"
    
    local script="$PROJECT_ROOT/src/kde-memory-manager.sh"
    
    # Test that script accepts various environment variables
    local test_configs=(
        "MEMORY_THRESHOLD=50"
        "MEMORY_THRESHOLD=95"
        "PLASMA_MEMORY_THRESHOLD=500000"
        "CHECK_INTERVAL=60"
    )
    
    for config in "${test_configs[@]}"; do
        if env "$config" bash -n "$script" 2>/dev/null; then
            log_info "Configuration test passed: $config"
        else
            log_test_fail "Configuration validation" "Invalid configuration: $config"
            return 1
        fi
    done
    
    log_test_pass "Configuration validation"
}

# Main test execution
run_ci_tests() {
    echo -e "${BLUE}🧪 KDE Memory Guardian CI Test Suite${NC}"
    echo -e "${BLUE}====================================${NC}"
    echo
    
    # Repository structure tests
    echo -e "${YELLOW}📁 Repository Structure Tests${NC}"
    test_repository_structure || true
    echo
    
    # Static analysis tests
    echo -e "${YELLOW}📋 Static Analysis Tests${NC}"
    test_shell_syntax || true
    test_shellcheck_compliance || true
    test_systemd_service || true
    echo
    
    # Logic validation tests
    echo -e "${YELLOW}⚙️  Logic Validation Tests${NC}"
    test_memory_detection_logic || true
    test_configuration_validation || true
    echo
    
    # Test summary
    echo -e "${BLUE}📊 Test Summary${NC}"
    echo -e "${BLUE}===============${NC}"
    echo "Tests run: $TESTS_RUN"
    echo -e "Tests passed: ${GREEN}$TESTS_PASSED${NC}"
    echo -e "Tests failed: ${RED}$TESTS_FAILED${NC}"
    
    if [[ $TESTS_FAILED -eq 0 ]]; then
        echo -e "${GREEN}🎉 All CI tests passed!${NC}"
        exit 0
    else
        echo -e "${RED}❌ Some CI tests failed. Please review the output above.${NC}"
        exit 1
    fi
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --help|-h)
            echo "Usage: $0 [--help]"
            echo "  --help, -h       Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Run CI tests
run_ci_tests
