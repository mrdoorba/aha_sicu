import { useState, useEffect } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '../ui/dialog';
import { Input } from '../ui/input';
import { Button } from '../ui/button';
import { reauthenticateUser } from '../../firebase/auth';

interface PasswordConfirmDialogProps {
  open: boolean;
  onConfirm: () => Promise<void>;
  onCancel: () => void;
  isLoading: boolean;
}

export const PasswordConfirmDialog = ({
  open,
  onConfirm,
  onCancel,
  isLoading,
}: PasswordConfirmDialogProps) => {
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isReauthing, setIsReauthing] = useState(false);

  const isBusy = isLoading || isReauthing;

  useEffect(() => {
    if (open) {
      setPassword('');
      setError('');
    }
  }, [open]);

  const handleConfirm = async () => {
    setError('');
    setIsReauthing(true);
    try {
      await reauthenticateUser(password);
    } catch {
      setError('Incorrect password');
      setIsReauthing(false);
      return;
    }
    setIsReauthing(false);
    try {
      await onConfirm();
    } catch {
      setError('Failed to save changes. Please try again.');
    }
  };

  const handleCancel = () => {
    setPassword('');
    setError('');
    onCancel();
  };

  const handleOpenChange = (isOpen: boolean) => {
    if (!isOpen) {
      handleCancel();
    }
  };

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Confirm Password</DialogTitle>
          <DialogDescription>
            Enter your password to confirm scoring rule changes.
          </DialogDescription>
        </DialogHeader>
        <div className="space-y-2">
          <Input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => {
              setPassword(e.target.value);
              setError('');
            }}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && password && !isBusy) {
                handleConfirm();
              }
            }}
            disabled={isBusy}
            aria-label="Password"
          />
          {error && (
            <p className="text-sm text-destructive">{error}</p>
          )}
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={handleCancel} disabled={isBusy}>
            Cancel
          </Button>
          <Button onClick={handleConfirm} disabled={!password || isBusy}>
            {isBusy ? 'Confirming...' : 'Confirm'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};
