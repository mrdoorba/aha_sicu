# Calculator 2: Kalkulator Penjualan (Sales Calculator)

This calculator analyzes order data to find top-selling products and their stock levels. It produces 2 outputs used in the scoring system.

---

## Inputs

### Input 1: Order Export (Shopee)

- **Source**: Shopee order export Excel file (e.g., `Order_all_YYYYMMDD_YYYYMMDD.xlsx`)
- **Sheet**: `orders`
- **Row 1**: Headers
- **Row 2+**: Order data (one row per line item)

> **Important**: All orders are used regardless of status (Selesai, Batal, etc.). There is NO status filter.

Key columns used:

| Column | Name | Description |
|--------|------|-------------|
| Nama Produk | Product name | Used for grouping |
| Nomor Referensi SKU | SKU reference | Used to match with mass_update |
| Nama Variasi | Variant name | Used for grouping |
| Harga Setelah Diskon | Price after discount | String with `.` as thousands separator (e.g., "529.000" = IDR 529,000) |
| Jumlah | Quantity per line item | Number of items in this line |
| Jumlah Produk di Pesan | Total items in the order | Used to split order-level discounts |
| Voucher Ditanggung Penjual | Seller voucher | Order-level discount from seller |
| Cashback Koin | Coin cashback | Order-level cashback |
| Diskon dari Shopee | Shopee discount | Order-level discount from Shopee |

> **Important**: Price fields use Indonesian format where `.` is a thousands separator, not a decimal. Always treat as string first and remove `.` before converting to number. Example: `"529.000"` → `529000`.

### Input 2: Mass Update / Sales Info (Shopee)

- **Source**: Shopee mass update export Excel file (e.g., `mass_update_sales_info_*.xlsx`)
- **Row 1-2**: System metadata
- **Row 3**: Headers
- **Row 4+**: Product/variant data

Key columns used:

| Column | Name | Description |
|--------|------|-------------|
| Kode Produk | Product code | Product-level ID |
| Nama Produk | Product name | Full product name |
| Kode Variasi | Variant code | Unique variant-level ID |
| Nama Variasi | Variant name | Variant label |
| SKU | SKU code | Maps to Nomor Referensi SKU in orders |
| Harga | Price | Current listed price |
| Stok | Stock | Current stock count |

---

## Processing Pipeline

### Step 1: Extract Per-Line Data from Orders

For each completed order line item, extract:

- **SKU** (BO) = `Nomor Referensi SKU`
- **Product+Variant label** (BP) = `Nama Produk & " - " & Nama Variasi`
- **Quantity** (BQ) = `Jumlah`
- **Revenue per line** (BR) = calculated as:

```
Revenue = (Harga Setelah Diskon × Quantity)
          - (Voucher Ditanggung Penjual / Jumlah Produk di Pesan)
          - (Cashback Koin / Jumlah Produk di Pesan)
          + (Diskon dari Shopee / Jumlah Produk di Pesan)
```

> All price strings must have `.` removed before converting to numbers.
> Order-level discounts (voucher, cashback, Shopee discount) are split evenly across all items in the order using `Jumlah Produk di Pesan`.

### Step 2: Aggregate by Product

Group by **Nama Produk + " - " + Nama Variasi** (exact match):

- **CA** = Unique product+variant labels
- **CB** = Total quantity sold per product: `SUMIF(all labels, this label, quantities)`
- **CC** = Total revenue (omzet) per product: `SUMIF(all labels, this label, revenues)`

### Step 3: Rank Top Products

Query the aggregated data:

```
Sort by Total Omzet (CC) descending
Limit = MAX(ROUND(count_unique_products × 20%, 0), 20)
```

This produces the **Top 20% best-selling products** (minimum 20 items).

### Step 4: Enrich with Kode Variasi

For each top product, look up its **Kode Variasi** by matching the product name:

1. Mass_update data is prepared with a name column: `Nama Produk & " - " & Nama Variasi`
2. The top product's **BP label** (from orders) is looked up against this mass_update name column
3. If a match is found → return the **Kode Variasi** from mass_update
4. If no match → "Kode Variasi tidak ditemukan"

Formula: `XLOOKUP(product_name_from_orders, mass_update_name_column, mass_update_kode_variasi_column)`

> **Note**: Products with names that differ between orders and mass_update (e.g., short/old names vs long/new names) will not match and show "tidak ditemukan".

### Step 5: Calculate Rata-rata Harga Jual (Average Selling Price)

For each top product:

```
Rata2 Harga Jual = MAXIFS(Revenue_per_line, Product+Variant_label, this_product)
```

This is the **maximum single-line revenue** for that product across all orders. In practice, this represents the highest amount paid for that product in one order line (highest qty × price in a single transaction).

### Step 6: Look Up Stock

For each top product, use the **Kode Variasi from Step 4** to look up **Stok** from the mass_update file by matching Kode Variasi directly.

If Kode Variasi was "tidak ditemukan" → stock = 0.

### Step 7: Calculate Average Stock

```
Average Stock = ROUND(AVERAGE(stock of all Top 20% products), 0)
```

This single number appears in the Output 2 header.

---

## Output 1: Top Selling SKU with Revenue

A table sorted by Total Omzet descending:

| Column | Description |
|--------|-------------|
| Kode Variasi | From mass_update lookup (or "Kode Variasi tidak ditemukan") |
| TOP 20 [period] | Product name + " - " + variant (the BP label) |
| Total Omzet per Produk | Sum of revenue for this product (IDR) |
| Nama Produk | Same as TOP 20 column |
| Rata2 Harga Jual [period] (Best Month) | Max single-line revenue for this product (IDR) |

### Sample Output 1 (KYPSO, Oct 2025)

```
Kode Variasi        | TOP 20 Oct 2025                                              | Total Omzet  | Rata2 Harga Jual
301913525888        | KYPSO Sovereign ... - Cokelat Muda                            | 4,355,000    | 387,000
159308760763        | KYPSO Monarch ... - Cokelat Tua                               | 3,341,500    | 627,000
291913663532        | KYPSO Phantom ... - Cokelat Tua                               | 2,618,000    | 357,000
Tidak ditemukan     | KYPSO - Frontier - Tas Selempang Laptop Kulit Pria -          | 1,887,000    | 629,000
281913509128        | KYPSO Empyrean ... - Cokelat Muda                             | 1,821,000    | 627,000
249009108985        | KYPSO Valor ... - Hitam                                       | 1,613,000    | 807,000
Tidak ditemukan     | KYPSO Navigator ... -                                         | 1,598,000    | 799,000
306913670731        | KYPSO Archetype ... - Cokelat Tua                             | 1,572,000    | 657,000
276913562228        | KYPSO Atlas ... - Hitam                                       | 1,547,000    | 357,000
286913613063        | KYPSO Ethereal ... - Abu-abu                                  | 1,490,000    | 447,000
249009108986        | KYPSO Valor ... - Cokelat Tua                                 | 1,433,000    | 538,000
Tidak ditemukan     | KYPSO Frontier Tas Kerja ... -                                | 1,418,000    | 789,000
Tidak ditemukan     | KYPSO - Summit Tas Selempang Kulit Pria -                     | 1,258,000    | 629,000
287015651151        | KYPSO Vesper ... - Hitam                                      | 1,108,000    | 516,000
281913509130        | KYPSO Empyrean ... - Hitam                                    | 1,045,000    | 627,000
Tidak ditemukan     | KYPSO Roamer ... -                                            |   927,000    | 927,000
Tidak ditemukan     | KYPSO Apex ... -                                              |   916,000    | 229,000
281913509128        | KYPSO - Empyrean Tas Selempang ... - Cokelat Muda             |   894,000    | 149,000
292016983183        | KYPSO Aegis ... - Cokelat Muda                                |   894,000    | 447,000
301913525887        | KYPSO Sovereign ... - Cokelat Tua                             |   858,000    | 129,000
```

### Sample Output 1 (MND Moon Dae, Nov 2025)

```
Kode Variasi        | TOP 20 Nov 2025                                              | Total Omzet  | Rata2 Harga Jual
Tidak ditemukan     | Seoul Shoulder Bag ... - Black                                | 19,593,731   | 256,666
Tidak ditemukan     | Yonsei Bag ... - Latte                                        | 19,024,292   | 299,360
205151363035        | Namsan Bag ... - Ivory                                        |  9,783,402   | 137,480
Tidak ditemukan     | Honey Shoulder Bag ... - Pure Indigo                          |  8,389,463   | 253,242
222651478367        | Inha Bag ... - Biscuit                                        |  8,164,409   | 170,300
Tidak ditemukan     | Yonsei Bag ... - Cream                                        |  7,390,331   | 283,870
257230663343        | Wonee Shoulder Bag ... - Pure Indigo                          |  5,640,890   | 142,700
253857224548        | Haru Pack ... - Chestnut                                      |  4,972,307   | 231,489
370149555717        | Yonsei Bag ... - Latte,Non Bundling                           |  4,716,733   | 180,300
310150260900        | Seoul Shoulder Bag ... - Black,Non Bundling                   |  4,334,640   | 288,764
119169772626        | Yara Bag ... - Holo Grey                                      |  3,830,077   | 350,664
138830602975        | Naomi Bag ... - Black [NEW COLOR]                             |  3,807,682   | 151,300
Tidak ditemukan     | Yonsei Bag ... - Black                                        |  3,631,466   | 535,680
253857224547        | Haru Pack ... - Cream Latte                                   |  3,402,258   | 260,000
355149745340        | Honey Shoulder Bag ... - Pure Indigo,Non Bundling             |  3,139,644   | 160,300
205151363033        | Namsan Bag ... - Biscuit                                      |  2,931,204   | 150,300
205151363036        | Namsan Bag ... - Black                                        |  2,465,916   | 150,300
253857224546        | Haru Pack ... - Charcoal                                      |  2,448,424   | 252,900
Tidak ditemukan     | Seoul Shoulder Bag ... - Tan                                  |  2,355,196   | 160,300
205151363034        | Namsan Bag ... - Choco                                        |  2,130,010   | 150,300
```

---

## Output 2: Top Selling SKU with Stock

Same product list as Output 1, but with stock information:

| Column | Description |
|--------|-------------|
| Top 20% Selling SKU | Kode Variasi (or "Kode Variasi tidak ditemukan") |
| Nama Produk | Product name (without variant) |
| Varian | Variant name only |
| Average Stok [number] | Stock from mass_update; header shows the average across all listed SKUs |

The header row includes `Average Stok [X]` where X = `ROUND(AVERAGE(all stocks in list), 0)`.

The header also shows the **date of the stock snapshot** (from when mass_update was exported).

### Sample Output 2 (KYPSO, stock snapshot)

```
Top 20% Selling SKU | Nama Produk                              | Varian       | Avg Stok 123
301913525888        | KYPSO Sovereign ...                       | Cokelat Muda | 782
159308760763        | KYPSO Monarch ...                         | Cokelat Tua  | 0
291913663532        | KYPSO Phantom ...                         | Cokelat Tua  | 0
Tidak ditemukan     |                                           |              | 0
281913509128        | KYPSO Empyrean ...                        | Cokelat Muda | 193
249009108985        | KYPSO Valor ...                           | Hitam        | 126
Tidak ditemukan     |                                           |              | 0
306913670731        | KYPSO Archetype ...                       | Cokelat Tua  | 107
276913562228        | KYPSO Atlas ...                           | Hitam        | 210
286913613063        | KYPSO Ethereal ...                        | Abu-abu      | 174
249009108986        | KYPSO Valor ...                           | Cokelat Tua  | 109
Tidak ditemukan     |                                           |              | 0
Tidak ditemukan     |                                           |              | 0
287015651151        | KYPSO Vesper ...                          | Hitam        | 23
281913509130        | KYPSO Empyrean ...                        | Hitam        | 163
Tidak ditemukan     |                                           |              | 0
Tidak ditemukan     |                                           |              | 0
281913509128        | KYPSO Empyrean ...                        | Cokelat Muda | 193
292016983183        | KYPSO Aegis ...                           | Cokelat Muda | 44
301913525887        | KYPSO Sovereign ...                       | Cokelat Tua  | 452
```

> **Note**: Items with "Tidak ditemukan" in Output 1 stay "Tidak ditemukan" in Output 2 with Stok = 0.

### Sample Output 2 (MND Moon Dae, Nov 2025)

```
Top 20% Selling SKU | Nama Produk                              | Varian                   | Avg Stok 125
Tidak ditemukan     |                                           |                          | 0
Tidak ditemukan     |                                           |                          | 0
205151363035        | MOON DAE Namsan Bag ...                   | Ivory                    | 278
Tidak ditemukan     |                                           |                          | 0
222651478367        | MOON DAE Inha Bag ...                     | Biscuit                  | 104
Tidak ditemukan     |                                           |                          | 0
257230663343        | MOON DAE Wonee Shoulder Bag ...           | Pure Indigo              | 156
253857224548        | MOON DAE Haru Pack ...                    | Chestnut                 | 237
370149555717        | MOON DAE Yonsei Bag ...                   | Latte,Non Bundling       | 314
310150260900        | MOON DAE Seoul Shoulder Bag ...           | Black,Non Bundling       | 226
119169772626        | MOON DAE Yara Bag ...                     | Holo Grey                | 189
138830602975        | MOON DAE Naomi Bag ...                    | Black [NEW COLOR]        | 153
Tidak ditemukan     |                                           |                          | 0
253857224547        | MOON DAE Haru Pack ...                    | Cream Latte              | 88
355149745340        | MOON DAE Honey Shoulder Bag ...           | Pure Indigo,Non Bundling | 547
205151363033        | MOON DAE Namsan Bag ...                   | Biscuit                  | 107
205151363036        | MOON DAE Namsan Bag ...                   | Black                    | 9
253857224546        | MOON DAE Haru Pack ...                    | Charcoal                 | 67
Tidak ditemukan     |                                           |                          | 0
205151363034        | MOON DAE Namsan Bag ...                   | Choco                    | 16
```

---

## How Outputs Feed into the Scoring System (Template SICU)

- **D70** = Average Stock number (from Output 2 header "Average Stok [X]"). This integer is pasted into cell D70 of the scoring system.
  - D70 >= 24 → score 10
  - D70 >= 12 → score 5
  - D70 < 12 → score -5

Both outputs are also used for reference in the final scoring system sheet. The key data points passed forward are:

- **Top 20% product list** with Kode Variasi identifiers
- **Total Omzet per product** for revenue analysis
- **Rata2 Harga Jual** for pricing analysis
- **Stock levels** for inventory health assessment
- **Average Stock (123)** as an overall inventory metric
