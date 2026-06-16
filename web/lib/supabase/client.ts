import { createClient } from "@supabase/supabase-js";

/**
 * Browser-side Supabase client using the public anon key.
 * Subject to RLS policies — never use for privileged operations.
 */
export function createBrowserClient() {
  return createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
  );
}
