'use client'

import { useState } from 'react'
import { FileText, Download } from 'lucide-react'
import StudentReportModal from '@/components/StudentReportModal'
import * as XLSX from 'xlsx'

export type StudentReport = {
  id: string
  name: string
  className: string
  absentDays: number
  presentDays: number
  absencePercentage: number
  totalDays: number
  absentDates: Date[]
}

export default function ReportsTable({ reports }: { reports: StudentReport[] }) {
  const [selectedStudent, setSelectedStudent] = useState<StudentReport | null>(null)

  const handleExportExcel = () => {
    const data = reports.map(r => ({
      "اسم الطالب": r.name,
      "الفصل": r.className,
      "إجمالي أيام الدراسة": r.totalDays,
      "أيام الحضور": r.presentDays,
      "أيام الغياب": r.absentDays,
      "نسبة الغياب (%)": r.absencePercentage,
    }))

    const worksheet = XLSX.utils.json_to_sheet(data)
    const workbook = XLSX.utils.book_new()
    XLSX.utils.book_append_sheet(workbook, worksheet, "تقرير الغياب")
    
    // Set RTL direction
    worksheet['!dir'] = 'rtl'

    XLSX.writeFile(workbook, "تقرير_الغياب_الشامل.xlsx")
  }

  return (
    <>
      <div className="flex justify-end mb-4">
        <button
          onClick={handleExportExcel}
          className="bg-green-600 hover:bg-green-700 text-white px-6 py-2 rounded-lg font-medium flex items-center gap-2 transition-colors shadow-sm"
        >
          <Download size={18} /> تصدير لإكسل
        </button>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <table className="w-full text-right">
          <thead className="bg-gray-50 border-b border-gray-100">
            <tr>
              <th className="px-6 py-4 text-sm font-semibold text-gray-600">اسم الطالب</th>
              <th className="px-6 py-4 text-sm font-semibold text-gray-600">الفصل</th>
              <th className="px-6 py-4 text-sm font-semibold text-gray-600">أيام الغياب</th>
              <th className="px-6 py-4 text-sm font-semibold text-gray-600">نسبة الغياب</th>
              <th className="px-6 py-4 text-sm font-semibold text-gray-600 text-left">إجراءات</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {reports.length === 0 ? (
              <tr>
                <td colSpan={5} className="px-6 py-8 text-center text-gray-500">
                  لا يوجد طلاب مسجلين لعرض تقاريرهم.
                </td>
              </tr>
            ) : (
              reports.map((report) => (
                <tr key={report.id} className="hover:bg-gray-50/50 transition-colors">
                  <td className="px-6 py-4 font-bold text-gray-900">{report.name}</td>
                  <td className="px-6 py-4 text-gray-600 font-medium">{report.className}</td>
                  <td className="px-6 py-4">
                    <span className="font-bold text-red-600">{report.absentDays}</span> 
                    <span className="text-gray-400 text-sm mx-1">/ {report.totalDays}</span>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`py-1 px-3 rounded-full text-sm font-bold ${
                      report.absencePercentage > 15 ? 'bg-red-100 text-red-700' : 
                      report.absencePercentage > 5 ? 'bg-amber-100 text-amber-700' : 'bg-green-100 text-green-700'
                    }`}>
                      {report.absencePercentage}%
                    </span>
                  </td>
                  <td className="px-6 py-4 text-left">
                    <button
                      onClick={() => setSelectedStudent(report)}
                      className="bg-blue-50 text-blue-600 hover:bg-blue-600 hover:text-white px-4 py-2 rounded-lg text-sm font-medium flex items-center gap-2 transition-colors ml-auto"
                    >
                      <FileText size={16} /> عرض التفاصيل والطباعة
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {selectedStudent && (
        <StudentReportModal student={selectedStudent} onClose={() => setSelectedStudent(null)} />
      )}
    </>
  )
}
