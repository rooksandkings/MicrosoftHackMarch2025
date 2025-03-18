import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { DollarSign, FileText, PlusCircle, Settings, Users } from "lucide-react"
import { DashboardNav } from "@/components/dashboard-nav"

export default function Dashboard() {
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

          {/* Initiate Change Button */}
          <div className="flex flex-col items-center justify-center py-12 px-4">
            <div className="text-center mb-8 max-w-md">
              <h3 className="text-xl font-bold text-[#0D1821] mb-2">Ready to start a new change initiative?</h3>
              <p className="text-[#344966]">Calculate the potential ROI of your next change management initiative</p>
            </div>
            <Link href="/dashboard/initiate-change">
              <Button className="bg-[#344966] hover:bg-[#2a3b54] text-white px-8 py-6 text-lg flex items-center gap-2">
                <PlusCircle className="h-5 w-5" />
                Initiate a Change
              </Button>
            </Link>
          </div>

          {/* Recent Changes */}
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

