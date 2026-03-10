import type { User } from 'firebase/auth';

export interface AuthService {
  getToken(): Promise<string | null>;
  subscribe(callback: (user: User | null) => void): () => void;
  login(email: string, password: string): Promise<void>;
  logout(): Promise<void>;
}
