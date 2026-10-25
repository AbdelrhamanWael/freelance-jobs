-- Add contact_email to site_settings
ALTER TABLE public.site_settings 
ADD COLUMN IF NOT EXISTS contact_email TEXT DEFAULT 'info@daremmar.com';
