from tools.web_scraping_tool import (
    WebScrapingTool,
    WebScrapingToolInput,
    WebScrapingTask,
)
from toolkit import ToolKit

import pytest
import json


@pytest.mark.asyncio
async def test_web_scraping_tool_simple():
    tool_input = WebScrapingToolInput(
        tasks=[
            WebScrapingTask(
                url="https://github.com/tensorflow/tensorflow",
                data_points={"Title": "strong.mr-2", "Description": "p.f4"},
            )
        ]
    )

    tk = ToolKit()
    scraping_tool = WebScrapingTool(tk)
    result = await scraping_tool.execute(tool_input)
    result_json = json.loads(result)[0]
    data_points = result_json["data_points"]
    assert data_points["Title"] == ["tensorflow"]
    assert (
        data_points["Description"][0]
        == "An Open Source Machine Learning Framework for Everyone"
    )


@pytest.mark.asyncio
async def test_web_scraping_tool_multiple_tasks():
    tool_input = WebScrapingToolInput(
        tasks=[
            WebScrapingTask(
                url="https://github.com/openai/gym",
                data_points={
                    "Title": "h1 strong",
                    "Stars": "a[aria-label='star this repository']",
                    "Forks": "a[aria-label^='fork']",
                },
            ),
            WebScrapingTask(
                url="https://pypi.org/project/requests/",
                data_points={
                    "LatestVersion": ".package-header__name",
                    "Description": ".package-description__summary",
                },
            ),
        ]
    )

    tk = ToolKit()
    scraping_tool = WebScrapingTool(tk)
    result = await scraping_tool.execute(tool_input)

    # Convert result to python object to make assertions more readable
    result_data = json.loads(result)

    # Assertion for the first task
    assert result_data[0]["url"] == "https://github.com/openai/gym"
    assert "Title" in result_data[0]["data_points"]
    assert "Stars" in result_data[0]["data_points"]
    assert "Forks" in result_data[0]["data_points"]

    # Assertion for the second task
    assert result_data[1]["url"] == "https://pypi.org/project/requests/"
    assert "LatestVersion" in result_data[1]["data_points"]
    assert "Description" in result_data[1]["data_points"]

    # Optionally, check the absence of HTML tags and non-negligible content length
    for task_result in result_data:
        for key, values in task_result["data_points"].items():
            for value in values:
                assert (
                    "<" not in value and ">" not in value
                ), f"HTML tags detected in {key}: {value}"
                assert len(value.strip()) > 0, f"No content found for {key}"
