import { getStudents, addStudent, deleteStudent } from "@/app/actions/student";
import { getClasses } from "@/app/actions/class";
import { Trash2, Plus, UserPlus } from "lucide-react";

export default async function StudentsPage() {
  const students = await getStudents();
  const classes = await getClasses();

  return (
    <div className="max-w-5xl mx-auto">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">إدارة الطلاب</h1>
          <p className="text-gray-500 mt-2">إجمالي الطلاب المسجلين ({students.length})</p>
        </div>
      </div>

      {/* Add Student Form */}
      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 mb-8">
        <h2 className="text-lg font-semibold mb-4 text-gray-800 flex items-center gap-2">
          <UserPlus size={20} className="text-blue-600"/>
          إضافة طالب جديد
        </h2>
        {classes.length === 0 ? (
          <div className="text-amber-600 bg-amber-50 p-4 rounded-lg text-sm border border-amber-200">
            يجب إضافة "فصل دراسي" واحد على الأقل قبل إضافة الطلاب.
          </div>
        ) : (
          <form action={addStudent} className="flex flex-col md:flex-row gap-4 items-end">
            <div className="flex-1 w-full">
              <label className="block text-sm font-medium text-gray-700 mb-1">اسم الطالب رباعي</label>
              <input
                type="text"
                name="name"
                placeholder="أدخل اسم الطالب..."
                required
                className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
              />
            </div>
            <div className="flex-1 w-full">
              <label className="block text-sm font-medium text-gray-700 mb-1">الفصل</label>
              <select
                name="classId"
                required
                className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none bg-white"
              >
                <option value="" disabled selected>اختر الفصل...</option>
                {classes.map(c => (
                  <option key={c.id} value={c.id}>{c.name}</option>
                ))}
              </select>
            </div>
            <button
              type="submit"
              className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-2 rounded-lg font-medium flex items-center justify-center gap-2 transition-colors w-full md:w-auto h-[42px]"
            >
              <Plus size={18} />
              إضافة
            </button>
          </form>
        )}
      </div>

      {/* Students List */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <table className="w-full text-right">
          <thead className="bg-gray-50 border-b border-gray-100">
            <tr>
              <th className="px-6 py-4 text-sm font-semibold text-gray-600">اسم الطالب</th>
              <th className="px-6 py-4 text-sm font-semibold text-gray-600">الفصل</th>
              <th className="px-6 py-4 text-sm font-semibold text-gray-600 text-left">إجراءات</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {students.length === 0 ? (
              <tr>
                <td colSpan={3} className="px-6 py-8 text-center text-gray-500">
                  لا يوجد طلاب مسجلين بعد.
                </td>
              </tr>
            ) : (
              students.map((s) => (
                <tr key={s.id} className="hover:bg-gray-50/50 transition-colors">
                  <td className="px-6 py-4 font-medium text-gray-900">{s.name}</td>
                  <td className="px-6 py-4 text-gray-600">
                    <span className="bg-gray-100 text-gray-700 py-1 px-3 rounded-full text-sm font-medium">
                      {s.class.name}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-left">
                    <form action={async () => {
                      'use server'
                      await deleteStudent(s.id)
                    }}>
                      <button
                        type="submit"
                        className="text-red-500 hover:text-red-700 p-2 hover:bg-red-50 rounded-lg transition-colors"
                        title="حذف الطالب"
                      >
                        <Trash2 size={18} />
                      </button>
                    </form>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
