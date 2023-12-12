from tools.base_tool import BaseTool

from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from enum import Enum
import asyncio
import httpx
import json



class HttpRequestType(Enum):
    GET = 'GET'
    POST = 'POST'

class HttpRequest(BaseModel):
    request_type: HttpRequestType = Field(description="HTTP request type")
    url: str = Field(description="URL for HTTP request")
    payload: Optional[Dict | List] = Field(description="Optional JSON payload for a POST request", default=None)
    headers: Optional[Dict[str, str]] = Field(description="Optional headers for request", default=None)
    

class HttpToolInput(BaseModel):
    requests: List[HttpRequest]

class HttpTool(BaseTool):
    input_model = HttpToolInput
    description = "Get the HTTP response from a given GET or POST request"

    async def execute(self, input_data: HttpToolInput) -> str:
        async with httpx.AsyncClient() as client:
            tasks = []
            for request in input_data.requests:
                    match request.request_type:
                        case HttpRequestType.GET:
                            tasks.append(
                                client.get(
                                    request.url,
                                    headers=request.headers
                                )
                            )
                        case HttpRequestType.POST:
                            tasks.append(
                                client.post(
                                    request.url,
                                    headers=request.headers,
                                    json=request.payload
                                )
                            )

            responses = await asyncio.gather(*tasks)
            response_contents = [response.content.decode() for response in responses]

        return json.dumps(response_contents)
