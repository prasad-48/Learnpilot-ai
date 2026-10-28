
import asyncio
import json
import os
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"

    server = StdioServerParameters(
        command=sys.executable,
        args=["-X", "utf8", "mcp_server.py"],
        env=env,
    )

    async with stdio_client(server) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            print("MCP initialized.")

            result = await session.call_tool(
                "invoke_tutor",
                arguments={
                    "task": "Explain photosynthesis in simple language and give 2 examples.",
                    "student_id": "mcp_test_student_001",
                    "student_name": "Alex",
                    "grade_level": "Grade 8",
                    "age": 13,
                    "learning_style": "reading",
                    "language": "English",
                },
            )

            print("\nTool response:")
            for item in result.content:
                if hasattr(item, "text"):
                    try:
                        print(json.dumps(json.loads(item.text), indent=2))
                    except json.JSONDecodeError:
                        print(item.text)

            print("\nTool reported error:", result.isError)


if __name__ == "__main__":
    asyncio.run(main())
