#!/usr/bin/env node

/**
 * Image crop script
 * Crops an image from the center to specified dimensions
 * 
 * Usage:
 *   node crop.js
 *   Or import as module: import cropImage from './crop.js'
 */

import { existsSync, mkdirSync } from 'fs';
import { dirname } from 'path';
import sharp from 'sharp';

export default async function cropImage(args = {}, context = {}) {
  // Filter out variables that weren't replaced (still contain ${...})
  const cleanArgs = {};
  for (const [key, value] of Object.entries(args)) {
    if (typeof value === 'string' && value.startsWith('${') && value.endsWith('}')) {
      // Variable not replaced, skip it
      continue;
    }
    cleanArgs[key] = value;
  }
  
  const { inputPath, outputPath, cropWidth, cropHeight } = cleanArgs;

  if (!inputPath) {
    return {
      success: false,
      error: 'Input path is required'
    };
  }

  if (!existsSync(inputPath)) {
    return {
      success: false,
      error: `Input file not found: ${inputPath}`
    };
  }

  if (!outputPath) {
    return {
      success: false,
      error: 'Output path is required'
    };
  }

  try {
    // Ensure output directory exists
    const outputDir = dirname(outputPath);
    if (!existsSync(outputDir)) {
      mkdirSync(outputDir, { recursive: true });
    }

    const image = sharp(inputPath);
    const metadata = await image.metadata();

    // Calculate crop dimensions (center crop)
    const cropW = cropWidth && cropWidth !== '' ? Number(cropWidth) : (metadata.width || 0);
    const cropH = cropHeight && cropHeight !== '' ? Number(cropHeight) : (metadata.height || 0);
    const left = Math.floor(((metadata.width || 0) - cropW) / 2);
    const top = Math.floor(((metadata.height || 0) - cropH) / 2);

    // Ensure crop dimensions don't exceed image dimensions
    const finalCropW = Math.min(cropW, metadata.width || 0);
    const finalCropH = Math.min(cropH, metadata.height || 0);
    const finalLeft = Math.max(0, left);
    const finalTop = Math.max(0, top);

    await image
      .extract({ left: finalLeft, top: finalTop, width: finalCropW, height: finalCropH })
      .toFile(outputPath);

    const newMetadata = await sharp(outputPath).metadata();

    return {
      success: true,
      output: `Cropped image to ${newMetadata.width}x${newMetadata.height}`,
      data: {
        inputPath,
        outputPath,
        originalSize: { width: metadata.width, height: metadata.height },
        newSize: { width: newMetadata.width, height: newMetadata.height },
        cropArea: { left: finalLeft, top: finalTop, width: finalCropW, height: finalCropH }
      }
    };
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : String(error)
    };
  }
}

// Allow direct execution if called from command line
if (import.meta.url === `file://${process.argv[1]}`) {
  // Parse command line arguments or use environment variables
  const args = {
    inputPath: process.env.INPUT_PATH || process.argv[2],
    outputPath: process.env.OUTPUT_PATH || process.argv[3],
    cropWidth: process.env.CROP_WIDTH || process.argv[4],
    cropHeight: process.env.CROP_HEIGHT || process.argv[5]
  };
  
  cropImage(args).then(result => {
    if (result.success) {
      console.log(result.output);
      console.log(JSON.stringify(result.data, null, 2));
    } else {
      console.error('Error:', result.error);
      process.exit(1);
    }
  }).catch(error => {
    console.error('Unexpected error:', error);
    process.exit(1);
  });
}
