const { createClient } = require('@supabase/supabase-js');
require('dotenv').config({ path: '.env.local' });

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY;

if (!supabaseUrl || !supabaseServiceKey) {
  console.error('Missing Supabase URL or Service Role Key in .env.local');
  process.exit(1);
}

const supabase = createClient(supabaseUrl, supabaseServiceKey);

async function resetPassword(newPassword) {
  const targetPassword = newPassword || process.argv[2] || 'DarEmaar@2026!';
  
  // 1. Get user
  const { data: { users }, error: listError } = await supabase.auth.admin.listUsers();
  if (listError || !users || users.length === 0) {
    console.error('Failed to find users:', listError?.message);
    return;
  }

  const adminUser = users.find(u => u.email === 'admin@dar-emaar.sa') || users[0];
  console.log(`Found user: ${adminUser.email} (ID: ${adminUser.id})`);

  // 2. Update password
  const { data, error } = await supabase.auth.admin.updateUserById(adminUser.id, {
    password: targetPassword,
  });

  if (error) {
    console.error('Failed to update password:', error.message);
  } else {
    console.log(`\n========================================`);
    console.log(`SUCCESS! Password has been updated.`);
    console.log(`Email:    ${adminUser.email}`);
    console.log(`Password: ${targetPassword}`);
    console.log(`========================================\n`);
  }
}

resetPassword();

