"""
Sierra V2 Stream Emitter.
=========================

Typed, safe utilities for emitting Protocol V2 streaming events to SIERRA's
real-time canvas renderer.

Usage
-----
    from sierra.stream import StreamEmitter

    with StreamEmitter() as stream:
        stream.progress("Initializing scan...")
        stream.result(id="node_1", content="### Found Target")
        stream.result(id="node_2", content="### Sub-Target", parent="node_1")
        stream.end(summary="Scan complete: 2 nodes found.")

Notes
-----
- Every event is emitted as a single compact JSON line to ``stdout``.
- ``stdout`` is flushed immediately after each emission.
- All diagnostic/debug output MUST go to ``stderr``.
- The context manager ensures graceful ``end`` or ``error`` on exit.
"""

import json
import sys
import typing
from contextlib import contextmanager

__all__ = ["StreamEmitter", "stream_context"]

# ---------------------------------------------------------------------------
# Core Protocol Constants
# ---------------------------------------------------------------------------

_V2_VERSION: typing.Final[int] = 2

_VALID_EVENT_TYPES: typing.Final[frozenset[str]] = frozenset({"progress", "result", "end", "error"})


class StreamEmitter:
    """
    Safe, typed emitter for SIERRA Protocol V2 streaming events.

    Tracks emitted node IDs to validate parent references and ensures
    every session terminates cleanly (via ``end`` or ``error``).

    Parameters
    ----------
    auto_end : bool
        If ``True`` (default), the emitter will automatically send an ``end``
        event when exiting the context manager without an error.

    Attributes
    ----------
    emitted_ids : set[str]
        Set of all node IDs emitted during this session.
    is_terminated : bool
        Whether the stream has been terminated (via ``end`` or ``error``).

    Examples
    --------
    >>> emitter = StreamEmitter()
    >>> emitter.progress("Starting...")
    >>> emitter.result(id="root", content="### Root Node")
    >>> emitter.end(summary="Done.")
    """

    __slots__ = ("_auto_end", "emitted_ids", "is_terminated", "_event_count")

    def __init__(self, *, auto_end: bool = True) -> None:
        self._auto_end = auto_end
        self.emitted_ids: set[str] = set()
        self.is_terminated: bool = False
        self._event_count: int = 0

    # ------------------------------------------------------------------
    # Context manager protocol
    # ------------------------------------------------------------------

    def __enter__(self) -> "StreamEmitter":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: typing.Any,
    ) -> bool:
        if self.is_terminated:
            return False

        if exc_type is not None:
            # An unhandled exception occurred — emit error
            self.error(message=f"Unhandled exception: {exc_val}")
            return True  # Suppress the exception after emitting

        if self._auto_end:
            self.end(summary=f"Stream completed: {self._event_count} events emitted.")

        return False

    # ------------------------------------------------------------------
    # Low-level emission
    # ------------------------------------------------------------------

    def _emit(self, event_type: str, **kwargs: typing.Any) -> None:
        """
        Emit a raw V2 event to stdout.

        Parameters
        ----------
        event_type : str
            One of ``"progress"``, ``"result"``, ``"end"``, ``"error"``.
        **kwargs
            Additional event fields. ``None`` values are stripped.

        Raises
        ------
        ValueError
            If ``event_type`` is not a recognized V2 event type.
        RuntimeError
            If the stream has already been terminated.
        """
        if event_type not in _VALID_EVENT_TYPES:
            raise ValueError(
                f"Invalid V2 event type: {event_type!r}. "
                f"Must be one of: {', '.join(sorted(_VALID_EVENT_TYPES))}"
            )

        if self.is_terminated:
            raise RuntimeError(
                "Cannot emit events after stream termination (end/error already sent)."
            )

        event: dict[str, typing.Any] = {"version": _V2_VERSION, "type": event_type}
        event.update(kwargs)

        # Strip None values for clean output
        payload = {k: v for k, v in event.items() if v is not None}

        print(json.dumps(payload, ensure_ascii=False), flush=True)
        self._event_count += 1

    # ------------------------------------------------------------------
    # Typed event methods
    # ------------------------------------------------------------------

    def progress(self, message: str) -> None:
        """
        Emit a progress update event.

        Parameters
        ----------
        message : str
            Human-readable progress label (e.g. ``"Scanning port 443 (60%)"``).
        """
        if not message or not message.strip():
            raise ValueError("Progress message must not be empty.")
        self._emit("progress", message=message)

    def result(
        self,
        *,
        id: str,
        content: str,
        parent: str | None = None,
    ) -> None:
        """
        Emit an incremental graph node result.

        Parameters
        ----------
        id : str
            Unique identifier for this node. Must be non-empty and alphanumeric
            (underscores allowed).
        content : str
            Markdown content rendered inside the node on the canvas.
        parent : str or None
            ID of the parent node to anchor to. If ``None``, the node attaches
            directly to the invoking trigger node. If specified, must reference
            a previously emitted ID.

        Raises
        ------
        ValueError
            If ``id`` is empty, not alphanumeric, or ``parent`` references
            a node that has not been emitted yet.
        """
        if not id or not id.strip():
            raise ValueError("Result node 'id' must not be empty.")

        # Validate ID format: alphanumeric + underscores
        if not all(c.isalnum() or c == "_" for c in id):
            raise ValueError(f"Result node 'id' must be alphanumeric (underscores ok), got: {id!r}")

        if parent is not None and parent not in self.emitted_ids:
            raise ValueError(
                f"Parent node '{parent}' has not been emitted yet. "
                f"Emitted IDs: {sorted(self.emitted_ids)}"
            )

        if not content or not content.strip():
            raise ValueError("Result node 'content' must not be empty.")

        self.emitted_ids.add(id)
        self._emit("result", id=id, content=content, parent=parent)

    def end(self, *, summary: str | None = None) -> None:
        """
        Emit a graceful stream termination event.

        Parameters
        ----------
        summary : str or None
            Optional summary note for the canvas (e.g. ``"Found 5 targets."``).
        """
        self._emit("end", summary=summary)
        self.is_terminated = True

    def error(self, *, message: str) -> None:
        """
        Emit a stream error and halt execution.

        Parameters
        ----------
        message : str
            Human-readable error description for the canvas.
        """
        if not message or not message.strip():
            message = "Unknown stream error."
        self._emit("error", message=message)
        self.is_terminated = True

    # ------------------------------------------------------------------
    # Diagnostic helpers
    # ------------------------------------------------------------------

    def log(self, message: str) -> None:
        """
        Write a diagnostic message to stderr (invisible to SIERRA parser).

        Parameters
        ----------
        message : str
            Debug/log message.
        """
        sys.stderr.write(f"[SIERRA-STREAM] {message}\n")
        sys.stderr.flush()

    @property
    def event_count(self) -> int:
        """Total number of events emitted in this session."""
        return self._event_count

    @property
    def node_count(self) -> int:
        """Total number of result nodes emitted in this session."""
        return len(self.emitted_ids)


@contextmanager
def stream_context(*, auto_end: bool = True) -> typing.Generator[StreamEmitter, None, None]:
    """
    Convenience context manager for V2 streaming sessions.

    Parameters
    ----------
    auto_end : bool
        If ``True``, automatically sends an ``end`` event on clean exit.

    Yields
    ------
    StreamEmitter
        A configured stream emitter instance.

    Examples
    --------
    >>> from sierra.stream import stream_context
    >>> with stream_context() as stream:
    ...     stream.progress("Working...")
    ...     stream.result(id="n1", content="### Node 1")
    """
    emitter = StreamEmitter(auto_end=auto_end)
    try:
        yield emitter
    except Exception as exc:
        if not emitter.is_terminated:
            emitter.error(message=f"Unhandled exception: {exc}")
    finally:
        if not emitter.is_terminated and auto_end:
            emitter.end(summary=f"Stream completed: {emitter.event_count} events emitted.")
