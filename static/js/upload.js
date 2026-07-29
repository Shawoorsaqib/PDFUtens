document.addEventListener("DOMContentLoaded", () => {
    const uploadForm = document.getElementById("uploadForm");
    const fileInput = document.getElementById("fileInput");
    const chooseButton = document.getElementById("chooseFileBtn");
    const addMoreBtn = document.getElementById("addMoreBtn");
    const uploadContent = document.getElementById("uploadContent");
    const selectedFilesContainer = document.getElementById("selectedFilesContainer");
    const uploadActions = document.getElementById("uploadActions");
    const uploadBtn = document.getElementById("uploadBtn");
    const uploadStatus = document.getElementById("uploadStatus");
    const successCard = document.getElementById("successCard");
    const downloadBtn = document.getElementById("downloadBtn");
    const convertAnotherBtn = document.getElementById("convertAnotherBtn");
    const uploadBox = document.querySelector(".upload-box");

    if (!uploadForm || !fileInput || !uploadBox) return;

    let selectedFiles = [];

    // Helper: format file size
    function formatBytes(bytes, decimals = 2) {
        if (!bytes || bytes === 0) return '0 Bytes';
        const k = 1024;
        const dm = decimals < 0 ? 0 : decimals;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
    }

    // Open File Explorer on choose file button click
    if (chooseButton) {
        chooseButton.addEventListener("click", (e) => {
            e.stopPropagation();
            fileInput.value = "";
            fileInput.click();
        });
    }

    if (addMoreBtn) {
        addMoreBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            fileInput.value = "";
            fileInput.click();
        });
    }

    // Open File Explorer when clicking upload drop zone area
    uploadBox.addEventListener("click", (e) => {
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

    // Handle File Selection
    fileInput.addEventListener("change", () => {
        if (fileInput.files && fileInput.files.length > 0) {
            addFiles(Array.from(fileInput.files));
        }
    });

    function addFiles(newFiles) {
        newFiles.forEach(file => {
            const isDuplicate = selectedFiles.some(f => f.name === file.name && f.size === file.size && f.lastModified === file.lastModified);
            if (!isDuplicate) {
                selectedFiles.push(file);
            }
        });
        renderSelectedFiles();
    }

    function removeFile(index) {
        selectedFiles.splice(index, 1);
        renderSelectedFiles();
    }

    function resetFileSelection() {
        selectedFiles = [];
        fileInput.value = "";
        renderSelectedFiles();
    }

    function renderSelectedFiles() {
        if (!selectedFilesContainer) return;
        selectedFilesContainer.innerHTML = "";

        if (selectedFiles.length === 0) {
            selectedFilesContainer.style.display = "none";
            if (uploadActions) uploadActions.style.display = "none";
            if (uploadContent) uploadContent.classList.remove("file-selected");
            if (addMoreBtn) addMoreBtn.style.display = "none";
            if (uploadStatus) {
                uploadStatus.style.display = "none";
                uploadStatus.textContent = "";
                uploadStatus.className = "upload-status";
            }
            return;
        }

        selectedFilesContainer.style.display = "flex";
        if (uploadActions) uploadActions.style.display = "block";
        if (uploadContent) uploadContent.classList.add("file-selected");
        if (addMoreBtn) addMoreBtn.style.display = "inline-flex";

        if (uploadStatus) {
            uploadStatus.style.display = "none";
            uploadStatus.textContent = "";
            uploadStatus.className = "upload-status";
        }

        selectedFiles.forEach((file, index) => {
            const card = document.createElement("div");
            card.className = "selected-file-card";

            const previewContainer = document.createElement("div");
            previewContainer.className = "preview-container active";

            if (typeof renderFilePreview === "function") {
                renderFilePreview(file, previewContainer);
            }

            const fileInfo = document.createElement("div");
            fileInfo.className = "file-info";

            const fileNameP = document.createElement("p");
            fileNameP.className = "file-name";
            fileNameP.textContent = file.name;

            const fileSizeSpan = document.createElement("span");
            fileSizeSpan.className = "file-size";
            fileSizeSpan.textContent = formatBytes(file.size);

            fileInfo.appendChild(fileNameP);
            fileInfo.appendChild(fileSizeSpan);

            const removeBtn = document.createElement("button");
            removeBtn.type = "button";
            removeBtn.className = "remove-file-btn";
            removeBtn.title = "Remove selected file";
            removeBtn.innerHTML = `<i class="bi bi-x-lg"></i>`;
            removeBtn.addEventListener("click", (e) => {
                e.stopPropagation();
                removeFile(index);
            });

            card.appendChild(previewContainer);
            card.appendChild(fileInfo);
            card.appendChild(removeBtn);

            selectedFilesContainer.appendChild(card);
        });
    }

    // Drag and Drop Handling
    let dragCounter = 0;

    ["dragenter", "dragover", "dragleave", "drop"].forEach(eventName => {
        uploadBox.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
        });
        document.body.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
        });
    });

    uploadBox.addEventListener("dragenter", () => {
        dragCounter++;
        uploadBox.classList.add("drag-over");
    });

    uploadBox.addEventListener("dragover", (e) => {
        e.dataTransfer.dropEffect = "copy";
        if (!uploadBox.classList.contains("drag-over")) {
            uploadBox.classList.add("drag-over");
        }
    });

    uploadBox.addEventListener("dragleave", () => {
        dragCounter--;
        if (dragCounter <= 0) {
            dragCounter = 0;
            uploadBox.classList.remove("drag-over");
        }
    });

    uploadBox.addEventListener("drop", (e) => {
        dragCounter = 0;
        uploadBox.classList.remove("drag-over");

        const dt = e.dataTransfer;
        if (dt.files && dt.files.length > 0) {
            addFiles(Array.from(dt.files));
        }
    });

    // Upload Form Submission Handler
    uploadForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        if (selectedFiles.length === 0) {
            if (uploadStatus) {
                uploadStatus.style.display = "block";
                uploadStatus.textContent = "⚠ Please choose at least one file first.";
                uploadStatus.className = "upload-status upload-error";
            }
            return;
        }

        const formData = new FormData();
        selectedFiles.forEach(file => {
            formData.append("file", file);
        });

        if (uploadBtn) {
            uploadBtn.disabled = true;
            uploadBtn.innerHTML = `<i class="bi bi-arrow-repeat spin"></i> Uploading & Converting...`;
        }

        if (uploadStatus) {
            uploadStatus.style.display = "block";
            uploadStatus.textContent = "Uploading file(s), please wait...";
            uploadStatus.className = "upload-status upload-loading";
        }

        try {
            const response = await fetch("/upload", {
                method: "POST",
                body: formData
            });

            const data = await response.json();

            if (response.ok && data.success) {
                if (uploadStatus) uploadStatus.style.display = "none";

                if (downloadBtn) {
                    downloadBtn.href = data.download_url;
                    downloadBtn.setAttribute("download", data.pdf_file || "converted.pdf");
                }

                if (uploadContent) uploadContent.style.display = "none";
                if (selectedFilesContainer) selectedFilesContainer.style.display = "none";
                if (uploadActions) uploadActions.style.display = "none";

                if (successCard) {
                    successCard.style.display = "block";
                    successCard.classList.add("show");
                }
            } else {
                if (uploadStatus) {
                    uploadStatus.style.display = "block";
                    uploadStatus.textContent = data.message || "❌ Upload failed. Please try again.";
                    uploadStatus.className = "upload-status upload-error";
                }
                if (uploadBtn) {
                    uploadBtn.disabled = false;
                    uploadBtn.innerHTML = `<i class="bi bi-upload"></i> Upload & Convert`;
                }
            }
        } catch (error) {
            console.error("Upload error:", error);
            if (uploadStatus) {
                uploadStatus.style.display = "block";
                uploadStatus.textContent = "❌ Network error. Please check your connection and try again.";
                uploadStatus.className = "upload-status upload-error";
            }
            if (uploadBtn) {
                uploadBtn.disabled = false;
                uploadBtn.innerHTML = `<i class="bi bi-upload"></i> Upload & Convert`;
            }
        }
    });

    // Convert Another Button Handler
    if (convertAnotherBtn) {
        convertAnotherBtn.addEventListener("click", (e) => {
            e.stopPropagation();

            uploadForm.reset();
            resetFileSelection();

            if (uploadContent) uploadContent.style.display = "block";
            if (successCard) {
                successCard.style.display = "none";
                successCard.classList.remove("show");
            }

            if (uploadBtn) {
                uploadBtn.disabled = false;
                uploadBtn.innerHTML = `<i class="bi bi-upload"></i> Upload & Convert`;
            }
        });
    }
});
