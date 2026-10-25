"use client";

import { useMemo } from "react";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell,
  PieChart, Pie, Legend
} from "recharts";

type Lead = {
  id: string;
  status: string;
  source: string;
  service: string | null;
  created_at: string;
};

type Props = { leads: Lead[] };

const STATUS_LABELS: Record<string, string> = {
  new: "جديد",
  contacted: "تم التواصل",
  converted: "تحوّل لعميل",
  closed: "مغلق",
};

const STATUS_COLORS: Record<string, string> = {
  new: "#C9A227",
  contacted: "#3B82F6",
  converted: "#16A34A",
  closed: "#94A3B8",
};

const PIE_COLORS = ["#C9A227", "#3B82F6", "#16A34A", "#F59E0B", "#8B5CF6", "#EC4899", "#14B8A6", "#64748B"];

function StatCard({ label, value, sub, color }: { label: string; value: number | string; sub?: string; color: string }) {
  return (
    <div className="bg-white rounded-2xl p-6 shadow-sm border border-[#E2E8F0]">
      <div className={`w-10 h-10 rounded-xl flex items-center justify-center mb-4`} style={{ backgroundColor: color + "20" }}>
        <div className="w-4 h-4 rounded-full" style={{ backgroundColor: color }} />
      </div>
      <p className="text-3xl font-black text-[#1B2A4A]">{value}</p>
      <p className="text-[#64748B] text-sm font-medium mt-1">{label}</p>
      {sub && <p className="text-[#94A3B8] text-xs mt-0.5">{sub}</p>}
    </div>
  );
}

// Generate last-N-days labels
function getLast30Days() {
  const days = [];
  for (let i = 29; i >= 0; i--) {
    const d = new Date();
    d.setDate(d.getDate() - i);
    days.push(d.toISOString().split("T")[0]);
  }
  return days;
}

export default function DashboardStats({ leads }: Props) {
  const now = new Date();

  const stats = useMemo(() => {
    const total = leads.length;
    const thisWeek = leads.filter((l) => {
      const d = new Date(l.created_at);
      const diff = (now.getTime() - d.getTime()) / (1000 * 60 * 60 * 24);
      return diff <= 7;
    }).length;
    const newLeads = leads.filter((l) => l.status === "new").length;
    const converted = leads.filter((l) => l.status === "converted").length;
    const convRate = total > 0 ? Math.round((converted / total) * 100) : 0;
    return { total, thisWeek, newLeads, converted, convRate };
  }, [leads]);

  // Lead volume by day (last 30 days)
  const volumeData = useMemo(() => {
    const days = getLast30Days();
    const countByDay: Record<string, number> = {};
    days.forEach((d) => (countByDay[d] = 0));
    leads.forEach((l) => {
      const d = l.created_at.split("T")[0];
      if (d in countByDay) countByDay[d]++;
    });
    return days.map((d) => ({
      date: d.slice(5), // MM-DD
      count: countByDay[d],
    }));
  }, [leads]);

  // Leads by service
  const serviceData = useMemo(() => {
    const counts: Record<string, number> = {};
    leads.forEach((l) => {
      const key = l.service || "غير محدد";
      counts[key] = (counts[key] || 0) + 1;
    });
    return Object.entries(counts)
      .map(([name, value]) => ({ name, value }))
      .sort((a, b) => b.value - a.value)
      .slice(0, 6);
  }, [leads]);

  // Leads by status
  const statusData = useMemo(() => {
    const counts: Record<string, number> = {};
    leads.forEach((l) => {
      counts[l.status] = (counts[l.status] || 0) + 1;
    });
    return Object.entries(counts).map(([status, value]) => ({
      name: STATUS_LABELS[status] || status,
      value,
      status,
    }));
  }, [leads]);

  return (
    <div className="space-y-8">

      {/* KPI Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard label="إجمالي الطلبات" value={stats.total} color="#C9A227" />
        <StatCard label="طلبات هذا الأسبوع" value={stats.thisWeek} sub="آخر 7 أيام" color="#3B82F6" />
        <StatCard label="طلبات جديدة" value={stats.newLeads} sub="بانتظار التواصل" color="#F59E0B" />
        <StatCard label="معدل التحويل" value={`${stats.convRate}%`} sub={`${stats.converted} عميل محوّل`} color="#16A34A" />
      </div>

      {/* Charts row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

        {/* Volume chart — 2/3 width */}
        <div className="lg:col-span-2 bg-white rounded-2xl p-6 shadow-sm border border-[#E2E8F0]">
          <h2 className="text-base font-bold text-[#1B2A4A] mb-6">حجم الطلبات — آخر 30 يوماً</h2>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={volumeData} barSize={12}>
              <XAxis dataKey="date" tick={{ fontSize: 10, fill: "#94A3B8" }} tickLine={false} axisLine={false} />
              <YAxis allowDecimals={false} tick={{ fontSize: 10, fill: "#94A3B8" }} tickLine={false} axisLine={false} />
              <Tooltip
                contentStyle={{ background: "#1B2A4A", border: "none", borderRadius: "8px", color: "#fff", fontSize: "12px" }}
                cursor={{ fill: "rgba(201,162,39,0.08)" }}
              />
              <Bar dataKey="count" name="طلبات" radius={[4, 4, 0, 0]}>
                {volumeData.map((_, i) => (
                  <Cell key={i} fill={i === volumeData.length - 1 ? "#C9A227" : "#1B2A4A"} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Status donut — 1/3 width */}
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-[#E2E8F0]">
          <h2 className="text-base font-bold text-[#1B2A4A] mb-6">توزيع الحالات</h2>
          {statusData.length === 0 ? (
            <div className="h-[220px] flex items-center justify-center text-[#94A3B8] text-sm">
              لا توجد بيانات بعد
            </div>
          ) : (
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie
                  data={statusData}
                  cx="50%"
                  cy="50%"
                  innerRadius={55}
                  outerRadius={80}
                  paddingAngle={3}
                  dataKey="value"
                >
                  {statusData.map((entry, i) => (
                    <Cell key={i} fill={STATUS_COLORS[entry.status] || PIE_COLORS[i]} />
                  ))}
                </Pie>
                <Legend
                  iconType="circle"
                  iconSize={8}
                  formatter={(value) => <span style={{ fontSize: "11px", color: "#64748B" }}>{value}</span>}
                />
                <Tooltip
                  contentStyle={{ background: "#1B2A4A", border: "none", borderRadius: "8px", color: "#fff", fontSize: "12px" }}
                />
              </PieChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>

      {/* Service breakdown */}
      <div className="bg-white rounded-2xl p-6 shadow-sm border border-[#E2E8F0]">
        <h2 className="text-base font-bold text-[#1B2A4A] mb-6">الطلبات حسب نوع الخدمة</h2>
        {serviceData.length === 0 ? (
          <p className="text-[#94A3B8] text-sm text-center py-8">لا توجد بيانات بعد — ستظهر البيانات عند وصول أول طلب</p>
        ) : (
          <div className="space-y-3">
            {serviceData.map((item, i) => {
              const max = serviceData[0].value;
              const pct = Math.round((item.value / max) * 100);
              return (
                <div key={item.name} className="flex items-center gap-4">
                  <span className="text-[#64748B] text-sm w-44 flex-shrink-0 truncate">{item.name}</span>
                  <div className="flex-1 bg-[#F1F5F9] rounded-full h-2">
                    <div
                      className="h-2 rounded-full transition-all duration-500"
                      style={{ width: `${pct}%`, backgroundColor: PIE_COLORS[i % PIE_COLORS.length] }}
                    />
                  </div>
                  <span className="text-[#1B2A4A] font-bold text-sm w-6 text-end flex-shrink-0">{item.value}</span>
                </div>
              );
            })}
          </div>
        )}
      </div>

    </div>
  );
}
