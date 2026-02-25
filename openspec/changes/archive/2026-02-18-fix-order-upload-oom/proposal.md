## Why

Order Export upload for brands with thousands of orders (e.g., full-month Shopee exports) crashes the Cloud Run container with OOM (Out of Memory). The current memory limit is 512 MiB, but processing a 9 MB ZIP with thousands of rows spikes memory to 560+ MiB — loading the entire ZIP, extracting all Excel parts, parsing into DataFrames, concatenating, and converting to JSON all in-memory simultaneously. The container gets killed, and the browser receives a CORS-less error response that surfaces as a cryptic "NetworkError when attempting to fetch resource."

## What Changes

- Increase Cloud Run memory allocation from 512 MiB to 1 GiB for immediate relief
- Optimize ZIP/Excel processing to reduce peak memory usage (process parts incrementally, avoid holding duplicate copies of data in memory)
- Ensure the double JSON encoding fix (commits `890346f`, `8469a2b`) is effective for upload `parsed_data` — calculator errors show `parsed_data` is still a string instead of dict in some code paths

## Capabilities

### New Capabilities

- `upload-memory-optimization`: Memory-efficient processing for large ZIP uploads containing multiple Excel parts, reducing peak memory footprint during parse→store pipeline

### Modified Capabilities

- `upload-error-reporting`: When Cloud Run terminates a request due to resource limits, the user currently sees a cryptic "NetworkError". The error experience should be improved with a frontend timeout/retry mechanism.

## Impact

- **Backend**: `zip_handler.py`, `service.py`, `parser.py` — refactor processing pipeline for lower memory usage
- **Backend**: `calculator_service.py` — fix `parsed_data` type handling (string vs dict)
- **Infrastructure**: Cloud Run service config — memory limit change (512 MiB → 1 GiB)
- **Frontend**: `useUpload.ts` — add timeout handling and better error messaging for long-running process requests
