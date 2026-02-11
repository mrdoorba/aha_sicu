# Calculator 3: Hitung Rata Diskon (% Disc Check Up)

This calculator analyzes discount patterns across orders to detect potential fake discounts.

---

## Input

- **Source**: Same Shopee order export as Calculator 2
- **All orders are included** (no status filter)

### Columns Used from Order Data

| Raw Column | Name | Description |
|------------|------|-------------|
| A | No. Pesanan | Order number (for Urutan grouping) |
| B | Nama Produk | Product name (for grouping) |
| C | Harga Awal | Original price |
| D | Harga Setelah Diskon | Discounted price |
| E | Jumlah | Quantity per line |
| F | Voucher Ditanggung Penjual | Seller voucher (order-level) |
| G | Paket Diskon (Diskon dari Penjual) | Bundle discount from seller |

> **Price format**: Indonesian format where `.` = thousands separator. Remove `.` before converting to number.

---

## Sheet Layout

The calculator sheet has these column sections:

| Section | Columns | Purpose |
|---------|---------|---------|
| Raw data | A-G | Order data pasted from export |
| Calculated | I-P | Cleaned prices, discount calculations |
| Product summary | R-T | Grouped by product name |
| TOP SKU | V-X | Top 20% products by quantity |
| Output | Z | Final output values |

---

## Processing Pipeline

### Step 1: Calculate Urutan (Column I)

Counts item position within the same order:

```
=IF(A2="",, IF(A2=A1, I1+1, 1))
```

- Same order number as row above → increment
- Different order number → reset to 1

> **Purpose**: Voucher and Paket Diskon are order-level discounts. To avoid double-counting, they are only applied to **Urutan = 1** (the first line item of each order).

### Step 2: Clean Price Data (Columns J-K)

Remove `.` thousands separator and convert to number:
- **J** = Harga Awal (cleaned)
- **K** = Harga Setelah Diskon (cleaned)

### Step 3: Apply Voucher and Paket (Columns L-M)

Only applied when **Urutan = 1**:
- **L** = Voucher amount (0 if Urutan > 1)
- **M** = Paket Diskon amount (0 if Urutan > 1)

Header row shows the overall percentage:
- L header: `="Voucher " & TEXT(SUM(L2:L) / SUM(K2:K), "0.0%")` → e.g., "Voucher 0.3%"
- M header: `="Paket Diskon " & TEXT(SUM(M2:M) / SUM(K2:K), "0.0%")` → e.g., "Paket Diskon 0.0%"

> **Note**: Denominator is **K (Harga Setelah Diskon)**, NOT J (Harga Awal).

L column formula:
```
=ARRAYFORMULA(IF(D2:D="",, IF(I2:I>1, 0, VALUE(SUBSTITUTE(F2:F,".",)))))
```

### Step 4: Calculate Total Discount (Column N)

```
N = (Harga Awal - Harga Setelah Diskon) + Voucher(Urutan=1) + Paket(Urutan=1)
```

This combines price discount + seller voucher + bundle discount.

### Step 5: Calculate Discount Percentage (Column O)

```
% Disc = N / Harga Awal
```

Named "% Disc (inc. Voucher)" because it includes voucher in the discount total.

### Step 6: Calculate Total Paid (Column P)

```
P = Harga Setelah Diskon - Voucher(Urutan=1) - Paket(Urutan=1)
```

Named "Total Terbayarkan (diluar subsidi SHO)" — the actual amount paid by customer excluding Shopee subsidies.

### Step 7: Product Summary (Columns R-T)

Group by **Nama Produk** (exact match):

- **R** = Unique product names
- **S (Qty Terjual)** = Total quantity sold per product (SUM of Jumlah)
- **T (Rata² % Disc)** = Average of % Disc (column O) per product

### Step 8: TOP SKU Filter (Columns V-X)

Filters product summary using a QUERY with multiple conditions:

```
=QUERY(R2:T, "select * where S > " & AVERAGE(S:S) & " and T < 1 order by S desc limit " & ROUND(COUNTA(UNIQUE(R2:R)) * 20%, 0))
```

Conditions:
1. **Qty > AVERAGE(Qty)** — only products selling above average
2. **AvgDisc < 1** — exclude products with 100%+ discount (anomalies)
3. **Order by Qty descending**
4. **Limit** = ROUND(unique_products × 20%) — no MIN(..., 20) floor

- **V** = Product name
- **W** = Quantity sold
- **X** = Average discount percentage

> **Important**: TOP SKU ranking is by **quantity (Qty)**, NOT by revenue. This differs from Calculator 2 which ranks by revenue (omzet). The limit also differs — Calculator 2 uses MAX(ROUND(20%), 20) while Calculator 3 uses just ROUND(20%).

---

## Output (Column Z)

5 output cells:

### Cell 1: % Diskon TOP SKU

```
="% Diskon TOP SKU: " & TEXT(SUMIF(P:P, ">0", N:N) / SUM(P:P), "0.0%")
```

Total discount amount / Total amount paid across ALL order lines.

### Cell 2: Discount Range

```
="Range: " & TEXT(ROUNDUP(MIN(X:X), 3), "0.0%") & " ~ " & TEXT(ROUNDUP(MAX(X:X), 3), "0.0%")
```

Min and max average discount % among TOP SKUs. ROUNDUP to 3 decimal places.

### Cell 3: Voucher Percentage

```
=L1
```

The header value from column L (e.g., "Voucher 0.3%").

### Cell 4: Bundle Discount Percentage

```
=M1
```

The header value from column M (e.g., "Paket Diskon 0.0%").

### Cell 5: Fake Discount Flag

```
=IF(SUM(N:N)/SUM(P:P) > 20%, "📌 Berpotensi menggunakan 'fake discount'", )
```

If total discounts exceed 20% of total payments → flags potential fake discount.

---

## Sample Output (SUKA, Nov 2025)

```
% Diskon TOP SKU: 2.7%
Range: 0.0% ~ 6.7%
Voucher 0.3%
Paket Diskon 0.0%
```

(No fake discount flag because 2.7% < 20%)

### Sample Output (KYPSO, Oct 2025)

```
% Diskon TOP SKU: 217.3%
Range: 56.1% ~ 73.1%
Voucher 0.1%
Paket Diskon 0.0%
📌 Berpotensi menggunakan 'fake discount'
```

### Sample Output (Second validation dataset, Nov 2025)

```
% Diskon TOP SKU: 27.9%
Range: 20.4% ~ 95.8%
Voucher 2.7%
Paket Diskon 0.1%
📌 Berpotensi menggunakan 'fake discount'
```

### Sample Output (MND Moon Dae, Nov 2025)

```
% Diskon TOP SKU: 102.9%
Range: 42.2% ~ 50.4%
Voucher 3.9%
Paket Diskon 0.2%
📌 Berpotensi menggunakan 'fake discount'
```

---

## Key Differences from Calculator 2

| Aspect | Calculator 2 | Calculator 3 |
|--------|-------------|-------------|
| Ranking | By revenue (omzet) | By quantity (Qty) |
| Grouping | Nama Produk + Variasi (BP) | Nama Produk only |
| Voucher handling | Divided by Jumlah Produk di Pesan | Applied only to Urutan=1 |
| Purpose | Identify top revenue products | Analyze discount health |
