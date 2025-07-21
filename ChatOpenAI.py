import openai
import os
from util import logTitle
from dotenv import load_dotenv

# 加载.env文件中的环境变量
load_dotenv(verbose=True)
class ChatOpenAI:
    def __init__(self, model_name, system_prompt: str = "", tools = [],content: str = "",):
        self.model_name = model_name
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.system_prompt = system_prompt
        self.tools = tools
        self.messages = []
        if content:
            self.messages.append({"role": "user", "content": content})
        if system_prompt:
            self.messages.append({"role": "system", "content": system_prompt})

    def chat(self, prompt: str):
        logTitle("CHAT")
        if prompt:
            self.messages.append({"role": "user", "content": prompt})

            stream = self.client.chat.completions.create(
                model=self.model_name,
                messages=self.messages,
                stream=True,
                tools=self.getToolsDefinition(),
            )

            content = ""
            toolCalls = []
            logTitle("RESPONSE")

            for chunk in stream:
                delta = chunk.choices[0].delta
                
                #处理content
                if delta.content:
                    contentChunk = delta.content or ""
                    content += contentChunk
                    print(contentChunk, end="", flush=True)
                #处理tool_calls
                if delta.tool_calls:
                    for toolCallsChunk in delta.tool_calls:
                        # 第一个toolCall
                        if toolCalls.lenth <= toolCallsChunk.index:
                            toolCalls.append({'id':"", function:{'name':"", 'arguments':""}})
                        
                        currentCall = toolCalls[toolCallsChunk.index]
                        if toolCallsChunk['id']: 
                            currentCall['id'] += toolCallsChunk['id']
                        if toolCallsChunk['function']:
                            currentCall['function'] += toolCallsChunk['function']
                        if toolCallsChunk['arguments']:
                            currentCall['arguments'] += toolCallsChunk['arguments']

            self.messages.append({
                "role": "assistant", 
                "content": content, 
                "tool_calls": [{"id": call['id'], "function": call['function'], "arguments": call['arguments']} for call in toolCalls] if toolCalls else None
            })

            return {"content": content, "toolCalls": toolCalls}

    def getToolsDefinition(self):
        return [
            {
                "type": "function",
                "function": {
                    "name": tool['name'],
                    "description": tool['description'],
                    "parameters": tool['inputSchema']
                }
            } for tool in self.tools
        ]
    
    def appendToolResult(self,tooCallId:str, toolOutput:str):
        self.messages.append({
            "role": "tool", 
            "content": toolOutput, 
            "tool_call_id": tooCallId
        })

if __name__ == "__main__":
    chat = ChatOpenAI(model_name="gpt-4.1-mini")
    result = chat.chat("你好")
    print(result['content'])
    print(result['toolCalls'])


