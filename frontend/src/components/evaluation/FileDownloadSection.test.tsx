import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { FileDownloadSection } from './FileDownloadSection';
import type { UploadInfo } from '../../hooks/useUpload';

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string) => key,
  }),
}));

vi.mock('../../hooks/useUpload', () => ({
  useDownloadFile: () => ({
    mutateAsync: vi.fn().mockResolvedValue({
      download_url: 'https://example.com/download',
      filename: 'test.csv',
    }),
    isPending: false,
  }),
}));

const mockUploads: UploadInfo[] = [
  {
    id: 1,
    file_type: 'cpc_ad_report',
    filename: 'Brand_report.csv',
    file_size: 1024,
    row_count: 25,
    uploaded_at: '2026-03-10T13:00:00Z',
  },
];

describe('FileDownloadSection', () => {
  it('should render collapsed by default', () => {
    render(<FileDownloadSection brandId={1} uploads={mockUploads} />);
    expect(screen.getByText(/fileDownload.title/)).toBeInTheDocument();
    expect(screen.queryByText('Brand_report.csv')).not.toBeInTheDocument();
  });

  it('should expand when header is clicked', () => {
    render(<FileDownloadSection brandId={1} uploads={mockUploads} />);
    fireEvent.click(screen.getByText(/fileDownload.title/));
    expect(screen.getByText('Brand_report.csv')).toBeInTheDocument();
  });

  it('should not render when no uploads exist', () => {
    const { container } = render(
      <FileDownloadSection brandId={1} uploads={[]} />,
    );
    expect(container.firstChild).toBeNull();
  });
});
