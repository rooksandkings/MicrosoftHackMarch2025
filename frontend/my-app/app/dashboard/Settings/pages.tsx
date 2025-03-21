"use client"
import { useState } from “react”;
import Link from “next/link”;
import { Button } from “@/components/ui/button”;
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from “@/components/ui/card”;
import { DashboardNav } from “@/components/dashboard-nav”;
export default function Settings() {
  const [formData, setFormData] = useState({
    // Add any settings-related state here
    notification: true,
    theme: “light”,
  });
  const handleToggleNotification = () => {
    setFormData((prev) => ({
      ...prev,
      notification: !prev.notification,
    }));
  };
  return (
    <div className=“flex min-h-screen bg-[#F0F4EF]“>
      {/* Sidebar */}
      <DashboardNav />
      {/* Main Content */}
      <div className=“flex-1”>
        <header className=“bg-[#344966] text-white py-4 px-6">
          <div className=“flex justify-between items-center”>
            <h1 className=“text-xl font-bold”>Settings</h1>
            <div className=“flex items-center gap-4”>
              <Button variant=“ghost” className=“text-white hover:bg-[#2A3B54]“>
                {/* Add any icon here if needed */}
              </Button>
              <div className=“h-8 w-8 rounded-full bg-[#BFC994] flex items-center justify-center text-[#0D1821] font-bold”>
                U
              </div>
            </div>
          </div>
        </header>
        <main className=“p-6">
          <div className=“mb-6”>
            <h2 className=“text-2xl font-bold text-[#0D1821]“>User Settings</h2>
            <p className=“text-[#344966] mt-1”>Adjust your preferences below.</p>
          </div>
          <Card className=“border-[#B4CDED] mb-8">
            <CardHeader>
              <CardTitle>Notification Settings</CardTitle>
              <CardDescription>Manage your notification preferences.</CardDescription>
            </CardHeader>
            <CardContent>
              <div className=“flex items-center justify-between”>
                <span className=“text-[#0D1821]“>Email Notifications</span>
                <Button onClick={handleToggleNotification} className=“bg-[#344966] text-white”>
                  {formData.notification ? “Disable” : “Enable”}
                </Button>
              </div>
            </CardContent>
          </Card>
          <Card className=“border-[#B4CDED] mb-8">
            <CardHeader>
              <CardTitle>Theme Settings</CardTitle>
              <CardDescription>Select your preferred theme.</CardDescription>
            </CardHeader>
            <CardContent>
              <div className=“flex items-center justify-between”>
                <span className=“text-[#0D1821]“>Theme</span>
                <select
                  value={formData.theme}
                  onChange={(e) => setFormData({ ...formData, theme: e.target.value })}
                  className=“border-[#B4CDED] focus:border-[#344966] focus:ring-[#344966] p-2”
                >
                  <option value=“light”>Light</option>
                  <option value=“dark”>Dark</option>
                </select>
              </div>
            </CardContent>
          </Card>
          <div className=“flex justify-end gap-4 pt-4">
            <Button type=“button” variant=“outline” className=“border-[#344966] text-[#344966]“>
              Save Changes
            </Button>
          </div>
        </main>
      </div>
    </div>
  );
}