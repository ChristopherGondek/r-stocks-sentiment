# r/Stocks Sentiment Analysis MCP Server

A Model Context Protocol (MCP) server that analyzes sentiment and presence of stocks mentioned in the r/Stocks subreddit. This tool fetches recent posts from r/Stocks, analyzes the sentiment around mentioned stocks, and creates interactive visualizations to help understand market sentiment.

## Features

- **Reddit Integration**: Fetches the latest posts from r/Stocks subreddit using the Reddit API
- **Sentiment Analysis**: Analyzes how positively or negatively stocks are mentioned in posts
- **Presence Tracking**: Measures how frequently stocks are discussed
- **Interactive Visualization**: Creates scatter plots showing sentiment vs presence with hover functionality
- **MCP Protocol**: Implements the Model Context Protocol for integration with AI assistants

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd r-stocks-sentiment
```

2. Install dependencies using uv (recommended) or pip:

```bash
# Using uv
uv sync

# Or using pip
pip install -e .
```

3. Create and update .env file (see below)

4. Install the MCP with claude desktop

```bash
uv run fastmcp install claude-desktop server.py --env-file .env
```

## Configuration

### Reddit API Setup

You need to set up Reddit API credentials to fetch posts from r/Stocks:

1. Go to [Reddit App Preferences](https://www.reddit.com/prefs/apps)
2. Click "Create App" or "Create Another App"
3. Choose "script" as the app type
4. Note down your `client_id` and `client_secret`

### Environment Variables

Create a `.env` file in the project root with your Reddit API credentials:

```bash
cp .env.example .env
```

```env
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_client_secret_here
```

## Usage

### Running the MCP Server

Start the server:

```bash
python server.py
```

The server provides the following MCP tools:

### Available Tools

1. **`make_stocks_plot_plan`**: Returns a detailed plan for creating sentiment analysis plots
2. **`fetch_stocks_subreddit_posts`**: Fetches the latest posts from r/Stocks subreddit
3. **`fetch_single_reddit_post`**: Fetches detailed data for a single Reddit post by ID or URL
4. **`create_plot`**: Creates an interactive scatter plot visualization of stock sentiment and presence

### Typical Workflow

1. **Get the Plan**: Call `make_stocks_plot_plan` to understand the analysis workflow
2. **Fetch Data**: Use `fetch_stocks_subreddit_posts` to get recent r/Stocks posts
3. **Get Detailed Posts**: Use `fetch_single_reddit_post` to get complete post data including content, scores, and engagement metrics for thorough analysis
4. **Analyze**: Extract stock mentions, calculate sentiment (-1.0 to 1.0) and presence (0.0 to 1.0)
5. **Visualize**: Use `create_plot` with the analyzed data to create an interactive chart

### Data Format

The `create_plot` tool expects data in the following format:

```python
[
    {
        "Symbol": "Apple Inc. (AAPL)",
        "Sentiment": 0.75,  # -1.0 (very negative) to 1.0 (very positive)
        "Presence": 0.85    # 0.0 (rarely mentioned) to 1.0 (very present)
    },
    # ... more stocks
]
```

## Visualization Features

The generated plots include:

- **X-axis**: Sentiment score (-1.0 to 1.0)
- **Y-axis**: Presence score (0.0 to 1.0)
- **Color-coded markers**: Each stock has a unique color
- **Size-based markers**: Marker size reflects presence level
- **Interactive hover**: Hover over markers to see detailed information
- **Legend**: Shows all stocks with their corresponding colors

## Dependencies

### Core Dependencies

- **asyncpraw**: Reddit API client for Python
- **fastmcp**: FastMCP framework for MCP server implementation
- **textblob**: Text processing and sentiment analysis
- **matplotlib**: Plotting and visualization
- **pandas**: Data manipulation and analysis
- **numpy**: Numerical computations
- **pillow**: Image processing library
- **adjusttext**: Text positioning in plots
- **mpld3**: Interactive matplotlib plots for web display
- **python-dotenv**: Environment variable management

### Development Dependencies

- **pytest**: Testing framework
- **pytest-asyncio**: Async testing support
- **pytest-cov**: Test coverage reporting
- **pytest-mock**: Mocking utilities for tests
- **ruff**: Code formatting and linting
- **pre-commit**: Git hooks for code quality

## Technical Details

- **Python Version**: Requires Python 3.11 or higher
- **Protocol**: Implements Model Context Protocol (MCP)
- **API**: Uses Reddit's API through asyncpraw
- **Visualization**: Interactive matplotlib plots with hover functionality
- **Logging**: Comprehensive logging for debugging and monitoring

## Contributing

We welcome contributions! To ensure code quality and consistency, please follow these steps:

### Setup for Contributors

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone <your-fork-url>
   cd r-stocks-sentiment
   ```
3. Install dependencies:
   ```bash
   uv sync
   ```
4. Install pre-commit hooks to ensure code formatting with ruff:
   ```bash
   uv run pre-commit install
   ```

### Making Changes

1. Create a feature branch from main
2. Make your changes
3. Run tests to ensure everything works:
   ```bash
   uv run pytest
   ```
4. The pre-commit hooks will automatically run ruff formatting when you commit
5. Add tests if applicable
6. Submit a pull request

### Code Quality

This project uses:

- **ruff** for code formatting and linting
- **pre-commit** hooks to enforce code quality standards
- **pytest** for testing

The pre-commit hooks will automatically format your code and catch common issues before commits.

## License

This project is open source. Please check the license file for details.

## Version

Current version: 0.1.0
