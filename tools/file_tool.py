from tools.base_tool import BaseTool

from pydantic import BaseModel, Field
from typing import Optional, List
from pathlib import Path
from enum import Enum
import traceback
from rich import print
import os


class FileOperationType(Enum):
    CREATE = "CREATE"
    DELETE = "DELETE"
    INSERT_LINE = "INSERT_LINE"
    UPDATE_LINE = "UPDATE_LINE"
    DELETE_LINE = "DELETE_LINE"


class FileOperation(BaseModel):
    operation_type: FileOperationType = Field(description="Type of file operation")
    path: str = Field(description="Path of the file to operate on")
    content: Optional[str] = Field(
        description="New file content for create / insert_line / update_line",
        default=None,
    )
    line_number: Optional[int] = Field(
        description="Line number of file operation for line-specific operations",
        default=None,
    )


class FileToolInput(BaseModel):
    operations: List[FileOperation]


class FileTool(BaseTool):
    input_model = FileToolInput
    description = "Execute a sequence of file operations"

    async def execute(self, input_data: FileToolInput) -> str:
        try:
            for op in input_data.operations:
                match op.operation_type:
                    case FileOperationType.CREATE:
                        with open(op.path, "w") as file:
                            file.write(op.content or "")
                    case FileOperationType.DELETE:
                        Path(op.path).unlink(missing_ok=True)
                    case FileOperationType.INSERT_LINE:
                        content = Path(op.path).read_text().splitlines()
                        content.insert(op.line_number, op.content)
                        Path(op.path).write_text("\n".join(content))
                    case FileOperationType.UPDATE_LINE:
                        content = Path(op.path).read_text().splitlines()
                        content[op.line_number] = op.content
                        Path(op.path).write_text("\n".join(content))
                    case FileOperationType.DELETE_LINE:
                        content = Path(op.path).read_text().splitlines()
                        del content[op.line_number]
                        Path(op.path).write_text("\n".join(content))
            return "File operations executed successfully."
        except Exception as e:
            print(f"Error executing file operations: {e} {traceback.format_exc()}")


if __name__ == "__main__":
    print(FileToolInput.model_dump())
