import itertools

import networkx as nx
from fastapi import Depends
from sqlmodel import SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

from egame179_backend.db.session import get_db_session


class Market(SQLModel, table=True):
    """Markets table."""

    __tablename__ = "markets"  # type: ignore

    id: int
    name: str
    ring: int
    home_user: int | None


class MarketConnection(SQLModel, table=True):
    """Market connections table."""

    __tablename__ = "market_connections"  # type: ignore

    source: int
    target: int


class MarketShare(SQLModel, table=True):
    """Market shares table."""

    __tablename__ = "market_shares"  # type: ignore

    cycle: int
    user: int
    market: int
    share: float
    position: int
    unlocked: bool


class MarketDAO:
    """Class for accessing markets & market_connections table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def select_markets(self) -> list[Market]:
        """Get markets.

        Returns:
            list[Market]: markets in the game.
        """
        query = select(Market)
        raw_markets = await self.session.exec(query)  # type: ignore
        return raw_markets.all()

    async def select_connections(self) -> list[MarketConnection]:
        """Get market graph edges.

        Returns:
            list[MarketConnections]: graph edges.
        """
        query = select(MarketConnection)
        raw_connections = await self.session.exec(query)  # type: ignore
        return raw_connections.all()

    async def get_graph(self) -> nx.Graph:
        """Get market graph.

        Returns:
            nx.Graph: networkx Graph.
        """
        graph = nx.Graph()
        edges = await self.select_connections()
        graph.add_edges_from([(edge.source, edge.target) for edge in edges])
        return graph

    async def select_shares(
        self,
        cycle: int | None = None,
        user: int | None = None,
        nonzero: bool = False,
    ) -> list[MarketShare]:
        """Get market shares.

        Args:
            cycle (int, optional): target cycle. If None, return shares for all cycles.
            user (int, optional): target user id. If None, return shares for all users.
            nonzero (bool): select only nonzero positions. Defaults to False.

        Returns:
            list[MarketShare]: markets shares.
        """
        query = select(MarketShare)
        if cycle is not None:
            query = query.where(MarketShare.cycle == cycle)
        if user is not None:
            query = query.where(MarketShare.user == user)
        if nonzero:
            query = query.where(MarketShare.position > 0)
        raw_shares = await self.session.exec(query)  # type: ignore
        return raw_shares.all()

    async def create_shares(self, cycle: int, users: list[int], unlocked: set[tuple[int, int]]) -> None:
        """Create share records for new cycle.

        Args:
            cycle (int): target cycle.
            users (list[int]): player ids.
            unlocked (set[tuple[int, int]]): set of unlocked markets (user id, market_id).
        """
        markets = await self.select_markets()
        shares = [
            MarketShare(
                cycle=cycle,
                user=user,
                market=market.id,
                share=0,
                position=0,
                unlocked=(user, market.id) in unlocked or (market.home_user == user),
            )
            for user, market in itertools.product(users, markets)
        ]
        self.session.add_all(shares)
        await self.session.commit()

    async def update_shares(self, shares: list[MarketShare]) -> None:
        """Update share records.

        Args:
            shares (list[MarketShare]): updated share records.
        """
        self.session.add_all(shares)
        await self.session.commit()
