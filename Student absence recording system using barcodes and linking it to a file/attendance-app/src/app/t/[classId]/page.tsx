import prisma from "@/lib/prisma"
import TeacherAttendanceForm from "@/components/TeacherAttendanceForm"
import { notFound } from "next/navigation"

export default async function TeacherClassPage({ params }: { params: Promise<{ classId: string }> }) {
  const { classId } = await params

  const classData = await prisma.class.findUnique({
    where: { id: classId },
    include: {
      students: {
        orderBy: { name: 'asc' }
      }
    }
  })

  if (!classData) {
    notFound()
  }

  const today = new Date().toLocaleDateString('ar-EG', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })

  return (
    <div className="min-h-screen bg-gray-50 pb-20">
      <div className="bg-blue-600 text-white p-6 rounded-b-3xl shadow-md mb-6">
        <h1 className="text-2xl font-bold mb-1">تسجيل الغياب</h1>
        <div className="flex justify-between items-end mt-4">
          <div>
            <p className="text-blue-100 text-sm">الفصل</p>
            <p className="text-xl font-bold">{classData.name}</p>
          </div>
          <div className="text-right">
            <p className="text-blue-100 text-sm">تاريخ اليوم</p>
            <p className="font-medium text-sm">{today}</p>
          </div>
        </div>
      </div>

      <div className="px-4">
        <div className="bg-blue-50 border border-blue-100 text-blue-800 p-4 rounded-xl mb-6 text-sm flex gap-3">
          <div className="text-xl">ℹ️</div>
          <p>
            القائمة بالأسفل لجميع طلاب الفصل. اضغط على اسم الطالب 
            <span className="font-bold text-red-600 mx-1">الغائب فقط</span> 
            لتحويل حالته للون الأحمر، ثم اضغط على زر الاعتماد بالأسفل.
          </p>
        </div>

        <TeacherAttendanceForm classId={classId} students={classData.students} />
      </div>
    </div>
  )
}
