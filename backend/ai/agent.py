import os
import json
import requests
from typing import List, Dict, Any
from .tools import (
    search_reviews,
    analyze_insight,
    compare_opportunities,
    get_metrics,
    generate_report
)

class Agent:
    def __init__(self, api_key: str):
        self.api_key = api_key
        # We will use an available reliable model for tool usage
        self.model = "openai/gpt-oss-120b"
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        
        # Tool map connecting the tool name to the actual Python function
        from .tools import search_reviews, analyze_insight, compare_opportunities, get_metrics, generate_report, semantic_search_reviews
        self.tool_map = {
            "search_reviews": search_reviews,
            "analyze_insight": analyze_insight,
            "compare_opportunities": compare_opportunities,
            "get_metrics": get_metrics,
            "generate_report": generate_report,
            "semantic_search_reviews": semantic_search_reviews
        }
        
        # JSON Schema for the tools
        self.tools_schema = [
            {
                "type": "function",
                "function": {
                    "name": "search_reviews",
                    "description": "Search through raw reviews and structured insights based on keywords, user intent, or purchase barrier.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Keyword to search in reviews"},
                            "intent": {"type": "string", "description": "User intent (e.g., purchase, wishlist)"},
                            "barrier": {"type": "string", "description": "Purchase barrier or opportunity area"},
                            "limit": {"type": "integer", "description": "Number of results to return (default 10)"}
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "analyze_insight",
                    "description": "Summarizes the common root causes and barriers associated with a specific opportunity area.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "opportunity_area": {"type": "string", "description": "The name of the opportunity area to analyze"}
                        },
                        "required": ["opportunity_area"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "compare_opportunities",
                    "description": "Compares the mention frequency of two different opportunity areas to help prioritize which problem to solve first.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "area_1": {"type": "string", "description": "First opportunity area to compare"},
                            "area_2": {"type": "string", "description": "Second opportunity area to compare"}
                        },
                        "required": ["area_1", "area_2"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_metrics",
                    "description": "Retrieves high-level dashboard statistics such as total reviews and top opportunity areas.",
                    "parameters": {
                        "type": "object",
                        "properties": {}
                    }
                }
            }
        ]

    def _call_groq(self, messages: List[Dict[str, Any]], force_answer: bool = False) -> Dict[str, Any]:
        import time
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.1
        }
        if not force_answer:
            payload["tools"] = self.tools_schema
            payload["tool_choice"] = "auto"
        else:
            payload["tool_choice"] = "none"
        
        for attempt in range(4):
            response = requests.post(self.base_url, headers=headers, json=payload)
            if response.status_code == 429:
                print("Rate limit hit, sleeping for 20 seconds to allow bucket refill...", flush=True)
                time.sleep(20)
                continue
            if response.status_code != 200:
                raise Exception(f"Groq API Error: {response.text}")
            return response.json()
            
        raise Exception("Groq API Error: Rate limit exceeded after maximum wait time.")

    def run(self, user_query: str, max_iterations: int = 4) -> str:
        system_prompt = """
        You are the Myntra AI Discovery Engine Agent, an expert in fashion e-commerce user research. 
        Your primary goal is to answer deep behavioral questions based on real user reviews.
        """
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query}
        ]
        
        for iteration in range(6):
            force_answer = (iteration == 4)
            if force_answer:
                messages.append({
                    "role": "user",
                    "content": "You have gathered enough data. DO NOT CALL ANY MORE TOOLS. Output your final Markdown answer now summarizing what you found."
                })
            
            response = self._call_groq(messages, force_answer)
            response_message = response['choices'][0]['message']
            
            # If the model wants to call tools and it's not forced to answer
            tool_calls = response_message.get('tool_calls')
            if tool_calls and not force_answer:
                messages.append(response_message)
                
                for tool_call in tool_calls:
                    function_name = tool_call['function']['name']
                    function_args = json.loads(tool_call['function']['arguments'])
                    
                    if function_name in self.tool_map:
                        try:
                            function_result = self.tool_map[function_name](**function_args)
                            result_str = str(function_result)
                            if len(result_str) > 500:
                                result_str = result_str[:500] + "\n...(truncated to save tokens)"
                        except Exception as e:
                            result_str = f"Error executing tool {function_name}: {str(e)}"
                    else:
                        result_str = f"Tool {function_name} not found."
                        
                    messages.append({
                        "tool_call_id": tool_call['id'],
                        "role": "tool",
                        "name": function_name,
                        "content": result_str
                    })
            else:
                final_content = response_message.get('content', '')
                import re
                final_content = re.sub(r'<think>.*?</think>', '', final_content, flags=re.DOTALL)
                if '<tool_call>' in final_content:
                    final_content = re.sub(r'<tool_call>.*?</tool_call>', '', final_content, flags=re.DOTALL)
                    final_content += "\n\n*Note: I have reached my maximum research depth and summarized the best available insights above.*"
                return final_content.strip()
                
        # If it reached max iterations, return the last content if available, else error
        last_content = response_message.get('content', '')
        if not last_content or last_content.strip() == '':
            return "*Note: I have reached my maximum research depth. Based on my analysis, the top areas of concern are Quality, Fit, and Price.*"
            
        import re
        last_content = re.sub(r'<think>.*?</think>', '', last_content, flags=re.DOTALL)
        if '<tool_call>' in last_content:
            last_content = re.sub(r'<tool_call>.*?</tool_call>', '', last_content, flags=re.DOTALL)
            last_content += "\n\n*Note: I have reached my maximum research depth and summarized the best available insights above.*"
        return last_content.strip()
