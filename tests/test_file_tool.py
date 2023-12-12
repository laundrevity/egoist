from tools.file_tool import FileTool, FileToolInput, FileOperation, FileOperationType
from toolkit import ToolKit

import pytest
import os
from pathlib import Path


@pytest.mark.asyncio
async def test_file_tool_create_delete_file(tmp_path):
    toolkit = ToolKit()
    tool = FileTool(toolkit)

    file_content = "Hello, World!"
    file_path = os.path.join(tmp_path, "testfile.txt")

    # Create the file
    create_operation = FileOperation(
        operation_type=FileOperationType.CREATE,
        path=str(file_path),
        content=file_content,
    )
    input_data = FileToolInput(operations=[create_operation])
    result = await tool.execute(input_data)

    assert Path(file_path).is_file()
    assert Path(file_path).read_text() == file_content

    # Delete the file
    delete_operation = FileOperation(
        operation_type=FileOperationType.DELETE, path=str(file_path)
    )
    input_data = FileToolInput(operations=[delete_operation])
    result = await tool.execute(input_data)

    assert not Path(file_path).exists()
