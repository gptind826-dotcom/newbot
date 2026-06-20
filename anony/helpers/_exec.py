"""
eXuCoDeR Music Bot - Code Execution
Copyright (c) 2025 eXuCoDeR
Licensed under the MIT License.
"""

import traceback
import io
import sys


async def meval(code, local_vars):
    """Safely evaluate Python code."""
    stdout = io.StringIO()
    stderr = io.StringIO()

    local_vars["__stdout__"] = stdout
    local_vars["__stderr__"] = stderr

    old_stdout = sys.stdout
    old_stderr = sys.stderr
    sys.stdout = stdout
    sys.stderr = stderr

    try:
        # Wrap in async function
        wrapped_code = f"async def __ex():\n" + "\n".join(
            f"    {line}" for line in code.split("\n")
        )
        exec(wrapped_code, local_vars)
        result = await local_vars["__ex"]()
        return result, stdout.getvalue(), stderr.getvalue()
    except Exception:
        return None, stdout.getvalue(), traceback.format_exc()
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr


def format_exception(error: str) -> str:
    """Format exception for display."""
    lines = error.strip().split("\n")
    return "\n".join(lines[-5:])  # Last 5 lines
