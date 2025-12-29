# -*- coding: utf-8 -*-
"""
Model API Client Module
Supports custom API endpoints and streaming output
"""

import requests
import json
import os
from typing import Dict, List, Optional, Generator, Any
from dotenv import load_dotenv


class APIClient:
    """Model API Client"""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize API client

        Args:
            config_path: Configuration file path, if None uses environment variables
        """
        if config_path and os.path.exists(config_path):
            load_dotenv(config_path)
        else:
            load_dotenv()

        self.base_url = os.getenv('API_BASE_URL', 'https://api.example.com/v1')
        self.api_key = os.getenv('API_KEY', '')
        self.model = os.getenv('MODEL_NAME', 'gpt-4')
        self.timeout = int(os.getenv('TIMEOUT', '1200'))
        self.max_tokens = int(os.getenv('MAX_TOKENS', '81920'))
        self.temperature = float(os.getenv('TEMPERATURE', '0.7'))

        if not self.api_key:
            raise ValueError("API_KEY not set, please configure in .env file")

    def _prepare_headers(self) -> Dict[str, str]:
        """Prepare request headers"""
        return {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}',
            'User-Agent': 'AI-Tool-Client/1.0'
        }

    def _prepare_payload(self, messages: List[Dict[str, str]], stream: bool = False) -> Dict[str, Any]:
        """Prepare request payload"""
        # Anthropic format - filter out system messages (if present)
        filtered_messages = []
        system_message = None

        for msg in messages:
            if msg['role'] == 'system':
                system_message = msg['content']
            else:
                filtered_messages.append(msg)

        # Use default if no messages
        if not filtered_messages:
            filtered_messages = messages

        payload = {
            'model': self.model,
            'messages': filtered_messages,
            'max_tokens': self.max_tokens,
            'stream': stream
        }

        # Add system message if present
        if system_message:
            payload['system'] = system_message

        # Add temperature if not streaming
        if not stream:
            payload['temperature'] = self.temperature
        return payload

    def send_message(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Send non-streaming message request

        Args:
            messages: Message list, format [{"role": "user", "content": "..."}]

        Returns:
            Response data (converted to OpenAI format)
        """
        url = f"{self.base_url}/v1/messages"
        headers = self._prepare_headers()
        payload = self._prepare_payload(messages, stream=False)

        try:
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            result = response.json()

            # Convert to OpenAI format
            if 'content' in result:
                return {
                    'id': result.get('id', 'chatcmpl-123'),
                    'object': 'chat.completion',
                    'created': result.get('created_at', 1234567890),
                    'model': result.get('model', self.model),
                    'choices': [{
                        'index': 0,
                        'message': {
                            'role': 'assistant',
                            'content': result['content'][0]['text']
                        },
                        'finish_reason': result.get('stop_reason', 'stop')
                    }],
                    'usage': result.get('usage', {})
                }
            return result
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {e}")

    def send_message_stream(self, messages: List[Dict[str, str]]) -> Generator[str, None, None]:
        """
        Send streaming message request

        Args:
            messages: Message list

        Yields:
            Streaming response content
        """
        url = f"{self.base_url}/v1/messages"
        headers = self._prepare_headers()
        payload = self._prepare_payload(messages, stream=True)

        try:
            with requests.post(
                url,
                headers=headers,
                json=payload,
                stream=True,
                timeout=self.timeout
            ) as response:
                response.raise_for_status()

                for line in response.iter_lines():
                    if line:
                        line_str = line.decode('utf-8')
                        if line_str.startswith('data: '):
                            data = line_str[6:]  # Remove 'data: ' prefix
                            if data == '[DONE]':
                                break
                            try:
                                # Anthropic streaming response format
                                chunk = json.loads(data)
                                if 'delta' in chunk:
                                    delta = chunk['delta']
                                    if 'text' in delta:
                                        yield delta['text']
                                elif 'content' in chunk:
                                    # Non-streaming response format
                                    yield chunk['content'][0]['text']
                            except json.JSONDecodeError:
                                continue
        except requests.exceptions.RequestException as e:
            raise Exception(f"Streaming API request failed: {e}")

    def test_connection(self) -> bool:
        """
        Test API connection

        Returns:
            Whether connection is successful
        """
        test_messages = [{"role": "user", "content": "Hello"}]
        try:
            result = self.send_message(test_messages)
            return 'choices' in result or 'error' not in result
        except Exception:
            return False


class MockAPIClient:
    """Mock API client for testing"""

    def send_message(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """Mock non-streaming response"""
        last_message = messages[-1]['content']

        return {
            'id': 'mock-chatcmpl-123',
            'object': 'chat.completion',
            'created': 1234567890,
            'model': 'mock-model',
            'choices': [{
                'index': 0,
                'message': {
                    'role': 'assistant',
                    'content': f"This is a mock response to your message:\n\n{last_message}\n\n(This is a simulated response for testing)"
                },
                'finish_reason': 'stop'
            }],
            'usage': {
                'prompt_tokens': 10,
                'completion_tokens': 50,
                'total_tokens': 60
            }
        }

    def send_message_stream(self, messages: List[Dict[str, str]]) -> Generator[str, None, None]:
        """Mock streaming response"""
        last_message = messages[-1]['content']
        response_text = f"This is a streaming mock response:\n\n{last_message}\n\nStreaming character by character..."

        for char in response_text:
            yield char
            import time
            time.sleep(0.02)  # Simulate delay

    def test_connection(self) -> bool:
        """Mock connection test"""
        return True
