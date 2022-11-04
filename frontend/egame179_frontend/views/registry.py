from typing import ClassVar, Protocol


class AppView(Protocol):
    """App view protocol."""

    idx: ClassVar[int]
    menu_option: ClassVar[str]
    icon: ClassVar[str]
    roles: ClassVar[tuple[str]]

    def check_view_data(self) -> bool:
        """Check if data for this view is already fetched.

        Returns:
            bool: True if data is already fetched.
        """
        return True

    def fetch_data(self) -> None:
        """Fetch data for view from backend via API."""

    def render(self) -> None:
        """Render view."""


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
    AppViewsRegistry.views[cls.idx] = cls
    return cls
