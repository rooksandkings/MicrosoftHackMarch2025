"use client"

import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { DollarSign, FileText, Settings, Users, Calendar } from "lucide-react"
import { DashboardNav } from "@/components/dashboard-nav"
import { useState } from "react"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Slider } from "@/components/ui/slider"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

export default function Dashboard() {
  const [employeeMorale, setEmployeeMorale] = useState(5)

  return (
    <div className="flex min-h-screen bg-[#F0F4EF]">
      {/* Sidebar */}
      <DashboardNav />

      {/* Main Content */}
      <div className="flex-1">
        <header className="bg-[#344966] text-white py-4 px-6">
          <div className="flex justify-between items-center">
            <h1 className="text-xl font-bold">Dashboard</h1>
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
          <div className="mb-8">
            <h2 className="text-2xl font-bold text-[#0D1821]">Welcome back, User</h2>
            <p className="text-[#344966] mt-1">Here's an overview of your change management initiatives</p>
          </div>

          {/* Stats Overview */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <Card className="border-[#B4CDED]">
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-[#344966]">Active Changes</CardTitle>
                <FileText className="h-4 w-4 text-[#344966]" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-[#0D1821]">3</div>
                <p className="text-xs text-[#344966] mt-1">2 pending approval</p>
              </CardContent>
            </Card>
            <Card className="border-[#B4CDED]">
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-[#344966]">Total ROI</CardTitle>
                <DollarSign className="h-4 w-4 text-[#344966]" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-[#0D1821]">$245,000</div>
                <p className="text-xs text-[#344966] mt-1">+12% from last quarter</p>
              </CardContent>
            </Card>
            <Card className="border-[#B4CDED]">
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-[#344966]">Team Adoption</CardTitle>
                <Users className="h-4 w-4 text-[#344966]" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-[#0D1821]">78%</div>
                <p className="text-xs text-[#344966] mt-1">+5% from last month</p>
              </CardContent>
            </Card>
          </div>

          {/* Quick Change Initiative Form */}
          <Card className="border-[#B4CDED] mb-8">
            <CardHeader>
              <CardTitle>Quick Change Initiative</CardTitle>
              <CardDescription>Enter the basic details to start a new change initiative</CardDescription>
            </CardHeader>
            <CardContent>
              <form className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label htmlFor="initiative-name" className="text-[#0D1821]">
                      Change Initiative Name
                    </Label>
                    <Input
                      id="initiative-name"
                      placeholder="e.g., CRM Implementation"
                      className="border-[#B4CDED] focus:border-[#344966] focus:ring-[#344966]"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="industry" className="text-[#0D1821]">
                      What industry does your business operate in?
                    </Label>
                    <Select>
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
                        <SelectItem value="other">Other</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2 md:col-span-2">
                    <Label htmlFor="short-description" className="text-[#0D1821]">
                      Short Description
                    </Label>
                    <Textarea
                      id="short-description"
                      placeholder="Briefly describe the change initiative..."
                      className="border-[#B4CDED] focus:border-[#344966] focus:ring-[#344966]"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="services" className="text-[#0D1821]">
                      What services do you provide?
                    </Label>
                    <Input
                      id="services"
                      placeholder="e.g., Software Development, Consulting"
                      className="border-[#B4CDED] focus:border-[#344966] focus:ring-[#344966]"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="department" className="text-[#0D1821]">
                      Department
                    </Label>
                    <Select>
                      <SelectTrigger className="border-[#B4CDED] focus:border-[#344966] focus:ring-[#344966]">
                        <SelectValue placeholder="Select department" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="sales">Sales</SelectItem>
                        <SelectItem value="marketing">Marketing</SelectItem>
                        <SelectItem value="operations">Operations</SelectItem>
                        <SelectItem value="it">IT</SelectItem>
                        <SelectItem value="hr">Human Resources</SelectItem>
                        <SelectItem value="finance">Finance</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="start-date" className="text-[#0D1821]">
                      Start Date
                    </Label>
                    <div className="relative">
                      <Input
                        id="start-date"
                        type="date"
                        className="border-[#B4CDED] focus:border-[#344966] focus:ring-[#344966]"
                      />
                      <Calendar className="absolute right-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-[#344966] pointer-events-none" />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="end-date" className="text-[#0D1821]">
                      Expected Completion Date
                    </Label>
                    <div className="relative">
                      <Input
                        id="end-date"
                        type="date"
                        className="border-[#B4CDED] focus:border-[#344966] focus:ring-[#344966]"
                      />
                      <Calendar className="absolute right-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-[#344966] pointer-events-none" />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="budget-min" className="text-[#0D1821]">
                      Realistic Budget Range (Min)
                    </Label>
                    <div className="relative">
                      <Input
                        id="budget-min"
                        type="number"
                        placeholder="0.00"
                        className="border-[#B4CDED] focus:border-[#344966] focus:ring-[#344966] pl-8"
                      />
                      <DollarSign className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-[#344966]" />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="budget-max" className="text-[#0D1821]">
                      Realistic Budget Range (Max)
                    </Label>
                    <div className="relative">
                      <Input
                        id="budget-max"
                        type="number"
                        placeholder="0.00"
                        className="border-[#B4CDED] focus:border-[#344966] focus:ring-[#344966] pl-8"
                      />
                      <DollarSign className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-[#344966]" />
                    </div>
                  </div>

                  <div className="space-y-2 md:col-span-2">
                    <Label htmlFor="business-goals" className="text-[#0D1821]">
                      What business goals will this initiative address?
                    </Label>
                    <Textarea
                      id="business-goals"
                      placeholder="Describe the specific business goals this change will help achieve..."
                      className="border-[#B4CDED] focus:border-[#344966] focus:ring-[#344966]"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="retraining-percentage" className="text-[#0D1821]">
                      Percentage of employees needing retraining
                    </Label>
                    <div className="relative">
                      <Input
                        id="retraining-percentage"
                        type="number"
                        min="0"
                        max="100"
                        placeholder="0"
                        className="border-[#B4CDED] focus:border-[#344966] focus:ring-[#344966] pr-8"
                      />
                      <span className="absolute right-3 top-1/2 transform -translate-y-1/2 text-[#344966]">%</span>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="affected-employees" className="text-[#0D1821]">
                      Number of Affected Employees
                    </Label>
                    <div className="relative">
                      <Input
                        id="affected-employees"
                        type="number"
                        placeholder="0"
                        className="border-[#B4CDED] focus:border-[#344966] focus:ring-[#344966] pl-8"
                      />
                      <Users className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-[#344966]" />
                    </div>
                  </div>

                  <div className="space-y-4 md:col-span-2">
                    <Label className="text-[#0D1821]">Employee Morale (1-10)</Label>
                    <div className="space-y-3">
                      <Slider
                        value={[employeeMorale]}
                        min={1}
                        max={10}
                        step={1}
                        onValueChange={(value) => setEmployeeMorale(value[0])}
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
                      <div className="text-center font-medium text-[#344966]">Selected: {employeeMorale}</div>
                    </div>
                  </div>
                </div>

                <div className="flex justify-end gap-4 pt-4">
                  <Button variant="outline" className="border-[#344966] text-[#344966]">
                    Save as Draft
                  </Button>
                  <Link href="/dashboard/initiate-change">
                    <Button className="bg-[#344966] hover:bg-[#2a3b54] text-white">Continue to Full Form</Button>
                  </Link>
                </div>
              </form>
            </CardContent>
          </Card>

          {/* Recent Changes Section - Keep this section as is */}
          <div className="mt-8">
            <h3 className="text-xl font-bold text-[#0D1821] mb-4">Recent Changes</h3>
            <Card className="border-[#B4CDED]">
              <CardContent className="p-0">
                <div className="divide-y divide-[#B4CDED]">
                  {[
                    {
                      title: "CRM Implementation",
                      date: "Started 2 weeks ago",
                      roi: "$120,000",
                      status: "In Progress",
                    },
                    {
                      title: "Remote Work Policy",
                      date: "Started 1 month ago",
                      roi: "$85,000",
                      status: "Completed",
                    },
                    {
                      title: "Sales Process Optimization",
                      date: "Started 3 months ago",
                      roi: "$40,000",
                      status: "Completed",
                    },
                  ].map((change, index) => (
                    <div key={index} className="flex items-center justify-between p-4">
                      <div className="flex items-center gap-4">
                        <div className="h-10 w-10 rounded-full bg-[#B4CDED] flex items-center justify-center text-[#344966]">
                          <FileText className="h-5 w-5" />
                        </div>
                        <div>
                          <h4 className="font-medium text-[#0D1821]">{change.title}</h4>
                          <p className="text-sm text-[#344966]">{change.date}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-4">
                        <div className="text-right">
                          <div className="font-medium text-[#0D1821]">{change.roi}</div>
                          <div className="text-sm text-[#344966]">Estimated ROI</div>
                        </div>
                        <div
                          className={`px-3 py-1 rounded-full text-xs font-medium ${
                            change.status === "Completed"
                              ? "bg-[#BFC994] bg-opacity-30 text-[#0D1821]"
                              : "bg-[#B4CDED] bg-opacity-30 text-[#344966]"
                          }`}
                        >
                          {change.status}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </main>
      </div>
    </div>
  )
}

