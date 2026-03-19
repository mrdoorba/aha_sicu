import { useState } from 'react';
import { useTranslation } from 'react-i18next';
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
  const { t } = useTranslation();
  const [confirmInput, setConfirmInput] = useState('');
  const [copied, setCopied] = useState(false);

  const isMatch = confirmInput.toLowerCase() === brandName.toLowerCase();

  const handleCopyBrandName = async () => {
    try {
      await navigator.clipboard.writeText(brandName);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      toast.error(t('deleteDialog.toast.copyFailed'));
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
          <DialogTitle>{t('deleteDialog.title')}</DialogTitle>
          <DialogDescription>
            {t('deleteDialog.description')}
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-2">
          <div>
            <p className="text-sm text-muted-foreground">
              {t('deleteDialog.confirmPrompt')}
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
                aria-label={t('deleteDialog.aria.copyBrand')}
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
            placeholder={t('deleteDialog.placeholder')}
            aria-label={t('deleteDialog.aria.confirmInput')}
          />
        </div>

        <DialogFooter>
          <Button
            variant="outline"
            onClick={() => handleOpenChange(false)}
            disabled={isDeleting}
          >
            {t('common.cancel')}
          </Button>
          <Button
            variant="destructive"
            onClick={onConfirm}
            disabled={!isMatch || isDeleting}
          >
            {isDeleting && <Loader2 className="mr-2 size-4 animate-spin" />}
            {t('common.delete')}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
