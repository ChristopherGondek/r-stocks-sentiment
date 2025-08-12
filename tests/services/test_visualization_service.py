"""Test cases for the VisualizationService."""

import pytest

from models import PlotDataPoint
from services.visualization_service import VisualizationService


@pytest.mark.asyncio
async def test_create_plot_html(sample_plot_data: list[PlotDataPoint]) -> None:
    """Test creating plot HTML with sample data."""
    # Create VisualizationService instance
    service = await VisualizationService.create()

    html = await service.create_plot_html(data=sample_plot_data)

    # Verify that the HTML contains expected elements
    assert "<head>" in html
    assert "<body>" in html

    assert sample_plot_data[0].symbol in html
    assert sample_plot_data[0].links[0].title in html
    assert str(sample_plot_data[0].links[0].url) in html
    assert sample_plot_data[0].summary in html
