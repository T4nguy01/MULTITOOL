from core import network, ping


def test_set_ip_rejects_bad_input_without_running_anything(monkeypatch):
    monkeypatch.setattr(network.subprocess, "run", lambda *a, **k: (_ for _ in ()).throw(AssertionError))
    monkeypatch.setattr(network, "is_admin", lambda: True)
    assert "invalides" in network.set_ip("eth0", "1.2.3", "255.255.255.0")
    assert "invalides" in network.set_ip("eth0", "1.2.3.4", "255.0.255.0")


def test_set_ip_linux_uses_prefix(monkeypatch):
    calls = []
    monkeypatch.setattr(network.sys, "platform", "linux")
    monkeypatch.setattr(network.subprocess, "run", lambda cmd, **k: calls.append(cmd))
    network.set_ip("eth0", "192.168.1.10", "255.255.255.0", "192.168.1.1")
    assert calls[0] == ["sudo", "ip", "addr", "add", "192.168.1.10/24", "dev", "eth0"]
    assert calls[1][:5] == ["sudo", "ip", "route", "add", "default"]


def test_ping_rejects_option_injection():
    assert "invalide" in ping.ping_host("-f 8.8.8.8")
