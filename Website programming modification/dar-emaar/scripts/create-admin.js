const { createClient } = require('@supabase/supabase-js');

const supabaseUrl = 'https://yustlqkzjkwctinhfbjk.supabase.co';
const supabaseServiceKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inl1c3RscWt6amt3Y3RpbmhmYmprIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4ODI3NjYxNiwiZXhwIjoyMTAzODUyNjE2fQ.I53w85CH2SZ8TFjVS3kwD03xjinfZsIgh7LqhYxEZB0';

const supabase = createClient(supabaseUrl, supabaseServiceKey, {
  auth: {
    autoRefreshToken: false,
    persistSession: false
  }
});

async function createAdmin() {
  const { data, error } = await supabase.auth.admin.createUser({
    email: 'admin@dar-emaar.sa',
    password: 'SecurePassword123!',
    email_confirm: true
  });
  if (error) {
    console.error('Error creating user:', error);
  } else {
    console.log('User created successfully:', data.user.id);
  }
}

createAdmin();
