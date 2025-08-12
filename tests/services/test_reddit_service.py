"""Test cases for RedditService to ensure it correctly fetches posts from a subreddit."""

import pytest
from unittest.mock import MagicMock, patch

from services.reddit_service import RedditService


@pytest.mark.asyncio
async def test_fetch_subreddit_posts(
    reddit_client_mock: MagicMock,
    mock_reddit_service: callable,
    sample_posts: list[dict],
) -> None:
    """Test fetching posts from a subreddit using the RedditService."""
    # Setup mock with 5 posts
    mock_reddit, mock_subreddit, mock_posts = mock_reddit_service(limit=5)

    # Configure the reddit client mock to return our mock reddit instance
    reddit_client_mock.Reddit.return_value = mock_reddit

    # Create RedditService instance
    service = await RedditService.create()

    # Test fetch_subreddit_posts
    result = await service.fetch_subreddit_posts(subreddit_name="Stocks", limit=5)

    # Verify the result structure
    assert "posts" in result
    assert len(result["posts"]) == 5

    # Verify the first post matches sample data
    first_post = result["posts"][0]
    expected_first_post = sample_posts[0]

    assert first_post["title"] == expected_first_post["title"]
    assert first_post["content"] == expected_first_post["content"]
    assert first_post["url"] == expected_first_post["url"]
    assert first_post["author"] == expected_first_post["author"]
    assert first_post["created_utc"] == expected_first_post["created_utc"]

    # Verify Reddit client was called correctly
    mock_reddit.subreddit.assert_called_once_with("Stocks")
    mock_subreddit.hot.assert_called_once_with(limit=5)


@pytest.mark.asyncio
async def test_fetch_subreddit_posts_no_credentials() -> None:
    """Test fetching posts when Reddit credentials are missing."""
    with patch.dict("os.environ", {}, clear=True):
        # Create RedditService instance without credentials
        service = await RedditService.create()

        # Test fetch_subreddit_posts should return error
        result = await service.fetch_subreddit_posts(subreddit_name="Stocks", limit=5)

        # Verify error response
        assert "error" in result
        assert "Failed to create Reddit client" in result["error"]


@pytest.mark.asyncio
async def test_fetch_subreddit_posts_api_error(
    reddit_client_mock: MagicMock,
    mock_reddit_service: callable,
    sample_posts: list[dict],
) -> None:
    """Test fetching posts when Reddit API throws an exception."""
    # Setup mock to fail with API error
    mock_reddit, mock_subreddit, mock_posts = mock_reddit_service(
        should_fail=True, fail_message="API Error"
    )

    # Configure the reddit client mock to return our mock reddit instance
    reddit_client_mock.Reddit.return_value = mock_reddit

    # Create RedditService instance
    service = await RedditService.create()

    # Test fetch_subreddit_posts should return error
    result = await service.fetch_subreddit_posts(subreddit_name="Stocks", limit=5)

    # Verify error response
    assert "error" in result
    assert "Failed to fetch posts: API Error" in result["error"]
