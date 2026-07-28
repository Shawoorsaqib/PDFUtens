document.addEventListener("DOMContentLoaded", () => {
    const uploadForm = document.getElementById("removeWatermarkForm");
    const uploadContent = document.getElementById("uploadContent");
    const chooseBtn = document.getElementById("chooseRemoveWmBtn");
    const fileInput = document.getElementById("removeWatermarkFileInput");
    const selectedFilesContainer = document.getElementById("selectedFilesContainer");
    const uploadActions = document.getElementById("uploadActions");
    const uploadBtn = document.getElementById("removeWatermarkSubmitBtn");
    const uploadStatus = document.getElementById("uploadStatus");
    const successCard = document.getElementById("successCard");
    const downloadBtn = document.getElementById("downloadCleanedBtn");
    const convertAnotherBtn = document.getElementById("convertAnotherBtn");
    const removeWatermarkTextInput = document.getElementById("removeWatermarkTextInput");

    if (!uploadForm || !fileInput) return;

    let selectedFile = null;

    function formatBytes(bytes) {
        if (!bytes || bytes === 0) return "0 KB";
        return (bytes / 1024).toFixed(1) + " KB";
    }

    if (chooseBtn) {
        chooseBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            fileInput.value = "";
            fileInput.click();
        });
    }

    uploadForm.addEventListener("click", (e) => {
        if (
            e.target.closest("button") ||
            e.target.closest("a") ||
            e.target.closest("input") ||
            e.target.closest(".remove-file-btn") ||
            e.target.closest(".selected-file-card") ||
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
            renderSelectedFile();
        }
    });

    function renderSelectedFile() {
        if (!selectedFilesContainer) return;
        selectedFilesContainer.innerHTML = "";

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

        if (uploadStatus) {
            uploadStatus.style.display = "none";
            uploadStatus.textContent = "";
        }

        const sizeStr = formatBytes(selectedFile.size);

        selectedFilesContainer.innerHTML = `
            <div class="selected-file-card">
                <div class="document-icon" style="display: flex;">
                    <i class="bi bi-file-earmark-pdf-fill"></i>
                </div>
                <div class="file-info">
                    <p class="file-name">${selectedFile.name}</p>
                    <span class="file-size">${sizeStr}</span>
                </div>
                <button class="remove-file-btn" id="removeFileBtn" type="button" title="Remove file">
                    <i class="bi bi-x-lg"></i>
                </button>
            </div>
        `;

        const removeBtn = document.getElementById("removeFileBtn");
        if (removeBtn) {
            removeBtn.addEventListener("click", (e) => {
                e.stopPropagation();
                removeFile();
            });
        }
    }

    function removeFile() {
        selectedFile = null;
        fileInput.value = "";
        if (selectedFilesContainer) {
            selectedFilesContainer.innerHTML = "";
            selectedFilesContainer.style.display = "none";
        }
        if (uploadActions) uploadActions.style.display = "none";
        if (uploadStatus) {
            uploadStatus.style.display = "none";
            uploadStatus.textContent = "";
        }
    }

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

        if (uploadBtn) {
            uploadBtn.disabled = true;
            uploadBtn.innerHTML = `<i class="bi bi-arrow-repeat spin"></i> Removing Watermark...`;
        }

        if (uploadStatus) {
            uploadStatus.style.display = "block";
            uploadStatus.className = "upload-status upload-loading";
            uploadStatus.textContent = "Cleaning PDF file, please wait...";
        }

        const formData = new FormData();
        formData.append("file", selectedFile);
        if (removeWatermarkTextInput) formData.append("text", removeWatermarkTextInput.value.trim());

        try {
            const response = await fetch("/remove-watermark/upload", {
                method: "POST",
                body: formData
            });

            const data = await response.json();

            if (!response.ok || !data.success) {
                throw new Error(data.message || "Failed to remove watermark.");
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
                downloadBtn.setAttribute("download", data.filename || "cleaned.pdf");
                downloadBtn.innerHTML = `<i class="bi bi-download"></i> Download Cleaned PDF`;
            }

        } catch (error) {
            console.error("PDF Watermark removal error:", error);
            if (uploadStatus) {
                uploadStatus.style.display = "block";
                uploadStatus.className = "upload-status upload-error";
                uploadStatus.textContent = "❌ " + error.message;
            }
            if (uploadBtn) {
                uploadBtn.disabled = false;
                uploadBtn.innerHTML = `<i class="bi bi-eraser-fill"></i> Clean Watermarks & Download`;
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
                uploadBtn.innerHTML = `<i class="bi bi-eraser-fill"></i> Clean Watermarks & Download`;
            }
        });
    }
});
