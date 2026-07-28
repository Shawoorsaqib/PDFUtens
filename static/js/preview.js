/**
 * PDFUtens - Universal Input File Preview Engine
 * Generates instant visual previews for uploaded files (Images, PDFs via PDF.js, Text snippets, Word/Excel/PPT cards).
 */

if (window.pdfjsLib) {
    window.pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';
}

function renderFilePreview(file, containerElement, options = {}) {
    if (!containerElement || !file) return;

    containerElement.innerHTML = "";
    containerElement.classList.add("active");

    const fileName = file.name || "";
    const ext = fileName.split('.').pop().toLowerCase();
    const mimeType = file.type || "";

    // 1. Image Files Preview
    if (mimeType.startsWith("image/") || ["png", "jpg", "jpeg", "webp", "bmp", "tiff", "gif", "svg"].includes(ext)) {
        const img = document.createElement("img");
        img.alt = fileName;
        img.style.width = "100%";
        img.style.height = "100%";
        img.style.objectFit = "cover";
        img.style.borderRadius = "8px";
        img.src = URL.createObjectURL(file);
        containerElement.appendChild(img);
        return;
    }

    // 2. PDF Files Preview (using PDF.js)
    if (mimeType === "application/pdf" || ext === "pdf") {
        const loadingDiv = document.createElement("div");
        loadingDiv.className = "document-icon pdf-preview-icon";
        loadingDiv.innerHTML = `<i class="bi bi-file-earmark-pdf-fill"></i>`;
        containerElement.appendChild(loadingDiv);

        if (window.pdfjsLib) {
            const reader = new FileReader();
            reader.onload = async function(e) {
                try {
                    const typedarray = new Uint8Array(e.target.result);
                    const pdf = await window.pdfjsLib.getDocument({ data: typedarray }).promise;
                    const page = await pdf.getPage(1);

                    const viewport = page.getViewport({ scale: 0.3 });
                    const canvas = document.createElement("canvas");
                    canvas.className = "pdf-thumbnail-canvas";
                    canvas.width = viewport.width;
                    canvas.height = viewport.height;
                    canvas.style.width = "100%";
                    canvas.style.height = "100%";
                    canvas.style.objectFit = "contain";
                    canvas.style.borderRadius = "6px";
                    canvas.style.background = "#ffffff";
                    canvas.style.boxShadow = "0 2px 6px rgba(0,0,0,0.1)";

                    const context = canvas.getContext("2d");
                    await page.render({ canvasContext: context, viewport: viewport }).promise;

                    containerElement.innerHTML = "";
                    containerElement.appendChild(canvas);
                } catch (err) {
                    console.log("PDF.js render fallback for:", fileName, err);
                }
            };
            reader.readAsArrayBuffer(file);
        }
        return;
    }

    // 3. Text Files Preview (.txt)
    if (mimeType === "text/plain" || ext === "txt") {
        const textCard = document.createElement("div");
        textCard.className = "text-preview-card";
        textCard.innerHTML = `<div class="text-preview-header"><i class="bi bi-file-earmark-text"></i> TXT</div><div class="text-snippet">Loading...</div>`;
        containerElement.appendChild(textCard);

        const reader = new FileReader();
        reader.onload = function(e) {
            const content = e.target.result || "";
            const snippet = content.trim().slice(0, 80) || "Empty file";
            const snippetEl = textCard.querySelector(".text-snippet");
            if (snippetEl) snippetEl.textContent = snippet;
        };
        reader.readAsText(file);
        return;
    }

    // 4. Word / Office / Other Document Cards
    let iconClass = "bi-file-earmark-text-fill";
    let badgeBg = "#eff6ff";
    let badgeColor = "#2563eb";
    let typeLabel = ext.toUpperCase();

    if (["doc", "docx"].includes(ext)) {
        iconClass = "bi-file-earmark-word-fill";
        badgeBg = "#eff6ff";
        badgeColor = "#1d4ed8";
    } else if (["xls", "xlsx"].includes(ext)) {
        iconClass = "bi-file-earmark-excel-fill";
        badgeBg = "#f0fdf4";
        badgeColor = "#15803d";
    } else if (["ppt", "pptx"].includes(ext)) {
        iconClass = "bi-file-earmark-ppt-fill";
        badgeBg = "#fff7ed";
        badgeColor = "#c2410c";
    }

    const docCard = document.createElement("div");
    docCard.className = "doc-type-preview-card";
    docCard.style.background = badgeBg;
    docCard.style.color = badgeColor;
    docCard.innerHTML = `
        <i class="bi ${iconClass}"></i>
        <span class="doc-badge">${typeLabel}</span>
    `;
    containerElement.appendChild(docCard);
}
