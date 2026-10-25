import Link from "next/link";
import { Users, BookOpen, QrCode, FileText } from "lucide-react";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-h-screen bg-gray-50">
      {/* Sidebar */}
      <aside className="w-64 bg-white border-l border-gray-200 flex-shrink-0 hidden md:block">
        <div className="p-6">
          <h1 className="text-2xl font-bold text-blue-600">نظام الغياب</h1>
          <p className="text-sm text-gray-500 mt-1">لوحة الإدارة</p>
        </div>
        <nav className="mt-6 px-4 space-y-2">
          <Link
            href="/dashboard/classes"
            className="flex items-center gap-3 px-4 py-3 text-gray-700 hover:bg-blue-50 hover:text-blue-600 rounded-lg transition-colors"
          >
            <BookOpen size={20} />
            <span className="font-medium">الفصول الدراسية</span>
          </Link>
          <Link
            href="/dashboard/students"
            className="flex items-center gap-3 px-4 py-3 text-gray-700 hover:bg-blue-50 hover:text-blue-600 rounded-lg transition-colors"
          >
            <Users size={20} />
            <span className="font-medium">الطلاب</span>
          </Link>
          <Link
            href="/dashboard/qr"
            className="flex items-center gap-3 px-4 py-3 text-gray-700 hover:bg-blue-50 hover:text-blue-600 rounded-lg transition-colors"
          >
            <QrCode size={20} />
            <span className="font-medium">توليد QR Codes</span>
          </Link>
          <Link
            href="/dashboard/reports"
            className="flex items-center gap-3 px-4 py-3 text-gray-700 hover:bg-blue-50 hover:text-blue-600 rounded-lg transition-colors"
          >
            <FileText size={20} />
            <span className="font-medium">تقارير الغياب</span>
          </Link>
        </nav>
      </aside>

      {/* Main Content */}
      <main className="flex-1 p-8 overflow-y-auto">
        {children}
      </main>
    </div>
  );
}
