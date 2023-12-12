from bs4 import BeautifulSoup
from tools.base_tool import BaseTool
from pydantic import BaseModel, Field
from typing import Dict
import traceback
import asyncio
import httpx
import json
import re


class WebScrapingTask(BaseModel):
    url: str = Field(description="URL of the page to scrape")
    data_points: Dict[str, str] = Field(
        description="Mapping from str to str of data point names to their CSS selectors. THIS FIELD IS NECESSARY."
    )


class WebScrapingToolInput(BaseModel):
    tasks: list[WebScrapingTask] = Field(
        description="List of web scraping tasks to perform. Every task must include a URL and MUST INCLUDE data_points"
    )


class WebScrapingTool(BaseTool):
    input_model = WebScrapingToolInput
    description = "Scrape structured information from web pages based on provided CSS selectors. A data_points mapping MUST be provided."

    async def execute(self, input_data: WebScrapingToolInput) -> str:
        scraping_results = []

        async with httpx.AsyncClient() as client:
            for task in input_data.tasks:
                try:
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
                except Exception as e:
                    scraping_results.append(
                        f"Got error on {task}: {e} {traceback.format_exc()}"
                    )

        return json.dumps(scraping_results)
