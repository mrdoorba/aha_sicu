import { useSearchParams } from 'react-router-dom';
import { BrandSearch } from '../components/dashboard/BrandSearch';
import { PresentationDashboard } from '../components/dashboard/PresentationDashboard';

export const DashboardPage = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const brandId = searchParams.get('brandId');

  const handleSelectBrand = (id: number) => {
    setSearchParams({ brandId: id.toString() });
  };

  const handleBackToSearch = () => {
    setSearchParams({});
  };

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      {brandId ? (
        <PresentationDashboard brandId={Number(brandId)} onBack={handleBackToSearch} />
      ) : (
        <BrandSearch onSelect={handleSelectBrand} />
      )}
    </div>
  );
};
