#!/usr/bin/env node

import { Command } from 'commander';
import YtScrapper from './index.js';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const program = new Command();
const scrapper = new YtScrapper();

program
    .name('pyytscrapper')
    .description('YouTube video downloader - A Node.js/Python hybrid tool')
    .version('1.0.0');

program
    .command('info')
    .description('Get video information')
    .argument('<url>', 'YouTube video URL')
    .action(async (url) => {
        try {
            console.log('Fetching video information...\n');
            const info = await scrapper.getInfo(url);
            
            console.log('Title:', info.title);
            console.log('Author:', info.author);
            console.log('Duration:', info.duration, 'seconds');
            console.log('Views:', info.viewCount);
            console.log('Video ID:', info.id);
            console.log('\nAvailable formats:', info.formats.length);
            
            // Show some format details
            console.log('\nTop formats:');
            info.formats.slice(0, 5).forEach((fmt, idx) => {
                console.log(`  ${idx + 1}. Quality: ${fmt.qualityLabel || fmt.quality}, ` +
                           `Type: ${fmt.mimeType?.split(';')[0]}, ` +
                           `Audio: ${fmt.hasAudio ? 'Yes' : 'No'}, ` +
                           `Video: ${fmt.hasVideo ? 'Yes' : 'No'}`);
            });
        } catch (error) {
            console.error('Error:', error.message);
            process.exit(1);
        }
    });

program
    .command('download')
    .description('Download a video')
    .argument('<url>', 'YouTube video URL')
    .option('-o, --output <path>', 'Output directory', join(__dirname, '../downloads'))
    .option('-a, --audio-only', 'Download audio only', false)
    .option('-q, --quality <resolution>', 'Video quality/resolution (e.g., 720p, 1080p, 480p, 360p, best, worst)', 'best')
    .action(async (url, options) => {
        try {
            console.log('Starting download...\n');
            
            const downloadOptions = {
                audioOnly: options.audioOnly,
                quality: options.quality
            };
            
            const result = options.audioOnly 
                ? await scrapper.downloadAudio(url, options.output)
                : await scrapper.download(url, options.output, downloadOptions);
            
            if (result.success) {
                console.log('\n✓ Download complete!');
                console.log('Title:', result.title);
                console.log('Saved to:', result.filepath);
            } else {
                console.error('Download failed:', result.error);
                process.exit(1);
            }
        } catch (error) {
            console.error('Error:', error.message);
            process.exit(1);
        }
    });

program
    .command('formats')
    .description('List all available formats for a video')
    .argument('<url>', 'YouTube video URL')
    .action(async (url) => {
        try {
            console.log('Fetching available formats...\n');
            const formats = await scrapper.getFormats(url);
            
            console.log(`Found ${formats.length} formats:\n`);
            
            formats.forEach((fmt, idx) => {
                console.log(`${idx + 1}. Format ID: ${fmt.itag}`);
                console.log(`   Quality: ${fmt.qualityLabel || fmt.quality}`);
                console.log(`   Type: ${fmt.mimeType?.split(';')[0]}`);
                console.log(`   Audio: ${fmt.hasAudio ? 'Yes' : 'No'}, Video: ${fmt.hasVideo ? 'Yes' : 'No'}`);
                if (fmt.bitrate) {
                    console.log(`   Bitrate: ${(fmt.bitrate / 1000).toFixed(0)} kbps`);
                }
                console.log('');
            });
        } catch (error) {
            console.error('Error:', error.message);
            process.exit(1);
        }
    });

program.parse();
