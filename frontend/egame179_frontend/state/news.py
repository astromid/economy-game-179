from dataclasses import dataclass
from typing import Any

from egame179_frontend import api
from egame179_frontend.api.cycle import Cycle


@dataclass
class NewsState:  # noqa: WPS214
    """News game state."""

    cycle: Cycle
    _bulletins: list[dict[str, Any]] | None = None

    @property
    def bulletins(self) -> list[dict[str, Any]]:
        """News bulletins.

        Returns:
            list[dict[str, Any]]: list of news bulletins.
        """
        if self._bulletins is None:
            self._bulletins = [bul.dict() for bul in api.BulletinAPI.get_bulletins()]
        return self._bulletins
