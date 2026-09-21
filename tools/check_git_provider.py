"""Run provider tests from exact audited pure wheels without installing them."""
import argparse
import hashlib
from pathlib import Path
import sys
import unittest
import zipfile

PINS = {
    "dulwich-1.2.15-py3-none-any.whl": "5c863992962bab0fc5f75be132399a16f670f2a9283faf9aaeb953fd8891db83",
    "urllib3-2.8.0-py3-none-any.whl": "0cf3cae568d36aa9576b28dfb35f11328f1cb974ca7647d9475ebb86c75ac6e3",
    "typing_extensions-4.16.0-py3-none-any.whl": "481caa481374e813c1b176ada14e97f1f67a4539ce9cfeb3f350d78d6370c2e8",
}


def reject_process_and_network(event, args):
    if event.startswith(("subprocess.", "os.exec", "os.spawn")) or event in {
        "os.system", "os.fork", "socket.connect", "socket.bind", "socket.getaddrinfo"
    }:
        raise RuntimeError("Offline provider test rejected " + event)


def load_verified_wheels(wheel_directory):
    for name, expected in PINS.items():
        path = wheel_directory/name
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError("Unapproved wheel bytes")
        with zipfile.ZipFile(path) as archive:
            if any(Path(member).suffix.lower() in {".pyd", ".so", ".dll", ".dylib", ".exe", ".a", ".lib"}
                   for member in archive.namelist()):
                raise ValueError("Native archive member")
        sys.path.insert(0, str(path.resolve()))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("wheel_directory", type=Path)
    args = parser.parse_args()
    load_verified_wheels(args.wheel_directory)
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root/"src"))
    sys.addaudithook(reject_process_and_network)
    result = unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.discover(str(root/"tests_git")))
    sys.exit(not result.wasSuccessful())
