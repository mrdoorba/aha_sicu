import { useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { useBrandUploads, useDownloadFile, useUploadFile, type UploadInfo } from '../../hooks/useUpload';
import { FileUploadSlot, type FileSlotConfig } from './FileUploadSlot';
import { toast } from 'sonner';

const SLOTS: FileSlotConfig[] = [
  {
    label: 'fileUpload.slot.cpcAdReport',
    fileType: 'cpc_ad_report',
    accept: '.csv',
    format: '.csv',
    calculator: 'fileUpload.slot.cpcAdReportCalc',
    link: 'https://seller.shopee.co.id/portal/marketing/pas/assembly?&type=all&group=last-thirty-days',
  },
  {
    label: 'fileUpload.slot.keywordReport',
    fileType: 'keyword_report',
    accept: '.csv',
    format: '.csv',
    calculator: 'fileUpload.slot.keywordReportCalc',
    link: 'https://seller.shopee.co.id/portal/marketing/pas/assembly?&type=all&group=last-thirty-days',
  },
  {
    label: 'fileUpload.slot.orderExport',
    fileType: 'order_export',
    accept: '.xlsx,.zip',
    format: '.xlsx, .zip',
    calculator: 'fileUpload.slot.orderExportCalc',
    link: 'https://seller.shopee.co.id/portal/sale/order',
  },
  {
    label: 'fileUpload.slot.massUpdate',
    fileType: 'mass_update',
    accept: '.xlsx,.zip',
    format: '.xlsx, .zip',
    calculator: 'fileUpload.slot.massUpdateCalc',
    link: 'https://seller.shopee.co.id/portal/product-mass/mass-update/download',
  },
];

interface FileUploadSectionProps {
  brandId: number;
}

export function FileUploadSection({ brandId }: FileUploadSectionProps) {
  const { data: brandUploads } = useBrandUploads(brandId);

  return (
    <div className="grid gap-4 sm:grid-cols-2">
      {SLOTS.map((slot) => (
        <SlotWrapper
          key={slot.fileType}
          config={slot}
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
