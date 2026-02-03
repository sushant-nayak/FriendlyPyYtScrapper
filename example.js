import YtScrapper from './src/index.js';

// Example usage
const scrapper = new YtScrapper();

async function demo() {
    const testUrl = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ';
    
    try {
        // Get video info
        // console.log('=== Getting Video Info ===');
        // const info = await scrapper.getInfo(testUrl);
        // console.log('Title:', info.title);
        // console.log('Author:', info.author);
        // console.log('Duration:', info.duration, 'seconds');
        // console.log('Formats available:', info.formats.length);
        // console.log('Formats available:', nfo.formats.map(f => "Quality: " + f.quality + " mimeType: " + f.mimeType + " hasAudio: " + f.hasAudio + " hasVideo: " + f.hasVideo).join(', '));

        // Uncomment to download
        // console.log('\n=== Downloading Video ===');
        // const result = await scrapper.download(testUrl);
        // console.log('Downloaded to:', result.filepath);
        
        // Uncomment to download audio only
        // console.log('\n=== Downloading Audio Only ===');
        // const audioResult = await scrapper.downloadAudio(testUrl);
        // console.log('Downloaded to:', audioResult.filepath);
        
    } catch (error) {
        console.error('Error:', error.message);
    }
}

// Uncomment to run demo
 demo();
