"""Main server file for the r/Stocks Sentiment Reddit MCP."""

import logging

from fastmcp import FastMCP
from services.reddit_service import RedditService
from services.visualization_service import VisualizationService

from models import PlotDataPoint


# Create the server
mcp = FastMCP(
    name="r/Stocks Sentiment Reddit",
    dependencies=[
        "asyncpraw>=7.8.1",
        "fastmcp>=2.11.1",
        "textblob>=0.17.1",
        "matplotlib>=3.7.0",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "pillow>=9.5.0",
        "adjusttext>=1.3.0",
        "mpld3>=0.5.11",
        "pytest>=8.4.1",
        "pytest-asyncio>=1.1.0",
        "pytest-cov>=6.2.1",
        "pytest-mock>=3.14.1",
        "python-dotenv>=1.0.0",
        "ruff>=0.12.8",
        "pre-commit>=3.2.0",
    ],
)


# ---- Logging Setup ----


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ---- MCP Tools ----


@mcp.prompt
async def make_r_stocks_plot() -> str:
    """Get a prompt to create a plot with the r/Stocks data."""
    return """Please create a sentiment plot for the r/Stocks subreddit posts. Start by creating a plan by calling 'make_stocks_plot_plan' before you create the plot."""


@mcp.tool
async def make_stocks_plot_plan() -> str:
    """Returns a plan for creating a plot with the r/Stocks data.

    Before you call the create_plot tool, always call this tool to get an exact plan.

    Returns:
        str: A detailed plan for creating the plot with the r/Stocks data.
    """
    return """Here is the exact plan you need to follow to create the plot:

Step 1: Fetch posts
Fetch the latest posts from the r/Stocks subreddit using the fetch_stocks_subreddit_posts tool.

Step 2: Present thoughts
Present your thoughts on the posts to the user. Try to answer the following questions:
- What do I need to analyze to get a good overview of the stocks mentioned in the posts?
- What do I need to analyze to get a good sentiment overview of the stocks mentioned in the posts?
- What stocks are mentioned?
- How often is each stock mentioned? How is the stock mentioned in the posts?
- How is the sentiment for each stock? Is it positive or negative?
- For each stock, why do I judge the sentiment as positive or negative? What are the reasons for this?

Step 3: Fetch detailed post data
For each post from Step 1 that appears to contain stock discussions or mentions (based on title and any available content), call the fetch_single_reddit_post tool to get the complete post data including:
- Full post content (selftext)
- Score and upvote ratio for popularity assessment
- Number of comments for engagement metrics
- Complete metadata for thorough analysis

You should prioritize posts that:
- Have stock symbols or company names in the title
- Appear to be discussion posts (not just links)
- Have substantial engagement (comments/upvotes)
- Look like they contain sentiment-rich content

Step 4: Extract data
Extract the relevant data from the detailed posts obtained in Step 3. Combine different mentions of the same stock to a single symbol. For example, AAPL, Apple, and Apple Inc. should all be combined to AAPL.
Then, you need to calculate the sentiment and presence for each stock symbol:
- Symbol: The stock name with symbol in parentheses (e.g., 'Apple Inc. (AAPL)', 'Tesla Inc. (TSLA)'). It is very important that you convert all stock mentions to this format.
- Sentiment: Estimate how positive or negatively the stock was mentioned in the posts. A positive sentiment means that the authors were optimistic about the stock. 0.0 means neutral, -1.00 means very negative, and 1.00 means very positive. Use the detailed post content, score, and upvote ratio to make more accurate sentiment assessments.
- Presence: Estimate how present the stock was in the posts. A high presence means that the stock was mentioned a lot in the posts. Consider both frequency of mentions and the engagement metrics (score, comments) of posts mentioning the stock.
IT IS CRITICAL THAT YOU DON'T CREATE TWO MARKERS IN THE EXACT SAME POSITION. PLEASE MAKE SLIGHT ADJUSTMENTS (0.02 or so) TO THE SENTIMENT TO AVOID OVERLAPPING MARKERS.

Step 5: Give the user the data
Before the plot is created, return the data to the user. For each stock, return the following information:
- Symbol: The stock name with symbol in parentheses (e.g., 'Apple Inc. (AAPL)', 'Tesla Inc. (TSLA)').
- Sentiment: The sentiment of the stock, a float between -1.00 and 1.00.
- Presence: The presence of the stock, a float between 0.00 and 1.00.
- Summary: A short summary of the stock, including your reasoning for the sentiment and presence values based on the detailed post analysis.
- Links: Direct links to the posts where the stock was mentioned. This should be a list of dictionaries with 'url' and 'title' keys, where 'title' is the original post title.
IT IS CRITICAL THAT YOU TELL THE USER ABOUT THE DATA BEFORE YOU CALL THE create_plot TOOL. THE USER NEEDS TO SEE THE DATA BEFORE THE PLOT IS CREATED.

Step 6: Show the plot to the user
Call the create_plot tool with the extracted data. The data should be a list of dictionaries,
where each dictionary contains the following keys:
- 'Symbol': The stock name with symbol in parentheses (e.g., 'Apple Inc. (AAPL)', 'Tesla Inc. (TSLA)').
- 'Sentiment': -1.00 to 1.00, where 1.00 means that the stock was mentioned positively. The precision of the sentiment should be at least 0.01. 0.00 means neutral, -1.00 means very negative, and 1.00 means very positive.
- 'Presence': 0.00 to 1.00, where 1.00 means that the stock was very very present. The precision of the presence should be at least 0.01.
- 'Summary': A short summary of the stock analysis and reasoning for sentiment/presence values.
- 'Links': A list of dictionaries with 'url' and 'title' keys for the posts where the stock was mentioned.


"""


@mcp.tool
async def fetch_stocks_subreddit_posts() -> dict:
    """Fetches the latest posts from the r/Stocks subreddit.

    Returns:
        dict: A dictionary containing a list of posts with titles and content.
    """
    reddit_service = await RedditService.create()
    return await reddit_service.fetch_subreddit_posts()


@mcp.tool
async def fetch_single_reddit_post(post_id: str) -> dict:
    """Fetches a single Reddit post by ID or URL.

    Args:
        post_id: The Reddit post ID (e.g., '1a2b3c4') or full Reddit URL.

    Returns:
        dict: A dictionary containing the post data with additional metadata like score,
              upvote ratio, number of comments, and subreddit name.
    """
    reddit_service = await RedditService.create()
    return await reddit_service.fetch_single_post(post_id=post_id)


@mcp.tool
async def create_plot(data: list[PlotDataPoint]) -> None:
    """Shows a plot with the r/Stocks data to the user. Before you call this tool, always call the make_stocks_plot_plan tool to get an exact plan.

    Args:
        data (list[PlotDataPoint]): A list of PlotDataPoint containing post data.
    """
    visualization_service = await VisualizationService.create()
    await visualization_service.create_plot(data=data)
