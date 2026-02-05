# Multi-File Uploads in Laravel Vapor

## Requirements
*   TALL Stack (Laravel 11)
*   Laravel Vapor
*   AWS S3
*   AWS RDS (Optional)

## Challenges
1.  AWS S3: Doesn't natively support multiple file uploads as a single stream.
2.  AWS Lambda: 4.5MB payload size limitation for synchronous invocations.

## Approach: Frontend-First Upload to S3

Upload files directly from the frontend to S3, then notify the backend.

### 1. Upload Trigger (HTML)

Use a multi-file input or a button to trigger the upload.

```html
<!-- Input file -->
<input multiple @click.self="openError = false" type="file" id="fileUploads" name="files[]" class="..." />

<!-- Or Button -->
<button id="fileUploads" type="submit" @click="handleFileUpload()" class="...">
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5"
        stroke="currentColor" class="h-5 w-5">
        <path stroke-linecap="round" stroke-linejoin="round"
            d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5" />
    </svg>
    <span>Upload</span>
</button>
```

### 2. Client-Side JavaScript Logic

Iterate through selected files and stream each to S3 using `Vapor.store()`. After all files are streamed, notify the backend.

```js
async function handleFileUpload() {
    const files = /* get files from input */; 
    if (!files || files.length === 0) return;

    let filesData = [];
    for (const file of files) {
        try {
            const uploadedFileDetails = await vaporUpload(file);
            filesData.push(uploadedFileDetails);
        } catch (error) {
            console.error(`Upload failed for ${file.name}:`, error);
        }
    }
    if (filesData.length > 0) {
        await handlePostUpload(filesData);
    }
}

/** Stream single file to S3 via Laravel Vapor client library */
function vaporUpload(item) {
    return Vapor.store(item, {
        progress: progress => {
            this.uploadProgress = Math.round(progress * 100);
        }
    }).then(response => {
        return {
            "key": response.key,
            "name": item.name,
            "extension": response.extension,
            "size": item.size,
        };
    });
}

/** Notify backend for post-upload processing */
function handlePostUpload(uploadedFilesDetails) {
    axios.post("{{ route('file_upload.file-upload-vapor') }}", { files: uploadedFilesDetails })
    .then(response => console.log("Backend processing successful:", response))
    .catch(error => console.error("Backend processing failed:", error));
}
```

### 3. Initialize Laravel Vapor JS

Include `laravel-vapor` in your main JavaScript file.

```js
// app.js
window.Vapor = require('laravel-vapor');
```

## Installation

```bash
npm install --save-dev laravel-vapor
```

## Flow

1.  **Frontend:** `handleFileUpload` loops through files.
2.  **S3 Stream:** `vaporUpload` streams each file directly to S3's tmp folder.
3.  **Backend Notification:** `handlePostUpload` sends S3 keys and metadata to Laravel backend.
4.  **Backend Processing:** Laravel endpoint validates, moves files from tmp to permanent S3, and updates database (e.g., RDS).
