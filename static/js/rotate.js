document.addEventListener("DOMContentLoaded", () => {
    // Configure pdf.js worker URL if available
    if (window.pdfjsLib) {
        window.pdfjsLib.GlobalWorkerOptions.workerSrc = "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js";
    }

    const uploadForm = document.getElementById("rotatePdfForm") || document.getElementById("uploadForm");
    const uploadContent = document.getElementById("uploadContent");
    const chooseFileBtn = document.getElementById("chooseRotateBtn") || document.getElementById("chooseFileBtn");
    const fileInput = document.getElementById("rotatePdfFileInput") || document.getElementById("fileInput");
    const selectedFilesContainer = document.getElementById("selectedFilesContainer");
    const uploadActions = document.getElementById("uploadActions");
    const uploadBtn = document.getElementById("rotatePdfSubmitBtn") || document.getElementById("uploadBtn");
    const uploadStatus = document.getElementById("uploadStatus");
    const successCard = document.getElementById("successCard");
    const downloadBtn = document.getElementById("downloadRotatedBtn") || document.getElementById("downloadBtn");
    const convertAnotherBtn = document.getElementById("convertAnotherBtn");
    const rotationAngleSelect = document.getElementById("rotationAngleSelect");

    // Rotation Control Elements
    const rotateLeftBtn = document.getElementById("rotateLeftBtn");
    const rotateRightBtn = document.getElementById("rotateRightBtn");
    const angleBadge = document.getElementById("angleBadge");
    const pdfCanvasContainer = document.getElementById("pdfCanvasContainer");
    const pdfPreviewCanvas = document.getElementById("pdfPreviewCanvas");
    const fileNameDisplay = document.getElementById("fileNameDisplay");
    const removeFileBtn = document.getElementById("removeFileBtn");

    if (!uploadForm || !fileInput) return;

    let selectedFile = null;
    let currentAngle = 0;

    function updateRotationView() {
        if (pdfCanvasContainer) {
            pdfCanvasContainer.style.transform = `rotate(${currentAngle}deg)`;
            pdfCanvasContainer.style.transition = "transform 0.4s cubic-bezier(0.4, 0, 0.2, 1)";
        }
        if (angleBadge) {
            angleBadge.textContent = `${currentAngle}°`;
        }
        if (rotationAngleSelect) {
            rotationAngleSelect.value = String(currentAngle);
        }
    }

    if (rotateLeftBtn) {
        rotateLeftBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            currentAngle = (currentAngle - 90 + 360) % 360;
            updateRotationView();
        });
    }

    if (rotateRightBtn) {
        rotateRightBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            currentAngle = (currentAngle + 90) % 360;
            updateRotationView();
        });
    }

    if (chooseFileBtn) {
        chooseFileBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            fileInput.value = "";
            fileInput.click();
        });
    }

    uploadForm.addEventListener("click", (e) => {
        if (
            e.target.closest("button") ||
            e.target.closest("a") ||
            e.target.closest("select") ||
            e.target.closest(".remove-file-btn") ||
            e.target.closest(".selected-file-card") ||
            e.target.closest("#canvasViewport") ||
            (successCard && successCard.style.display !== "none")
        ) {
            return;
        }
        fileInput.value = "";
        fileInput.click();
    });

    fileInput.addEventListener("change", () => {
        if (fileInput.files && fileInput.files.length > 0) {
            selectedFile = fileInput.files[0];
            currentAngle = 0;
            renderSelectedFile();
        }
    });

    async function renderSelectedFile() {
        if (!selectedFilesContainer) return;

        if (!selectedFile) {
            selectedFilesContainer.style.display = "none";
            if (uploadActions) uploadActions.style.display = "none";
            if (uploadStatus) {
                uploadStatus.style.display = "none";
                uploadStatus.textContent = "";
            }
            return;
        }

        selectedFilesContainer.style.display = "flex";
        if (uploadActions) uploadActions.style.display = "block";
        if (uploadContent) uploadContent.style.display = "none";

        if (uploadStatus) {
            uploadStatus.style.display = "none";
            uploadStatus.textContent = "";
        }

        if (fileNameDisplay) {
            const sizeKB = (selectedFile.size / 1024).toFixed(1);
            fileNameDisplay.textContent = `${selectedFile.name} (${sizeKB} KB)`;
        }

        currentAngle = 0;
        updateRotationView();

        // Render first page of PDF using PDF.js if available
        if (window.pdfjsLib && pdfPreviewCanvas) {
            try {
                const arrayBuffer = await selectedFile.arrayBuffer();
                const pdf = await window.pdfjsLib.getDocument({ data: arrayBuffer }).promise;
                const page = await pdf.getPage(1);
                
                const viewport = page.getViewport({ scale: 1.0 });
                const maxDim = 320;
                const scale = Math.min(maxDim / viewport.width, maxDim / viewport.height);
                const scaledViewport = page.getViewport({ scale });

                const ctx = pdfPreviewCanvas.getContext("2d");
                pdfPreviewCanvas.width = scaledViewport.width;
                pdfPreviewCanvas.height = scaledViewport.height;

                await page.render({
                    canvasContext: ctx,
                    viewport: scaledViewport
                }).promise;

            } catch (err) {
                console.warn("Could not render PDF preview using PDF.js:", err);
                renderFallbackCanvas();
            }
        } else {
            renderFallbackCanvas();
        }
    }

    function renderFallbackCanvas() {
        if (!pdfPreviewCanvas) return;
        const ctx = pdfPreviewCanvas.getContext("2d");
        pdfPreviewCanvas.width = 240;
        pdfPreviewCanvas.height = 320;

        ctx.fillStyle = "#f8fafc";
        ctx.fillRect(0, 0, 240, 320);

        ctx.strokeStyle = "#cbd5e1";
        ctx.lineWidth = 2;
        ctx.strokeRect(10, 10, 220, 300);

        ctx.fillStyle = "#ef4444";
        ctx.font = "bold 42px sans-serif";
        ctx.textAlign = "center";
        ctx.fillText("PDF", 120, 140);

        ctx.fillStyle = "#64748b";
        ctx.font = "14px sans-serif";
        ctx.fillText("Page Preview", 120, 180);
    }

    if (removeFileBtn) {
        removeFileBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            removeFile();
        });
    }

    function removeFile() {
        selectedFile = null;
        fileInput.value = "";
        currentAngle = 0;
        if (selectedFilesContainer) {
            selectedFilesContainer.style.display = "none";
        }
        if (uploadContent) {
            uploadContent.style.display = "block";
        }
        if (uploadActions) uploadActions.style.display = "none";
        if (uploadStatus) {
            uploadStatus.style.display = "none";
            uploadStatus.textContent = "";
        }
    }

    // Drag and Drop
    let dragCounter = 0;

    ["dragenter", "dragover", "dragleave", "drop"].forEach(eventName => {
        uploadForm.addEventListener(eventName, e => {
            e.preventDefault();
            e.stopPropagation();
        });
    });

    uploadForm.addEventListener("dragenter", () => {
        dragCounter++;
        uploadForm.classList.add("drag-over");
    });

    uploadForm.addEventListener("dragover", (e) => {
        e.dataTransfer.dropEffect = "copy";
        if (!uploadForm.classList.contains("drag-over")) {
            uploadForm.classList.add("drag-over");
        }
    });

    uploadForm.addEventListener("dragleave", () => {
        dragCounter--;
        if (dragCounter <= 0) {
            dragCounter = 0;
            uploadForm.classList.remove("drag-over");
        }
    });

    uploadForm.addEventListener("drop", e => {
        dragCounter = 0;
        uploadForm.classList.remove("drag-over");
        const files = e.dataTransfer.files;
        if (files && files.length > 0) {
            selectedFile = files[0];
            renderSelectedFile();
        }
    });

    // Submit Form
    uploadForm.addEventListener("submit", async e => {
        e.preventDefault();

        if (!selectedFile) {
            if (uploadStatus) {
                uploadStatus.style.display = "block";
                uploadStatus.className = "upload-status upload-error";
                uploadStatus.textContent = "⚠ Please select a PDF file first.";
            }
            return;
        }

        if (!selectedFile.name.toLowerCase().endsWith(".pdf")) {
            if (uploadStatus) {
                uploadStatus.style.display = "block";
                uploadStatus.className = "upload-status upload-error";
                uploadStatus.textContent = "⚠ Please select a valid PDF file (.pdf).";
            }
            return;
        }

        if (uploadBtn) {
            uploadBtn.disabled = true;
            uploadBtn.innerHTML = `<i class="bi bi-arrow-repeat spin"></i> Rotating PDF...`;
        }

        if (uploadStatus) {
            uploadStatus.style.display = "block";
            uploadStatus.className = "upload-status upload-loading";
            uploadStatus.textContent = "Rotating PDF pages, please wait...";
        }

        const formData = new FormData();
        formData.append("file", selectedFile);
        formData.append("angle", String(currentAngle));

        try {
            const response = await fetch("/rotate-pdf/upload", {
                method: "POST",
                body: formData
            });

            const data = await response.json();

            if (!response.ok || !data.success) {
                throw new Error(data.message || "Failed to rotate PDF.");
            }

            if (uploadStatus) uploadStatus.style.display = "none";
            if (uploadContent) uploadContent.style.display = "none";
            if (uploadActions) uploadActions.style.display = "none";
            if (selectedFilesContainer) selectedFilesContainer.style.display = "none";

            if (successCard) {
                successCard.style.display = "block";
                successCard.classList.add("show");
            }

            if (downloadBtn) {
                downloadBtn.href = data.download_url;
                downloadBtn.setAttribute("download", data.filename || "rotated.pdf");
                downloadBtn.innerHTML = `<i class="bi bi-download"></i> Download Rotated PDF`;
            }

        } catch (error) {
            console.error("PDF Rotation error:", error);
            if (uploadStatus) {
                uploadStatus.style.display = "block";
                uploadStatus.className = "upload-status upload-error";
                uploadStatus.textContent = "❌ " + error.message;
            }
            if (uploadBtn) {
                uploadBtn.disabled = false;
                uploadBtn.innerHTML = `<i class="bi bi-arrow-clockwise"></i> Apply Rotation & Download`;
            }
        }
    });

    if (convertAnotherBtn) {
        convertAnotherBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            removeFile();

            if (uploadContent) uploadContent.style.display = "block";
            if (successCard) {
                successCard.style.display = "none";
                successCard.classList.remove("show");
            }
            if (uploadBtn) {
                uploadBtn.disabled = false;
                uploadBtn.innerHTML = `<i class="bi bi-arrow-clockwise"></i> Apply Rotation & Download`;
            }
        });
    }
});
