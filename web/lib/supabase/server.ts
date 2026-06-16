import { createClient } from "@supabase/supabase-js";

/**
 * Server-side Supabase client using the service role key.
 * Bypasses RLS — use only in server components and API routes.
 */
export function createServerClient() {
  return createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.SUPABASE_SERVICE_ROLE_KEY!,
  );
}
