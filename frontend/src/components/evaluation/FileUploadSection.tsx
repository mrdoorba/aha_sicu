import { useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { useBrandUploads, useDownloadFile, useUploadFile, type UploadInfo } from '../../hooks/useUpload';
import { FileUploadSlot, type FileSlotConfig } from './FileUploadSlot';
import { toast } from 'sonner';
import { localizeSellerLink } from './forms/formConfig';
import { FILE_UPLOAD_SLOTS } from './fileUploadConfig';

interface FileUploadSectionProps {
  brandId: number;
  marketplace?: string;
}

export function FileUploadSection({ brandId, marketplace = 'ID' }: FileUploadSectionProps) {
  const { data: brandUploads } = useBrandUploads(brandId);

  return (
    <div className="grid gap-4 sm:grid-cols-2">
      {FILE_UPLOAD_SLOTS.map((slot) => (
        <SlotWrapper
          key={slot.fileType}
          config={{ ...slot, link: slot.link ? localizeSellerLink(slot.link, marketplace) : slot.link }}
          brandId={brandId}
          uploadInfo={
            brandUploads?.uploads.find((u) => u.file_type === slot.fileType) ?? null
          }
        />
      ))}
    </div>
  );
}

function SlotWrapper({
  config,
  brandId,
  uploadInfo,
}: {
  config: FileSlotConfig;
  brandId: number;
  uploadInfo: UploadInfo | null;
}) {
  const { t } = useTranslation();
  const { upload, progress, status, error, reset } = useUploadFile(brandId);
  const downloadMutation = useDownloadFile();

  const handleDownload = useCallback(async () => {
    try {
      const result = await downloadMutation.mutateAsync({
        brandId,
        fileType: config.fileType,
      });
      window.open(result.download_url, '_blank');
    } catch {
      toast.error(t('fileUpload.downloadError'));
    }
  }, [brandId, config.fileType, downloadMutation, t]);

  const handleFileSelect = async (file: File) => {
    try {
      await upload(file, config.fileType);
      toast.success(t('fileUpload.uploadSuccess', { label: t(config.label) }));
    } catch {
      toast.error(t('fileUpload.uploadFailed', { label: t(config.label) }));
    }
  };

  return (
    <FileUploadSlot
      config={config}
      uploadInfo={uploadInfo}
      uploadStatus={status}
      uploadProgress={progress}
      uploadError={error}
      onFileSelect={handleFileSelect}
      onReset={reset}
      onDownload={uploadInfo ? handleDownload : undefined}
      isDownloading={downloadMutation.isPending}
    />
  );
}
