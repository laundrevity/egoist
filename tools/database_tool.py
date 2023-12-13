from tools.base_tool import BaseTool
from pydantic import BaseModel, Field
from enum import Enum
from typing import List, Optional
import asyncpg
import json


class DbType(str, Enum):
    CREATE_DB = "create_db"
    CREATE_TABLE = "create_table"
    DROP_TABLE = "drop_table"
    INSERT = "insert"
    QUERY = "query"
    UPDATE = "update"


class DbOperation(BaseModel):
    type: DbType = Field(description="Type of database operation")
    query: str = Field(description="SQL query to execute")
    parameters: Optional[List] = Field(
        default=None, description="Parameters for the SQL query, if needed"
    )


class DatabaseToolInput(BaseModel):
    dsn: str = Field(description="Data Source Name for database connection")
    operations: List[DbOperation] = Field(
        description="List of database operations to perform"
    )


class DatabaseTool(BaseTool):
    input_model = DatabaseToolInput
    description = "Perform various database operations."

    async def execute(self, input_data: DatabaseToolInput) -> str:
        results = []
        conn = None
        try:
            conn = await asyncpg.connect(input_data.dsn)
            for operation in input_data.operations:
                params = operation.parameters or []
                if operation.type == DbType.QUERY:
                    fetched = await conn.fetch(operation.query, *params)
                    # Serialize asyncpg.Record objects
                    results.append([dict(record) for record in fetched])
                else:
                    result = await conn.execute(operation.query, *params)
                    results.append(result)
            return json.dumps(results)
        except Exception as e:
            return f"Database operation failed: {e}"
        finally:
            if conn:
                await conn.close()
