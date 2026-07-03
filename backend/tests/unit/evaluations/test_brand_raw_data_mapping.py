"""Unit tests for marketplace-aware BrandRawData extraction."""



def test_brand_raw_data_uses_thai_columns_when_marketplace_th():
    """BrandRawData should use the unified schema columns for TH marketplace."""
    from app.modules.evaluations.service import _BRAND_RAW_DATA_COLUMNS

    th_cols = _BRAND_RAW_DATA_COLUMNS["TH"]
    assert th_cols["pic_name"] == "PIC"
    assert th_cols["store_link"] == "Store Link"
    assert th_cols["kategori"] == "Category"


def test_brand_raw_data_uses_indonesian_columns_when_marketplace_id():
    """BrandRawData should use the unified schema columns for ID marketplace."""
    from app.modules.evaluations.service import _BRAND_RAW_DATA_COLUMNS

    id_cols = _BRAND_RAW_DATA_COLUMNS["ID"]
    assert id_cols["pic_name"] == "PIC"
    assert id_cols["store_link"] == "Store Link"
    assert id_cols["kategori"] == "Category"
