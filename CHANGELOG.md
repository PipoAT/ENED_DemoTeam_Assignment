# Changelog

## [Unreleased] - 2026-01-30

### Fixed
- Multiple instances colliding with each other when running simultaneously
- Information not updating properly across different browser sessions
- Concurrent submissions causing data inconsistencies

### Added
- File-based state persistence (`app_state.json`) to support multiple instances
- WebSocket support using Flask-SocketIO for real-time updates
- Thread-safe locking mechanism for concurrent access protection
- Automatic polling fallback when WebSocket is unavailable
- Input validation for all API endpoints
- Comprehensive test suite for concurrent operations (`test_concurrent.py`)
- `.gitignore` file to exclude runtime state files

### Changed
- Replaced AJAX polling with WebSocket push notifications
- Updated all HTML templates to support real-time updates
- Improved error handling with specific exception catching
- Banner text updated to reflect real-time capabilities

### Removed
- Unused global variables from old in-memory implementation
- Manual refresh requirement (now updates automatically)

### Technical Details
- All state operations now use file-based persistence with thread locks
- WebSocket events emitted on every state change (assign, remove, toggle)
- Fallback to 2-second polling if WebSocket CDN is blocked
- Tested with 10 concurrent requests - zero data loss
- Queue processing automatically triggers when stations become available
