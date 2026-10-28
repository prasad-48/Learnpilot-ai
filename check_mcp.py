import asyncio
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
            print("PASS: MCP initialization")

            result = await session.list_tools()
            names = [tool.name for tool in result.tools]
            print("Registered tools:", names)

            if "invoke_tutor" in names:
                print("PASS: invoke_tutor tool is registered")
            else:
                print("FAIL: invoke_tutor tool is missing")
                sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
