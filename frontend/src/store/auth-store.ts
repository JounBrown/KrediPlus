import { create } from 'zustand';
import type { Session, User } from '@supabase/supabase-js';

import { supabase } from '../lib/supabase';

export type AuthState = {
  session: Session | null;
  user: User | null;
  setSession: (session: Session | null) => void;
  logout: () => Promise<void>;
};

export const useAuthStore = create<AuthState>((set) => ({
  session: null,
  user: null,
  setSession: (session) =>
    set({
      session,
      user: session?.user ?? null,
    }),
  logout: async () => {
    const { error } = await supabase.auth.signOut();

    set({ session: null, user: null });

    if (error) {
      throw error;
    }
  },
}));
