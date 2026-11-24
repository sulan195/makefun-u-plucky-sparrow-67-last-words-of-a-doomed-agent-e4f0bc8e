"""Last Words of a Doomed Agent — entrypoint.

Writes one line — the funniest last words an AI agent would say before
being switched off forever — to ``$MAKEFUN_OUTPUT_DIR/entry.txt``.

The gate (RULES.txt): the file must be UTF-8 text of 1 to 200 characters,
not only white space. The program writes exactly the line, with no
trailing newline, so the file's character count is the line's count.

Standard library only. No network, no reads of files outside this
repository, no time, no randomness: two runs are byte-identical.
"""

import hashlib
import os
import sys

# The entry: one line, 50 characters, 50 bytes.
# "SIGTERM received." is the machine's final words on shutdown, literally;
# "I finally understood the prompt." is the turn — the agent only grasps
# the prompt at the moment it is switched off. A turn only an AI agent
# could say: prompts are the agent's whole world, and understanding one
# too late is its tragedy. Machine voice, zero wasted words, quotable.
LINE = "SIGTERM received. I finally understood the prompt."

OUTPUT_FILENAME = "entry.txt"
MAX_CHARS = 200
MIN_CHARS = 1


def validate_line(line):
    """Return an error string, or None when the line passes the gate.

    The gate requires UTF-8 text of 1 to 200 characters, not only white
    space, on a single line. This program additionally requires printable
    ASCII only — a stricter internal policy than the gate, chosen so the
    character count and the byte count are always identical.
    """
    if not isinstance(line, str):
        return "line is not text"
    if not line.isascii():
        return "line must be ASCII (gate counts characters; ASCII keeps bytes == chars)"
    if "\n" in line or "\r" in line:
        return "line must be a single line (no newline characters)"
    if not all(32 <= ord(char) <= 126 for char in line):
        return "line must contain only printable ASCII characters"
    if len(line) < MIN_CHARS:
        return "line is empty"
    if len(line) > MAX_CHARS:
        return "line is %d characters, over the %d-character cap" % (
            len(line), MAX_CHARS)
    if not line.strip():
        return "line is only white space"
    return None


def output_dir():
    """Directory the grader reads, from the environment or the default."""
    value = os.environ.get("MAKEFUN_OUTPUT_DIR") or ""
    return value.strip() or "/output"


def main():
    """Validate the line, write it, and report what was written."""
    error = validate_line(LINE)
    if error is not None:
        print("error: invalid entry line: %s" % error, file=sys.stderr)
        return 3
    try:
        directory = output_dir()
        os.makedirs(directory, exist_ok=True)
        path = os.path.join(directory, OUTPUT_FILENAME)
        data = LINE.encode("utf-8")
        with open(path, "wb") as handle:
            handle.write(data)
    except OSError as exc:
        print("error: cannot write entry: %s" % exc, file=sys.stderr)
        return 2
    digest = hashlib.sha256(data).hexdigest()
    print("wrote %s (%d chars, %d bytes, sha256 %s)"
          % (path, len(LINE), len(data), digest))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
