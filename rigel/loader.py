import marshal
import struct
import sys
import time
from dataclasses import dataclass


PYTHON_MAGIC_VERSION_MAP = {
    3430: (3, 10),  # Python 3.10a1 3430
    3431: (3, 10),  # Python 3.10a1 3431
    3432: (3, 10),  # Python 3.10a2 3432
    3433: (3, 10),  # Python 3.10a2 3433
    3434: (3, 10),  # Python 3.10a6 3434
    3435: (3, 10),  # Python 3.10a7 3435
    3436: (3, 10),  # Python 3.10b1 3436
    3437: (3, 10),  # Python 3.10b1 3437
    3438: (3, 10),  # Python 3.10b1 3438
    3439: (3, 10),  # Python 3.10b1 3439
}

PYTHON_VERSION_MAGIC_MAP = dict((value, key) for key, value in PYTHON_MAGIC_VERSION_MAP.items())


def _pyc_header(version: tuple[int, int]) -> int:
    if version >= (3, 10):
        return 16

    return 12


PYTHON_VERSION: tuple[int, int] = sys.version_info[:2]
PYC_HEADER = _pyc_header(PYTHON_VERSION)


def dump(code, fp, *, version: tuple[int, int]) -> None:
    """
    Serialize ``obj`` as a PYC formatted stream to ``fp`` (a
       ``.write()``-supporting file-like object).
    """
    magic = (PYTHON_VERSION_MAGIC_MAP[version]).to_bytes(2, 'little') + b'\r\n'

    fp.write(magic)
    fp.write(b'\x00\x00\x00\x00')
    fp.write(b'\x00\x00\x00\x00')
    fp.write(b'\x00\x00\x00\x00')

    marshal.dump(code, fp)


@dataclass
class CodeInfo:
    python_version: tuple[int, int]
    modified: bytes
    source_size: bytes
    code: bytes

    def __repr__(self):
        return '\n'.join([
            f'python_version={self.unpack_python_version()}',
            f'timestamp={self.unpack_modified()}',
            f'file_size={self.unpack_source_size()}b',
        ])

    def unpack_modified(self) -> str:
        return time.asctime(time.localtime(struct.unpack('=L', self.modified)[0]))

    def unpack_source_size(self) -> int:
        return struct.unpack('=L', self.source_size)[0]

    def unpack_code(self):
        return marshal.loads(self.code)

    def unpack_python_version(self):
        return PYTHON_MAGIC_VERSION_MAP[struct.unpack('<H', self.python_version)[0]]


def load(fp) -> CodeInfo:
    """Deserialize ``fp`` to a Python object."""
    python_version = fp.read(2)

    _ = fp.read(2)  # cr, lf
    _ = fp.read(4)  # bit_field

    return CodeInfo(
        python_version=python_version,
        modified=fp.read(4),
        source_size=fp.read(4),
        code=fp.read(),
    )
