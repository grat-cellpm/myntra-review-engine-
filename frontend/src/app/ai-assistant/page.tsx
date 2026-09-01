"use client";
import React, { useState } from 'react';
import { Plus, Send, MoreHorizontal, Menu, Bot } from 'lucide-react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';

export default function AIAssistant() {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);


  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await axios.post('http://localhost:5000/api/agent/query', {
        question: userMessage.content
      });
      
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: response.data.answer || "No response generated." 
      }]);
    } catch (error: any) {
      console.error("Agent error:", error);
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: `Error: ${error.message || "Failed to reach backend."}` 
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-[calc(100vh-6rem)] -m-8">
      {/* Inner Sidebar */}
      <div className="w-64 border-r border-slate-800 bg-[#171923] p-4 flex flex-col gap-4">
        <button className="glass-button w-full justify-between mt-2" onClick={() => setMessages([])}>
          New Chat
          <Plus className="w-4 h-4" />
        </button>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col bg-[#1a1d27] relative">
        {/* Chat Header */}
        <div className="h-14 border-b border-slate-800 flex items-center justify-between px-6">
          <h2 className="font-semibold text-white">AI Insights Assistant</h2>
          <button className="text-slate-400 hover:text-white transition-colors">
            <MoreHorizontal className="w-5 h-5" />
          </button>
        </div>

        {/* Chat Messages */}
        <div className="flex-1 overflow-y-auto p-6 flex flex-col gap-8">
          
          {messages.length === 0 && !loading && (
            <div className="flex flex-col items-center justify-center h-full opacity-50 text-slate-400 gap-4">
               <Bot className="w-12 h-12" />
               <p>Ask the agent about user intents, barriers, and opportunities.</p>
            </div>
          )}

          {messages.map((msg, i) => (
            <div key={i} className={`flex max-w-4xl w-full ${msg.role === 'user' ? 'justify-end ml-auto' : 'gap-4'}`}>
              
              {msg.role === 'assistant' && (
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-[#F34C74] to-[#F88B46] flex items-center justify-center shrink-0 mt-1">
                  <Bot className="w-5 h-5 text-white" />
                </div>
              )}

              {msg.role === 'user' ? (
                <div className="bg-white/10 text-white px-5 py-3 rounded-2xl rounded-tr-sm text-sm">
                  {msg.content}
                </div>
              ) : (
                <div className="glass-panel p-5 rounded-2xl rounded-tl-sm w-full bg-[#222635] text-slate-300 text-sm whitespace-pre-wrap leading-relaxed prose prose-invert prose-p:leading-relaxed prose-pre:bg-[#1a1d27] prose-pre:border prose-pre:border-slate-800 max-w-none">
                  <ReactMarkdown>{msg.content}</ReactMarkdown>
                </div>
              )}
            </div>
          ))}

          {/* AI Loading State */}
          {loading && (
            <div className="flex gap-4 max-w-4xl">
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-[#F34C74] to-[#F88B46] flex items-center justify-center shrink-0 mt-1">
                <Bot className="w-5 h-5 text-white" />
              </div>
              
              <div className="w-full max-w-2xl">
                <div className="glass-panel p-4 rounded-xl border border-[#F88B46]/30 bg-[#222635] shadow-[0_0_15px_rgba(248,139,70,0.05)] mb-3">
                  <div className="flex items-center gap-2 mb-2 text-sm">
                    <span className="font-semibold text-white">Agent is thinking and using tools...</span>
                  </div>
                  <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
                    <div className="h-full bg-gradient-to-r from-[#F34C74] to-[#F88B46] w-[45%] rounded-full animate-pulse"></div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Input Box */}
        <div className="p-6 border-t border-slate-800">
          <div className="relative max-w-4xl mx-auto flex items-center">
            <button className="absolute left-4 text-slate-400 hover:text-white transition-colors">
              <Menu className="w-5 h-5" />
            </button>
            <input 
              type="text" 
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              placeholder="Ask about product insights, reviews, or trends..." 
              className="w-full bg-[#222635] border border-[#F88B46]/40 shadow-[0_0_20px_rgba(248,139,70,0.1)] rounded-full py-4 pl-12 pr-14 text-white focus:outline-none focus:border-[#F88B46] transition-all"
            />
            <button 
              onClick={handleSend}
              disabled={loading}
              className="absolute right-2 w-10 h-10 rounded-full flex items-center justify-center bg-gradient-to-r from-[#F34C74] to-[#F88B46] text-white shadow-lg hover:opacity-90 transition-opacity disabled:opacity-50"
            >
              <Send className="w-4 h-4 ml-0.5" />
            </button>
          </div>
        </div>

      </div>
    </div>
  );
}
