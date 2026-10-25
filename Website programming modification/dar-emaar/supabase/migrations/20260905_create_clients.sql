-- Create the clients table
CREATE TABLE IF NOT EXISTS public.clients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    logo_url TEXT,
    sort_order INTEGER DEFAULT 0,
    is_published BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Enable RLS
ALTER TABLE public.clients ENABLE ROW LEVEL SECURITY;

-- Allow public read access to published clients
CREATE POLICY "Public clients are viewable by everyone" ON public.clients
    FOR SELECT USING (is_published = true);

-- Allow authenticated users (admins) full access
CREATE POLICY "Admins have full access to clients" ON public.clients
    FOR ALL USING (auth.role() = 'authenticated');
    
-- Ensure the storage bucket exists for client logos
INSERT INTO storage.buckets (id, name, public) 
VALUES ('clients', 'clients', true)
ON CONFLICT (id) DO NOTHING;

-- Storage policies for the 'clients' bucket
CREATE POLICY "Public Access to clients images" ON storage.objects
    FOR SELECT USING (bucket_id = 'clients');

CREATE POLICY "Admins can upload clients images" ON storage.objects
    FOR INSERT WITH CHECK (bucket_id = 'clients' AND auth.role() = 'authenticated');

CREATE POLICY "Admins can update clients images" ON storage.objects
    FOR UPDATE USING (bucket_id = 'clients' AND auth.role() = 'authenticated');

CREATE POLICY "Admins can delete clients images" ON storage.objects
    FOR DELETE USING (bucket_id = 'clients' AND auth.role() = 'authenticated');
