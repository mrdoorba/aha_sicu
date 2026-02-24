import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
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
  const { t } = useTranslation();
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isReauthing, setIsReauthing] = useState(false);

  const isBusy = isLoading || isReauthing;

  // Reset form state when dialog opens
  useEffect(() => {
    if (open) {
      setPassword(''); // eslint-disable-line react-hooks/set-state-in-effect -- intentional reset on open
      setError('');
    }
  }, [open]);

  const handleConfirm = async () => {
    setError('');
    setIsReauthing(true);
    try {
      await reauthenticateUser(password);
    } catch {
      setError(t('passwordConfirm.incorrectPassword'));
      setIsReauthing(false);
      return;
    }
    setIsReauthing(false);
    try {
      await onConfirm();
    } catch {
      setError(t('passwordConfirm.saveFailed'));
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
          <DialogTitle>{t('passwordConfirm.title')}</DialogTitle>
          <DialogDescription>
            {t('passwordConfirm.description')}
          </DialogDescription>
        </DialogHeader>
        <div className="space-y-2">
          <Input
            type="password"
            placeholder={t('passwordConfirm.passwordPlaceholder')}
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
            aria-label={t('passwordConfirm.passwordPlaceholder')}
          />
          {error && (
            <p className="text-sm text-destructive">{error}</p>
          )}
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={handleCancel} disabled={isBusy}>
            {t('common.cancel')}
          </Button>
          <Button onClick={handleConfirm} disabled={!password || isBusy}>
            {isBusy ? t('passwordConfirm.confirming') : t('passwordConfirm.confirm')}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};
