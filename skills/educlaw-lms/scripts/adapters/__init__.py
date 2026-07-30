"""EduClaw LMS Integration — Adapter package.

Adapter modules provide LMS-specific API implementations behind a common interface.
All adapters extend BaseLMSAdapter and implement the same method signatures.

Usage:
    from adapters.canvas import CanvasAdapter
    adapter = CanvasAdapter(connection_row, encryption_key)
    result = adapter.test_connection()
"""
