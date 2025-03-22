import Link from "next/link"
import { Button } from "@/components/ui/button"
import { ArrowRight, BarChart3, TrendingUp, Users } from "lucide-react"

export default function Home() {
  return (
    <div className="flex flex-col min-h-screen bg-[#F0F4EF]">
      <header className="bg-[#344966] text-white py-4">
        <div className="container mx-auto px-4 flex justify-between items-center">
          <div className="flex items-center gap-2">
            <TrendingUp className="h-6 w-6" />
            <h1 className="text-xl font-bold">TransformX</h1>
          </div>
          <Link href="/dashboard">
            <Button className="bg-[#BFC994] hover:bg-[#a8b27e] text-[#0D1821]">Login</Button>
          </Link>
        </div>
      </header>

      <main className="flex-1">
        <section className="py-20 px-4">
          <div className="container mx-auto max-w-5xl">
            <div className="grid md:grid-cols-2 gap-12 items-center">
              <div className="space-y-6">
                <h2 className="text-4xl md:text-5xl font-bold text-[#0D1821] leading-tight">
                  Quantify the Impact of Change Management
                </h2>
                <p className="text-lg text-[#344966]">
                  Calculate the return on investment for your change management initiatives with our easy-to-use tool.
                </p>
                <div className="flex gap-4">
                  <Button className="bg-[#344966] hover:bg-[#2a3b54] text-white px-6">
                    Get Started
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </Button>
                  <Link href="/dashboard">
                    <Button variant="outline" className="border-[#344966] text-[#344966]">
                      Login
                    </Button>
                  </Link>
                </div>
              </div>
              <div className="bg-[#B4CDED] rounded-lg p-8 shadow-lg">
                <div className="aspect-square relative flex items-center justify-center">
                  <div className="absolute inset-0 flex items-center justify-center">
                    <BarChart3 className="w-32 h-32 text-[#344966] opacity-20" />
                  </div>
                  <div className="relative z-10 text-center space-y-4">
                    <h3 className="text-2xl font-bold text-[#0D1821]">ROI Calculator</h3>
                    <p className="text-[#344966]">Measure the financial impact of your change initiatives</p>
                    <Button className="bg-[#344966] hover:bg-[#2a3b54] text-white mt-4">Try Calculator</Button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section className="py-16 px-4 bg-[#B4CDED] bg-opacity-30">
          <div className="container mx-auto max-w-5xl">
            <h2 className="text-3xl font-bold text-center text-[#0D1821] mb-12">
              Why Calculate Change Management ROI?
            </h2>
            <div className="grid md:grid-cols-3 gap-8">
              {[
                {
                  icon: <TrendingUp className="h-10 w-10" />,
                  title: "Justify Investments",
                  description: "Demonstrate the financial value of change management initiatives to stakeholders.",
                },
                {
                  icon: <Users className="h-10 w-10" />,
                  title: "Improve Adoption",
                  description: "Measure how change management impacts user adoption and productivity.",
                },
                {
                  icon: <BarChart3 className="h-10 w-10" />,
                  title: "Data-Driven Decisions",
                  description: "Make informed decisions based on quantifiable metrics and outcomes.",
                },
              ].map((feature, index) => (
                <div key={index} className="bg-white rounded-lg p-6 shadow-md border border-[#B4CDED]">
                  <div className="text-[#344966] mb-4">{feature.icon}</div>
                  <h3 className="text-xl font-bold text-[#0D1821] mb-2">{feature.title}</h3>
                  <p className="text-[#344966]">{feature.description}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="py-20 px-4">
          <div className="container mx-auto max-w-3xl text-center">
            <h2 className="text-3xl font-bold text-[#0D1821] mb-6">Ready to Calculate Your Change Management ROI?</h2>
            <p className="text-lg text-[#344966] mb-8">
              Join organizations that make data-driven decisions about their change management initiatives.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button className="bg-[#344966] hover:bg-[#2a3b54] text-white px-8 py-6 text-lg">Get Started Now</Button>
              <Link href="/dashboard">
                <Button variant="outline" className="border-[#344966] text-[#344966] px-8 py-6 text-lg">
                  Login
                </Button>
              </Link>
            </div>
          </div>
        </section>
      </main>

      <footer className="bg-[#0D1821] text-white py-8">
        <div className="container mx-auto px-4">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="flex items-center gap-2 mb-4 md:mb-0">
              <TrendingUp className="h-5 w-5" />
              <span className="font-bold">TransformX</span>
            </div>
            <div className="text-sm text-gray-400">
              © {new Date().getFullYear()} ROI Calculator for Change Management. All rights reserved.
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}

