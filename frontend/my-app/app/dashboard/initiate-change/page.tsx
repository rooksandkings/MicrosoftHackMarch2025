"use client"

import type React from "react"

import Link from "next/link"
import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { ArrowLeft, Calendar, DollarSign, Settings, Users } from "lucide-react"
import { DashboardNav } from "@/components/dashboard-nav"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Slider } from "@/components/ui/slider"
import { toast } from "@/hooks/use-toast"
import { useRouter } from "next/navigation"

const departments = [
  { label: "Sales", value: "sales" },
  { label: "Marketing", value: "marketing" },
  { label: "Operations", value: "operations" },
  { label: "Engineering", value: "engineering" },
  { label: "Human Resources", value: "hr" },
  { label: "Finance", value: "finance" },
  { label: "Customer Service", value: "customer-service" },
  { label: "Research & Development", value: "r-and-d" },
  { label: "Product", value: "product" },
  { label: "Other", value: "other" },
]

export default function InitiateChange() {
  const router = useRouter()
  // Form state
  const [formData, setFormData] = useState({
    change_initiative_name: "",
    change_details: "",
    industry: "",
    services_provided: "",
    department: [] as string[],
    start_date: "",
    end_date: "",
    min_budget: "",
    max_budget: "",
    targeted_business_goals: "",
    employee_retraining_percent: "",
    num_affected_employees: "",
    employee_morale: 5,
  })

  const [isSubmitting, setIsSubmitting] = useState(false)

  // Handle input changes
  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { id, value } = e.target
    setFormData((prev) => ({
      ...prev,
      [id]: value,
    }))
  }

  // Handle select changes
  const handleSelectChange = (id: string, value: string) => {
    setFormData((prev) => ({
      ...prev,
      [id]: value,
    }))
  }

  // Handle slider changes
  const handleSliderChange = (value: number[]) => {
    setFormData((prev) => ({
      ...prev,
      employee_morale: value[0],
    }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)
  
    try {
      const response = await fetch('/api/roi', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
      });
  
      if (!response.ok) {
        throw new Error(`Request failed with status code ${response.status}`);
      }
  
      const result = await response.json();
      console.log("ROI calculation response:", result);
      
      toast({
        title: "ROI Calculation Successful",
        description: "Your ROI calculation is complete.",
      });

      // Create URL parameters from the API response
      const params = new URLSearchParams();
      
      // Add form data to URL parameters
      Object.entries(formData).forEach(([key, value]) => {
        if (Array.isArray(value)) {
          params.append(key, value.join(','));
        } else {
          params.append(key, String(value));
        }
      });

      // Add API response data
      Object.entries(result).forEach(([key, value]) => {
        if (Array.isArray(value)) {
          // Handle arrays (cocvar and concvar)
          value.forEach((item, index) => {
            if (Array.isArray(item)) {
              item.forEach((subItem, subIndex) => {
                params.append(`${key}[${index}][${subIndex}]`, String(subItem));
              });
            }
          });
        } else {
          // Handle other values
          params.append(key, String(value));
        }
      });

      // Navigate to ROI results page with the response data
      router.push(`/dashboard/roi-results?${params.toString()}`);
      
    } catch (error) {
      console.error("Error:", error);
      toast({
        title: "Error",
        description: "Failed to calculate ROI. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex min-h-screen bg-[#F0F4EF]">
      {/* Sidebar */}
      <DashboardNav />

      {/* Main Content */}
      <div className="flex-1">
        <header className="bg-[#344966] text-white py-4 px-6">
          <div className="flex justify-between items-center">
            <h1 className="text-xl font-bold">Initiate a Change</h1>
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
            <Link href="/dashboard" className="text-[#344966] hover:text-[#0D1821] flex items-center gap-1 mb-4">
              <ArrowLeft className="h-4 w-4" />
              Back to Dashboard
            </Link>
            <h2 className="text-2xl font-bold text-[#0D1821]">Initiate a New Change</h2>
            <p className="text-[#344966] mt-1">
              Fill out the form below to calculate the ROI of your change initiative
            </p>
          </div>

          <Card className="border-[#B4CDED] mb-8">
            <CardHeader>
              <CardTitle>Change Initiative Details</CardTitle>
              <CardDescription>Provide information about your change initiative</CardDescription>
            </CardHeader>
            <CardContent>
              <form className="space-y-6" onSubmit={handleSubmit}>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label htmlFor="change_initiative_name" className="text-[#0D1821]">
                      Change Initiative Name
                    </Label>
                    <Input
                      id="change_initiative_name"
                      placeholder="e.g., CRM Implementation"
                      className="border-[#B4CDED] focus:border-[#344966] focus:ring-[#344966]"
                      value={formData.change_initiative_name}
                      onChange={handleChange}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="industry" className="text-[#0D1821]">
                      What industry does your business operate in?
                    </Label>
                    <Select onValueChange={(value) => handleSelectChange("industry", value)}>
                      <SelectTrigger className="border-[#B4CDED] focus:border-[#344966] focus:ring-[#344966]">
                        <SelectValue placeholder="Select industry" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="technology">Technology</SelectItem>
                        <SelectItem value="healthcare">Healthcare</SelectItem>
                        <SelectItem value="finance">Finance</SelectItem>
                        <SelectItem value="retail">Retail</SelectItem>
                        <SelectItem value="manufacturing">Manufacturing</SelectItem>
                        <SelectItem value="education">Education</SelectItem>
                        <SelectItem value="government">Government</SelectItem>
                        <SelectItem value="other">Other</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2 md:col-span-2">
                    <Label htmlFor="change_details" className="text-[#0D1821]">
                      Short Description
                    </Label>
                    <Textarea
                      id="change_details"
                      placeholder="Briefly describe the change initiative. Provide potential subscription costs, etc."
                      className="border-[#B4CDED] focus:border-[#344966] focus:ring-[#344966]"
                      value={formData.change_details}
                      onChange={handleChange}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="services_provided" className="text-[#0D1821]">
                      What services do you provide?
                    </Label>
                    <Input
                      id="services_provided"
                      placeholder="e.g., Software Development, Consulting"
                      className="border-[#B4CDED] focus:border-[#344966] focus:ring-[#344966]"
                      value={formData.services_provided}
                      onChange={handleChange}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="department" className="text-[#0D1821]">
                      Departments Affected (Select multiple)
                    </Label>
                    <div className="grid grid-cols-2 gap-2">
                      {departments.map((department) => (
                        <div key={department.value} className="flex items-center space-x-2">
                          <input
                            type="checkbox"
                            id={`dept-${department.value}`}
                            checked={formData.department.includes(department.value)}
                            onChange={(e) => {
                              if (e.target.checked) {
                                setFormData((prev) => ({
                                  ...prev,
                                  department: [...prev.department, department.value],
                                }))
                              } else {
                                setFormData((prev) => ({
                                  ...prev,
                                  department: prev.department.filter((d: string) => d !== department.value),
                                }))
                              }
                            }}
                            className="h-4 w-4 rounded border-[#B4CDED] text-[#344966] focus:ring-[#344966]"
                          />
                          <label htmlFor={`dept-${department.value}`} className="text-sm text-[#0D1821]">
                            {department.label}
                          </label>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="start_date" className="text-[#0D1821]">
                      Start Date
                    </Label>
                    <div className="relative">
                      <Input
                        id="start_date"
                        type="date"
                        className="border-[#B4CDED] focus:border-[#344966] focus:ring-[#344966]"
                        value={formData.start_date}
                        onChange={handleChange}
                      />
                      <Calendar className="absolute right-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-[#344966] pointer-events-none" />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="end_date" className="text-[#0D1821]">
                      Expected Completion Date
                    </Label>
                    <div className="relative">
                      <Input
                        id="end_date"
                        type="date"
                        className="border-[#B4CDED] focus:border-[#344966] focus:ring-[#344966]"
                        value={formData.end_date}
                        onChange={handleChange}
                      />
                      <Calendar className="absolute right-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-[#344966] pointer-events-none" />
                    </div>
                  </div>

                  <div className="space-y-4">
                    <Label className="text-[#0D1821]">Realistic Budget Range</Label>
                    <div className="grid grid-cols-2 gap-4">
                      <div className="relative">
                        <Label htmlFor="min_budget" className="text-[#0D1821] text-sm">
                          Min ($)
                        </Label>
                        <div className="relative mt-1">
                          <Input
                            id="min_budget"
                            type="number"
                            placeholder="0.00"
                            className="border-[#B4CDED] focus:border-[#344966] focus:ring-[#344966] pl-8"
                            value={formData.min_budget}
                            onChange={handleChange}
                          />
                          <DollarSign className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-[#344966]" />
                        </div>
                      </div>
                      <div className="relative">
                        <Label htmlFor="max_budget" className="text-[#0D1821] text-sm">
                          Max ($)
                        </Label>
                        <div className="relative mt-1">
                          <Input
                            id="max_budget"
                            type="number"
                            placeholder="0.00"
                            className="border-[#B4CDED] focus:border-[#344966] focus:ring-[#344966] pl-8"
                            value={formData.max_budget}
                            onChange={handleChange}
                          />
                          <DollarSign className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-[#344966]" />
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="space-y-2 md:col-span-2">
                    <Label htmlFor="targeted_business_goals" className="text-[#0D1821]">
                      What business goals will this initiative address?
                    </Label>
                    <Textarea
                      id="targeted_business_goals"
                      placeholder="Describe the specific business goals this change will help achieve..."
                      className="border-[#B4CDED] focus:border-[#344966] focus:ring-[#344966]"
                      value={formData.targeted_business_goals}
                      onChange={handleChange}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="employee_retraining_percent" className="text-[#0D1821]">
                      Percentage of employees needing retraining
                    </Label>
                    <div className="relative">
                      <Input
                        id="employee_retraining_percent"
                        type="number"
                        min="0"
                        max="100"
                        placeholder="0"
                        className="border-[#B4CDED] focus:border-[#344966] focus:ring-[#344966] pr-8"
                        value={formData.employee_retraining_percent}
                        onChange={handleChange}
                      />
                      <span className="absolute right-3 top-1/2 transform -translate-y-1/2 text-[#344966]">%</span>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="num_affected_employees" className="text-[#0D1821]">
                      Number of Affected Employees
                    </Label>
                    <div className="relative">
                      <Input
                        id="num_affected_employees"
                        type="number"
                        placeholder="0"
                        className="border-[#B4CDED] focus:border-[#344966] focus:ring-[#344966] pl-8"
                        value={formData.num_affected_employees}
                        onChange={handleChange}
                      />
                      <Users className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-[#344966]" />
                    </div>
                  </div>

                  <div className="space-y-4 md:col-span-2">
                    <Label className="text-[#0D1821]">Employee Morale (1-10)</Label>
                    <div className="space-y-3">
                      <Slider
                        value={[formData.employee_morale]}
                        min={1}
                        max={10}
                        step={1}
                        onValueChange={handleSliderChange}
                        className="w-full"
                      />
                      <div className="flex justify-between text-sm text-[#344966]">
                        <span>1</span>
                        <span>2</span>
                        <span>3</span>
                        <span>4</span>
                        <span>5</span>
                        <span>6</span>
                        <span>7</span>
                        <span>8</span>
                        <span>9</span>
                        <span>10</span>
                      </div>
                      <div className="text-center font-medium text-[#344966]">Selected: {formData.employee_morale}</div>
                    </div>
                  </div>
                </div>

                <div className="flex justify-end gap-4 pt-4">
                  <Button type="button" variant="outline" className="border-[#344966] text-[#344966]">
                    Save as Draft
                  </Button>
                  <Button type="submit" className="bg-[#344966] hover:bg-[#2a3b54] text-white" disabled={isSubmitting}>
                    {isSubmitting ? "Calculating..." : "Calculate ROI"}
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        </main>
      </div>
    </div>
  )
}

