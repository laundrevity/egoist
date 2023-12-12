from toolkit import ToolKit
from tools.http_tool import HttpTool, HttpToolInput, HttpRequest, HttpRequestType

import pytest
import json

@pytest.mark.asyncio
async def test_http_tool_get_request():
    toolkit = ToolKit()
    tool = HttpTool(toolkit)
    
    request = HttpRequest(request_type=HttpRequestType.GET, url='https://www.example.com')
    input_data = HttpToolInput(requests=[request])
    result = await tool.execute(input_data)
    
    assert isinstance(result, str)
    assert 'Example Domain' in result

@pytest.mark.asyncio
async def test_http_tool_post_request():
    toolkit = ToolKit()
    tool = HttpTool(toolkit)

    request = HttpRequest(request_type=HttpRequestType.POST, url='https://httpbin.org/post', payload={"key": "value"}, headers={"Content-Type": "application/json"})
    input_data = HttpToolInput(requests=[request])
    result = await tool.execute(input_data)
    
    result_json = json.loads(json.loads(result)[0])

    assert isinstance(result, str)
    assert result_json['json']['key'] == 'value'
