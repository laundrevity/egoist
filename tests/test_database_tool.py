from tools.database_tool import DatabaseTool, DatabaseToolInput, DbOperation, DbType
from toolkit import ToolKit
import pytest
import json
import os

DATABASE_URL = "postgresql://assistant_user:abc123@postgres/assistant_db"


@pytest.mark.asyncio
@pytest.mark.skipif(os.getenv('SKIP_DB_TESTS', 'false').lower() == 'true',
                    reason="Skipping DatabaseTool tests in CI/CD environment")
async def test_create_table():
    print("test create table")
    toolkit = ToolKit()
    db_tool = DatabaseTool(toolkit)
    input_data = DatabaseToolInput(
        dsn=DATABASE_URL,
        operations=[
            DbOperation(
                type=DbType.CREATE_TABLE,
                query="CREATE TABLE IF NOT EXISTS test_table (id serial PRIMARY KEY, data text)",
            )
        ],
    )
    result = await db_tool.execute(input_data)
    assert "CREATE TABLE" in result


@pytest.mark.asyncio
@pytest.mark.skipif(os.getenv('SKIP_DB_TESTS', 'false').lower() == 'true',
                    reason="Skipping DatabaseTool tests in CI/CD environment")
async def test_insert_record():
    toolkit = ToolKit()
    db_tool = DatabaseTool(toolkit)
    input_data = DatabaseToolInput(
        dsn=DATABASE_URL,
        operations=[
            DbOperation(
                type=DbType.INSERT,
                query="INSERT INTO test_table (data) VALUES ($1)",
                parameters=["test_data"],
            )
        ],
    )
    result = await db_tool.execute(input_data)
    assert "INSERT 0 1" in result


@pytest.mark.asyncio
@pytest.mark.skipif(os.getenv('SKIP_DB_TESTS', 'false').lower() == 'true',
                    reason="Skipping DatabaseTool tests in CI/CD environment")
async def test_query_record():
    toolkit = ToolKit()
    db_tool = DatabaseTool(toolkit)
    input_data = DatabaseToolInput(
        dsn=DATABASE_URL,
        operations=[
            DbOperation(
                type=DbType.QUERY,
                query="SELECT * FROM test_table WHERE data = $1",
                parameters=["test_data"],
            )
        ],
    )
    result = await db_tool.execute(input_data)
    result_json = json.loads(result)[0][0]
    assert "test_data" == result_json["data"]


@pytest.mark.asyncio
@pytest.mark.skipif(os.getenv('SKIP_DB_TESTS', 'false').lower() == 'true',
                    reason="Skipping DatabaseTool tests in CI/CD environment")
async def test_update_record():
    toolkit = ToolKit()
    db_tool = DatabaseTool(toolkit)
    input_data = DatabaseToolInput(
        dsn=DATABASE_URL,
        operations=[
            DbOperation(
                type=DbType.UPDATE,
                query="UPDATE test_table SET data = $1 WHERE data = $2",
                parameters=["updated_data", "test_data"],
            )
        ],
    )
    result = await db_tool.execute(input_data)
    assert "UPDATE 1" in result


@pytest.mark.asyncio
@pytest.mark.skipif(os.getenv('SKIP_DB_TESTS', 'false').lower() == 'true',
                    reason="Skipping DatabaseTool tests in CI/CD environment")
async def test_drop_table():
    toolkit = ToolKit()
    db_tool = DatabaseTool(toolkit)
    input_data = DatabaseToolInput(
        dsn=DATABASE_URL,
        operations=[
            DbOperation(type=DbType.DROP_TABLE, query="DROP TABLE IF EXISTS test_table")
        ],
    )
    result = await db_tool.execute(input_data)
    assert "DROP TABLE" in result
