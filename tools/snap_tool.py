from pydantic import BaseModel, Field
from tools.base_tool import BaseTool
from typing import Optional
import os


class SnapToolInput(BaseModel):
    line_numbers: Optional[bool] = Field(
        default=False, description="Include line numbers in output"
    )
    infra_files: Optional[bool] = Field(
        default=False, description="Include infrastructure files in output"
    )


class SnapTool(BaseTool):
    input_model = SnapToolInput
    description = "Concatenate and optionally annotate source code files with line numbers (possibly including infrastructure files)."

    async def execute(self, input_data: SnapToolInput) -> str:
        concatenated_code = ""

        dirs_to_include = ["tools", "tests"]
        filetypes_to_include = [".py"]

        code_files = [path for path in os.listdir(os.getcwd()) if path.endswith(".py")]
        for source_dir in dirs_to_include:
            code_files += [
                os.path.join(source_dir, path)
                for path in os.listdir(os.path.join(os.getcwd(), source_dir))
                if any(path.endswith(ft) for ft in filetypes_to_include)
            ]
        if input_data.infra_files:
            code_files += [
                "Dockerfile",
                "docker-compose.yml",
                "requirements.txt",
                ".github/workflows/pytest.yml",
            ]

        for file in code_files:
            concatenated_code += f"--- {file} ---\n```\n"
            with open(file, "r") as f:
                if input_data.line_numbers:
                    line_num = 1
                    for line in f:
                        concatenated_code += f"{line_num:>6}  {line}"
                        line_num += 1
                else:
                    concatenated_code += f.read()

            concatenated_code += "\n"

        with open("state.txt", "w") as f:
            f.write(concatenated_code)

        return concatenated_code
