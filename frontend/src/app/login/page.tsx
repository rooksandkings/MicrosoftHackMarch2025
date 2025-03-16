import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { TrendingUp } from "lucide-react"

export default function Login() {
  return (
    <div className="min-h-screen bg-[#F0F4EF] flex flex-col">
      <header className="bg-[#344966] text-white py-4">
        <div className="container mx-auto px-4">
          <Link href="/" className="flex items-center gap-2 w-fit">
            <TrendingUp className="h-6 w-6" />
            <h1 className="text-xl font-bold">ROI Calculator</h1>
          </Link>
        </div>
      </header>

      <main className="flex-1 flex items-center justify-center p-4">
        <div className="w-full max-w-md">
          <div className="bg-white rounded-lg shadow-lg p-8 border border-[#B4CDED]">
            <div className="text-center mb-8">
              <TrendingUp className="h-12 w-12 text-[#344966] mx-auto mb-4" />
              <h2 className="text-2xl font-bold text-[#0D1821]">Welcome Back</h2>
              <p className="text-[#344966] mt-2">Log in to access your ROI calculator</p>
            </div>

            <form className="space-y-6">
              <div className="space-y-2">
                <Label htmlFor="email" className="text-[#0D1821]">
                  Email
                </Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="your@email.com"
                  className="border-[#B4CDED] focus:border-[#344966] focus:ring-[#344966]"
                />
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label htmlFor="password" className="text-[#0D1821]">
                    Password
                  </Label>
                  <Link href="/forgot-password" className="text-sm text-[#344966] hover:underline">
                    Forgot password?
                  </Link>
                </div>
                <Input
                  id="password"
                  type="password"
                  className="border-[#B4CDED] focus:border-[#344966] focus:ring-[#344966]"
                />
              </div>

              <Button type="submit" className="w-full bg-[#344966] hover:bg-[#2a3b54] text-white">
                Log In
              </Button>
            </form>

            <div className="mt-6 text-center">
              <p className="text-[#344966]">
                Don't have an account?{" "}
                <Link href="/signup" className="text-[#344966] font-semibold hover:underline">
                  Sign up
                </Link>
              </p>
            </div>
          </div>
        </div>
      </main>

      <footer className="bg-[#0D1821] text-white py-4">
        <div className="container mx-auto px-4 text-center text-sm">
          © {new Date().getFullYear()} ROI Calculator for Change Management. All rights reserved.
        </div>
      </footer>
    </div>
  )
}

