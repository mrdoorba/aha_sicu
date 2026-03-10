import { useState, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { ChevronDown, ChevronUp, Download } from 'lucide-react';
import { Button } from '../ui/button';
import { useDownloadFile, type UploadInfo } from '../../hooks/useUpload';
import { toast } from 'sonner';

interface FileDownloadSectionProps {
  brandId: number;
  uploads: UploadInfo[];
}

export function FileDownloadSection({
  brandId,
  uploads,
}: FileDownloadSectionProps) {
  const { t } = useTranslation();
  const [isExpanded, setIsExpanded] = useState(false);
  const downloadMutation = useDownloadFile();

  const handleDownload = useCallback(
    async (fileType: string) => {
      try {
        const result = await downloadMutation.mutateAsync({
          brandId,
          fileType,
        });
        window.open(result.download_url, '_blank');
      } catch {
        toast.error(t('fileUpload.downloadError'));
      }
    },
    [brandId, downloadMutation, t],
  );

  if (uploads.length === 0) return null;

  return (
    <div className="mt-6">
      <button
        type="button"
        className="flex w-full items-center justify-between rounded-lg bg-muted px-4 py-3"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center gap-2">
          <h4 className="text-base font-semibold text-primary">
            {t('fileDownload.title')}
          </h4>
          <span className="rounded-full bg-primary px-2 py-0.5 text-xs font-medium text-primary-foreground">
            {uploads.length} {t('fileDownload.files')}
          </span>
        </div>
        {isExpanded ? (
          <ChevronUp className="size-5 text-primary" />
        ) : (
          <ChevronDown className="size-5 text-primary" />
        )}
      </button>

      {isExpanded && (
        <div className="mt-2 overflow-hidden rounded-lg border">
          <table className="w-full text-sm">
            <thead className="bg-muted">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                  {t('fileDownload.column.fileType')}
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                  {t('fileDownload.column.filename')}
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                  {t('fileDownload.column.size')}
                </th>
                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                  {t('fileDownload.column.date')}
                </th>
                <th className="px-4 py-3 text-center text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                  {t('fileDownload.column.action')}
                </th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {uploads.map((upload) => (
                <tr key={upload.id}>
                  <td className="px-4 py-3 font-medium">{upload.file_type}</td>
                  <td className="px-4 py-3 text-muted-foreground">
                    {upload.filename}
                  </td>
                  <td className="px-4 py-3 text-muted-foreground">
                    {formatFileSize(upload.file_size)}
                  </td>
                  <td className="px-4 py-3 text-muted-foreground">
                    {new Date(upload.uploaded_at).toLocaleDateString()}
                  </td>
                  <td className="px-4 py-3 text-center">
                    <Button
                      variant="ghost"
                      size="sm"
                      className="text-green-600 hover:text-green-700"
                      onClick={() => handleDownload(upload.file_type)}
                      disabled={downloadMutation.isPending}
                    >
                      <Download className="size-4" />
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}
