"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import { useLanguage } from "@/contexts/LanguageContext";
import { apiClient } from "@/lib/api";
import { normalizePhoneNumber } from "@/utils/phone";
import Header from "@/components/Header";
import BottomNavigation from "@/components/BottomNavigation";

const languages = [
  { code: "en", name: "English" },
  { code: "am", name: "Amharic" },
  { code: "om", name: "Afaan Oromo" },
  { code: "ti", name: "Tigrinya" },
];

export default function SettingsPage() {
  const { isAuthenticated, user, refreshUser } = useAuth();
  const { t, language: currentLanguage, setLanguage: setLanguageContext } = useLanguage();
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [phoneNumber, setPhoneNumber] = useState("");
  const [language, setLanguage] = useState("en");
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!isAuthenticated) {
      router.push("/login");
      return;
    }
    // Use user data from context if available
    if (user) {
      setPhoneNumber(user.phone_number || "");
      setLanguage(user.language || "en");
      setLoading(false);
      setError(null);
    }
  }, [isAuthenticated, router, user]);

  const loadUserData = async () => {
    try {
      setLoading(true);
      const userData = await apiClient.getCurrentUser();
      setPhoneNumber(userData.phone_number || "");
      setLanguage(userData.language || "en");
    } catch (error) {
      console.error("Failed to load user data:", error);
      setError("Failed to load user data");
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSaving(true);
    try {
      const updateData: { phone_number?: string; language?: string } = {};
      
      if (phoneNumber) {
        updateData.phone_number = normalizePhoneNumber(phoneNumber);
      }
      
      if (language) {
        updateData.language = language;
      }
      
      await apiClient.updateCurrentUser(updateData);
      setSuccess(true);
      // Refresh user data to update language preference
      await refreshUser();
      // Update language context if language was changed
      if (updateData.language) {
        setLanguageContext(updateData.language as any);
      }
      setTimeout(() => setSuccess(false), 3000);
    } catch (err: any) {
      let errorMessage = "Failed to save changes. Please try again.";
      if (err.response?.data?.detail) {
        const detail = err.response.data.detail;
        if (typeof detail === "string") {
          errorMessage = detail;
        } else if (Array.isArray(detail) && detail.length > 0) {
          errorMessage = detail.map((e: any) => e.msg || JSON.stringify(e)).join(", ");
        } else if (typeof detail === "object") {
          errorMessage = detail.msg || JSON.stringify(detail);
        }
      }
      setError(errorMessage);
    } finally {
      setSaving(false);
    }
  };

  if (!isAuthenticated || loading) return null;

  return (
    <div className="min-h-screen bg-white flex flex-col font-sans pb-24">
      <Header />

      <main className="max-w-2xl mx-auto w-full px-6 py-10 flex-grow">
        <h1 className="text-3xl font-bold text-gray-900 mb-10">Settings</h1>

        <form onSubmit={handleSubmit} className="space-y-12">
          {/* Account Information Section */}
          <section>
            <h2 className="text-lg font-bold text-gray-800 mb-2">Account Information</h2>
            <div className="border-t border-gray-200 pt-6">
              <div className="flex flex-col md:flex-row md:items-center mb-6">
                <label className="w-40 text-gray-700 font-medium mb-2 md:mb-0">
                  Phone Number
                </label>
                <div className="flex-grow">
                  <input
                    type="tel"
                    value={phoneNumber}
                    onChange={(e) => setPhoneNumber(e.target.value)}
                    className="w-full px-4 py-2 bg-[#f8fafc] border border-gray-200 rounded-md focus:outline-none focus:ring-1 focus:ring-green-500"
                    placeholder="+251912345678"
                  />
                  <p className="text-xs text-blue-500 mt-1">
                    Used for SMS alerts.
                  </p>
                </div>
              </div>
            </div>
          </section>

          {/* Preferences Section */}
          <section>
            <h2 className="text-lg font-bold text-gray-800 mb-2">Preferences</h2>
            <div className="border-t border-gray-200 pt-6 space-y-6">
              <div className="flex flex-col md:flex-row md:items-center">
                <label className="w-40 text-gray-700 font-medium mb-2 md:mb-0">
                  App Language
                </label>
                <div className="relative flex-grow">
                  <select
                    value={language}
                    onChange={(e) => setLanguage(e.target.value)}
                    className="w-full appearance-none px-4 py-2 bg-[#f8fafc] border border-gray-200 rounded-md focus:outline-none focus:ring-1 focus:ring-green-500"
                  >
                    {languages.map((lang) => (
                      <option key={lang.code} value={lang.code}>
                        {lang.name}
                      </option>
                    ))}
                  </select>
                  <div className="absolute inset-y-0 right-3 flex items-center pointer-events-none">
                    <svg
                      className="w-4 h-4 text-gray-400"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth="2"
                        d="M19 9l-7 7-7-7"
                      />
                    </svg>
                  </div>
                </div>
              </div>
            </div>
          </section>

          {error && (
            <div className="rounded-xl bg-red-50 p-4">
              <p className="text-sm text-red-800">{error}</p>
            </div>
          )}

          <div className="pt-4">
            <button
              type="submit"
              disabled={saving}
              className="px-8 py-2.5 bg-[#4ce434] hover:bg-[#45cc2f] text-white font-bold rounded-full transition-colors shadow-sm disabled:opacity-50"
            >
              {saving ? t('saving') : t('saveChanges')}
            </button>
            {success && (
              <p className="text-green-600 text-sm mt-2 font-medium">
                {t('changesSaved')}
              </p>
            )}
          </div>
        </form>
      </main>

      <BottomNavigation />
    </div>
  );
}
