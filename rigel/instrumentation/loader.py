import sys
from importlib.abc import MetaPathFinder
from importlib.machinery import ModuleSpec, PathFinder, SourceFileLoader, SourcelessFileLoader
from types import ModuleType
from typing import Sequence

from more_itertools import first_true


class RigelLoader:
    loaders: list['RigelLoader'] = []

    def __init_subclass__(cls, **kwargs) -> None:
        cls.loaders.append(cls)

    @classmethod
    def get_loader(cls):
        return cls.__mro__[2]


class RigelSourceFileLoader(RigelLoader, SourcelessFileLoader):
    ...


class RigelSourcelessFileLoader(RigelLoader, SourceFileLoader):
    ...


def is_loader(loader, loader_b: RigelLoader) -> bool:
    return isinstance(loader, loader_b.get_loader())


def rigel_loader(loader):
    return first_true(RigelLoader.loaders, pred=lambda loader_: is_loader(loader, loader_))


class ImportHook:
    def __enter__(self) -> 'ImportHook':
        if first_true(sys.meta_path, pred=lambda _: isinstance(_, RigelMetaPathFinder)) is None:
            sys.meta_path.insert(0, RigelMetaPathFinder())

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.meta_path = [
            meta_path_object
            for meta_path_object in sys.meta_path
            if not isinstance(meta_path_object, RigelMetaPathFinder)
        ]


def instrument_imports() -> ImportHook:
    return ImportHook()


class RigelMetaPathFinder(MetaPathFinder):
    def find_spec(
            self,
            fullname: str, path: Sequence[str] | None,
            target: ModuleType | None = ...
    ) -> ModuleSpec | None:
        spec = PathFinder.find_spec(fullname, path, target)
        if spec is None:
            return

        spec.loader = rigel_loader(loader=spec.loader)(spec.loader.name, spec.loader.path)

        return spec
