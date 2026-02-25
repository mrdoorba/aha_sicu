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
    <div className="p-8">
      <main id="main-content" className="mx-auto max-w-7xl">
        {brandId ? (
          <PresentationDashboard brandId={Number(brandId)} onBack={handleBackToSearch} />
        ) : (
          <BrandSearch onSelect={handleSelectBrand} />
        )}
      </main>
    </div>
  );
};
