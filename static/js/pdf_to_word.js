document.addEventListener("DOMContentLoaded", () => {
    const uploadForm = document.getElementById("pdfToWordForm") || document.getElementById("uploadForm");
    const uploadContent = document.getElementById("uploadContent");
    const chooseFileBtn = document.getElementById("choosePdfBtn") || document.getElementById("chooseFileBtn");
    const fileInput = document.getElementById("pdfToWordFileInput") || document.getElementById("fileInput");
    const selectedFilesContainer = document.getElementById("selectedFilesContainer");
    const uploadActions = document.getElementById("uploadActions");
    const uploadBtn = document.getElementById("pdfToWordSubmitBtn") || document.getElementById("uploadBtn");
    const uploadStatus = document.getElementById("uploadStatus");
    const successCard = document.getElementById("successCard");
    const downloadBtn = document.getElementById("downloadWordBtn") || document.getElementById("downloadBtn");
    const convertAnotherBtn = document.getElementById("convertAnotherBtn");

    if (!uploadForm || !fileInput) return;

    let selectedFile = null;

    // Helper: format bytes
    function formatBytes(bytes) {
        if (!bytes || bytes === 0) return "0 KB";
        return (bytes / 1024).toFixed(1) + " KB";
    }

    // Open File Picker
    if (chooseFileBtn) {
        chooseFileBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            fileInput.value = "";
            fileInput.click();
        });
    }

    // Open File Picker when clicking drop zone area
    uploadForm.addEventListener("click", (e) => {
        if (
            e.target.closest("button") ||
            e.target.closest("a") ||
            e.target.closest(".remove-file-btn") ||
            e.target.closest(".selected-file-card") ||
            (successCard && successCard.style.display !== "none")
        ) {
            return;
        }
        fileInput.value = "";
        fileInput.click();
    });

    // File Selection Change
    fileInput.addEventListener("change", () => {
        if (fileInput.files && fileInput.files.length > 0) {
            selectedFile = fileInput.files[0];
            renderSelectedFile();
        }
    });

    // Render Selected File
    function renderSelectedFile() {
        if (!selectedFilesContainer) return;
        selectedFilesContainer.innerHTML = "";

        if (!selectedFile) {
            selectedFilesContainer.style.display = "none";
            if (uploadActions) uploadActions.style.display = "none";
            if (uploadStatus) {
                uploadStatus.style.display = "none";
                uploadStatus.textContent = "";
                uploadStatus.className = "upload-status";
            }
            return;
        }

        selectedFilesContainer.style.display = "flex";
        if (uploadActions) uploadActions.style.display = "block";

        if (uploadStatus) {
            uploadStatus.style.display = "none";
            uploadStatus.textContent = "";
            uploadStatus.className = "upload-status";
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
                <button class="remove-file-btn" id="removeFileBtn" type="button" title="Remove selected file">
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

    // Remove File
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

    // Drag & Drop
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

    // Upload PDF to Word Form Submission
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
            uploadBtn.innerHTML = `<i class="bi bi-arrow-repeat spin"></i> Converting PDF...`;
        }

        if (uploadStatus) {
            uploadStatus.style.display = "block";
            uploadStatus.className = "upload-status upload-loading";
            uploadStatus.textContent = "Converting PDF to Word, please wait...";
        }

        const formData = new FormData();
        formData.append("file", selectedFile);

        try {
            const response = await fetch("/pdf-to-word/upload", {
                method: "POST",
                body: formData
            });

            const data = await response.json();

            if (!response.ok || !data.success) {
                throw new Error(data.message || "Failed to convert PDF to Word.");
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
                downloadBtn.setAttribute("download", data.filename || "converted.docx");
                downloadBtn.innerHTML = `<i class="bi bi-download"></i> Download Word`;
            }

        } catch (error) {
            console.error("PDF to Word conversion error:", error);
            if (uploadStatus) {
                uploadStatus.style.display = "block";
                uploadStatus.className = "upload-status upload-error";
                uploadStatus.textContent = "❌ " + error.message;
            }
            if (uploadBtn) {
                uploadBtn.disabled = false;
                uploadBtn.innerHTML = `<i class="bi bi-file-earmark-word-fill"></i> Convert to Word`;
            }
        }
    });

    // Convert Another Button
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
                uploadBtn.innerHTML = `<i class="bi bi-file-earmark-word-fill"></i> Convert to Word`;
            }
        });
    }
});