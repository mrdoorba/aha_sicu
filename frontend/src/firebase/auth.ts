import {
  signInWithEmailAndPassword,
  signOut,
  onAuthStateChanged,
  EmailAuthProvider,
  reauthenticateWithCredential,
  type User,
} from 'firebase/auth';
import { firebaseAuth } from './config';

export const loginWithEmail = async (email: string, password: string) => {
  return signInWithEmailAndPassword(firebaseAuth, email, password);
};

export const reauthenticateUser = async (password: string): Promise<void> => {
  const user = firebaseAuth.currentUser;
  if (!user || !user.email) {
    throw new Error('No authenticated user found');
  }
  const credential = EmailAuthProvider.credential(user.email, password);
  await reauthenticateWithCredential(user, credential);
};

export const logout = async () => {
  return signOut(firebaseAuth);
};

export const subscribeToAuthChanges = (
  callback: (user: User | null) => void
) => {
  return onAuthStateChanged(firebaseAuth, callback);
};

export const getCurrentUserToken = async (): Promise<string | null> => {
  const user = firebaseAuth.currentUser;
  if (!user) return null;
  return user.getIdToken();
};
