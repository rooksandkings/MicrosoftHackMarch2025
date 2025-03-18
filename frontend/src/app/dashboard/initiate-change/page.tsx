import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { ArrowLeft, Calendar, DollarSign, Settings, Users } from "lucide-react"
import { DashboardNav } from "@/components/dashboard-nav"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

export default function InitiateChange() {
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
              <CardDescription>Provide basic information about your change initiative</CardDescription>
            </CardHeader>
            <CardContent>
              <form className="space-y-6">
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

                  <div className="space-y-2 md:col-span-2">
                    <Label htmlFor="description" className="text-[#0D1821]">
                      Description
                    </Label>
                    <Textarea
                      id="description"
                      placeholder="Describe the change initiative and its objectives..."
                      className="border-[#B4CDED] focus:border-[#344966] focus:ring-[#344966] min-h-[100px]"
                    />
                  </div>
                </div>

                <div className="border-t border-[#B4CDED] pt-6">
                  <h3 className="text-lg font-medium text-[#0D1821] mb-4">Cost Factors</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-2">
                      <Label htmlFor="implementation-cost" className="text-[#0D1821]">
                        Implementation Cost ($)
                      </Label>
                      <div className="relative">
                        <Input
                          id="implementation-cost"
                          type="number"
                          placeholder="0.00"
                          className="border-[#B4CDED] focus:border-[#344966] focus:ring-[#344966] pl-8"
                        />
                        <DollarSign className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-[#344966]" />
                      </div>
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="training-cost" className="text-[#0D1821]">
                        Training Cost ($)
                      </Label>
                      <div className="relative">
                        <Input
                          id="training-cost"
                          type="number"
                          placeholder="0.00"
                          className="border-[#B4CDED] focus:border-[#344966] focus:ring-[#344966] pl-8"
                        />
                        <DollarSign className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-[#344966]" />
                      </div>
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="resource-cost" className="text-[#0D1821]">
                        Resource Cost ($)
                      </Label>
                      <div className="relative">
                        <Input
                          id="resource-cost"
                          type="number"
                          placeholder="0.00"
                          className="border-[#B4CDED] focus:border-[#344966] focus:ring-[#344966] pl-8"
                        />
                        <DollarSign className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-[#344966]" />
                      </div>
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="other-costs" className="text-[#0D1821]">
                        Other Costs ($)
                      </Label>
                      <div className="relative">
                        <Input
                          id="other-costs"
                          type="number"
                          placeholder="0.00"
                          className="border-[#B4CDED] focus:border-[#344966] focus:ring-[#344966] pl-8"
                        />
                        <DollarSign className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-[#344966]" />
                      </div>
                    </div>
                  </div>
                </div>

                <div className="border-t border-[#B4CDED] pt-6">
                  <h3 className="text-lg font-medium text-[#0D1821] mb-4">Benefit Factors</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-2">
                      <Label htmlFor="productivity-gain" className="text-[#0D1821]">
                        Expected Productivity Gain (%)
                      </Label>
                      <Input
                        id="productivity-gain"
                        type="number"
                        placeholder="0"
                        className="border-[#B4CDED] focus:border-[#344966] focus:ring-[#344966]"
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="revenue-increase" className="text-[#0D1821]">
                        Expected Revenue Increase ($)
                      </Label>
                      <div className="relative">
                        <Input
                          id="revenue-increase"
                          type="number"
                          placeholder="0.00"
                          className="border-[#B4CDED] focus:border-[#344966] focus:ring-[#344966] pl-8"
                        />
                        <DollarSign className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-[#344966]" />
                      </div>
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="cost-reduction" className="text-[#0D1821]">
                        Expected Cost Reduction ($)
                      </Label>
                      <div className="relative">
                        <Input
                          id="cost-reduction"
                          type="number"
                          placeholder="0.00"
                          className="border-[#B4CDED] focus:border-[#344966] focus:ring-[#344966] pl-8"
                        />
                        <DollarSign className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-[#344966]" />
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
                  </div>
                </div>

                <div className="flex justify-end gap-4 pt-4">
                  <Button variant="outline" className="border-[#344966] text-[#344966]">
                    Save as Draft
                  </Button>
                  <Button className="bg-[#344966] hover:bg-[#2a3b54] text-white">Calculate ROI</Button>
                </div>
              </form>
            </CardContent>
          </Card>
        </main>
      </div>
    </div>
  )
}

