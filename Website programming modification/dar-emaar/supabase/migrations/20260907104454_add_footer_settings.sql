ALTER TABLE public.site_settings 
ADD COLUMN IF NOT EXISTS phone TEXT DEFAULT '+966 50 000 0000',
ADD COLUMN IF NOT EXISTS address TEXT DEFAULT 'المملكة العربية السعودية — جدة، حي الواجهة',
ADD COLUMN IF NOT EXISTS working_hours TEXT DEFAULT 'السبت – الخميس: 8ص – 6م',
ADD COLUMN IF NOT EXISTS instagram TEXT DEFAULT '#',
ADD COLUMN IF NOT EXISTS twitter TEXT DEFAULT '#',
ADD COLUMN IF NOT EXISTS whatsapp TEXT DEFAULT 'https://wa.me/966500000000',
ADD COLUMN IF NOT EXISTS footer_description TEXT DEFAULT 'شركة رائدة في مجال المقاولات العامة تأسست عام 2009، تقدم حلولاً إنشائية متكاملة بجودة عالية وكفاءة محترفة.';
