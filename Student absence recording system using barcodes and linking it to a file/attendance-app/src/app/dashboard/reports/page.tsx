import { getStudentsReport } from "@/app/actions/report";
import ReportsTable from "./ReportsTable";
import { Download } from "lucide-react";

export default async function ReportsPage() {
  const reports = await getStudentsReport();

  return (
    <div className="max-w-5xl mx-auto">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">تقارير الغياب</h1>
          <p className="text-gray-500 mt-2">متابعة غياب الطلاب وإصدار الإشعارات</p>
        </div>
        <button
          className="bg-green-600 hover:bg-green-700 text-white px-6 py-2 rounded-lg font-medium flex items-center gap-2 transition-colors shadow-sm"
        >
          <Download size={18} /> تصدير لإكسل
        </button>
      </div>

      <div className="mb-6 bg-blue-50 border border-blue-100 p-4 rounded-xl flex gap-3">
        <div className="text-xl">💡</div>
        <p className="text-sm text-blue-800">
          هذا الجدول يوضح الإجمالي العام لغياب كل طالب خلال العام الدراسي. اضغط على زر "عرض التفاصيل والطباعة" لاستخراج وطباعة تقرير PDF مفصل لتقديمه لولي الأمر.
        </p>
      </div>

      <ReportsTable reports={reports} />
    </div>
  );
}
