from MCPClient import MCPClient
from ChatOpenAI import ChatOpenAI
import asyncio
from util import logTitle
import json

class Agent:
    def __init__(self, mcp_clients: list[MCPClient], model: str, system_prompt: str = "", 
                 content:str = ""):
        self.mcp_clients = mcp_clients
        self.llm = None
        self.model = model
        self.system_prompt = system_prompt 
        self.content = content
        

    async def init(self):
        logTitle('TOOLS')
        for mcp in self.mcp_clients:
            await mcp.init()
        tools = []
        for mcp in self.mcp_clients:
            tools.extend(mcp.get_tools())
        self.llm = ChatOpenAI(model_name=self.model, system_prompt=self.system_prompt, content=self.content,tools=tools)

    async def close(self):
        logTitle("CLOSE")
        for mcp_client in self.mcp_clients:
            await mcp_client.close()

    async def invoke(self, prompt: str):
        if self.llm is None:
            raise Exception("LLM is not initialized")
        response = await self.llm.chat(prompt)
        while True:
            # 处理工具调用
            if len(response['toolCalls']) > 0:
                for toolCall in response['toolCalls']:
                    mcp = next(
                        (client for client in self.mcp_clients 
                                if any(t['name'] == toolCall['function']['name'] for t in client.get_tools())), 
                        None)
                    if mcp:
                        logTitle(f"TOOL USE: {toolCall['function']['name']}")
                        print("Calling tool..." + toolCall['function']['name'])
                        print(toolCall['function']['arguments'])
                        result = await mcp.call_tool(toolCall['function']['name'], json.loads(toolCall['function']['arguments']))

                        result_str = ""
                        if hasattr(result, 'content') and result.content:
                             # 只取第一个内容的文本
                            result_dict = {
                                "content": result.content[0].text if result.content else "",
                                "isError": getattr(result, 'isError', False)
                            }
                            result_str = json.dumps(result_dict)
                        else:
                            result_str = str(result)

                        print('result:'+result_str)
                        self.llm.appendToolResult(toolCall['id'], str(result_str))
                    else:
                        self.llm.appendToolResult(toolCall['id'], "MCP client not found")
                #工具调用后继续对话
                response = await self.llm.chat()
                continue
            # 没有工具调用，则返回对话内容
            await self.close()
            return response['content']


                
