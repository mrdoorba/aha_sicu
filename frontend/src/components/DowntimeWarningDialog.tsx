import { AlertTriangle } from 'lucide-react';
import { Trans, useTranslation } from 'react-i18next';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from './ui/dialog';
import { Button } from './ui/button';

interface DowntimeWarningDialogProps {
  open: boolean;
  onDismiss: () => void;
}

export function DowntimeWarningDialog({
  open,
  onDismiss,
}: DowntimeWarningDialogProps) {
  const { t } = useTranslation();
  return (
    <Dialog open={open} onOpenChange={(isOpen) => { if (!isOpen) onDismiss(); }}>
      <DialogContent showCloseButton={false}>
        <DialogHeader>
          <div className="flex justify-center mb-2">
            <AlertTriangle className="size-10 text-amber-500" />
          </div>
          <DialogTitle className="text-center">
            {t('downtime.title')}
          </DialogTitle>
          <DialogDescription className="text-center">
            <Trans
              i18nKey="downtime.description"
              components={{ bold: <strong className="text-foreground" /> }}
            />
          </DialogDescription>
        </DialogHeader>
        <DialogFooter className="sm:justify-center">
          <Button onClick={onDismiss}>{t('downtime.dismiss')}</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
