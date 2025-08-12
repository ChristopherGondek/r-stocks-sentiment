"""Conftest file for pytest configuration and fixtures."""

import json
import sys
from pathlib import Path
from typing import AsyncGenerator
import pytest
from pytest_mock import MockerFixture
from unittest.mock import AsyncMock, MagicMock
from dotenv import load_dotenv

# Add project root to Python path IMMEDIATELY (at import time)
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Now we can import models
from models import PlotDataPoint  # noqa: E402


# Load environment variables from .env file before running tests
def pytest_configure(config: pytest.Config) -> None:
    """Load .env file before running tests."""
    # Load environment variables
    env_path = project_root / ".env"
    if env_path.exists():
        load_dotenv(env_path)


@pytest.fixture
def reddit_client_mock(mocker: MockerFixture) -> MagicMock:
    """Mock the asyncpraw Reddit client."""
    return mocker.patch("services.reddit_service.asyncpraw")


@pytest.fixture
def sample_posts() -> list[dict]:
    """Load sample posts data from JSON file."""
    data_file = Path(__file__).parent / "data" / "sample_posts.json"
    return json.loads(data_file.read_text(encoding="utf-8"))


@pytest.fixture
def mock_reddit_client() -> tuple[AsyncMock, AsyncMock]:
    """Create a mock Reddit client with subreddit."""
    mock_reddit = AsyncMock()
    mock_subreddit = AsyncMock()
    mock_reddit.subreddit.return_value = mock_subreddit
    return mock_reddit, mock_subreddit


@pytest.fixture
def mock_posts_factory(sample_posts: list[dict]) -> list[MagicMock]:
    """Factory to create mock posts from sample data."""

    def _create_mock_posts(*, limit: int = None) -> list[MagicMock]:
        posts_data = sample_posts[:limit] if limit else sample_posts
        mock_posts = []

        for post_data in posts_data:
            mock_post = MagicMock()
            mock_post.title = post_data["title"]
            mock_post.selftext = post_data["content"]
            mock_post.url = post_data["url"]
            mock_post.created_utc = post_data["created_utc"]

            # Create mock author
            mock_author = MagicMock()
            mock_author.__str__ = MagicMock(return_value=post_data["author"])
            mock_post.author = mock_author

            mock_posts.append(mock_post)

        return mock_posts

    return _create_mock_posts


@pytest.fixture
def mock_reddit_service(
    mock_reddit_client: tuple[AsyncMock, AsyncMock], mock_posts_factory: callable
) -> callable:
    """Complete mock setup for Reddit service testing."""
    mock_reddit, mock_subreddit = mock_reddit_client

    def _setup_service(
        *, limit: int = 5, should_fail: bool = False, fail_message: str = "API Error"
    ) -> tuple[AsyncMock, AsyncMock, list[MagicMock]]:
        """Setup mock Reddit service with optional failure behavior."""
        if should_fail:
            mock_reddit.subreddit.side_effect = Exception(fail_message)
            return mock_reddit, mock_subreddit, []

        # Reset any previous side effects
        mock_reddit.subreddit.side_effect = None
        mock_reddit.subreddit.return_value = mock_subreddit

        mock_posts = mock_posts_factory(limit=limit)

        # Create async generator for hot posts
        async def mock_hot_posts() -> AsyncGenerator[MagicMock, None]:
            """Async generator to yield mock posts."""
            for post in mock_posts:
                yield post

        mock_subreddit.hot = MagicMock(
            side_effect=lambda *args, **kwargs: mock_hot_posts()
        )

        return mock_reddit, mock_subreddit, mock_posts

    return _setup_service


@pytest.fixture
def sample_plot_data() -> list[PlotDataPoint]:
    """Load sample plot data from JSON file."""
    data_file = Path(__file__).parent / "data" / "sample_plot_data.json"
    return [
        PlotDataPoint(**item)
        for item in json.loads(data_file.read_text(encoding="utf-8"))["data"]
    ]
