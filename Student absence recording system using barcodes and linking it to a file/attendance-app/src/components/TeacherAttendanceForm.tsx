'use client'

import { useState } from 'react'
import { submitAttendance } from '@/app/actions/attendance'
import { Check, X, Send } from 'lucide-react'

type Student = { id: string; name: string }

export default function TeacherAttendanceForm({ classId, students }: { classId: string, students: Student[] }) {
  const [absentIds, setAbsentIds] = useState<Set<string>>(new Set())
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [success, setSuccess] = useState(false)

  const toggleStatus = (id: string) => {
    const newSet = new Set(absentIds)
    if (newSet.has(id)) {
      newSet.delete(id)
    } else {
      newSet.add(id)
    }
    setAbsentIds(newSet)
  }

  const handleSubmit = async () => {
    setIsSubmitting(true)
    try {
      await submitAttendance(classId, Array.from(absentIds))
      setSuccess(true)
    } catch (e) {
      console.error(e)
      alert("حدث خطأ أثناء حفظ البيانات")
    }
    setIsSubmitting(false)
  }

  if (success) {
    return (
      <div className="bg-green-50 text-green-700 p-8 rounded-xl text-center shadow-sm border border-green-100">
        <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <Check size={32} className="text-green-600" />
        </div>
        <h2 className="text-2xl font-bold mb-2">تم تسجيل الغياب بنجاح!</h2>
        <p>شكراً لك، تم حفظ البيانات في النظام.</p>
      </div>
    )
  }

  return (
    <div className="pb-24">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-lg font-semibold text-gray-800">قائمة الطلاب ({students.length})</h2>
        <div className="text-sm font-medium bg-gray-100 px-3 py-1 rounded-full text-gray-600">
          الغياب: <span className="text-red-500 font-bold">{absentIds.size}</span>
        </div>
      </div>

      <div className="space-y-3">
        {students.map(student => {
          const isAbsent = absentIds.has(student.id)
          return (
            <div 
              key={student.id}
              onClick={() => toggleStatus(student.id)}
              className={`flex items-center justify-between p-4 rounded-xl border-2 cursor-pointer transition-all ${
                isAbsent ? 'border-red-500 bg-red-50' : 'border-gray-100 bg-white hover:border-gray-200'
              }`}
            >
              <span className={`font-semibold text-lg ${isAbsent ? 'text-red-700' : 'text-gray-900'}`}>
                {student.name}
              </span>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center transition-colors ${
                isAbsent ? 'bg-red-500 text-white' : 'bg-gray-100 text-gray-400'
              }`}>
                {isAbsent ? <X size={18} /> : <Check size={18} />}
              </div>
            </div>
          )
        })}
      </div>

      <div className="fixed bottom-0 left-0 right-0 p-4 bg-white border-t border-gray-200 shadow-[0_-4px_6px_-1px_rgba(0,0,0,0.05)]">
        <button
          onClick={handleSubmit}
          disabled={isSubmitting}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white py-4 rounded-xl font-bold text-lg flex items-center justify-center gap-2 disabled:opacity-70 transition-colors"
        >
          {isSubmitting ? 'جاري الحفظ...' : (
            <>
              <Send size={20} />
              اعتماد غياب اليوم ({absentIds.size} غائب)
            </>
          )}
        </button>
      </div>
    </div>
  )
}
