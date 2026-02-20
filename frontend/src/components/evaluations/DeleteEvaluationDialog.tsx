import { useState } from 'react';
import { Copy, ClipboardCheck, Loader2 } from 'lucide-react';
import { toast } from 'sonner';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '../ui/dialog';
import { Button } from '../ui/button';
import { Input } from '../ui/input';

interface DeleteEvaluationDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  brandName: string;
  onConfirm: () => void;
  isDeleting: boolean;
}

export function DeleteEvaluationDialog({
  open,
  onOpenChange,
  brandName,
  onConfirm,
  isDeleting,
}: DeleteEvaluationDialogProps) {
  const [confirmInput, setConfirmInput] = useState('');
  const [copied, setCopied] = useState(false);

  const isMatch = confirmInput.toLowerCase() === brandName.toLowerCase();

  const handleCopyBrandName = async () => {
    try {
      await navigator.clipboard.writeText(brandName);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      toast.error('Gagal menyalin nama brand');
    }
  };

  const handleOpenChange = (nextOpen: boolean) => {
    if (!nextOpen) {
      setConfirmInput('');
      setCopied(false);
    }
    onOpenChange(nextOpen);
  };

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Hapus Evaluasi</DialogTitle>
          <DialogDescription>
            Tindakan ini bersifat permanen dan tidak dapat dibatalkan.
            Evaluasi akan dihapus secara permanen dari database.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-2">
          <div>
            <p className="text-sm text-muted-foreground">
              Ketik nama brand untuk konfirmasi:
            </p>
            <div className="mt-1 flex items-center gap-2">
              <span className="rounded bg-muted px-2 py-1 font-mono text-sm font-medium">
                {brandName}
              </span>
              <Button
                variant="ghost"
                size="sm"
                className="size-7 p-0"
                onClick={handleCopyBrandName}
                aria-label="Salin nama brand"
              >
                {copied
                  ? <ClipboardCheck className="size-4" aria-hidden="true" />
                  : <Copy className="size-4" aria-hidden="true" />
                }
              </Button>
            </div>
          </div>

          <Input
            value={confirmInput}
            onChange={(e) => setConfirmInput(e.target.value)}
            placeholder="Ketik nama brand di sini..."
            aria-label="Konfirmasi nama brand"
          />
        </div>

        <DialogFooter>
          <Button
            variant="outline"
            onClick={() => handleOpenChange(false)}
            disabled={isDeleting}
          >
            Batal
          </Button>
          <Button
            variant="destructive"
            onClick={onConfirm}
            disabled={!isMatch || isDeleting}
          >
            {isDeleting && <Loader2 className="mr-2 size-4 animate-spin" />}
            Hapus
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
