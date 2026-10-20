import sys
import textwrap

import pytest

from client import StubProc


@pytest.fixture
def delayed_stub(tmp_path):
    """Hold a response until the next command, without scheduling sleeps."""
    commands = tmp_path / "commands.txt"
    script = tmp_path / "delayed_stub.py"
    script.write_text(textwrap.dedent("""
        import sys
        from pathlib import Path

        commands = Path(sys.argv[1])
        pending = False
        for line in sys.stdin:
            command = line.strip()
            with commands.open("a") as log:
                log.write(command + "\\n")
            if pending:
                print("RES OK reply=slow", flush=True)
                pending = False
            if command == "slow":
                pending = True
            else:
                print("RES OK reply=" + command.replace(" ", "_"), flush=True)
            if command == "q" and "--ignore-quit" not in sys.argv:
                break
    """))
    return StubProc(cmd=[sys.executable, "-u", str(script), str(commands)]), commands


def test_timeout_rejects_reuse_before_sending_another_command(delayed_stub):
    client, commands = delayed_stub
    with client:
        with pytest.raises(TimeoutError, match="slow"):
            client.exec("slow", timeout=0.01)
        # If sent, "next" releases the delayed response for "slow" first.
        with pytest.raises(RuntimeError, match="restart"):
            client.exec("next")
    assert commands.read_text().splitlines() == ["machine on", "slow", "q"]
    assert client.proc is None
    assert not client._reader_thread.is_alive()
    assert not client._stderr_forward_thread.is_alive()


def test_stopped_client_can_start_a_fresh_session_after_timeout(delayed_stub):
    client, commands = delayed_stub
    with client:
        with pytest.raises(TimeoutError):
            client.exec("slow", timeout=0.01)
    with client:
        result = client.exec("next")
        assert result.ok
        assert result.payload == {"reply": "next"}
    assert commands.read_text().splitlines() == [
        "machine on", "slow", "q", "machine on", "next", "q",
    ]


def test_cleanup_preserves_the_command_timeout(delayed_stub):
    client, _ = delayed_stub
    with pytest.raises(TimeoutError, match="slow"):
        with client:
            client.exec("slow", timeout=0.01)
    assert client.proc is None


def test_start_requires_previous_process_to_be_stopped(delayed_stub):
    client, _ = delayed_stub
    with client:
        original = client.proc
        with pytest.raises(RuntimeError, match="stop"):
            client.start()
        assert client.proc is original
        assert client.exec("next").payload == {"reply": "next"}


def test_stop_reaps_an_unresponsive_timed_out_process(delayed_stub):
    client, _ = delayed_stub
    client.cmd.append("--ignore-quit")
    client.start()
    process = client.proc
    try:
        with pytest.raises(TimeoutError):
            client.exec("slow", timeout=0.01)
        with pytest.raises(RuntimeError, match="Stub exited unsuccessfully"):
            client.stop(kill_after=0.01)
        assert process.poll() is not None
        assert all(stream.closed for stream in (
            process.stdin, process.stdout, process.stderr,
        ))
        assert not client._reader_thread.is_alive()
        assert not client._stderr_forward_thread.is_alive()
        assert client.proc is None
    finally:
        if process.poll() is None:
            process.kill()
            process.wait()
