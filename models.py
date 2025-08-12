"""Pydantic models."""

from typing import Annotated

from pydantic import BaseModel, Field, HttpUrl, StrictStr, StrictFloat


class Link(BaseModel):
    """Link to where a stock was mentioned."""

    url: Annotated[
        HttpUrl,
        Field(description="Direct link to the post where the stock was mentioned."),
    ]

    title: Annotated[
        StrictStr,
        Field(
            min_length=1,
            max_length=200,
            description="Human-readable title for the link.",
        ),
    ]


class PlotDataPoint(BaseModel):
    """Raw data to plot in the final plot."""

    symbol: Annotated[
        StrictStr,
        Field(
            pattern=r"^.+ \(([A-Z]{1,5})\)$",
            description="Stock name with ticker in parentheses, e.g. 'Apple Inc. (AAPL)'."
            "It is critical that the ticker is in uppercase and has at least 1 and at most 5 characters.",
            examples=["Apple Inc. (AAPL)", "Tesla Inc. (TSLA)"],
        ),
    ]

    sentiment: Annotated[
        StrictFloat,
        Field(
            ge=-1.0,
            le=1.0,
            description="Normalized sentiment in [-1.00, 1.00]. "
            "1.00 means very positive, 0.00 means neutral. "
            "-1.00 means very negative.",
        ),
    ]

    presence: Annotated[
        StrictFloat,
        Field(
            ge=0.0,
            le=1.0,
            description="Share-of-voice in [0.00, 1.00]. 1.00 ≈ appears in nearly all posts. ",
        ),
    ]

    summary: Annotated[
        StrictStr,
        Field(
            max_length=2000,
            description="A short summary of the stock analysis and reasoning for sentiment/presence values.",
        ),
    ]

    links: Annotated[
        list[Link],
        Field(
            default_factory=list,
            min_length=0,
            description="References to posts where the stock was mentioned (url + title).",
        ),
    ]


# --- Data to plot in the final plot ---


class PlotDatasetPointData(BaseModel):
    """Coordinates for a dataset point in the plot."""

    x: Annotated[StrictFloat, Field(description="X-axis value (sentiment).")]
    y: Annotated[StrictFloat, Field(description="Y-axis value (presence).")]


class PlotDatasetPoint(BaseModel):
    """Dataset point to plot in the final plot."""

    label: Annotated[
        StrictStr, Field(description="Label for the dataset point in the plot.")
    ]

    data: Annotated[
        list[PlotDatasetPointData],
        Field(
            min_length=1,
            description="List of PlotDatasetPointData containing coordinates for the dataset point.",
        ),
    ]

    backgroundColor: Annotated[
        StrictStr,
        Field(
            description="Background color for the dataset point in the plot.",
            pattern=r"^#[0-9a-fA-F]{6}$",
            examples=["#FF5733", "#33FF57"],
        ),
    ]

    borderColor: Annotated[
        StrictStr,
        Field(
            description="Border color for the dataset point in the plot.",
            pattern=r"^#[0-9a-fA-F]{6}$",
            examples=["#FF5733", "#33FF57"],
        ),
    ]

    pointRadius: Annotated[
        StrictFloat,
        Field(
            description="Radius of the point in the plot. 0.0 means no point.",
            examples=[5.0, 10.0],
        ),
    ]

    pointHoverRadius: Annotated[
        StrictFloat,
        Field(
            description="Radius of the point when hovered in the plot.",
            examples=[7.0, 15.0],
        ),
    ]
