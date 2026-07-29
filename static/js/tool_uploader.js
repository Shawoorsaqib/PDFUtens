/**
 * PDFUtens - Shared Tool Uploader Engine
 * Reusable utility to handle single-file upload drag-and-drop, state UI, fetch submission, and download rendering.
 */
function createToolUploader(options) {
    const {
        formId,
        fileInputId,
        chooseBtnId,
        uploadEndpoint,
        allowedExtensions = [],
        invalidExtensionMsg = "Invalid file type.",
        loadingMsg = "Processing file, please wait...",
        buttonIconClass = "bi-file-earmark",
        buttonText = "Upload & Process",
        downloadBtnText = "Download File",
        defaultOutputFilename = "result.pdf"
    } = options;

    function init() {
        const uploadForm = document.getElementById(formId);
        const fileInput = document.getElementById(fileInputId);
        const chooseBtn = document.getElementById(chooseBtnId);
        const uploadContent = document.getElementById("uploadContent");
        const selectedFilesContainer = document.getElementById("selectedFilesContainer");
        const uploadActions = document.getElementById("uploadActions");
        const uploadBtn = document.getElementById("uploadBtn") || (uploadForm ? uploadForm.querySelector("button[type='submit']") : null);
        const uploadStatus = document.getElementById("uploadStatus");
        const successCard = document.getElementById("successCard");
        const downloadBtn = document.getElementById("downloadBtn") || (uploadForm ? uploadForm.querySelector("a[download]") : null);
        const convertAnotherBtn = document.getElementById("convertAnotherBtn");
        const clearSelectionBtn = document.getElementById("clearSelectionBtn");

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
                e.target.closest("select") ||
                e.target.closest("textarea") ||
                e.target.closest("label") ||
                e.target.closest(".upload-actions") ||
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

            const card = document.createElement("div");
            card.className = "selected-file-card";

            const previewContainer = document.createElement("div");
            previewContainer.className = "preview-container active";

            const fileInfo = document.createElement("div");
            fileInfo.className = "file-info";
            fileInfo.innerHTML = `
                <p class="file-name">${selectedFile.name}</p>
                <span class="file-size">${sizeStr}</span>
            `;

            const removeBtn = document.createElement("button");
            removeBtn.className = "remove-file-btn";
            removeBtn.type = "button";
            removeBtn.title = "Remove file";
            removeBtn.innerHTML = `<i class="bi bi-x-lg"></i>`;
            removeBtn.addEventListener("click", (e) => {
                e.stopPropagation();
                removeFile();
            });

            card.appendChild(previewContainer);
            card.appendChild(fileInfo);
            card.appendChild(removeBtn);

            selectedFilesContainer.appendChild(card);

            if (typeof renderFilePreview === "function") {
                renderFilePreview(selectedFile, previewContainer);
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

        // Form Submission
        uploadForm.addEventListener("submit", async e => {
            e.preventDefault();

            if (!selectedFile) {
                if (uploadStatus) {
                    uploadStatus.style.display = "block";
                    uploadStatus.className = "upload-status upload-error";
                    uploadStatus.textContent = "⚠ Please select a file first.";
                }
                return;
            }

            const ext = selectedFile.name.split('.').pop().toLowerCase();
            if (allowedExtensions.length > 0 && !allowedExtensions.includes(ext)) {
                if (uploadStatus) {
                    uploadStatus.style.display = "block";
                    uploadStatus.className = "upload-status upload-error";
                    uploadStatus.textContent = `⚠ ${invalidExtensionMsg}`;
                }
                return;
            }

            if (uploadBtn) {
                uploadBtn.disabled = true;
                uploadBtn.innerHTML = `<i class="bi bi-arrow-repeat spin"></i> Processing...`;
            }

            if (uploadStatus) {
                uploadStatus.style.display = "block";
                uploadStatus.className = "upload-status upload-loading";
                uploadStatus.textContent = loadingMsg;
            }

            const formData = new FormData(uploadForm);
            if (selectedFile) {
                formData.set("file", selectedFile);
            }

            try {
                const response = await fetch(uploadEndpoint, {
                    method: "POST",
                    body: formData
                });

                const data = await response.json();

                if (!response.ok || !data.success) {
                    throw new Error(data.message || "Processing failed.");
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
                    downloadBtn.setAttribute("download", data.filename || defaultOutputFilename);
                    downloadBtn.innerHTML = `<i class="bi bi-download"></i> ${downloadBtnText}`;
                }

            } catch (error) {
                console.error("Processing error:", error);
                if (uploadStatus) {
                    uploadStatus.style.display = "block";
                    uploadStatus.className = "upload-status upload-error";
                    uploadStatus.textContent = "❌ " + error.message;
                }
                if (uploadBtn) {
                    uploadBtn.disabled = false;
                    uploadBtn.innerHTML = `<i class="bi ${buttonIconClass}"></i> ${buttonText}`;
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
                    uploadBtn.innerHTML = `<i class="bi ${buttonIconClass}"></i> ${buttonText}`;
                }
            });
        }

        if (clearSelectionBtn) {
            clearSelectionBtn.addEventListener("click", (e) => {
                e.stopPropagation();
                removeFile();
            });
        }
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
}
