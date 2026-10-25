"use client";

import { useState, useTransition } from "react";
import { updateLeadStatus, deleteLead } from "@/app/actions/leads";

type Lead = {
  id: string;
  name: string;
  phone: string;
  service: string | null;
  message: string | null;
  source: string;
  status: string;
  created_at: string;
};

const STATUS_OPTIONS = [
  { value: "new", label: "جديد", color: "bg-amber-100 text-amber-700 border-amber-200" },
  { value: "contacted", label: "تم التواصل", color: "bg-blue-100 text-blue-700 border-blue-200" },
  { value: "converted", label: "تحوّل لعميل", color: "bg-green-100 text-green-700 border-green-200" },
  { value: "closed", label: "مغلق", color: "bg-slate-100 text-slate-600 border-slate-200" },
];

const STATUS_FILTERS = [{ value: "", label: "كل الحالات" }, ...STATUS_OPTIONS];

const DATE_FILTERS = [
  { value: "7", label: "آخر 7 أيام" },
  { value: "30", label: "آخر 30 يوماً" },
  { value: "90", label: "آخر 90 يوماً" },
  { value: "", label: "كل الوقت" },
];

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString("ar-SA", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function StatusBadge({
  status,
  id,
  onUpdate,
}: {
  status: string;
  id: string;
  onUpdate: (id: string, s: string) => void;
}) {
  const [open, setOpen] = useState(false);
  const current = STATUS_OPTIONS.find((s) => s.value === status) || STATUS_OPTIONS[0];

  return (
    <div className="relative inline-block text-start">
      <button
        type="button"
        onClick={(e) => {
          e.stopPropagation();
          setOpen(!open);
        }}
        className={`border text-xs font-semibold px-3 py-1.5 rounded-full flex items-center gap-1.5 transition-all ${current.color} hover:opacity-90 cursor-pointer`}
      >
        {current.label}
        <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M19 9l-7 7-7-7" />
        </svg>
      </button>
      {open && (
        <div
          onClick={(e) => e.stopPropagation()}
          className="absolute top-full start-0 mt-1 w-40 bg-white border border-[#E2E8F0] rounded-xl shadow-lg z-20 overflow-hidden py-1"
        >
          {STATUS_OPTIONS.map((opt) => (
            <button
              key={opt.value}
              type="button"
              onClick={() => {
                onUpdate(id, opt.value);
                setOpen(false);
              }}
              className={`w-full text-start px-4 py-2 text-xs font-semibold hover:bg-[#F1F5F9] transition-colors flex items-center justify-between ${
                opt.value === status ? "bg-[#F8FAFC]" : ""
              }`}
            >
              <span className={`inline-block border px-2 py-0.5 rounded-full ${opt.color}`}>
                {opt.label}
              </span>
              {opt.value === status && (
                <svg className="w-3.5 h-3.5 text-[#004B4B]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
                </svg>
              )}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

export default function LeadsTable({ initialLeads }: { initialLeads: Lead[] }) {
  const [leads, setLeads] = useState<Lead[]>(initialLeads);
  const [statusFilter, setStatusFilter] = useState("");
  const [dateFilter, setDateFilter] = useState("");
  const [search, setSearch] = useState("");
  const [selectedLead, setSelectedLead] = useState<Lead | null>(null);
  const [isDeleting, setIsDeleting] = useState<string | null>(null);
  const [, startTransition] = useTransition();

  const handleStatusUpdate = (id: string, newStatus: string) => {
    setLeads((prev) =>
      prev.map((l) => (l.id === id ? { ...l, status: newStatus } : l))
    );
    if (selectedLead && selectedLead.id === id) {
      setSelectedLead((prev) => (prev ? { ...prev, status: newStatus } : null));
    }
    startTransition(async () => {
      try {
        await updateLeadStatus(id, newStatus);
      } catch {
        setLeads(initialLeads);
      }
    });
  };

  const handleDeleteLead = async (id: string, name: string) => {
    if (!confirm(`هل أنت متأكد من رغبتك في حذف طلب "${name}"؟`)) return;
    setIsDeleting(id);
    setLeads((prev) => prev.filter((l) => l.id !== id));
    if (selectedLead?.id === id) setSelectedLead(null);
    try {
      await deleteLead(id);
    } catch {
      alert("حدث خطأ أثناء حذف الطلب، يرجى المحاولة مرة أخرى.");
      setLeads(initialLeads);
    } finally {
      setIsDeleting(null);
    }
  };

  const filtered = leads.filter((lead) => {
    const matchStatus = !statusFilter || lead.status === statusFilter;
    const query = search.trim().toLowerCase();
    const matchSearch =
      !query ||
      lead.name.toLowerCase().includes(query) ||
      lead.phone.toLowerCase().includes(query) ||
      (lead.service || "").toLowerCase().includes(query) ||
      (lead.message || "").toLowerCase().includes(query);

    const matchDate =
      !dateFilter ||
      (() => {
        const d = new Date(lead.created_at);
        const diff = (Date.now() - d.getTime()) / (1000 * 60 * 60 * 24);
        return diff <= parseInt(dateFilter);
      })();

    return matchStatus && matchSearch && matchDate;
  });

  return (
    <div>
      {/* Filters & Search */}
      <div className="bg-white rounded-2xl p-5 shadow-sm border border-[#E2E8F0] mb-5">
        <div className="flex flex-wrap items-center gap-4">
          {/* Search */}
          <div className="flex-1 min-w-56">
            <div className="relative">
              <svg
                className="w-4 h-4 absolute top-1/2 -translate-y-1/2 start-3 text-[#94A3B8]"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="بحث بالاسم، الجوال، الخدمة، أو تفاصيل المشروع..."
                className="form-input-light ps-9 w-full"
              />
            </div>
          </div>

          {/* Status filter */}
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="form-input-light w-40"
          >
            {STATUS_FILTERS.map((f) => (
              <option key={f.value} value={f.value}>
                {f.label}
              </option>
            ))}
          </select>

          {/* Date filter */}
          <select
            value={dateFilter}
            onChange={(e) => setDateFilter(e.target.value)}
            className="form-input-light w-40"
          >
            {DATE_FILTERS.map((f) => (
              <option key={f.value} value={f.value}>
                {f.label}
              </option>
            ))}
          </select>

          <div className="flex items-center text-[#94A3B8] text-sm whitespace-nowrap ms-auto font-medium">
            {filtered.length} طلب
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="bg-white rounded-2xl shadow-sm border border-[#E2E8F0] overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-start">
            <thead>
              <tr className="border-b border-[#E2E8F0] bg-[#F8FAFC]">
                <th className="text-start px-5 py-4 text-xs font-bold text-[#64748B] uppercase tracking-wider">
                  التاريخ
                </th>
                <th className="text-start px-5 py-4 text-xs font-bold text-[#64748B] uppercase tracking-wider">
                  الاسم
                </th>
                <th className="text-start px-5 py-4 text-xs font-bold text-[#64748B] uppercase tracking-wider">
                  الجوال
                </th>
                <th className="text-start px-5 py-4 text-xs font-bold text-[#64748B] uppercase tracking-wider">
                  الخدمة المطلوبة
                </th>
                <th className="text-start px-5 py-4 text-xs font-bold text-[#64748B] uppercase tracking-wider min-w-[260px]">
                  تفاصيل المشروع (اهتمام العميل)
                </th>
                <th className="text-start px-5 py-4 text-xs font-bold text-[#64748B] uppercase tracking-wider">
                  المصدر
                </th>
                <th className="text-start px-5 py-4 text-xs font-bold text-[#64748B] uppercase tracking-wider">
                  الحالة
                </th>
                <th className="text-start px-5 py-4 text-xs font-bold text-[#64748B] uppercase tracking-wider">
                  الإجراءات
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#F1F5F9]">
              {filtered.length === 0 ? (
                <tr>
                  <td colSpan={8} className="text-center py-16 text-[#94A3B8] text-sm">
                    لا توجد طلبات مطابقة للبحث أو التصفية
                  </td>
                </tr>
              ) : (
                filtered.map((lead) => (
                  <tr
                    key={lead.id}
                    onClick={() => setSelectedLead(lead)}
                    className="hover:bg-[#F8FAFC] transition-colors cursor-pointer group"
                  >
                    {/* Date */}
                    <td className="px-5 py-4 text-[#64748B] text-xs whitespace-nowrap">
                      {formatDate(lead.created_at)}
                    </td>

                    {/* Name */}
                    <td className="px-5 py-4 font-bold text-[#1B2A4A] text-sm whitespace-nowrap">
                      {lead.name}
                    </td>

                    {/* Phone */}
                    <td className="px-5 py-4 whitespace-nowrap" onClick={(e) => e.stopPropagation()}>
                      <a
                        href={`tel:${lead.phone}`}
                        dir="ltr"
                        className="text-[#004B4B] font-semibold text-sm hover:underline flex items-center gap-1.5"
                      >
                        <svg className="w-3.5 h-3.5 text-[#64748B]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.948V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"
                          />
                        </svg>
                        {lead.phone}
                      </a>
                    </td>

                    {/* Service */}
                    <td className="px-5 py-4 text-xs font-semibold text-[#1B2A4A] whitespace-nowrap">
                      {lead.service ? (
                        <span className="bg-[#F1F5F9] text-[#1B2A4A] px-2.5 py-1 rounded-md border border-[#E2E8F0]">
                          {lead.service}
                        </span>
                      ) : (
                        <span className="text-[#CBD5E1] font-normal">—</span>
                      )}
                    </td>

                    {/* Project Details (Customer Interest) */}
                    <td className="px-5 py-4 text-sm" onClick={(e) => e.stopPropagation()}>
                      {lead.message ? (
                        <div className="max-w-[280px]">
                          <p
                            className="text-xs text-[#334155] line-clamp-2 leading-relaxed font-normal bg-[#F8FAFC] p-2 rounded-lg border border-[#E2E8F0]"
                            title={lead.message}
                          >
                            {lead.message}
                          </p>
                          <button
                            type="button"
                            onClick={() => setSelectedLead(lead)}
                            className="text-[11px] text-[#004B4B] hover:text-[#003838] font-bold mt-1 inline-flex items-center gap-1 hover:underline cursor-pointer"
                          >
                            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                            </svg>
                            عرض التفاصيل كاملة
                          </button>
                        </div>
                      ) : (
                        <span className="text-[#94A3B8] text-xs font-normal italic">
                          لم يُدخل تفاصيل إضافية
                        </span>
                      )}
                    </td>

                    {/* Source */}
                    <td className="px-5 py-4 whitespace-nowrap">
                      <span className="text-xs text-[#64748B] bg-[#F1F5F9] px-2 py-1 rounded-full border border-[#E2E8F0]">
                        {lead.source === "quote_form" ? "نموذج الموقع" : lead.source}
                      </span>
                    </td>

                    {/* Status */}
                    <td className="px-5 py-4 whitespace-nowrap" onClick={(e) => e.stopPropagation()}>
                      <StatusBadge status={lead.status} id={lead.id} onUpdate={handleStatusUpdate} />
                    </td>

                    {/* Actions */}
                    <td className="px-5 py-4 whitespace-nowrap" onClick={(e) => e.stopPropagation()}>
                      <div className="flex items-center gap-2">
                        {/* WhatsApp */}
                        <a
                          href={`https://wa.me/${lead.phone.replace(/^0/, "966")}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex items-center gap-1 bg-green-50 text-green-700 hover:bg-green-100 border border-green-200 px-2.5 py-1.5 rounded-lg text-xs font-semibold transition-colors"
                          title="تواصل عبر WhatsApp"
                        >
                          <svg className="w-3.5 h-3.5 fill-current" viewBox="0 0 24 24">
                            <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347zM12 0C5.373 0 0 5.373 0 12c0 2.124.554 4.122 1.528 5.858L0 24l6.336-1.508A11.93 11.93 0 0012 24c6.627 0 12-5.373 12-12S18.627 0 12 0zm0 21.818a9.8 9.8 0 01-5.004-1.373l-.36-.213-3.76.896.952-3.653-.235-.375A9.79 9.79 0 012.182 12C2.182 6.58 6.58 2.182 12 2.182S21.818 6.58 21.818 12 17.42 21.818 12 21.818z" />
                          </svg>
                          واتساب
                        </a>

                        {/* View Button */}
                        <button
                          type="button"
                          onClick={() => setSelectedLead(lead)}
                          className="text-[#64748B] hover:text-[#004B4B] bg-[#F1F5F9] hover:bg-[#E2E8F0] p-1.5 rounded-lg transition-colors cursor-pointer"
                          title="عرض تفاصيل الطلب"
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                          </svg>
                        </button>

                        {/* Delete Button */}
                        <button
                          type="button"
                          disabled={isDeleting === lead.id}
                          onClick={() => handleDeleteLead(lead.id, lead.name)}
                          className="text-[#94A3B8] hover:text-red-600 hover:bg-red-50 p-1.5 rounded-lg transition-colors cursor-pointer disabled:opacity-50"
                          title="حذف هذا الطلب"
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                          </svg>
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Lead Details Modal */}
      {selectedLead && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-xs animate-in fade-in duration-200"
          onClick={() => setSelectedLead(null)}
        >
          <div
            className="bg-white rounded-2xl max-w-xl w-full max-h-[90vh] overflow-y-auto shadow-2xl border border-[#E2E8F0] p-6 text-start"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal Header */}
            <div className="flex items-start justify-between pb-4 border-b border-[#E2E8F0]">
              <div>
                <span className="text-xs font-semibold text-[#004B4B] bg-[#004B4B]/10 px-2.5 py-1 rounded-full inline-block mb-1.5">
                  تفاصيل طلب استشارة
                </span>
                <h2 className="text-xl font-black text-[#1B2A4A]">{selectedLead.name}</h2>
                <p className="text-xs text-[#64748B] mt-0.5">
                  تاريخ الإرسال: {formatDate(selectedLead.created_at)}
                </p>
              </div>
              <button
                type="button"
                onClick={() => setSelectedLead(null)}
                className="text-[#94A3B8] hover:text-[#1B2A4A] bg-[#F1F5F9] hover:bg-[#E2E8F0] p-2 rounded-xl transition-colors cursor-pointer"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {/* Modal Body */}
            <div className="py-5 space-y-5">
              {/* Quick Info Grid */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {/* Phone */}
                <div className="bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl p-3.5">
                  <span className="text-xs text-[#64748B] block mb-1">رقم الجوال</span>
                  <div className="flex items-center justify-between">
                    <a
                      href={`tel:${selectedLead.phone}`}
                      dir="ltr"
                      className="font-bold text-[#004B4B] text-base hover:underline"
                    >
                      {selectedLead.phone}
                    </a>
                    <a
                      href={`tel:${selectedLead.phone}`}
                      className="text-xs bg-[#004B4B] text-white px-2 py-1 rounded-md hover:bg-[#003838]"
                    >
                      اتصال
                    </a>
                  </div>
                </div>

                {/* Service */}
                <div className="bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl p-3.5">
                  <span className="text-xs text-[#64748B] block mb-1">الخدمة المطلوبة</span>
                  <p className="font-bold text-[#1B2A4A] text-sm">
                    {selectedLead.service || "لم يتم تحديد خدمة"}
                  </p>
                </div>

                {/* Status */}
                <div className="bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl p-3.5">
                  <span className="text-xs text-[#64748B] block mb-1">حالة الطلب الحالية</span>
                  <StatusBadge
                    status={selectedLead.status}
                    id={selectedLead.id}
                    onUpdate={handleStatusUpdate}
                  />
                </div>

                {/* Source */}
                <div className="bg-[#F8FAFC] border border-[#E2E8F0] rounded-xl p-3.5">
                  <span className="text-xs text-[#64748B] block mb-1">مصدر الطلب</span>
                  <p className="font-semibold text-[#1B2A4A] text-sm">
                    {selectedLead.source === "quote_form" ? "نموذج الموقع الإلكتروني" : selectedLead.source}
                  </p>
                </div>
              </div>

              {/* Project Details Box (Customer Interest) */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="text-sm font-bold text-[#1B2A4A] flex items-center gap-1.5">
                    <svg className="w-4 h-4 text-[#004B4B]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    اهتمام العميل وتفاصيل المشروع (تفاصيل المشروع - اختياري):
                  </label>
                  {selectedLead.message && (
                    <span className="text-[11px] text-green-700 bg-green-50 border border-green-200 px-2 py-0.5 rounded-full font-medium">
                      بيانات متوفرة
                    </span>
                  )}
                </div>

                <div className="bg-[#F9F3EC]/50 border-2 border-[#004B4B]/20 rounded-xl p-4 min-h-[120px]">
                  {selectedLead.message ? (
                    <p className="text-sm text-[#1B2A4A] leading-relaxed whitespace-pre-wrap font-medium">
                      {selectedLead.message}
                    </p>
                  ) : (
                    <div className="flex flex-col items-center justify-center py-6 text-center text-[#94A3B8]">
                      <svg className="w-8 h-8 mb-2 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                      </svg>
                      <p className="text-xs">لم يقم هذا العميل بكتابة تفاصيل إضافية في هذا الحقل عند إرسال النموذج.</p>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Modal Footer */}
            <div className="pt-4 border-t border-[#E2E8F0] flex flex-wrap items-center justify-between gap-3">
              <div className="flex items-center gap-2">
                {/* WhatsApp */}
                <a
                  href={`https://wa.me/${selectedLead.phone.replace(/^0/, "966")}?text=${encodeURIComponent(`مرحباً أستاذ ${selectedLead.name}، نتواصل معك من شركة دار اعمار الغربية بخصوص طلبك (${selectedLead.service || "طلب استشارة"}).`)}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="bg-green-600 hover:bg-green-700 text-white font-bold text-xs px-4 py-2.5 rounded-xl flex items-center gap-2 transition-colors shadow-sm"
                >
                  <svg className="w-4 h-4 fill-current" viewBox="0 0 24 24">
                    <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347zM12 0C5.373 0 0 5.373 0 12c0 2.124.554 4.122 1.528 5.858L0 24l6.336-1.508A11.93 11.93 0 0012 24c6.627 0 12-5.373 12-12S18.627 0 12 0zm0 21.818a9.8 9.8 0 01-5.004-1.373l-.36-.213-3.76.896.952-3.653-.235-.375A9.79 9.79 0 012.182 12C2.182 6.58 6.58 2.182 12 2.182S21.818 6.58 21.818 12 17.42 21.818 12 21.818z" />
                  </svg>
                  مراسلة عبر واتساب
                </a>

                {/* Direct Call */}
                <a
                  href={`tel:${selectedLead.phone}`}
                  className="bg-[#004B4B] hover:bg-[#003838] text-white font-bold text-xs px-4 py-2.5 rounded-xl flex items-center gap-1.5 transition-colors shadow-sm"
                >
                  <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.948V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                  </svg>
                  اتصال هاتفي
                </a>
              </div>

              {/* Close Button */}
              <button
                type="button"
                onClick={() => setSelectedLead(null)}
                className="bg-[#F1F5F9] hover:bg-[#E2E8F0] text-[#1B2A4A] font-bold text-xs px-4 py-2.5 rounded-xl transition-colors cursor-pointer ms-auto"
              >
                إغلاق
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
