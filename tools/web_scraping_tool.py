from bs4 import BeautifulSoup
from tools.base_tool import BaseTool
from pydantic import BaseModel, Field
import asyncio
import httpx
import json
import re


class WebScrapingTask(BaseModel):
    url: str = Field(description="URL of the page to scrape")
    data_points: dict = Field(
        description="Mapping of data point names to their CSS selectors"
    )


class WebScrapingToolInput(BaseModel):
    tasks: list[WebScrapingTask] = Field(
        description="List of web scraping tasks to perform"
    )


class WebScrapingTool(BaseTool):
    input_model = WebScrapingToolInput
    description = (
        "Scrape structured information from web pages based on provided CSS selectors"
    )

    async def execute(self, input_data: WebScrapingToolInput) -> str:
        scraping_results = []

        async with httpx.AsyncClient() as client:
            for task in input_data.tasks:
                response = await client.get(task.url)
                soup = BeautifulSoup(response.content, "html.parser")

                task_result = {"url": task.url, "data_points": {}}
                for data_point_name, selector in task.data_points.items():
                    elements = soup.select(selector)
                    # We might want to extract text, or other attributes, or HTML content
                    task_result["data_points"][data_point_name] = [
                        elem.get_text(strip=True) for elem in elements
                    ]

                scraping_results.append(task_result)

        return json.dumps(scraping_results)


if __name__ == "__main__":
    # Example usage:
    tool_input = WebScrapingToolInput(
        tasks=[
            WebScrapingTask(
                url="https://github.com/tensorflow/tensorflow",
                data_points={"Title": "strong.mr-2", "Description": "p.f4"},
            ),
            # Add more tasks as needed.
        ]
    )

    scraping_tool = WebScrapingTool(None)
    result = asyncio.run(scraping_tool.execute(tool_input))
    print(result)
