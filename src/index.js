import { spawn } from 'child_process';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import fs from 'fs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

class YtScrapper {
    constructor() {
        this.pythonScript = join(__dirname, '../python/yt_downloader.py');
        this.defaultOutputDir = join(__dirname, '../downloads');
        
        // Ensure downloads directory exists
        if (!fs.existsSync(this.defaultOutputDir)) {
            fs.mkdirSync(this.defaultOutputDir, { recursive: true });
        }
    }

    /**
     * Execute Python script and return parsed JSON result
     */
    async _executePython(args) {
        return new Promise((resolve, reject) => {
            let stdout = '';
            let stderr = '';

            const pythonProcess = spawn('python3', [this.pythonScript, ...args]);

            pythonProcess.stdout.on('data', (data) => {
                stdout += data.toString();
            });

            pythonProcess.stderr.on('data', (data) => {
                stderr += data.toString();
            });

            pythonProcess.on('close', (code) => {
                if (code !== 0 && !stdout) {
                    reject(new Error(`Python script failed: ${stderr}`));
                    return;
                }

                try {
                    const result = JSON.parse(stdout);
                    if (result.error) {
                        reject(new Error(result.error));
                    } else {
                        resolve(result);
                    }
                } catch (e) {
                    reject(new Error(`Failed to parse Python output: ${stdout}\n${stderr}`));
                }
            });

            pythonProcess.on('error', (err) => {
                reject(new Error(`Failed to start Python process: ${err.message}`));
            });
        });
    }

    /**
     * Get video information without downloading
     * @param {string} url - YouTube video URL
     * @returns {Promise<Object>} Video information
     */
    async getInfo(url) {
        try {
            const result = await this._executePython(['info', url]);
            return result;
        } catch (error) {
            throw new Error(`Failed to get video info: ${error.message}`);
        }
    }

    /**
     * Download a YouTube video
     * @param {string} url - YouTube video URL
     * @param {string} outputPath - Directory to save the video
     * @param {Object} options - Download options
     * @returns {Promise<Object>} Download result
     */
    async download(url, outputPath = null, options = {}) {
        try {
            const output = outputPath || this.defaultOutputDir;
            
            // Ensure output directory exists
            if (!fs.existsSync(output)) {
                fs.mkdirSync(output, { recursive: true });
            }

            const args = ['download', url, output];
            
            if (options.audioOnly) {
                args.push('--audio-only');
            }

            const result = await this._executePython(args);
            return result;
        } catch (error) {
            throw new Error(`Failed to download video: ${error.message}`);
        }
    }

    /**
     * Download audio only from a YouTube video
     * @param {string} url - YouTube video URL
     * @param {string} outputPath - Directory to save the audio
     * @returns {Promise<Object>} Download result
     */
    async downloadAudio(url, outputPath = null) {
        return this.download(url, outputPath, { audioOnly: true });
    }

    /**
     * Get available formats for a video
     * @param {string} url - YouTube video URL
     * @returns {Promise<Array>} List of available formats
     */
    async getFormats(url) {
        try {
            const info = await this.getInfo(url);
            return info.formats || [];
        } catch (error) {
            throw new Error(`Failed to get formats: ${error.message}`);
        }
    }
}

export default YtScrapper;
