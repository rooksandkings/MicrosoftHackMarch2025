"use client"

import Link from "next/link"
import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { ArrowLeft, Calendar, DollarSign, Settings, Users } from "lucide-react"
import { DashboardNav } from "@/components/dashboard-nav"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Slider } from "@/components/ui/slider"

export default function InitiateChange() {
  const [resistanceScale, setResistanceScale] = useState(5)
  const [involvementScale, setInvolvementScale] = useState(5)
  const [pastResistanceScale, setPastResistanceScale] = useState(5)

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

          <form className="space-y-8 mb-12">
            <Accordion type="single" collapsible defaultValue="general" className="w-full">
              {/* General Background Section */}
              <AccordionItem value="general">
                <AccordionTrigger className="bg-[#344966] text-white px-4 py-3 rounded-t-md hover:no-underline">
                  <h3 className="text-lg font-medium">General Background</h3>
                </AccordionTrigger>
                <AccordionContent className="bg-white border border-[#B4CDED] border-t-0 rounded-b-md p-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-2">
                      <Label htmlFor="initiative-name" className="text-[#0D1821]">
                        Initiative Name
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
                          <SelectItem value="government">Government</SelectItem>
                          <SelectItem value="other">Other</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="services" className="text-[#0D1821]">
                        What services do you provide?
                      </Label>
                      <Textarea
                        id="services"
                        placeholder="Describe the services your business provides..."
                        className="border-[#B4CDED] focus:border-[#344966] focus:ring-[#344966]"
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="business-function" className="text-[#0D1821]">
                        Describe the function of your business in one paragraph
                      </Label>
                      <Textarea
                        id="business-function"
                        placeholder="Provide a concise description of your business function..."
                        className="border-[#B4CDED] focus:border-[#344966] focus:ring-[#344966]"
                      />
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
                  </div>
                </AccordionContent>
              </AccordionItem>

              {/* Financial ROI Section */}
              <AccordionItem value="financial">
                <AccordionTrigger className="bg-[#344966] text-white px-4 py-3 hover:no-underline mt-4 rounded-t-md">
                  <h3 className="text-lg font-medium">Financial ROI</h3>
                </AccordionTrigger>
                <AccordionContent className="bg-white border border-[#B4CDED] border-t-0 rounded-b-md p-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-2">
                      <Label htmlFor="realistic-budget-min" className="text-[#0D1821]">
                        What is the realistic budget range for this initiative?
                      </Label>
                      <div className="flex items-center gap-2">
                        <div className="relative flex-1">
                          <Input
                            id="realistic-budget-min"
                            type="number"
                            placeholder="Minimum"
                            className="border-[#B4CDED] focus:border-[#344966] focus:ring-[#344966] pl-8"
                          />
                          <DollarSign className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-[#344966]" />
                        </div>
                        <span className="text-[#344966]">to</span>
                        <div className="relative flex-1">
                          <Input
                            id="realistic-budget-max"
                            type="number"
                            placeholder="Maximum"
                            className="border-[#B4CDED] focus:border-[#344966] focus:ring-[#344966] pl-8"
                          />
                          <DollarSign className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-[#344966]" />
                        </div>
                      </div>
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="optimistic-budget-min" className="text-[#0D1821]">
                        What is the optimistic budget range for this initiative?
                      </Label>
                      <div className="flex items-center gap-2">
                        <div className="relative flex-1">
                          <Input
                            id="optimistic-budget-min"
                            type="number"
                            placeholder="Minimum"
                            className="border-[#B4CDED] focus:border-[#344966] focus:ring-[#344966] pl-8"
                          />
                          <DollarSign className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-[#344966]" />
                        </div>
                        <span className="text-[#344966]">to</span>
                        <div className="relative flex-1">
                          <Input
                            id="optimistic-budget-max"
                            type="number"
                            placeholder="Maximum"
                            className="border-[#B4CDED] focus:border-[#344966] focus:ring-[#344966] pl-8"
                          />
                          <DollarSign className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-[#344966]" />
                        </div>
                      </div>
                    </div>

                    <div className="space-y-2 md:col-span-2">
                      <Label htmlFor="budget-breakdown" className="text-[#0D1821]">
                        Provide a high level cost breakdown of the change initiative budget
                      </Label>
                      <Textarea
                        id="budget-breakdown"
                        placeholder="e.g., what funds go where, major expense categories..."
                        className="border-[#B4CDED] focus:border-[#344966] focus:ring-[#344966]"
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="timeline" className="text-[#0D1821]">
                        What is the desired timeline for this initiative?
                      </Label>
                      <Select>
                        <SelectTrigger className="border-[#B4CDED] focus:border-[#344966] focus:ring-[#344966]">
                          <SelectValue placeholder="Select timeline" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="1-3months">1-3 months</SelectItem>
                          <SelectItem value="3-6months">3-6 months</SelectItem>
                          <SelectItem value="6-12months">6-12 months</SelectItem>
                          <SelectItem value="1-2years">1-2 years</SelectItem>
                          <SelectItem value="2+years">2+ years</SelectItem>
                        </SelectContent>
                      </Select>
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

                    <div className="space-y-2 md:col-span-2">
                      <Label htmlFor="kpis" className="text-[#0D1821]">
                        What are the KPIs for the initiative?
                      </Label>
                      <Textarea
                        id="kpis"
                        placeholder="List the key performance indicators you'll use to measure success..."
                        className="border-[#B4CDED] focus:border-[#344966] focus:ring-[#344966]"
                      />
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
                  </div>
                </AccordionContent>
              </AccordionItem>

              {/* Employee Engagement Section */}
              <AccordionItem value="employee">
                <AccordionTrigger className="bg-[#344966] text-white px-4 py-3 hover:no-underline mt-4 rounded-t-md">
                  <h3 className="text-lg font-medium">Employee Engagement</h3>
                </AccordionTrigger>
                <AccordionContent className="bg-white border border-[#B4CDED] border-t-0 rounded-b-md p-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-2 md:col-span-2">
                      <Label htmlFor="affected-roles" className="text-[#0D1821]">
                        What departments / roles / positions will be most affected by this change?
                      </Label>
                      <Textarea
                        id="affected-roles"
                        placeholder="List the departments, roles, and positions most impacted..."
                        className="border-[#B4CDED] focus:border-[#344966] focus:ring-[#344966]"
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="retraining-percentage" className="text-[#0D1821]">
                        What percentage of employees will need retraining?
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
                      <Label className="text-[#0D1821]">
                        On a scale of 1-10, how involved have employees been in shaping this initiative?
                        <span className="block text-sm text-[#344966] mt-1">
                          Where 1 is 'a possibility of change has been mentioned' and 10 is 'extensive town meetings
                          have been held, training teams have been formed and concerns have been addressed'
                        </span>
                      </Label>
                      <div className="space-y-3">
                        <Slider
                          value={[involvementScale]}
                          min={1}
                          max={10}
                          step={1}
                          onValueChange={(value) => setInvolvementScale(value[0])}
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
                        <div className="text-center font-medium text-[#344966]">Selected: {involvementScale}</div>
                      </div>
                    </div>

                    <div className="space-y-4 md:col-span-2">
                      <Label className="text-[#0D1821]">
                        On a scale of 1-10, how many employees resisted change in previous change initiatives?
                      </Label>
                      <div className="space-y-3">
                        <Slider
                          value={[pastResistanceScale]}
                          min={1}
                          max={10}
                          step={1}
                          onValueChange={(value) => setPastResistanceScale(value[0])}
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
                        <div className="text-center font-medium text-[#344966]">Selected: {pastResistanceScale}</div>
                      </div>
                    </div>

                    <div className="space-y-2 md:col-span-2">
                      <Label htmlFor="past-strategies" className="text-[#0D1821]">
                        What strategies have been most effective for success in past adoption efforts?
                      </Label>
                      <Textarea
                        id="past-strategies"
                        placeholder="Describe successful strategies from previous change initiatives..."
                        className="border-[#B4CDED] focus:border-[#344966] focus:ring-[#344966]"
                      />
                    </div>
                  </div>
                </AccordionContent>
              </AccordionItem>

              {/* Change Readiness Analysis Section */}
              <AccordionItem value="readiness">
                <AccordionTrigger className="bg-[#344966] text-white px-4 py-3 hover:no-underline mt-4 rounded-t-md">
                  <h3 className="text-lg font-medium">Change Readiness Analysis</h3>
                </AccordionTrigger>
                <AccordionContent className="bg-white border border-[#B4CDED] border-t-0 rounded-b-md p-6">
                  <div className="grid grid-cols-1 gap-6">
                    <div className="space-y-2">
                      <Label className="text-[#0D1821]">Has a change management team been set up?</Label>
                      <RadioGroup defaultValue="no" className="flex flex-col space-y-1">
                        <div className="flex items-center space-x-2">
                          <RadioGroupItem value="yes" id="team-yes" />
                          <Label htmlFor="team-yes" className="font-normal">
                            Yes, we have a team in place
                          </Label>
                        </div>
                        <div className="flex items-center space-x-2">
                          <RadioGroupItem value="planning" id="team-planning" />
                          <Label htmlFor="team-planning" className="font-normal">
                            We are planning to set one up
                          </Label>
                        </div>
                        <div className="flex items-center space-x-2">
                          <RadioGroupItem value="no" id="team-no" />
                          <Label htmlFor="team-no" className="font-normal">
                            No, we don't have plans for a dedicated team
                          </Label>
                        </div>
                      </RadioGroup>
                    </div>

                    <div className="space-y-4">
                      <Label className="text-[#0D1821]">
                        On a scale of 1-10, how resistant are your employees to change?
                      </Label>
                      <div className="space-y-3">
                        <Slider
                          value={[resistanceScale]}
                          min={1}
                          max={10}
                          step={1}
                          onValueChange={(value) => setResistanceScale(value[0])}
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
                        <div className="text-center font-medium text-[#344966]">Selected: {resistanceScale}</div>
                      </div>
                    </div>
                  </div>
                </AccordionContent>
              </AccordionItem>

              {/* Industry Comparison Section */}
              <AccordionItem value="industry">
                <AccordionTrigger className="bg-[#344966] text-white px-4 py-3 hover:no-underline mt-4 rounded-t-md">
                  <h3 className="text-lg font-medium">Industry Comparison</h3>
                </AccordionTrigger>
                <AccordionContent className="bg-white border border-[#B4CDED] border-t-0 rounded-b-md p-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-2 md:col-span-2">
                      <Label htmlFor="industry-benchmarks" className="text-[#0D1821]">
                        What industry benchmarks will be the most relevant for your company?
                      </Label>
                      <Textarea
                        id="industry-benchmarks"
                        placeholder="List the key industry benchmarks you want to compare against..."
                        className="border-[#B4CDED] focus:border-[#344966] focus:ring-[#344966]"
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="direct-competitors" className="text-[#0D1821]">
                        Who are your biggest direct competitors?
                      </Label>
                      <Textarea
                        id="direct-competitors"
                        placeholder="List your main direct competitors..."
                        className="border-[#B4CDED] focus:border-[#344966] focus:ring-[#344966]"
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="indirect-competitors" className="text-[#0D1821]">
                        Who are your biggest indirect competitors?
                      </Label>
                      <Textarea
                        id="indirect-competitors"
                        placeholder="List your main indirect competitors..."
                        className="border-[#B4CDED] focus:border-[#344966] focus:ring-[#344966]"
                      />
                    </div>

                    <div className="space-y-2 md:col-span-2">
                      <Label htmlFor="competitor-sectors" className="text-[#0D1821]">
                        What sectors do your biggest direct competitors function in?
                      </Label>
                      <Textarea
                        id="competitor-sectors"
                        placeholder="List the sectors where your direct competitors operate..."
                        className="border-[#B4CDED] focus:border-[#344966] focus:ring-[#344966]"
                      />
                    </div>
                  </div>
                </AccordionContent>
              </AccordionItem>

              {/* Risk Assessment & Mitigation Section */}
              <AccordionItem value="risk">
                <AccordionTrigger className="bg-[#344966] text-white px-4 py-3 hover:no-underline mt-4 rounded-t-md">
                  <h3 className="text-lg font-medium">Risk Assessment & Mitigation</h3>
                </AccordionTrigger>
                <AccordionContent className="bg-white border border-[#B4CDED] border-t-0 rounded-b-md p-6">
                  <div className="grid grid-cols-1 gap-6">
                    <div className="space-y-2">
                      <Label htmlFor="internal-challenges" className="text-[#0D1821]">
                        What are the top 3 internal challenges your company has faced in previous change initiatives?
                      </Label>
                      <Textarea
                        id="internal-challenges"
                        placeholder="Describe the main internal challenges from past initiatives..."
                        className="border-[#B4CDED] focus:border-[#344966] focus:ring-[#344966]"
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="external-challenges" className="text-[#0D1821]">
                        What are the top 3 external challenges your company has faced in previous change initiatives?
                      </Label>
                      <Textarea
                        id="external-challenges"
                        placeholder="Describe the main external challenges from past initiatives..."
                        className="border-[#B4CDED] focus:border-[#344966] focus:ring-[#344966]"
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="critical-resources" className="text-[#0D1821]">
                        What tools / resources are extremely important for your business to function successfully?
                      </Label>
                      <Textarea
                        id="critical-resources"
                        placeholder="e.g., physical presence of employees, that could be disrupted by a pandemic..."
                        className="border-[#B4CDED] focus:border-[#344966] focus:ring-[#344966]"
                      />
                    </div>
                  </div>
                </AccordionContent>
              </AccordionItem>
            </Accordion>

            <div className="flex justify-end gap-4 pt-4">
              <Button variant="outline" className="border-[#344966] text-[#344966]">
                Save as Draft
              </Button>
              <Button className="bg-[#344966] hover:bg-[#2a3b54] text-white">Calculate ROI</Button>
            </div>
          </form>
        </main>
      </div>
    </div>
  )
}

