"use client"

import { useState, useRef, useEffect } from "react"
import { Send, Bot, User, Loader2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { cn } from "@/lib/utils"
import ReactMarkdown from 'react-markdown'
import type { Components } from 'react-markdown'

type Message = {
  id: string
  content: string
  role: "user" | "assistant"
  timestamp: Date
}

type FormData = {
  change_initiative_name: string;
  industry: string;
  services_provided: string;
  department: string[];
  start_date: string;
  end_date: string;
  min_budget: string;
  max_budget: string;
  targeted_business_goals: string;
  employee_retraining_percent: string;
  num_affected_employees: string;
  employee_morale: number;
  change_details: string;
}

const markdownComponents: Components = {
  p: ({ children }) => <p className="mb-2">{children}</p>,
  ul: ({ children }) => <ul className="list-disc pl-4 mb-2">{children}</ul>,
  ol: ({ children }) => <ol className="list-decimal pl-4 mb-2">{children}</ol>,
  li: ({ children }) => <li className="mb-1">{children}</li>,
  h1: ({ children }) => <h1 className="text-lg font-bold mb-2">{children}</h1>,
  h2: ({ children }) => <h2 className="text-base font-bold mb-2">{children}</h2>,
  h3: ({ children }) => <h3 className="text-sm font-bold mb-2">{children}</h3>,
  code: ({ children }) => (
    <code className="bg-black/20 px-1 py-0.5 rounded text-sm font-mono">
      {children}
    </code>
  ),
  pre: ({ children }) => (
    <pre className="bg-black/20 p-2 rounded mb-2 overflow-x-auto">
      {children}
    </pre>
  ),
}

export function ChatInterface({ formData }: { formData: FormData }) {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(true)
  const [initialMessageLoaded, setInitialMessageLoaded] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const abortControllerRef = useRef<AbortController | null>(null)

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  // Get initial message from LLM - only once when component mounts
  useEffect(() => {
    // Skip if we've already loaded the initial message
    if (initialMessageLoaded) return;
    
    const getInitialMessage = async () => {
      // Cancel any in-progress requests
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
      
      // Create a new AbortController for this request
      abortControllerRef.current = new AbortController();
      
      try {
        const response = await fetch('/api/chat', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ 
            messages: [],
            formData 
          }),
          signal: abortControllerRef.current.signal
        });

        if (!response.ok) {
          throw new Error('Failed to get response');
        }

        const data = await response.json();
        const initialMessage: Message = {
          id: "initial",
          content: data.content,
          role: "assistant",
          timestamp: new Date(),
        }
        setMessages([initialMessage])
        setInitialMessageLoaded(true);
      } catch (error) {
        // Only log and show error if it's not an abort error
        if (error instanceof Error && error.name !== 'AbortError') {
          console.error("Error getting initial AI response:", error)
          setMessages([{
            id: "initial",
            content: "Hello! I'm your ROI assistant. I can help you understand your calculation results and answer questions about the variables and formulas used. What would you like to know?",
            role: "assistant",
            timestamp: new Date(),
          }])
          setInitialMessageLoaded(true);
        }
      } finally {
        setIsLoading(false)
        abortControllerRef.current = null;
      }
    }

    getInitialMessage()
    
    // Cleanup function to abort any pending requests when component unmounts
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, [formData, initialMessageLoaded])

  const handleSendMessage = async () => {
    if (!input.trim() || isLoading) return;

    // Cancel any in-progress requests
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    
    // Create a new AbortController for this request
    abortControllerRef.current = new AbortController();

    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      content: input,
      role: "user",
      timestamp: new Date(),
    }
    setMessages((prev) => [...prev, userMessage])
    setInput("")
    setIsLoading(true)

    try {
      // Convert messages to the format expected by the API, including the current user message
      const apiMessages = [...messages, userMessage].map(msg => ({
        role: msg.role,
        content: msg.content
      }));

      // Get AI response from our API route
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          messages: apiMessages,
          formData 
        }),
        signal: abortControllerRef.current.signal
      });

      if (!response.ok) {
        throw new Error('Failed to get response');
      }

      const data = await response.json();
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: data.content,
        role: "assistant",
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, aiMessage])
    } catch (error) {
      // Only log and show error if it's not an abort error
      if (error instanceof Error && error.name !== 'AbortError') {
        console.error("Error getting AI response:", error)

        // Add error message
        const errorMessage: Message = {
          id: (Date.now() + 1).toString(),
          content: "Sorry, I encountered an error. Please try again.",
          role: "assistant",
          timestamp: new Date(),
        }
        setMessages((prev) => [...prev, errorMessage])
      }
    } finally {
      setIsLoading(false)
      abortControllerRef.current = null;
    }
  }

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={cn(
              "flex items-start gap-2 text-sm",
              message.role === "assistant" ? "flex-row" : "flex-row-reverse",
            )}
          >
            <div
              className={cn(
                "flex-shrink-0 rounded-full p-1.5",
                message.role === "assistant" ? "bg-[#344966] text-white" : "bg-[#BFC994] text-[#0D1821]",
              )}
            >
              {message.role === "assistant" ? <Bot className="h-4 w-4" /> : <User className="h-4 w-4" />}
            </div>
            <div
              className={cn(
                "rounded-lg px-3 py-2 max-w-[80%] prose prose-sm dark:prose-invert",
                message.role === "assistant"
                  ? "bg-[#344966] text-white"
                  : "bg-[#BFC994] bg-opacity-50 text-[#0D1821] ml-auto",
              )}
            >
              <ReactMarkdown components={markdownComponents}>
                {message.content}
              </ReactMarkdown>
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex items-start gap-2 text-sm">
            <div className="flex-shrink-0 rounded-full p-1.5 bg-[#344966] text-white">
              <Bot className="h-4 w-4" />
            </div>
            <div className="rounded-lg px-3 py-2 bg-[#344966] text-white">
              <Loader2 className="h-4 w-4 animate-spin" />
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      <div className="p-3 border-t border-[#B4CDED]">
        <form
          onSubmit={(e) => {
            e.preventDefault()
            handleSendMessage()
          }}
          className="flex items-center gap-2"
        >
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about your ROI calculation..."
            className="flex-1 border-[#B4CDED] focus:border-[#344966] focus:ring-[#344966]"
            disabled={isLoading}
          />
          <Button
            type="submit"
            size="sm"
            className="bg-[#344966] hover:bg-[#2a3b54] text-white"
            disabled={isLoading || !input.trim()}
          >
            {isLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
          </Button>
        </form>
      </div>
    </div>
  )
}