from __future__ import annotations

from abc import ABC, ABCMeta
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from ..files.ObjectReader import ObjectReader
    from ..files.SerializedFile import SerializedFile


class SubObject(ABC, metaclass=ABCMeta):
    def __init__(self, **kwargs):
        required_keys = getattr(self.__class__, "__required_keys__", None)
        if required_keys is None:
            required_keys = tuple(
                key
                for key, value in self.__annotations__.items()
                if not value.startswith("Optional[")
            )
            self.__class__.__required_keys__ = required_keys
        if not all(key in kwargs for key in required_keys):
            raise ValueError("Missing required keys")
        self.__dict__.update(kwargs)

    def __repr__(self) -> str:
        def format_value(v):
            vstr = repr(v)
            if len(vstr) > 100:
                return vstr[:97] + "..."
            return vstr

        inner_str = ", ".join(
            f"{k}={format_value(v)}" for k, v in self.__dict__.items()
        )

        return f"{self.__class__.__name__}({inner_str})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __hash__(self) -> int:
        return hash(tuple(self.__dict__.items()))


class Object(SubObject, ABC):
    object_reader: Optional[ObjectReader] = None

    def set_object_reader(self, object_info: ObjectReader[Any]):
        self.object_reader = object_info

    @property
    def assets_file(self) -> Optional[SerializedFile]:
        if self.object_reader:
            return self.object_reader.assets_file
        return None

    def save(self) -> None:
        if self.object_reader is None:
            raise ValueError("ObjectReader not set")

        self.object_reader.save_typetree(self)
