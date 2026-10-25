import { createServerClient } from "@/lib/supabase/server";

export type DbClient = {
  id: string;
  name: string;
  logo_url: string | null;
  sort_order: number;
  is_published: boolean;
  created_at: string;
};

export async function getDbClients(): Promise<DbClient[]> {
  try {
    const supabase = await createServerClient();
    const { data, error } = await supabase
      .from("clients")
      .select("*")
      .eq("is_published", true)
      .order("sort_order", { ascending: true })
      .order("created_at", { ascending: true });

    if (error) {
      console.warn("[db-clients] Error fetching clients:", error.message);
      return [];
    }

    return (data || []) as DbClient[];
  } catch {
    return [];
  }
}
