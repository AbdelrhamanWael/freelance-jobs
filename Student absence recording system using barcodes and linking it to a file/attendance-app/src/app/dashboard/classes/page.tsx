import { getClasses, addClass, deleteClass } from "@/app/actions/class";
import { Trash2, Plus } from "lucide-react";

export default async function ClassesPage() {
  const classes = await getClasses();

  return (
    <div className="max-w-4xl mx-auto">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">الفصول الدراسية</h1>
          <p className="text-gray-500 mt-2">إدارة الفصول في النظام (إجمالي {classes.length})</p>
        </div>
      </div>

      {/* Add Class Form */}
      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 mb-8">
        <h2 className="text-lg font-semibold mb-4 text-gray-800">إضافة فصل جديد</h2>
        <form action={addClass} className="flex gap-4">
          <input
            type="text"
            name="name"
            placeholder="اسم الفصل (مثال: أول أ)"
            required
            className="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
          />
          <button
            type="submit"
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-medium flex items-center gap-2 transition-colors"
          >
            <Plus size={18} />
            إضافة
          </button>
        </form>
      </div>

      {/* Classes List */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <table className="w-full text-right">
          <thead className="bg-gray-50 border-b border-gray-100">
            <tr>
              <th className="px-6 py-4 text-sm font-semibold text-gray-600">اسم الفصل</th>
              <th className="px-6 py-4 text-sm font-semibold text-gray-600">عدد الطلاب</th>
              <th className="px-6 py-4 text-sm font-semibold text-gray-600 text-left">إجراءات</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {classes.length === 0 ? (
              <tr>
                <td colSpan={3} className="px-6 py-8 text-center text-gray-500">
                  لا توجد فصول مضافة بعد.
                </td>
              </tr>
            ) : (
              classes.map((c) => (
                <tr key={c.id} className="hover:bg-gray-50/50 transition-colors">
                  <td className="px-6 py-4 font-medium text-gray-900">{c.name}</td>
                  <td className="px-6 py-4 text-gray-600">
                    <span className="bg-blue-50 text-blue-700 py-1 px-3 rounded-full text-sm font-medium">
                      {c._count.students} طالب
                    </span>
                  </td>
                  <td className="px-6 py-4 text-left">
                    <form action={async () => {
                      'use server'
                      await deleteClass(c.id)
                    }}>
                      <button
                        type="submit"
                        className="text-red-500 hover:text-red-700 p-2 hover:bg-red-50 rounded-lg transition-colors"
                        title="حذف الفصل"
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
