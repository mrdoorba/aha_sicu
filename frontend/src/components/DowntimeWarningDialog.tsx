import { AlertTriangle } from 'lucide-react';
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
  return (
    <Dialog open={open} onOpenChange={(isOpen) => { if (!isOpen) onDismiss(); }}>
      <DialogContent showCloseButton={false}>
        <DialogHeader>
          <div className="flex justify-center mb-2">
            <AlertTriangle className="size-10 text-amber-500" />
          </div>
          <DialogTitle className="text-center">
            Sistem Tidak Tersedia
          </DialogTitle>
          <DialogDescription className="text-center">
            Sistem mungkin sedang di luar jam operasional. Jam operasional
            database adalah <strong className="text-foreground">08:00 – 18:30 WIB</strong>.
            Silakan coba lagi dalam jam tersebut.
          </DialogDescription>
        </DialogHeader>
        <DialogFooter className="sm:justify-center">
          <Button onClick={onDismiss}>Mengerti</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
