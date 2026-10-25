"use server";

import { createServerClient, checkAuth } from "@/lib/supabase/server";
import { revalidatePath } from "next/cache";
import nodemailer from "nodemailer";
import { getSettings } from "@/lib/settings";

export type LeadFormState = {
  success: boolean;
  error?: string;
};

export async function submitLead(
  prevState: LeadFormState,
  formData: FormData
): Promise<LeadFormState> {
  const name = (formData.get("name") as string)?.trim();
  const phone = (formData.get("phone") as string)?.trim();
  const service = (formData.get("service") as string)?.trim();
  const message = (formData.get("message") as string)?.trim();
  const source = (formData.get("source") as string) || "quote_form";

  // Server-side validation
  if (!name || name.length < 2) {
    return { success: false, error: "يرجى إدخال الاسم الكامل" };
  }

  const phoneRegex = /^(05|5)\d{8}$/;
  const cleanPhone = phone?.replace(/\s|-/g, "");
  if (!cleanPhone || !phoneRegex.test(cleanPhone)) {
    return { success: false, error: "يرجى إدخال رقم جوال سعودي صحيح (مثال: 05xxxxxxxx)" };
  }

  const supabase = await createServerClient();

  const { error } = await supabase.from("leads").insert({
    name,
    phone: cleanPhone,
    service: service || null,
    message: message || null,
    source,
  });

  if (error) {
    console.error("Supabase insert error:", error);
    return { success: false, error: "حدث خطأ أثناء إرسال الطلب. يرجى المحاولة مرة أخرى." };
  }

  // Fetch settings to get dynamic contact_email
  const settings = await getSettings();
  const companyEmail = settings.contact_email || "info@daremmar.com";

  // Send Email Notification using Nodemailer
  if (process.env.SMTP_HOST && process.env.SMTP_USER && process.env.SMTP_PASS) {
    try {
      const transporter = nodemailer.createTransport({
        host: process.env.SMTP_HOST,
        port: parseInt(process.env.SMTP_PORT || "587"),
        secure: process.env.SMTP_PORT === "465",
        auth: {
          user: process.env.SMTP_USER,
          pass: process.env.SMTP_PASS,
        },
      });

      const fromEmail = process.env.SMTP_FROM || process.env.SMTP_USER;
      
      const emailHtml = `
        <div dir="rtl" style="font-family: Arial, sans-serif; color: #1B2A4A; max-width: 600px; margin: 0 auto; border: 1px solid #E2E8F0; border-radius: 12px; overflow: hidden;">
          <div style="background-color: #004B4B; padding: 24px; text-align: center;">
            <h2 style="color: #ffffff; margin: 0; font-size: 24px;">طلب استشارة جديد</h2>
          </div>
          <div style="padding: 32px; background-color: #F9F3EC;">
            <p style="font-size: 16px; margin-bottom: 24px;">لقد تلقيت للتو طلباً جديداً من الموقع الإلكتروني:</p>
            
            <table style="width: 100%; border-collapse: collapse;">
              <tr>
                <td style="padding: 12px 0; border-bottom: 1px solid #E2E8F0; width: 120px;"><strong>الاسم:</strong></td>
                <td style="padding: 12px 0; border-bottom: 1px solid #E2E8F0;">${name}</td>
              </tr>
              <tr>
                <td style="padding: 12px 0; border-bottom: 1px solid #E2E8F0;"><strong>رقم الجوال:</strong></td>
                <td style="padding: 12px 0; border-bottom: 1px solid #E2E8F0;" dir="ltr"><a href="tel:${cleanPhone}">${cleanPhone}</a></td>
              </tr>
              <tr>
                <td style="padding: 12px 0; border-bottom: 1px solid #E2E8F0;"><strong>الخدمة المطلوبة:</strong></td>
                <td style="padding: 12px 0; border-bottom: 1px solid #E2E8F0;">${service || "غير محدد"}</td>
              </tr>
              <tr>
                <td style="padding: 12px 0; border-bottom: 1px solid #E2E8F0;"><strong>المصدر:</strong></td>
                <td style="padding: 12px 0; border-bottom: 1px solid #E2E8F0;">${source}</td>
              </tr>
            </table>

            <div style="margin-top: 24px;">
              <strong>تفاصيل المشروع:</strong>
              <div style="background-color: #ffffff; padding: 16px; border-radius: 8px; margin-top: 8px; border: 1px solid #E2E8F0; white-space: pre-wrap;">${message || "لا توجد تفاصيل إضافية"}</div>
            </div>
            
            <div style="margin-top: 32px; text-align: center;">
              <a href="${process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000"}/dashboard/leads" style="background-color: #004B4B; color: #ffffff; text-decoration: none; padding: 12px 24px; border-radius: 6px; font-weight: bold; display: inline-block;">عرض جميع الطلبات في لوحة التحكم</a>
            </div>
          </div>
        </div>
      `;

      await transporter.sendMail({
        from: `"Dar Emaar" <${fromEmail}>`,
        to: companyEmail,
        subject: `طلب جديد من ${name}`,
        html: emailHtml,
      });
      
      console.log("Email notification sent successfully via SMTP.");
    } catch (emailError: any) {
      console.error("Failed to send email notification:", emailError);
      return { success: false, error: "SMTP Error: " + emailError.message };
    }
  } else {
    console.warn("SMTP variables are not fully set in .env. Email notification was skipped.");
    return { success: false, error: "SMTP Variables Missing" };
  }

  revalidatePath("/dashboard");
  revalidatePath("/dashboard/leads");

  return { success: true };
}

export async function updateLeadStatus(id: string, status: string) {
  await checkAuth();
  const supabase = await createServerClient();

  const { error } = await supabase
    .from("leads")
    .update({ status })
    .eq("id", id);

  if (error) throw new Error(error.message);

  revalidatePath("/dashboard");
  revalidatePath("/dashboard/leads");
}

export async function deleteLead(id: string) {
  await checkAuth();
  const supabase = await createServerClient();

  const { error } = await supabase
    .from("leads")
    .delete()
    .eq("id", id);

  if (error) throw new Error(error.message);

  revalidatePath("/dashboard");
  revalidatePath("/dashboard/leads");
}

