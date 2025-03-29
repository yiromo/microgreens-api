import asyncio
import base64
import uuid
from datetime import datetime
from typing import Any, Optional
from .schemas import MAXTOKENS, AIModelType, LLMTemperature
import openai
from core.config import settings

class LLMRequest:
    def __init__(
        self,
        model: str = AIModelType.GPT4OMINI,
        temperature: float = LLMTemperature.LOWEST,
        max_tokens: int = MAXTOKENS.MAX,
        client = None
    ):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.messages = []
        self.client = client or openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        self.request_id = str(uuid.uuid4())
        self.created_at = datetime.now()
        
    def add_system_message(self, content: str):
        """Add a system message to the conversation."""
        self.messages.append({"role": "system", "content": content})
        return self
        
    def add_user_message(self, content: str):
        """Add a user message to the conversation."""
        self.messages.append({"role": "user", "content": content})
        return self
    
    def add_assistant_message(self, content: str):
        """Add an assistant message to the conversation."""
        self.messages.append({"role": "assistant", "content": content})
        return self
    
    def clear_history(self):
        """Clear conversation history."""
        self.messages = []
        return self
        
    async def send(
        self,
        new_user_message: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        model: Optional[str] = None,
        timeout: int = 60
    ) -> str:
        if new_user_message:
            self.add_user_message(new_user_message)
            
        try:
            start_time = datetime.now()
            
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=model or self.model,
                messages=self.messages,
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens,
                timeout=timeout
            )
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            content = response.choices[0].message.content
            self.add_assistant_message(content)
            
            print(f"Request {self.request_id} completed in {duration:.2f}s")
            
            return content
            
        except Exception as e:
            print(f"Error in LLMRequest.send: {e}")
            raise
            
    async def send_with_image(
        self,
        image_data: bytes,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        model: Optional[str] = None,
        timeout: int = 120
    ) -> str:
        try:
            start_time = datetime.now()
            
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ]
            
            if self.messages and self.messages[0]["role"] == "system":
                messages.insert(0, self.messages[0])
            
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=model or AIModelType.GPT4OMINI, 
                messages=messages,
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens,
                timeout=timeout
            )
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            content = response.choices[0].message.content
            
            print(f"Image request {self.request_id} completed in {duration:.2f}s")
            
            return content
            
        except Exception as e:
            print(f"Error in LLMRequest.send_with_image: {e}")
            raise