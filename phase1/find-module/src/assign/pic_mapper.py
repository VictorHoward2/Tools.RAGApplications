from __future__ import annotations

from assign.keyword_config import PIC_BY_MODULE


def get_pic_by_module(module_name: str | None) -> str | None:
    if not module_name:
        return None
    return PIC_BY_MODULE.get(module_name)