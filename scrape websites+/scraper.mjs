import { PlaywrightCrawler, Dataset, KeyValueStore, log } from 'crawlee'; // <-- Aggiunto 'log' all'import

// Funzione principale del crawler
async function runCrawler(startUrl) {
    if (!startUrl) {
        console.error("Errore: Devi fornire un URL di partenza come argomento.");
        console.error("Esempio di utilizzo: node your-script.mjs https://www.example.com");
        return;
    }

    const crawler = new PlaywrightCrawler({
        // Richiede Playwright per gestire siti web dinamici con JavaScript
        async requestHandler({ request, page, enqueueLinks, log, saveSnapshot }) {
            log.info(`Processando URL: ${request.url}`);

            const pageTitle = await page.title();
            const pageUrl = request.loadedUrl; // URL effettivo dopo eventuali redirect

            // --- Estrazione Dati Testuali ---
            const textContent = await page.evaluate(() => document.body.innerText);
            const headings = await page.evaluate(() => {
                const hTags = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6'];
                const headingsData = {};
                hTags.forEach(tag => {
                    const elements = Array.from(document.querySelectorAll(tag));
                    if (elements.length) {
                        headingsData[tag] = elements.map(el => el.innerText);
                    }
                });
                return headingsData;
            });

            // --- Estrazione Link ---
            await enqueueLinks({
                globs: [`${new URL(pageUrl).origin}/**/*`], // Crawla solo link dello stesso dominio
            });
            const allLinksOnPage = await page.evaluate(() => Array.from(document.querySelectorAll('a[href]'), el => el.href));

            // --- Estrazione Immagini ---
            const images = await page.evaluate(() => Array.from(document.querySelectorAll('img[src]'), el => ({
                src: el.src,
                alt: el.alt
            })));

            // --- Estrazione Video (esempio basico, potrebbe necessitare affinamenti) ---
            const videos = await page.evaluate(() => Array.from(document.querySelectorAll('video source[src], video[src]'), el => el.src || el.getAttribute('src')));

            // --- Estrazione File (esempio basico, link a documenti comuni) ---
            const files = await page.evaluate(() => {
                const fileExtensions = ['pdf', 'docx', 'xlsx', 'pptx', 'zip', 'rar', 'csv', 'txt'];
                return Array.from(document.querySelectorAll('a[href]'))
                    .map(el => el.href)
                    .filter(href => fileExtensions.some(ext => href.toLowerCase().endsWith(`.${ext}`)));
            });

            // --- Salva Screenshot della Pagina ---
            const screenshotKey = `screenshot-${Date.now()}`;
            await saveSnapshot({ key: screenshotKey, saveHtml: false });
            const screenshotUrl = `KEY_VALUE_STORE/default/records/${screenshotKey}.png`; // URL fittizio, l'URL reale dipende dalla piattaforma Apify

            // --- Salva i dati estratti nel Dataset predefinito ---
            await Dataset.pushData({
                url: pageUrl,
                titoloPagina: pageTitle,
                headings: headings,
                testoCompleto: textContent.substring(0, 500) + "...", // Limita il testo per dataset, salva intero nel KVS
                linksPagina: allLinksOnPage,
                immagini: images,
                videos: videos,
                files: files,
                screenshotUrl: screenshotUrl, // URL fittizio per screenshot locale/Apify
            });

            // --- Salva il testo completo nel Key-Value Store per non limitare la dimensione ---
            const fullTextKey = `fullText-${Date.now()}`;
            await KeyValueStore.setValue(fullTextKey, textContent, { contentType: 'text/plain' });
            log.info(`Testo completo salvato nel Key-Value Store con chiave: ${fullTextKey}`);

            log.info(`Dati da URL: ${pageUrl} estratti e salvati.`);
        },

        // Limita il numero massimo di richieste per questo esempio dimostrativo
        maxRequestsPerCrawl: 50, // Aumenta o rimuovi per crawl più estesi
    });

    log.info(`Avvio del crawler per URL: ${startUrl}`);
    await crawler.run([startUrl]); // Avvia il crawler con l'URL fornito
    log.info('Crawler completato.');
}


// --- Esecuzione dello Script ---
const startUrl = process.argv[2]; // Ottieni l'URL di partenza dagli argomenti da riga di comando

if (!startUrl) {
    console.error("Errore: Devi fornire un URL di partenza come argomento.");
    console.error("Esempio di utilizzo: node your-script.mjs https://www.example.com");
} else {
    runCrawler(startUrl).catch(err => {
        console.error("Il crawler ha incontrato un errore:", err);
    });
}