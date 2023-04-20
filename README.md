<h1 align="center">
  <br>🪐 Rigel - WIP</br>
</h1>

*Python bytecode manipulation library and analysis framework.*

[![Build Status](https://github.com/PrVrSs/rigel/workflows/test/badge.svg?branch=main&event=push)](https://github.com/PrVrSs/rigel/actions?query=workflow%3Atest)
[![Codecov](https://codecov.io/gh/PrVrSs/rigel/branch/main/graph/badge.svg)](https://codecov.io/gh/PrVrSs/rigel)
[![License](https://img.shields.io/badge/License-Apache2.0-green.svg)](https://github.com/PrVrSs/rigel/blob/master/LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.10-blue)](https://www.python.org/)
[![Linting](https://img.shields.io/badge/linting-pylint-yellowgreen)](https://github.com/pylint-dev/pylint)

---

### Example

```python
import dis

from rigel import dump, make_code_object


def main():
    code_object = make_code_object(
        instructions=[
            dis.Instruction(opname='LOAD_NAME', opcode=101, arg=0, argval='print', argrepr='print', offset=0, starts_line=1, is_jump_target=False),
            dis.Instruction(opname='LOAD_CONST', opcode=100, arg=0, argval='string 1', argrepr="'string 1'", offset=2, starts_line=None, is_jump_target=False),
            dis.Instruction(opname='CALL_FUNCTION', opcode=131, arg=1, argval=1, argrepr='', offset=4, starts_line=None, is_jump_target=False),
            dis.Instruction(opname='POP_TOP', opcode=1, arg=None, argval=None, argrepr='', offset=6, starts_line=None, is_jump_target=False),
            dis.Instruction(opname='LOAD_CONST', opcode=100, arg=1, argval=None, argrepr='None', offset=8, starts_line=None, is_jump_target=False),
            dis.Instruction(opname='RETURN_VALUE', opcode=83, arg=None, argval=None, argrepr='', offset=10, starts_line=None, is_jump_target=False),
        ]
    )
    
    with open('filename.pyc', 'wb') as fp:
        dump(code_object, fp, version=(3, 10))


if __name__ == '__main__':
    main()
```


## Supported Python

- [ ] 3.9
- [X] 3.10
- [ ] 3.11
