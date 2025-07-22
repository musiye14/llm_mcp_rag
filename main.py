from MCPClient import MCPClient
from Agent import Agent
import asyncio
import os
import json

os.environ["HTTP_PROXY"] = "http://127.0.0.1:9853"
os.environ["HTTPS_PROXY"] = "http://127.0.0.1:9853" 

currentdir = os.path.dirname(os.path.abspath(__file__))
fetchMCP = MCPClient("fetch", "uvx", ["mcp-server-fetch"])
fileMCP = MCPClient("file", "npx", ["-y", "@modelcontextprotocol/server-filesystem", currentdir])

async def main():
    agent = Agent([fetchMCP, fileMCP], "gpt-4o-mini")
    await agent.init()
    result = await agent.invoke("帮我爬取https://juejin.cn/post/7507538833690705946的文章内容并保存到{currentdir}/latest.md中")
    print(result)

if __name__ == "__main__":
    asyncio.run(main())