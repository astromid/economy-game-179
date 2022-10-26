from collections.abc import Iterable
from typing import ClassVar, Protocol


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
    def role_views(cls, role: str) -> dict[str, AppView]:
        """Filter views by role.

        Args:
            role (str): role to filter views by.

        Returns:
            dict[str, AppView]: views for this role.
        """
        views = cls.views
        filtered_indexes = sorted(idx for idx, view in views.items() if role in view.roles)
        filtered_views = {views[idx].menu_option: views[idx] for idx in filtered_indexes}
        # create AppView instances
        return {option: view() for option, view in filtered_views.items()}


def appview(cls: type[AppView]) -> type[AppView]:
    """App view register decorator.

    Args:
        cls (AppView): app view class.

    Returns:
        AppView: input class.
    """
    AppViews.views[cls.idx] = cls
    return cls
