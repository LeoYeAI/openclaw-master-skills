const axios = require('axios');
const fs = require('fs');
const path = require('path');
const { getTenantAccessToken } = require('./lib/auth');

async function main() {
    const messageId = process.argv[2];
    const fileKey = process.argv[3];
    const outputPath = process.argv[4];

    if (!messageId || !fileKey || !outputPath) {
        console.error("Usage: node download_file.js <messageId> <fileKey> <outputPath>");
        process.exit(1);
    }

    try {
        fs.mkdirSync(path.dirname(outputPath), { recursive: true });

        const token = await getTenantAccessToken();
        // Correct endpoint for standalone files
        const url = `https://open.feishu.cn/open-apis/im/v1/files/${fileKey}`;
        
        console.log(`Downloading ${fileKey}...`);

        const response = await axios({
            method: 'GET',
            url: url,
            responseType: 'stream',
            headers: { 'Authorization': `Bearer ${token}` }
        });

        const writer = fs.createWriteStream(outputPath);
        response.data.pipe(writer);

        await new Promise((resolve, reject) => {
            writer.on('finish', resolve);
            writer.on('error', reject);
        });

        console.log(`Download complete: ${outputPath}`);
    } catch (error) {
        console.error("Download failed:", error.response ? error.response.data : error.message);
        process.exit(1);
    }
}

main();
