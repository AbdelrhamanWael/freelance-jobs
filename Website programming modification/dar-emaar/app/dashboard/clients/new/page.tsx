import ClientForm from "@/components/dashboard/ClientForm";

export default function NewClientPage() {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-[#1B2A4A]">إضافة عميل جديد</h1>
      <ClientForm />
    </div>
  );
}
