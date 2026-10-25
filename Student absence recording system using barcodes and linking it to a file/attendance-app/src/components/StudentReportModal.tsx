'use client'

import { useRef, useState } from 'react'
import { FileText, Printer, X } from 'lucide-react'
import { useReactToPrint } from 'react-to-print'

type StudentReport = {
  id: string
  name: string
  className: string
  absentDays: number
  presentDays: number
  absencePercentage: number
  totalDays: number
  absentDates: Date[]
}

export default function StudentReportModal({ student, onClose }: { student: StudentReport, onClose: () => void }) {
  const componentRef = useRef<HTMLDivElement>(null)
  
  const handlePrint = useReactToPrint({
    contentRef: componentRef,
    documentTitle: `تقرير_غياب_${student.name}`,
  })

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-2xl max-h-[90vh] flex flex-col overflow-hidden relative">
        <div className="flex justify-between items-center p-6 border-b border-gray-100 bg-gray-50">
          <h2 className="text-xl font-bold flex items-center gap-2">
            <FileText className="text-blue-600" />
            تقرير غياب طالب
          </h2>
          <div className="flex items-center gap-2">
            <button
              onClick={() => handlePrint()}
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium flex items-center gap-2 transition-colors"
            >
              <Printer size={16} /> طباعة PDF
            </button>
            <button onClick={onClose} className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-200 rounded-lg transition-colors">
              <X size={20} />
            </button>
          </div>
        </div>

        <div className="overflow-y-auto flex-1 p-8 bg-gray-100">
          {/* Printable Area */}
          <div ref={componentRef} className="bg-white p-10 shadow-sm border border-gray-200 min-h-[297mm] w-full rtl">
            
            <div className="text-center mb-10 border-b-2 border-gray-800 pb-6">
              <h1 className="text-3xl font-bold mb-2">إشعار غياب طالب</h1>
              <p className="text-gray-600">العام الدراسي الحالي</p>
            </div>

            <div className="grid grid-cols-2 gap-6 mb-8 text-lg">
              <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                <p className="text-gray-500 text-sm font-bold mb-1">اسم الطالب</p>
                <p className="font-bold text-gray-900">{student.name}</p>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                <p className="text-gray-500 text-sm font-bold mb-1">الفصل</p>
                <p className="font-bold text-gray-900">{student.className}</p>
              </div>
            </div>

            <div className="grid grid-cols-3 gap-4 mb-10 text-center">
              <div className="p-4 border-2 border-blue-100 rounded-xl">
                <p className="text-3xl font-bold text-blue-600 mb-1">{student.totalDays}</p>
                <p className="text-sm font-bold text-gray-600">إجمالي أيام الدراسة</p>
              </div>
              <div className="p-4 border-2 border-red-100 rounded-xl bg-red-50">
                <p className="text-3xl font-bold text-red-600 mb-1">{student.absentDays}</p>
                <p className="text-sm font-bold text-gray-600">أيام الغياب</p>
              </div>
              <div className="p-4 border-2 border-amber-100 rounded-xl">
                <p className="text-3xl font-bold text-amber-600 mb-1">{student.absencePercentage}%</p>
                <p className="text-sm font-bold text-gray-600">نسبة الغياب</p>
              </div>
            </div>

            <div className="mb-10">
              <h3 className="text-xl font-bold mb-4 border-b pb-2">بيان أيام الغياب:</h3>
              {student.absentDates.length === 0 ? (
                <p className="text-gray-500 italic text-center p-4">لم يتم تسجيل أي غياب لهذا الطالب.</p>
              ) : (
                <ul className="list-disc list-inside space-y-2 pr-4 columns-2">
                  {student.absentDates.map((date, i) => (
                    <li key={i} className="text-gray-800 font-medium pb-2">
                      {new Date(date).toLocaleDateString('ar-EG', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
                    </li>
                  ))}
                </ul>
              )}
            </div>

            <div className="mt-20 pt-8 border-t border-gray-300 flex justify-between px-10">
              <div className="text-center">
                <p className="font-bold text-gray-700 mb-8">توقيع ولي الأمر</p>
                <p className="text-gray-400">.................................</p>
              </div>
              <div className="text-center">
                <p className="font-bold text-gray-700 mb-8">إدارة المدرسة</p>
                <p className="text-gray-400">.................................</p>
              </div>
            </div>

          </div>
        </div>
      </div>
    </div>
  )
}
