"""Local HTTPS certificates so phone browsers allow camera access.

Browsers only give a web page the camera on a *secure* origin (HTTPS, or
http://localhost). Phones reach the Mac by its LAN address, so the server needs
HTTPS. We create our own small certificate authority (CA) once and sign a
server certificate for the Mac's current addresses with it.

Two ways to use it on a phone:

* Quick: open the page and accept the browser's certificate warning.
* Better (no warnings, and iOS WebSockets are happier): install the CA once.
  Download http://<mac>:8080/ca.crt on the phone. iPhone: Settings > General >
  VPN & Device Management > install the profile, then Settings > General >
  About > Certificate Trust Settings > enable full trust for "BallTracker
  Local CA". Android: Settings > Security > Install a certificate > CA.

The CA private key never leaves the Mac (``data/live/tls/ca.key``). Delete the
``tls`` folder to start over.
"""

from __future__ import annotations

import datetime as dt
import ipaddress
import socket
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID

CA_NAME = "BallTracker Local CA"


def lan_addresses() -> list[str]:
    """IPv4 addresses of this machine that phones on the LAN can reach."""
    ips: set[str] = set()
    try:
        # Connecting a UDP socket sends nothing; it just picks the outgoing interface.
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("10.255.255.255", 1))
        ips.add(s.getsockname()[0])
        s.close()
    except OSError:
        pass
    # Other interfaces (e.g. Ethernet + Wi-Fi). Resolving our own hostname can
    # hang for many seconds on macOS (mDNS), so read the interfaces instead.
    import subprocess

    v6: list[str] = []
    try:
        out = subprocess.run(["ifconfig"], capture_output=True, text=True, timeout=2).stdout
        for line in out.splitlines():
            parts = line.split()
            if len(parts) >= 2 and parts[0] == "inet":
                ips.add(parts[1])
            # Stable global IPv6 (not link-local, not temporary, not the CLAT address).
            elif (len(parts) >= 2 and parts[0] == "inet6" and not parts[1].lower().startswith("fe80")
                  and "%" not in parts[1] and parts[1] != "::1"
                  and "temporary" not in parts and "clat46" not in parts and "deprecated" not in parts):
                v6.append(parts[1])
    except (OSError, subprocess.SubprocessError):
        pass

    def reachable(ip: str) -> bool:
        # 127.x: loopback. 192.0.0.0/29: the IPv4 an iPhone hotspot on an IPv6-only carrier gives
        # (464XLAT/CLAT); other devices on the hotspot can't reach it. 169.254.x: link-local.
        return not (ip.startswith("127.") or ip.startswith("192.0.0.") or ip.startswith("169.254."))

    v4 = sorted(ip for ip in ips if reachable(ip))
    # IPv6 only when there is no usable IPv4 (e.g. an IPv6-only iPhone hotspot).
    return v4 if v4 else sorted(set(v6))


def url_host(ip: str) -> str:
    """Address as written in a URL: IPv6 in brackets."""
    return f"[{ip}]" if ":" in ip else ip


def hostnames() -> list[str]:
    names = {"localhost"}
    h = socket.gethostname()
    if h:
        names.add(h)
        names.add(h if h.endswith(".local") else h.split(".")[0] + ".local")
    return sorted(names)


def _write_key(path: Path, key) -> None:
    path.write_bytes(key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
                                       serialization.NoEncryption()))
    path.chmod(0o600)


def _load_key(path: Path):
    return serialization.load_pem_private_key(path.read_bytes(), password=None)


def ensure_ca(tls_dir: Path) -> tuple[Path, Path]:
    tls_dir.mkdir(parents=True, exist_ok=True)
    crt, key_p = tls_dir / "ca.crt", tls_dir / "ca.key"
    if crt.exists() and key_p.exists():
        return crt, key_p
    key = ec.generate_private_key(ec.SECP256R1())
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, CA_NAME),
                      x509.NameAttribute(NameOID.ORGANIZATION_NAME, "BallTracker (local)")])
    now = dt.datetime.now(dt.timezone.utc)
    cert = (
        x509.CertificateBuilder()
        .subject_name(name).issuer_name(name).public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - dt.timedelta(days=1))
        .not_valid_after(now + dt.timedelta(days=3650))
        .add_extension(x509.BasicConstraints(ca=True, path_length=0), critical=True)
        .add_extension(x509.KeyUsage(digital_signature=True, key_cert_sign=True, crl_sign=True,
                                     content_commitment=False, key_encipherment=False, data_encipherment=False,
                                     key_agreement=False, encipher_only=False, decipher_only=False), critical=True)
        .add_extension(x509.SubjectKeyIdentifier.from_public_key(key.public_key()), critical=False)
        .sign(key, hashes.SHA256())
    )
    _write_key(key_p, key)
    crt.write_bytes(cert.public_bytes(serialization.Encoding.PEM))
    return crt, key_p


def ensure_server_cert(tls_dir: Path, extra_hosts: list[str] | None = None) -> tuple[Path, Path, list[str]]:
    """Server cert for the current LAN addresses; re-issued when they change."""
    ca_crt_p, ca_key_p = ensure_ca(tls_dir)
    ips = lan_addresses() + ["127.0.0.1"]
    names = hostnames() + list(extra_hosts or [])
    want = sorted(set(ips) | set(names))
    crt_p, key_p, stamp = tls_dir / "server.crt", tls_dir / "server.key", tls_dir / "server.hosts"
    if crt_p.exists() and key_p.exists() and stamp.exists() and stamp.read_text().split() == want:
        return crt_p, key_p, want
    ca_cert = x509.load_pem_x509_certificate(ca_crt_p.read_bytes())
    ca_key = _load_key(ca_key_p)
    key = ec.generate_private_key(ec.SECP256R1())
    now = dt.datetime.now(dt.timezone.utc)
    sans: list[x509.GeneralName] = [x509.DNSName(n) for n in sorted(set(names))]
    for ip in sorted(set(ips)):
        sans.append(x509.IPAddress(ipaddress.ip_address(ip)))
    cert = (
        x509.CertificateBuilder()
        .subject_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "BallTracker server")]))
        .issuer_name(ca_cert.subject).public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - dt.timedelta(days=1))
        .not_valid_after(now + dt.timedelta(days=397))  # Apple caps trusted TLS certs at 398 days
        .add_extension(x509.SubjectAlternativeName(sans), critical=False)
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        .add_extension(x509.ExtendedKeyUsage([ExtendedKeyUsageOID.SERVER_AUTH]), critical=False)
        .add_extension(x509.AuthorityKeyIdentifier.from_issuer_public_key(ca_key.public_key()), critical=False)
        .sign(ca_key, hashes.SHA256())
    )
    _write_key(key_p, key)
    crt_p.write_bytes(cert.public_bytes(serialization.Encoding.PEM) + ca_crt_p.read_bytes())
    stamp.write_text(" ".join(want))
    return crt_p, key_p, want
