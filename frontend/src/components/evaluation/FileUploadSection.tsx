import { useBrandUploads, useUploadFile, type UploadInfo } from '../../hooks/useUpload';
import { FileUploadSlot, type FileSlotConfig } from './FileUploadSlot';
import { toast } from 'sonner';

const SLOTS: FileSlotConfig[] = [
  {
    label: 'CPC Ad Report',
    fileType: 'cpc_ad_report',
    accept: '.csv',
    format: '.csv',
    calculator: 'Calculator 1 (Ads Keyword — Sheet 1)',
  },
  {
    label: 'Keyword Placement Report',
    fileType: 'keyword_report',
    accept: '.csv',
    format: '.csv',
    calculator: 'Calculator 1 (Ads Keyword — Sheet 2)',
  },
  {
    label: 'Order Export',
    fileType: 'order_export',
    accept: '.xlsx,.zip',
    format: '.xlsx, .zip',
    calculator: 'Calculator 2 (Top SKU) & Calculator 3 (Discount Check)',
  },
  {
    label: 'Mass Update / Sales Info',
    fileType: 'mass_update',
    accept: '.xlsx,.zip',
    format: '.xlsx, .zip',
    calculator: 'Calculator 2 (Top SKU)',
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
  const { upload, progress, status, error, reset } = useUploadFile(brandId);

  const handleFileSelect = async (file: File) => {
    try {
      await upload(file, config.fileType);
      toast.success(`${config.label} uploaded successfully`);
    } catch {
      toast.error(`Failed to upload ${config.label}`);
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
    />
  );
}
