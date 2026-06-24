import {
  getCurrentUserToken,
  loginWithEmail,
  logout,
  subscribeToAuthChanges,
} from '../firebase/auth';
import type { User } from 'firebase/auth';

export const firebaseAuthService = {
  getToken: () => getCurrentUserToken(),
  subscribe: (callback: (user: User | null) => void) =>
    subscribeToAuthChanges(callback),
  login: async (email: string, password: string) => {
    await loginWithEmail(email, password);
  },
  logout: () => logout(),
};
