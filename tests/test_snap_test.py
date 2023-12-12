from tools.snap_tool import SnapTool, SnapToolInput
from toolkit import ToolKit

import pytest


@pytest.mark.asyncio
async def test_generate_code_snapshot():
    tooklit = ToolKit()
    tool = SnapTool(tooklit)

    await tool.execute(SnapToolInput(line_numbers=False, infra_files=False))
    assert "main.py" in open("state.txt").read()


@pytest.mark.asyncio
async def test_generate_full_snapshot():
    tooklit = ToolKit()
    tool = SnapTool(tooklit)

    await tool.execute(SnapToolInput(line_numbers=True, infra_files=True))
    assert "Dockerfile" in open("state.txt").read()
    assert ".github/workflows/pytest.yml" in open("state.txt").read()
