from tools.base_tool import BaseTool
from pydantic import BaseModel, Field
import traceback
import sys
import io
import re


class ExecToolInput(BaseModel):
    code: str = Field(
        description="Pyhton code to execute. Includes access to ToolKit instance via `toolkit` variable."
    )


class ExecTool(BaseTool):
    input_model = ExecToolInput
    description = "Execute the given Python source code. Note that variable and function definitions and modifications persist across calls to ExecTool."

    def __init__(self, toolkit):
        super().__init__(toolkit)
        self.persistent_locals = {"toolkit": toolkit}
        # Initialize a separate namespace for imports
        self.import_namespace = {}
        # Preload it with any necessary modules, if required

    async def execute(self, input_data: ExecToolInput) -> str:
        captured_output = io.StringIO()
        original_stdout = sys.stdout
        result = None
        try:
            sys.stdout = captured_output
            # Combine import_namespace with persistent_locals
            combined_namespace = {
                **self.import_namespace,
                **self.persistent_locals,
                "self": self,
            }
            modified_code = (
                input_data.code + "\n__result__ = locals().get('__result__', None)"
            )
            exec(modified_code, combined_namespace, combined_namespace)
            # Update persistent_locals with the new variables
            self.persistent_locals.update(
                {
                    k: v
                    for k, v in combined_namespace.items()
                    if k not in self.import_namespace
                }
            )
            # Identify if the last line is an expression
            input_lines = re.split(r"[;\n]+", input_data.code)
            last_line = input_lines[-1]

            if not last_line.endswith(
                ("=", ":", "pass", "continue", "break")
            ) and not last_line.startswith("print"):
                # Evaluate the last line as an expression within the same namespace
                result = str(eval(last_line, combined_namespace, combined_namespace))
                print(f"{result=}")
        except Exception as e:
            sys.stdout = original_stdout
            return f"Error executing code={input_data.code}:\n{e}\n{traceback.format_exc()}"
        finally:
            sys.stdout = original_stdout

        if result:
            return result
        else:
            output = captured_output.getvalue()
            return output if output else "Python code executed successfully."
