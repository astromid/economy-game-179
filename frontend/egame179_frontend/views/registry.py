from typing import ClassVar, Protocol


class AppView(Protocol):
    """App view protocol."""

    idx: ClassVar[int]
    name: ClassVar[str]
    icon: ClassVar[str]
    roles: ClassVar[tuple[str, ...]]

    def render(self) -> None:  # noqa: D102
        ...  # noqa: WPS428


class AppViewsRegistry:
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
        filtered_ids = sorted(idx for idx, view in views.items() if role in view.roles)
        filtered_views = {views[idx].name: views[idx] for idx in filtered_ids}
        # create AppView instances
        return {option: view() for option, view in filtered_views.items()}


def appview(cls: type[AppView]) -> type[AppView]:
    """App view register decorator.

    Args:
        cls (AppView): app view class.

    Raises:
        KeyError: in case of duplicated AppView indexes.

    Returns:
        AppView: input class.
    """
    if cls.idx in AppViewsRegistry.views:
        raise KeyError(f"Incorrect idx in {cls}: index {cls.idx} already in use")
    AppViewsRegistry.views[cls.idx] = cls
    return cls
