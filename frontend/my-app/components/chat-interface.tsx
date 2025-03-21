"use client"

import { useState, useRef, useEffect } from "react"
import { Send, Bot, User, Loader2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { cn } from "@/lib/utils"

type Message = {
  id: string
  content: string
  role: "user" | "assistant"
  timestamp: Date
}

export function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      content:
        "Hello! I'm your ROI assistant. I can help you understand your calculation results and answer questions about the variables and formulas used. What would you like to know?",
      role: "assistant",
      timestamp: new Date(),
    },
  ])
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  // Mock function to simulate AI response
  const getAIResponse = async (userMessage: string): Promise<string> => {
    // Simulate network delay
    await new Promise((resolve) => setTimeout(resolve, 1500))

    // Simple response logic based on keywords in the user message
    const lowerCaseMessage = userMessage.toLowerCase()

    if (lowerCaseMessage.includes("roi")) {
      return "ROI (Return on Investment) is calculated by comparing the cost of implementing a change versus the cost of not implementing it. A positive ROI indicates that the change is financially beneficial."
    } else if (lowerCaseMessage.includes("cost of change")) {
      return "The Cost of Change includes all expenses related to implementing your initiative, such as software costs, training expenses, and any impact on employee morale or productivity during the transition."
    } else if (lowerCaseMessage.includes("cost of no change")) {
      return "The Cost of No Change represents the ongoing expenses or opportunity costs if you don't implement the change. This often includes inefficiencies, lost opportunities, or continuing problems that the change would address."
    } else if (lowerCaseMessage.includes("variable")) {
      return "You can adjust any variable in the calculator by changing its value in the input fields. The ROI will automatically recalculate based on your changes."
    } else if (lowerCaseMessage.includes("formula") || lowerCaseMessage.includes("equation")) {
      return "You can view the exact formulas used in the calculation by clicking the 'View Calculation Formula' dropdown under each section. These formulas show exactly how each variable contributes to the final calculation."
    } else if (lowerCaseMessage.includes("hello") || lowerCaseMessage.includes("hi")) {
      return "Hello! How can I help you understand your ROI calculation today?"
    } else if (lowerCaseMessage.includes("improve roi")) {
      return "To improve your ROI, focus on reducing the Cost of Change by optimizing training costs and implementation duration. You can also look for ways to better quantify the Cost of No Change, as many organizations underestimate ongoing inefficiencies."
    } else if (lowerCaseMessage.includes("explain") && lowerCaseMessage.includes("result")) {
      return (
        "Your current calculation shows a " +
        (0 >= 0 ? "positive" : "negative") +
        " ROI of $" +
        (0).toFixed(2) +
        ". This means the change " +
        (0 >= 0 ? "is financially beneficial" : "may need reconsideration") +
        ". The Cost of Change is $" +
        (0).toFixed(2) +
        " while the Cost of No Change is $" +
        (0).toFixed(2) +
        "."
      )
    } else {
      return "I'm not sure I understand your question. Could you ask about specific aspects of the ROI calculation, such as the cost of change, cost of no change, or how to interpret the results?"
    }
  }

  const handleSendMessage = async () => {
    if (!input.trim()) return

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
      // Get AI response
      const response = await getAIResponse(input)

      // Add AI message
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: response,
        role: "assistant",
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, aiMessage])
    } catch (error) {
      console.error("Error getting AI response:", error)

      // Add error message
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: "Sorry, I encountered an error. Please try again.",
        role: "assistant",
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
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
                "rounded-lg px-3 py-2 max-w-[80%]",
                message.role === "assistant"
                  ? "bg-[#344966] text-white"
                  : "bg-[#BFC994] bg-opacity-50 text-[#0D1821] ml-auto",
              )}
            >
              {message.content}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex items-start gap-2 text-sm">
            <div className="flex-shrink-0 rounded-full p-1.5 bg-[#344966] text-white">
              <Bot className="h-4 w-4" />
            </div>
            <div className="rounded-lg px-3 py-2 bg-[#B4CDED] bg-opacity-20 text-[#0D1821]">
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

