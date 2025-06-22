# Contributing to KDE Memory Guardian

Thank you for your interest in contributing to KDE Memory Guardian! This project helps thousands of KDE users maintain stable systems by preventing memory leaks.

## 🎯 Project Goals

- **Reliability**: Prevent KDE memory leaks without causing system instability
- **Simplicity**: Easy installation and configuration for all skill levels  
- **Performance**: Minimal resource usage for the monitoring service
- **Compatibility**: Support for KDE Plasma 5 and 6 across Linux distributions

## 🚀 Getting Started

### Development Environment Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/kde-memory-guardian.git
   cd kde-memory-guardian
   ```

2. **Install development dependencies**
   ```bash
   # Fedora
   sudo dnf install shellcheck bash-completion systemd-devel
   
   # Ubuntu/Debian  
   sudo apt install shellcheck bash-completion systemd
   ```

3. **Set up testing environment**
   ```bash
   # Create test directory
   mkdir -p test/fixtures
   
   # Install in development mode
   ./install.sh --dev-mode
   ```

### Code Style Guidelines

#### Shell Script Standards
- **Use bash strict mode**: `set -euo pipefail`
- **Quote all variables**: `"$variable"` not `$variable`
- **Use readonly for constants**: `readonly CONSTANT_NAME="value"`
- **Function documentation**: Document WHAT, WHY, and HOW for each function
- **Error handling**: Always check return codes and handle errors gracefully

#### Example Function Documentation
```bash
# Get memory usage for a specific process name
# PARAMETERS: $1 = process name (e.g., "plasmashell")
# OUTPUT: Total memory usage in KB for all matching processes
# RETURNS: 0 if no processes found, sum of RSS values if found
get_process_memory() {
    local process_name="$1"
    # Implementation...
}
```

#### Systemd Service Standards
- **Comprehensive comments**: Explain each configuration option
- **Security hardening**: Use appropriate security restrictions
- **Resource limits**: Prevent service from consuming excessive resources
- **Proper dependencies**: Ensure correct startup/shutdown ordering

### Testing Requirements

#### Manual Testing Checklist
- [ ] Service starts successfully: `systemctl --user start kde-memory-manager.service`
- [ ] Service enables for auto-start: `systemctl --user enable kde-memory-manager.service`
- [ ] Logging works correctly: Check `~/.local/share/kde-memory-manager.log`
- [ ] Memory thresholds trigger correctly: Test with high memory usage
- [ ] Plasma restart works: Verify desktop remains functional after restart
- [ ] System optimizations apply: Check `sysctl vm.swappiness`

#### Automated Testing
```bash
# Run shell script linting
shellcheck src/kde-memory-manager.sh install.sh

# Run unit tests (when available)
./test/run-tests.sh

# Validate systemd service file
systemd-analyze --user verify src/kde-memory-manager.service
```

## 📝 Contribution Types

### 🐛 Bug Reports
When reporting bugs, please include:

- **System Information**: Distribution, KDE version, kernel version
- **Service Status**: Output of `systemctl --user status kde-memory-manager.service`
- **Log Files**: Recent entries from `~/.local/share/kde-memory-manager.log`
- **Steps to Reproduce**: Clear steps to reproduce the issue
- **Expected vs Actual Behavior**: What should happen vs what actually happens

### ✨ Feature Requests
For new features, please provide:

- **Use Case**: Why is this feature needed?
- **Proposed Solution**: How should it work?
- **Alternatives Considered**: What other approaches were considered?
- **Compatibility Impact**: How does this affect existing installations?

### 🔧 Code Contributions

#### Pull Request Process
1. **Fork the repository** and create a feature branch
2. **Make your changes** following the code style guidelines
3. **Test thoroughly** using the manual testing checklist
4. **Update documentation** if your changes affect user-facing behavior
5. **Submit pull request** with clear description of changes

#### Commit Message Format
```
type(scope): brief description

Detailed explanation of what changed and why.

- Specific change 1
- Specific change 2

Fixes #issue-number
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

### 📚 Documentation Improvements
- **README updates**: Keep installation and usage instructions current
- **Code comments**: Improve inline documentation
- **Wiki contributions**: Add troubleshooting guides and advanced configurations
- **Examples**: Provide configuration examples for different use cases

## 🔍 Code Review Guidelines

### For Contributors
- **Self-review first**: Check your own code before submitting
- **Test on multiple systems**: Verify compatibility across distributions
- **Keep changes focused**: One feature/fix per pull request
- **Respond to feedback**: Address review comments promptly

### For Reviewers
- **Be constructive**: Provide helpful suggestions, not just criticism
- **Check security**: Verify no security vulnerabilities are introduced
- **Test functionality**: Actually test the changes when possible
- **Consider compatibility**: Ensure changes work across supported systems

## 🛡️ Security Considerations

### Security Review Checklist
- [ ] No hardcoded credentials or sensitive information
- [ ] Proper input validation and sanitization
- [ ] Minimal required permissions (no unnecessary sudo/root access)
- [ ] Safe file operations (proper permissions, no race conditions)
- [ ] Resource limits to prevent DoS attacks

### Reporting Security Issues
For security vulnerabilities, please:
1. **Do NOT create public issues**
2. **Email directly**: security@yourproject.com
3. **Include details**: Steps to reproduce, potential impact
4. **Allow time**: Give maintainers time to fix before public disclosure

## 🌍 Community Guidelines

### Code of Conduct
- **Be respectful**: Treat all contributors with respect and kindness
- **Be inclusive**: Welcome contributors of all backgrounds and skill levels
- **Be constructive**: Focus on improving the project, not personal attacks
- **Be patient**: Remember that everyone is volunteering their time

### Communication Channels
- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and community discussion
- **Pull Requests**: Code review and technical discussion

## 📋 Development Roadmap

### Current Priorities
1. **Cross-distribution testing**: Verify compatibility with major Linux distributions
2. **Wayland support**: Ensure compatibility with Wayland sessions
3. **Configuration GUI**: Simple graphical interface for threshold configuration
4. **Advanced monitoring**: Additional metrics and alerting options

### Future Enhancements
- **Plasma 6 optimizations**: Specific improvements for KDE Plasma 6
- **Integration with system monitors**: Export metrics to Prometheus/Grafana
- **Machine learning**: Predictive memory leak detection
- **Mobile support**: Adaptation for mobile Linux environments

## 🏆 Recognition

Contributors will be recognized in:
- **README.md**: Contributors section
- **Release notes**: Acknowledgment of significant contributions
- **GitHub**: Contributor badges and statistics

## 📞 Getting Help

If you need help contributing:
- **GitHub Discussions**: Ask questions in the community forum
- **Documentation**: Check the wiki for detailed guides
- **Maintainers**: Tag maintainers in issues for guidance

Thank you for helping make KDE Memory Guardian better for everyone! 🎉
