import { useRef } from 'react';
import { Upload, FileText, X, Check, Loader2 } from 'lucide-react';
import { Card, CardContent } from '../ui/card';
import { Button } from '../ui/button';
import { Progress } from '../ui/progress';
import type { UploadInfo, UploadStatus } from '../../hooks/useUpload';

export interface FileSlotConfig {
  label: string;
  fileType: string;
  accept: string;
  format: string;
  calculator: string;
}

interface FileUploadSlotProps {
  config: FileSlotConfig;
  uploadInfo: UploadInfo | null;
  uploadStatus: UploadStatus;
  uploadProgress: number;
  uploadError: string | null;
  onFileSelect: (file: File) => void;
  onReset: () => void;
}

export function FileUploadSlot({
  config,
  uploadInfo,
  uploadStatus,
  uploadProgress,
  uploadError,
  onFileSelect,
  onReset,
}: FileUploadSlotProps) {
  const inputRef = useRef<HTMLInputElement>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      onFileSelect(file);
    }
    // Reset input so re-selecting the same file still fires onChange
    if (inputRef.current) inputRef.current.value = '';
  };

  const isUploading = uploadStatus === 'signing' || uploadStatus === 'uploading' || uploadStatus === 'processing';
  const isVerifying = uploadStatus === 'verifying';

  return (
    <Card>
      <CardContent className="flex items-start gap-3 pt-4">
        <FileText className="mt-0.5 size-5 shrink-0 text-muted-foreground" aria-hidden="true" />
        <div className="min-w-0 flex-1">
          <p className="font-medium">{config.label}</p>
          <p className="text-xs text-muted-foreground">
            Format: {config.format}
          </p>
          <p className="text-xs text-muted-foreground">
            Routes to: {config.calculator}
          </p>

          {/* Hidden file input */}
          <input
            ref={inputRef}
            type="file"
            accept={config.accept}
            onChange={handleChange}
            className="hidden"
            aria-label={`Upload ${config.label}`}
          />

          {/* State: Empty */}
          {!uploadInfo && uploadStatus === 'idle' && (
            <div className="mt-2">
              <p className="text-sm text-muted-foreground">No file uploaded</p>
              <Button
                variant="outline"
                size="sm"
                className="mt-1"
                onClick={() => inputRef.current?.click()}
              >
                <Upload className="mr-1.5 size-3.5" aria-hidden="true" />
                Upload File
              </Button>
            </div>
          )}

          {/* State: Uploading / Processing */}
          {isUploading && (
            <div className="mt-2 space-y-1">
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Loader2 className="size-3.5 animate-spin" aria-hidden="true" />
                <span>
                  {uploadStatus === 'signing' && 'Preparing upload…'}
                  {uploadStatus === 'uploading' && `Uploading… ${uploadProgress}%`}
                  {uploadStatus === 'processing' && 'Processing file…'}
                </span>
              </div>
              {uploadStatus === 'uploading' && (
                <Progress value={uploadProgress} className="h-1.5" />
              )}
            </div>
          )}

          {/* State: Verifying */}
          {isVerifying && (
            <div className="mt-2">
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Loader2 className="size-3.5 animate-spin" aria-hidden="true" />
                <span>Verifying upload…</span>
              </div>
            </div>
          )}

          {/* State: Error */}
          {uploadStatus === 'error' && (
            <div className="mt-2">
              <p className="text-sm text-destructive">{uploadError}</p>
              <Button
                variant="outline"
                size="sm"
                className="mt-1"
                onClick={() => {
                  onReset();
                  inputRef.current?.click();
                }}
              >
                <X className="mr-1.5 size-3.5" aria-hidden="true" />
                Retry
              </Button>
            </div>
          )}

          {/* State: Uploaded (includes done status and existing uploads) */}
          {uploadInfo && (uploadStatus === 'idle' || uploadStatus === 'done') && (
            <div className="mt-2">
              <div className="flex items-center gap-1.5 text-sm text-green-600">
                <Check className="size-3.5" aria-hidden="true" />
                <span>File uploaded successfully</span>
              </div>
              <p className="text-xs text-muted-foreground">
                {uploadInfo.filename}
              </p>
              <p className="text-xs text-muted-foreground">
                {uploadInfo.row_count.toLocaleString()} rows &middot;{' '}
                {new Date(uploadInfo.uploaded_at).toLocaleString()}
              </p>
              <Button
                variant="ghost"
                size="sm"
                className="mt-1 h-7 px-2 text-xs"
                onClick={() => {
                  onReset();
                  inputRef.current?.click();
                }}
              >
                <Upload className="mr-1 size-3" aria-hidden="true" />
                Re-upload
              </Button>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
