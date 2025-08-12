"""Visualization service for creating stock sentiment plots."""

import json
import logging
import os
import tempfile
import webbrowser

from models import PlotDataPoint, PlotDatasetPoint

logger = logging.getLogger(__name__)


class VisualizationService:
    """Service for creating interactive stock sentiment visualizations."""

    def __init__(self) -> None:
        """Initialize the visualization service."""
        self.colors = [
            "#FF6384",
            "#36A2EB",
            "#FFCE56",
            "#4BC0C0",
            "#9966FF",
            "#FF9F40",
            "#FF6384",
            "#C9CBCF",
            "#4BC0C0",
            "#FF6384",
        ]

    def _generate_datasets(
        self, *, data: list[PlotDataPoint]
    ) -> list[PlotDatasetPoint]:
        """Generate Chart.js datasets from stock data.

        Args:
            data: List of stock data dictionaries.

        Returns:
            List of Chart.js dataset dictionaries.
        """
        datasets: list[PlotDatasetPoint] = []
        for i, item in enumerate(data):
            # Calculate point size based on presence (radius between 5-20)
            point_radius = max(5, min(20, item.presence * 20))

            datasets.append(
                PlotDatasetPoint(
                    label=item.symbol,
                    data=[{"x": item.sentiment, "y": item.presence}],
                    backgroundColor=self.colors[i % len(self.colors)],
                    borderColor=self.colors[i % len(self.colors)],
                    pointRadius=point_radius,
                    pointHoverRadius=point_radius + 3,
                )
            )
        return datasets

    def _generate_stock_boxes_html(self, *, stock_data: list[PlotDataPoint]) -> str:
        """Generate HTML for stock information boxes.

        Args:
            stock_data: List of stock data dictionaries.

        Returns:
            HTML string for stock boxes.
        """
        boxes_html = ""
        for item in stock_data:
            # Format sentiment with color
            sentiment_color = (
                "#28a745"
                if item.sentiment > 0
                else "#dc3545"
                if item.sentiment < 0
                else "#6c757d"
            )

            # Generate links HTML
            links_html = ""
            if item.links:
                links_html = "<ul>"
                for link in item.links:
                    url = link.url
                    title = link.title
                    links_html += (
                        f'<li><a href="{url}" target="_blank">{title}</a></li>'
                    )

                links_html += "</ul>"
            else:
                links_html = "<p>No links available</p>"

            boxes_html += f"""
            <div class="stock-box">
                <div class="stock-header">{item.symbol}</div>
                <div class="stock-metrics">
                    <div class="metric">
                        <div class="metric-label">Sentiment</div>
                        <div class="metric-value" style="color: {sentiment_color}">{item.sentiment:.2f}</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">Presence</div>
                        <div class="metric-value">{item.presence:.2f}</div>
                    </div>
                </div>
                <div class="summary">
                    <h4>Analysis Summary</h4>
                    <p>{item.summary}</p>
                </div>
                <div class="links">
                    <h4>Related Posts</h4>
                    {links_html}
                </div>
            </div>
            """
        return boxes_html

    def _get_html_template(
        self, *, datasets: list[PlotDatasetPoint], stock_boxes_html: str
    ) -> str:
        """Generate the complete HTML template for the visualization.

        Args:
            datasets: Chart.js datasets.
            stock_boxes_html: HTML for stock information boxes.

        Returns:
            Complete HTML string.
        """
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>r/Stocks Sentiment Analysis</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            text-align: center;
            color: #333;
            margin-bottom: 30px;
        }}
        .chart-container {{
            position: relative;
            height: 600px;
            margin: 20px 0;
        }}
        .info {{
            background-color: #e3f2fd;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }}
        .info h3 {{
            margin-top: 0;
            color: #1976d2;
        }}
        .data-section {{
            margin-top: 40px;
        }}
        .stock-box {{
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        .stock-header {{
            font-size: 1.4em;
            font-weight: bold;
            color: #333;
            margin-bottom: 15px;
            border-bottom: 2px solid #007bff;
            padding-bottom: 8px;
        }}
        .stock-metrics {{
            display: flex;
            gap: 30px;
            margin-bottom: 15px;
        }}
        .metric {{
            background-color: white;
            padding: 10px 15px;
            border-radius: 5px;
            border: 1px solid #e0e0e0;
        }}
        .metric-label {{
            font-weight: bold;
            color: #666;
            font-size: 0.9em;
        }}
        .metric-value {{
            font-size: 1.2em;
            color: #333;
            margin-top: 5px;
        }}
        .summary {{
            background-color: white;
            padding: 15px;
            border-radius: 5px;
            border: 1px solid #e0e0e0;
            margin-bottom: 15px;
        }}
        .summary h4 {{
            margin-top: 0;
            color: #333;
        }}
        .links {{
            background-color: white;
            padding: 15px;
            border-radius: 5px;
            border: 1px solid #e0e0e0;
        }}
        .links h4 {{
            margin-top: 0;
            color: #333;
        }}
        .links ul {{
            margin: 10px 0;
            padding-left: 20px;
        }}
        .links li {{
            margin-bottom: 8px;
        }}
        .links a {{
            color: #007bff;
            text-decoration: none;
        }}
        .links a:hover {{
            text-decoration: underline;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>r/Stocks Sentiment Analysis</h1>
        
        <div class="info">
            <h3>Chart Information</h3>
            <p><strong>X-axis (Sentiment):</strong> -1.0 (Very Negative) to 1.0 (Very Positive)</p>
            <p><strong>Y-axis (Presence):</strong> 0.0 (Low Presence) to 1.0 (High Presence)</p>
            <p><strong>Point Size:</strong> Represents the presence level of each stock</p>
        </div>
        
        <div class="chart-container">
            <canvas id="sentimentChart"></canvas>
        </div>
        
        <div class="data-section">
            <h2>Stock Analysis Details</h2>
            {stock_boxes_html}
        </div>
    </div>

    <script>
        const ctx = document.getElementById('sentimentChart').getContext('2d');
        const chart = new Chart(ctx, {{
            type: 'scatter',
            data: {{
                datasets: {json.dumps([dataset.model_dump() for dataset in datasets])}
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    title: {{
                        display: true,
                        text: 'Stock Sentiment vs Presence Analysis',
                        font: {{
                            size: 16
                        }}
                    }},
                    legend: {{
                        display: true,
                        position: 'right'
                    }},
                    tooltip: {{
                        callbacks: {{
                            label: function(context) {{
                                const label = context.dataset.label || '';
                                const x = context.parsed.x.toFixed(2);
                                const y = context.parsed.y.toFixed(2);
                                return `${{label}}: Sentiment ${{x}}, Presence ${{y}}`;
                            }}
                        }}
                    }}
                }},
                scales: {{
                    x: {{
                        type: 'linear',
                        position: 'bottom',
                        title: {{
                            display: true,
                            text: 'Sentiment (-1.0 to 1.0)'
                        }},
                        min: -1.1,
                        max: 1.1,
                        grid: {{
                            color: function(context) {{
                                if (context.tick.value === 0) {{
                                    return '#666';
                                }}
                                return '#e0e0e0';
                            }},
                            lineWidth: function(context) {{
                                if (context.tick.value === 0) {{
                                    return 2;
                                }}
                                return 1;
                            }}
                        }}
                    }},
                    y: {{
                        title: {{
                            display: true,
                            text: 'Presence (0.0 to 1.0)'
                        }},
                        min: 0,
                        max: 1.1,
                        grid: {{
                            color: '#e0e0e0'
                        }}
                    }}
                }},
                interaction: {{
                    intersect: false,
                    mode: 'point'
                }}
            }}
        }});
    </script>
</body>
</html>"""

    def create_plot(self, *, data: list[PlotDataPoint]) -> None:
        """Create an interactive sentiment plot and open it in the browser.

        Args:
            data: List of stock data dictionaries containing Symbol, Sentiment, Presence, etc.
        """
        try:
            # Generate Chart.js datasets
            datasets: list[PlotDatasetPoint] = self._generate_datasets(data=data)

            # Generate stock information boxes
            stock_boxes_html = self._generate_stock_boxes_html(stock_data=data)

            # Generate complete HTML
            html = self._get_html_template(
                datasets=datasets, stock_boxes_html=stock_boxes_html
            )

            # Write to temporary file
            with tempfile.NamedTemporaryFile(
                delete=False, suffix=".html", dir="/tmp"
            ) as tmp:
                tmp.write(html.encode("utf-8"))
                html_path = tmp.name

            # Open in browser
            url = f"file://{os.path.abspath(html_path)}"
            webbrowser.open_new(url)

            logger.info(f"Created visualization at {html_path}")

        except Exception as e:
            logger.error(f"Error creating plot: {str(e)}")
            raise


# Global service instance
visualization_service = VisualizationService()
