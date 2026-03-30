---
name: image-crop
description: Crops images from center or specified regions. Supports extracting specific areas, creating fixed-size thumbnails, standardizing image dimensions, and removing edges. Use when cropping images, extracting regions, adjusting aspect ratios, or creating thumbnails from images.
---

# Image Crop

Crops images from the center or specified regions using the sharp library.

## Quick Start

Execute the crop script to crop an image:

```bash
node scripts/crop.js
```

Or import and use programmatically:

```javascript
import cropImage from './scripts/crop.js';

const result = await cropImage({
  inputPath: './input/image.jpg',
  outputPath: './output/cropped.jpg',
  cropWidth: 1920,  // optional, defaults to original width
  cropHeight: 720   // optional, defaults to original height
});
```

## Parameters

- `inputPath` (required): Input image file path
- `outputPath` (required): Output image file path
- `cropWidth` (optional): Crop width in pixels, defaults to original image width
- `cropHeight` (optional): Crop height in pixels, defaults to original image height

## Crop Behavior

- **Center crop** (default): Crops from the center of the image
- Automatically calculates crop position to ensure the crop area stays within image boundaries
- If crop dimensions exceed image size, uses maximum available dimensions

## Return Value

The script returns an object with the following structure:

```javascript
{
  success: true,
  output: "Cropped image to 1920x720",
  data: {
    inputPath: "...",
    outputPath: "...",
    originalSize: { width: 3840, height: 2160 },
    newSize: { width: 1920, height: 720 },
    cropArea: { left: 960, top: 720, width: 1920, height: 720 }
  }
}
```

On error, returns:

```javascript
{
  success: false,
  error: "Error message"
}
```

## Examples

### Crop to specific height (center crop)

```javascript
await cropImage({
  inputPath: './input/image.jpg',
  outputPath: './output/cropped.jpg',
  cropHeight: 720
});
```

### Crop to specific dimensions (center crop)

```javascript
await cropImage({
  inputPath: './input/image.jpg',
  outputPath: './output/cropped.jpg',
  cropWidth: 1920,
  cropHeight: 1080
});
```

### Command line usage

If using as a standalone script, pass arguments via environment variables or modify the script to accept command-line arguments.

## Technical Details

- Uses `sharp` library for image processing
- Supports common image formats: JPEG, PNG, WebP, GIF, TIFF, AVIF
- Automatically creates output directory if it doesn't exist
- Handles edge cases: ensures crop area doesn't exceed image boundaries
- Center crop calculation: `left = (imageWidth - cropWidth) / 2`, `top = (imageHeight - cropHeight) / 2`

## Dependencies

Requires `sharp` package. Install with:

```bash
npm install sharp
```

## References

For skill creation guidelines and best practices, see [skill-creator](../skill-creator/SKILL.md).
