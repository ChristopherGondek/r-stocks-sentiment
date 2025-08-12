"""Reddit service for fetching posts from r/Stocks subreddit."""

import logging
import os
from dataclasses import dataclass, field
from typing import Any, Dict, Generator, Optional

import asyncpraw


logger = logging.getLogger(__name__)


@dataclass
class RedditService:
    """Service for interacting with Reddit API."""

    client_id: Optional[str] = field(default=None, init=False)
    client_secret: Optional[str] = field(default=None, init=False)
    client: Optional[asyncpraw.Reddit] = field(default=None, init=False)

    @classmethod
    async def create(cls) -> "RedditService":
        """Create a new RedditService instance with credentials from environment.

        Returns:
            RedditService: A new instance of the service with credentials populated.
        """
        instance = cls()

        client_id = os.environ.get("REDDIT_CLIENT_ID")
        client_secret = os.environ.get("REDDIT_CLIENT_SECRET")

        instance.client_id = client_id
        instance.client_secret = client_secret

        if not client_id or not client_secret:
            logger.error("Reddit API credentials not found in environment variables")
            instance.client = None
            return instance

        try:
            client = asyncpraw.Reddit(
                client_id=client_id,
                client_secret=client_secret,
                user_agent="StocksAnalyzer/0.1 MCP",
            )
            instance.client = client
            return instance
        except Exception as e:
            logger.error(f"Error creating Reddit client: {str(e)}")
            instance.client = None
            return instance

    async def fetch_subreddit_posts(
        self, *, subreddit_name: str = "Stocks", limit: int = 10
    ) -> Dict[str, Any]:
        """Fetch posts from a specified subreddit.

        Args:
            subreddit_name: Name of the subreddit to fetch from.
            limit: Maximum number of posts to fetch.

        Returns:
            Dict containing either posts list or error message.
        """
        if self.client is None:
            return {"error": "Failed to create Reddit client. Check your credentials."}

        try:
            subreddit = await self.client.subreddit(subreddit_name)
            hot_posts = subreddit.hot(limit=limit)

            posts = []
            async for post in hot_posts:
                post_data = {
                    "title": post.title,
                    "content": post.selftext,
                    "url": post.url,
                    "author": str(post.author) if post.author else "Unknown",
                    "created_utc": post.created_utc,
                }
                posts.append(post_data)
                logger.info(
                    f"Fetched post: {post_data['title']} by {post_data['author']}"
                )

            return {"posts": posts}
        except Exception as e:
            logger.error(f"Error fetching posts from r/{subreddit_name}: {str(e)}")
            return {"error": f"Failed to fetch posts: {str(e)}"}

    async def fetch_single_post(
        self, *, post_id: str, comment_limit: int = 50
    ) -> Dict[str, Any]:
        """Fetch a single Reddit post by ID or URL with comments.

        Args:
            post_id: The Reddit post ID or full Reddit URL.
            comment_limit: Maximum number of comments to include.

        Returns:
            Dict containing either post data or error message.
        """
        if self.client is None:
            return {"error": "Failed to create Reddit client. Check your credentials."}

        try:
            # Accept raw ID or full URL
            if post_id.startswith("http"):
                parts = post_id.split("/")
                if "comments" in parts:
                    post_id = parts[parts.index("comments") + 1]
                else:
                    return {"error": "Invalid Reddit URL format"}

            # Fetch submission
            submission = await self.client.submission(id=post_id)
            await submission.load()

            # Fetch top comments
            submission.comment_sort = "top"
            submission.comment_limit = comment_limit
            await submission.comments.replace_more(limit=0)

            def _flatten_comments(forest: list) -> Generator[Any, None, None]:
                """Depth-first iterator over a comment forest."""
                for comment in forest:
                    yield comment
                    if comment.replies:
                        yield from _flatten_comments(comment.replies)

            raw_comments = list(_flatten_comments(submission.comments))[:comment_limit]

            comments = [
                {
                    "id": comment.id,
                    "author": str(comment.author) if comment.author else "Unknown",
                    "body": comment.body,
                    "score": comment.score,
                    "created_utc": comment.created_utc,
                    "parent_id": comment.parent_id,
                }
                for comment in raw_comments
            ]

            # Assemble response
            post_data = {
                "title": submission.title,
                "content": submission.selftext,
                "url": submission.url,
                "author": str(submission.author) if submission.author else "Unknown",
                "created_utc": submission.created_utc,
                "score": submission.score,
                "upvote_ratio": submission.upvote_ratio,
                "num_comments": submission.num_comments,
                "subreddit": str(submission.subreddit),
                "comments": comments,
            }

            logger.info(
                f"Fetched post '{post_data['title']}' with {len(comments)} comments"
            )
            return {"post": post_data}

        except Exception as e:
            logger.error(f"Error fetching post {post_id}: {e}")
            return {"error": f"Failed to fetch post: {e}"}

    async def close(self) -> None:
        """Close the Reddit client connection."""
        if self.client is not None:
            await self.client.close()
            self.client = None
