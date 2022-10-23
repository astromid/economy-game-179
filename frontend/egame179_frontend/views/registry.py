from typing import ClassVar, Protocol, Type
from collections.abc import Iterable


class AppView(Protocol):
    """App view protocol."""

    idx: ClassVar[int]
    menu_option: ClassVar[str]
    icon: ClassVar[str]
    roles: ClassVar[Iterable[str]]

    def render(self) -> None:
        """Render view."""


class AppViews:
    """App views registry."""

    views: dict[int, type[AppView]] = {}

    @classmethod
    def filter_views(cls, role: str) -> dict[str, type[AppView]]:
        """Filter views by role.

        Args:
            role (str): role to filter views by.

        Returns:
            dict[str, Type[AppView]]: filtered views.
        """
        filtered_views: dict[str, type[AppView]] = {}
        for idx in range(len(cls.views)):  # noqa: WPS518
            view = cls.views[idx]
            if role in view.roles:
                filtered_views[view.menu_option] = view
        return filtered_views


def appview(cls: type[AppView]) -> type[AppView]:
    """App view register decorator.

    Args:
        cls (AppView): app view class.

    Returns:
        AppView: input class.
    """
    AppViews.views[cls.idx] = cls
    return cls
