import { getClasses } from "@/app/actions/class";
import QRCodeDisplay from "@/components/QRCodeDisplay";
import PrintButton from "@/components/PrintButton";
import { headers } from "next/headers";

export default async function QRCodePage() {
  const classes = await getClasses();
  
  // Get base URL for generating absolute links
  const headersList = await headers();
  const host = headersList.get("host") || "localhost:3000";
  const protocol = process.env.NODE_ENV === "development" ? "http" : "https";
  const baseUrl = `${protocol}://${host}`;

  return (
    <div className="max-w-5xl mx-auto">
      <div className="flex justify-between items-center mb-8 print:hidden">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">رموز QR للفصول</h1>
          <p className="text-gray-500 mt-2">قم بطباعة هذه الرموز وتوزيعها على المعلمين</p>
        </div>
        <PrintButton />
      </div>

      {classes.length === 0 ? (
        <div className="bg-white p-8 rounded-xl shadow-sm border border-gray-100 text-center print:hidden">
          <p className="text-gray-500">لا توجد فصول مضافة. الرجاء إضافة فصول أولاً لتوليد الرموز.</p>
        </div>
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-8 print:grid-cols-3 print:gap-4">
          {classes.map((c) => (
            <div key={c.id} className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 flex flex-col items-center text-center print:border-gray-300 print:shadow-none break-inside-avoid">
              <h3 className="text-xl font-bold text-gray-900 mb-4">{c.name}</h3>
              <QRCodeDisplay text={`${baseUrl}/t/${c.id}`} />
              <p className="text-sm text-gray-500 mt-4">امسح الرمز لتسجيل الحضور</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
