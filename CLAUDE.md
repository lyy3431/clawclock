# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build & Test Commands

```bash
# Run application
python3 clock.py

# Run all tests
./run_tests.sh            # Normal output
./run_tests.sh -v         # Verbose output

# Run specific test module
python3 -m unittest tests.test_breath_light -v
python3 -m unittest tests.test_breath_light.TestBreathLight.test_default_config -v
```

## Architecture Overview

ClawClock v1.6.0+ is a modular Python Tkinter desktop clock application with the following structure:

```
clawclock/
├── main.py              # Entry point
├── clock.py             # Main application (ClockApp class)
├── config/              # Configuration module
│   ├── constants.py     # Global constants
│   ├── settings.py      # ConfigManager (load/save/get/set)
│   └── persistence.py   # PersistenceManager (alarms/state)
├── effects/             # Effects module
│   ├── breath_light.py  # BreathLightEffect + BreathStyle/TimerStatus enums
│   └── animations.py    # Animation, FadeAnimation, ColorAnimation
├── utils/               # Utility module
│   ├── errors.py        # Exception hierarchy + validate_* functions
│   └── logger.py        # ClockLogger (5 levels: debug/info/warning/error/critical)
├── tests/               # unittest-based tests (178 test cases)
└── themes/              # JSON theme files (dark/light/green/cyberpunk)
```

## Module Dependencies

```
main.py → clock.py → config/settings, effects/breath_light, utils/logger
                    → timer.py, stopwatch.py
                    → themes/*.json
```

## Key Patterns

**Configuration Management:**
- Use `get_config_manager()` for singleton access
- Config uses dot notation for nested keys: `config.get("breath_light.frequency")`
- Auto-merges custom config with defaults on load

**Error Handling:**
- Custom exception hierarchy: `ClockError` → `ConfigError`/`ThemeError`/`AlarmError`/`TimerError`/`IOError`
- Use `validate_time_format()`, `validate_preset_time()` for input validation
- Use `safe_execute()` for wrapping operations that may fail

**Effects System:**
- `BreathLightEffect` uses config dataclass (`BreathLightConfig`)
- Status-driven: `TimerStatus.NORMAL` → `WARNING` → `COMPLETED`
- 4 styles: `SOFT`, `TECH`, `COOL`, `MINIMAL`

**Logging:**
- Global functions: `info()`, `warning()`, `error()`, `debug()`, `critical()`
- Use `set_context(module="...", func="...")` for contextual logging

## Testing Conventions

- Test files: `tests/test_*.py`
- Test classes: `Test<Module>` (e.g., `TestBreathLight`)
- Test methods: `test_<feature>_<scenario>`
- Uses Python `unittest` (pytest optional for better output)

## Common Development Tasks

**Add new config option:**
1. Add to `config/settings.py` default_config dict
2. Document in API docs

**Add new effect:**
1. Create class in `effects/` with config dataclass
2. Add enums for styles/states if needed
3. Add tests in `tests/test_<effect>.py`

**Add new exception type:**
1. Extend `ClockError` in `utils/errors.py`
2. Follow existing pattern (message + context attribute)
