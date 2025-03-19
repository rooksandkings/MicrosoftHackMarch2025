"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { BarChart3, FileText, Home, PlusCircle, Settings, TrendingUp, Users } from "lucide-react"
import { cn } from "@/lib/utils"

export function DashboardNav() {
  const pathname = usePathname()

  const navItems = [
    {
      title: "Dashboard",
      href: "/dashboard",
      icon: Home,
    },
    {
      title: "Changes",
      href: "/dashboard/changes",
      icon: FileText,
    },
    {
      title: "Analytics",
      href: "/dashboard/analytics",
      icon: BarChart3,
    },
    {
      title: "Team",
      href: "/dashboard/team",
      icon: Users,
    },
    {
      title: "Settings",
      href: "/dashboard/settings",
      icon: Settings,
    },
  ]

  return (
    <div className="w-64 bg-white border-r border-[#B4CDED] hidden md:block">
      <div className="p-4 border-b border-[#B4CDED]">
        <Link href="/" className="flex items-center gap-2">
          <TrendingUp className="h-6 w-6 text-[#344966]" />
          <span className="font-bold text-[#0D1821]">ROI Calculator</span>
        </Link>
      </div>
      <div className="p-4">
        <Link href="/dashboard/initiate-change">
          <button className="w-full bg-[#344966] hover:bg-[#2a3b54] text-white rounded-md py-2 px-4 flex items-center justify-center gap-2">
            <PlusCircle className="h-4 w-4" />
            Initiate a Change
          </button>
        </Link>
      </div>
      <nav className="p-2">
        <ul className="space-y-1">
          {navItems.map((item, index) => (
            <li key={index}>
              <Link
                href={item.href}
                className={cn(
                  "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium",
                  pathname === item.href
                    ? "bg-[#B4CDED] bg-opacity-30 text-[#344966]"
                    : "text-[#344966] hover:bg-[#F0F4EF] hover:text-[#0D1821]",
                )}
              >
                <item.icon className="h-4 w-4" />
                {item.title}
              </Link>
            </li>
          ))}
        </ul>
      </nav>
    </div>
  )
}

