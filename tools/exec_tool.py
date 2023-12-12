from tools.base_tool import BaseTool
from pydantic import BaseModel, Field
import sys
import io


class ExecToolInput(BaseModel):
    code: str = Field(description="Pyhton code to execute. Includes access to ToolKit instance via `toolkit` variable.")

class ExecTool(BaseTool):
    input_model = ExecToolInput
    description = "Execute the given Python source code"

    def __init__(self, toolkit):
        super().__init__(toolkit)
        self.persistent_locals = {'toolkit': toolkit}
        # Initialize a separate namespace for imports
        self.import_namespace = {}
        # Preload it with any necessary modules, if required

    async def execute(self, input_data: ExecToolInput) -> str:
        captured_output = io.StringIO()
        original_stdout = sys.stdout
        try:
            sys.stdout = captured_output
            # Combine import_namespace with persistent_locals
            combined_namespace = {**self.import_namespace, **self.persistent_locals, 'self': self}
            exec(input_data.code, combined_namespace, combined_namespace)
            # Update persistent_locals with the new variables
            self.persistent_locals.update({k: v for k, v in combined_namespace.items() if k not in self.import_namespace})
        finally:
            sys.stdout = original_stdout
        
        return captured_output.getvalue()
