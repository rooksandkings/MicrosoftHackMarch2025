"use client"

import { useState, useEffect } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import Link from "next/link"
import { ArrowLeft, Calculator, DollarSign, Settings, MessageCircle } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { DashboardNav } from "@/components/dashboard-nav"
import { Separator } from "@/components/ui/separator"
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion"
import { ChatInterface } from "@/components/chat-interface"

interface ROIPayload {
  coceqn: string;
  cocvar: [string, string, string][];
  conceqn: string;
  concvar: [string, string, string][];
}

// Function to safely evaluate a mathematical expression
function evaluateExpression(expression: string, variables: Record<string, number>): number {
  // Replace variable names with their values
  let calculableExpression = expression

  // Sort variable names by length (descending) to avoid partial replacements
  const variableNames = Object.keys(variables).sort((a, b) => b.length - a.length)

  for (const varName of variableNames) {
    const regex = new RegExp(varName, "g")
    calculableExpression = calculableExpression.replace(regex, variables[varName].toString())
  }

  // Clean up the expression and make it safe to evaluate
  calculableExpression = calculableExpression.replace(/[^-()\d/*+.]/g, "")

  try {
    // Use Function constructor to evaluate the expression safely
    return new Function(`return ${calculableExpression}`)()
  } catch (error) {
    console.error("Error evaluating expression:", error)
    return 0
  }
}

// Function to format equation for display
function formatEquation(equation: string): string {
  return (
    equation
      // Replace operators with spaced versions
      .replace(/\*/g, " × ")
      .replace(/\//g, " ÷ ")
      .replace(/\+/g, " + ")
      .replace(/-/g, " - ")
      // Add spaces around parentheses
      .replace(/\(/g, "( ")
      .replace(/\)/g, " )")
      // Replace underscores with spaces for readability
      .replace(/_/g, " ")
      // Highlight variable names with a different style
      .split(" ")
      .map((part) => {
        // If the part contains letters (likely a variable) and isn't an operator
        if (/[a-zA-Z]/.test(part) && !["×", "÷", "+", "-", "(", ")"].includes(part)) {
          return `<span class="text-blue-600 font-semibold">${part}</span>`
        }
        return part
      })
      .join(" ")
  )
}

export default function ROIResults() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const [payload, setPayload] = useState<ROIPayload | null>(null)
  const [variables, setVariables] = useState<Record<string, number>>({})
  const [costOfChange, setCostOfChange] = useState<number>(0)
  const [costOfNoChange, setCostOfNoChange] = useState<number>(0)
  const [roi, setRoi] = useState<number>(0)

  // Initialize payload from URL parameters
  useEffect(() => {
    const fetchPayload = () => {
      try {
        // Convert URL parameters back to payload structure
        const payloadData: ROIPayload = {
          coceqn: searchParams.get('coceqn') || '',
          cocvar: [],
          conceqn: searchParams.get('conceqn') || '',
          concvar: []
        };

        // Process cocvar array
        const cocvarEntries = Array.from(searchParams.entries())
          .filter(([key]) => key.startsWith('cocvar['))
          .reduce((acc: any[], [key, value]) => {
            const matches = key.match(/cocvar\[(\d+)\]\[(\d+)\]/);
            if (matches) {
              const [, index, subIndex] = matches;
              if (!acc[Number(index)]) acc[Number(index)] = [];
              acc[Number(index)][Number(subIndex)] = value;
            }
            return acc;
          }, []);

        // Process concvar array
        const concvarEntries = Array.from(searchParams.entries())
          .filter(([key]) => key.startsWith('concvar['))
          .reduce((acc: any[], [key, value]) => {
            const matches = key.match(/concvar\[(\d+)\]\[(\d+)\]/);
            if (matches) {
              const [, index, subIndex] = matches;
              if (!acc[Number(index)]) acc[Number(index)] = [];
              acc[Number(index)][Number(subIndex)] = value;
            }
            return acc;
          }, []);

        payloadData.cocvar = cocvarEntries;
        payloadData.concvar = concvarEntries;

        setPayload(payloadData);
      } catch (error) {
        console.error("Error parsing payload from URL:", error);
      }
    };

    fetchPayload();
  }, [searchParams]);

  // Initialize variables from payload
  useEffect(() => {
    if (!payload) return;

    const initialVariables: Record<string, number> = {}

    // Process cost of change variables
    payload.cocvar.forEach(([name, _, defaultValue]: [string, string, string]) => {
      initialVariables[name] = Number.parseFloat(defaultValue)
    })

    // Process cost of no change variables
    payload.concvar.forEach(([name, _, defaultValue]: [string, string, string]) => {
      initialVariables[name] = Number.parseFloat(defaultValue)
    })

    setVariables(initialVariables)
  }, [payload])

  // Calculate costs whenever variables change
  useEffect(() => {
    if (Object.keys(variables).length === 0) return

    try {
      // Calculate cost of change
      const cocResult = evaluateExpression(payload?.coceqn || "", variables)
      setCostOfChange(cocResult)

      // Calculate cost of no change
      const concResult = evaluateExpression(payload?.conceqn || "", variables)
      setCostOfNoChange(concResult)

      // Calculate ROI
      const roiValue = concResult - cocResult
      setRoi(roiValue)
    } catch (error) {
      console.error("Calculation error:", error)
    }
  }, [variables, payload])

  // Handle variable value changes
  const handleVariableChange = (name: string, value: string) => {
    const numericValue = Number.parseFloat(value) || 0
    setVariables((prev) => ({
      ...prev,
      [name]: numericValue,
    }))
  }

  return (
    <div className="flex min-h-screen bg-[#F0F4EF]">
      {/* Sidebar */}
      <DashboardNav />

      {/* Main Content */}
      <div className="flex-1">
        <header className="bg-[#344966] text-white py-4 px-6">
          <div className="flex justify-between items-center">
            <h1 className="text-xl font-bold">ROI Calculator Results</h1>
            <div className="flex items-center gap-4">
              <Button variant="ghost" className="text-white hover:bg-[#2a3b54]">
                <Settings className="h-5 w-5" />
              </Button>
              <div className="h-8 w-8 rounded-full bg-[#BFC994] flex items-center justify-center text-[#0D1821] font-bold">
                U
              </div>
            </div>
          </div>
        </header>

        <main className="p-6">
          <div className="mb-6">
            <Link
              href="/dashboard/initiate-change"
              className="text-[#344966] hover:text-[#0D1821] flex items-center gap-1 mb-4"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to Change Form
            </Link>
            <h2 className="text-2xl font-bold text-[#0D1821]">ROI Calculation Results</h2>
            <p className="text-[#344966] mt-1">Adjust the variables below to see how they impact your ROI</p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
            {/* Results Summary Card */}
            <Card className="border-[#B4CDED] lg:col-span-3 overflow-hidden py-0">
              <div className="bg-[#344966] text-white px-6 py-4">
                <h3 className="text-xl font-semibold">ROI Summary</h3>
                <p className="text-gray-200 text-sm mt-1">
                  Based on your inputs, here's the calculated return on investment
                </p>
              </div>
              <div className="p-6">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="bg-[#B4CDED] bg-opacity-20 p-4 rounded-lg">
                    <h3 className="text-sm font-medium text-[#344966] mb-1">Cost of Change</h3>
                    <div className="text-2xl font-bold text-[#0D1821] flex items-center">
                      <DollarSign className="h-5 w-5 text-[#344966] mr-1" />
                      {costOfChange.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                    </div>
                  </div>
                  <div className="bg-[#B4CDED] bg-opacity-20 p-4 rounded-lg">
                    <h3 className="text-sm font-medium text-[#344966] mb-1">Cost of No Change</h3>
                    <div className="text-2xl font-bold text-[#0D1821] flex items-center">
                      <DollarSign className="h-5 w-5 text-[#344966] mr-1" />
                      {costOfNoChange.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                    </div>
                  </div>
                  <div className={`p-4 rounded-lg ${roi >= 0 ? "bg-green-50" : "bg-red-50"}`}>
                    <h3 className="text-sm font-medium text-[#344966] mb-1">Net ROI</h3>
                    <div className={`text-2xl font-bold flex items-center ${roi >= 0 ? "text-green-700" : "text-red-700"}`}>
                      <DollarSign className={`h-5 w-5 mr-1 ${roi >= 0 ? "text-green-600" : "text-red-600"}`} />
                      {roi.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                    </div>
                  </div>
                </div>
              </div>
            </Card>

            {/* Cost of Change Variables */}
            <Card className="border-[#B4CDED] lg:col-span-2">
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Calculator className="h-5 w-5 mr-2 text-[#344966]" />
                  Cost of Change Variables
                </CardTitle>
                <CardDescription>
                  Adjust these variables to calculate the cost of implementing the change
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {payload?.cocvar.map(([name, description, defaultValue]: [string, string, string]) => (
                    <div key={name} className="space-y-2">
                      <Label htmlFor={name} className="text-[#0D1821] flex justify-between">
                        <span>{name.replace(/_/g, " ")}</span>
                      </Label>
                      <div className="relative">
                        <Input
                          id={name}
                          type="number"
                          step="any"
                          value={variables[name] || ""}
                          onChange={(e) => handleVariableChange(name, e.target.value)}
                          className="border-[#B4CDED] focus:border-[#344966] focus:ring-[#344966] pl-8"
                        />
                        {name.toLowerCase().includes("cost") || name.toLowerCase().includes("per") ? (
                          <DollarSign className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-[#344966]" />
                        ) : null}
                      </div>
                      <p className="text-xs text-[#344966]">{description}</p>
                    </div>
                  ))}
                </div>
                <Separator className="my-4" />
                <Accordion type="single" collapsible className="mt-4 border rounded-md">
                  <AccordionItem value="equation" className="border-0">
                    <AccordionTrigger className="py-3 px-4 text-sm font-medium text-[#344966] hover:no-underline">
                      View Calculation Formula
                    </AccordionTrigger>
                    <AccordionContent className="px-4 pb-4">
                      <div className="p-3 bg-[#F0F4EF] rounded-md font-mono text-sm overflow-x-auto">
                        <div
                          className="text-[#0D1821] leading-relaxed"
                          dangerouslySetInnerHTML={{ __html: formatEquation(payload?.coceqn || "") }}
                        />
                      </div>
                      <p className="text-xs text-[#344966] mt-2 italic">
                        Variables are automatically replaced with their current values during calculation
                      </p>
                    </AccordionContent>
                  </AccordionItem>
                </Accordion>
              </CardContent>
            </Card>

            {/* Cost of No Change Variables */}
            <Card className="border-[#B4CDED]">
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Calculator className="h-5 w-5 mr-2 text-[#344966]" />
                  Cost of No Change Variables
                </CardTitle>
                <CardDescription>
                  Adjust these variables to calculate the cost of not implementing the change
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 gap-4">
                  {payload?.concvar.map(([name, description, defaultValue]: [string, string, string]) => (
                    <div key={name} className="space-y-2">
                      <Label htmlFor={name} className="text-[#0D1821] flex justify-between">
                        <span>{name.replace(/_/g, " ")}</span>
                      </Label>
                      <div className="relative">
                        <Input
                          id={name}
                          type="number"
                          step="any"
                          value={variables[name] || ""}
                          onChange={(e) => handleVariableChange(name, e.target.value)}
                          className="border-[#B4CDED] focus:border-[#344966] focus:ring-[#344966] pl-8"
                        />
                        {name.toLowerCase().includes("cost") || name.toLowerCase().includes("per") ? (
                          <DollarSign className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-[#344966]" />
                        ) : null}
                      </div>
                      <p className="text-xs text-[#344966]">{description}</p>
                    </div>
                  ))}
                </div>
                <Separator className="my-4" />
                <Accordion type="single" collapsible className="mt-4 border rounded-md">
                  <AccordionItem value="equation" className="border-0">
                    <AccordionTrigger className="py-3 px-4 text-sm font-medium text-[#344966] hover:no-underline">
                      View Calculation Formula
                    </AccordionTrigger>
                    <AccordionContent className="px-4 pb-4">
                      <div className="p-3 bg-[#F0F4EF] rounded-md font-mono text-sm overflow-x-auto">
                        <div
                          className="text-[#0D1821] leading-relaxed"
                          dangerouslySetInnerHTML={{ __html: formatEquation(payload?.conceqn || "") }}
                        />
                      </div>
                      <p className="text-xs text-[#344966] mt-2 italic">
                        Variables are automatically replaced with their current values during calculation
                      </p>
                    </AccordionContent>
                  </AccordionItem>
                </Accordion>
              </CardContent>
            </Card>
          </div>
          <div className="mt-8">
            <Card className="border-[#B4CDED] overflow-hidden py-0">
              <div className="bg-[#344966] text-white px-6 py-4">
                <h3 className="text-xl font-semibold">ROI Assistant</h3>
                <p className="text-gray-200 text-sm mt-1">
                  Ask questions about your ROI calculation or how to interpret the results
                </p>
              </div>
              <div className="p-0">
                <div className="h-[400px]">
                  <ChatInterface formData={{
                    change_initiative_name: searchParams.get('change_initiative_name') || '',
                    industry: searchParams.get('industry') || '',
                    services_provided: searchParams.get('services_provided') || '',
                    department: searchParams.get('department')?.split(',') || [],
                    start_date: searchParams.get('start_date') || '',
                    end_date: searchParams.get('end_date') || '',
                    min_budget: searchParams.get('min_budget') || '',
                    max_budget: searchParams.get('max_budget') || '',
                    targeted_business_goals: searchParams.get('targeted_business_goals') || '',
                    employee_retraining_percent: searchParams.get('employee_retraining_percent') || '',
                    num_affected_employees: searchParams.get('num_affected_employees') || '',
                    employee_morale: Number(searchParams.get('employee_morale')) || 5,
                    change_details: searchParams.get('change_details') || ''
                  }} />
                </div>
              </div>
            </Card>
          </div>
        </main>
      </div>
    </div>
  )
}