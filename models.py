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
            max_length=280,
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
