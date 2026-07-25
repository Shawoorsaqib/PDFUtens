document.addEventListener("DOMContentLoaded", () => {
    const uploadForm = document.getElementById("uploadForm");
    const fileInput = document.getElementById("fileInput");
    const chooseButton = document.getElementById("chooseFileBtn");
    const uploadContent = document.getElementById("uploadContent");
    const selectedFileCard = document.getElementById("selectedFileCard");
    const selectedFileName = document.getElementById("selectedFileName");
    const selectedFileSize = document.getElementById("selectedFileSize");
    const previewContainer = document.getElementById("previewContainer");
    const imagePreview = document.getElementById("imagePreview");
    const documentIcon = document.getElementById("documentIcon");
    const removeFileBtn = document.getElementById("removeFileBtn");
    const uploadActions = document.getElementById("uploadActions");
    const uploadBtn = document.getElementById("uploadBtn");
    const uploadStatus = document.getElementById("uploadStatus");
    const successCard = document.getElementById("successCard");
    const downloadBtn = document.getElementById("downloadBtn");
    const convertAnotherBtn = document.getElementById("convertAnotherBtn");
    const uploadBox = document.querySelector(".upload-box");

    if (!uploadForm || !fileInput || !uploadBox) return;

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
            fileInput.click();
        });
    }

    // Open File Explorer when clicking upload drop zone area
    uploadBox.addEventListener("click", (e) => {
        if (
            e.target.closest("button") ||
            e.target.closest("a") ||
            e.target.closest("#removeFileBtn") ||
            (successCard && successCard.style.display !== "none")
        ) {
            return;
        }
        fileInput.click();
    });

    // Handle File Selection
    fileInput.addEventListener("change", handleFileSelection);

    function handleFileSelection() {
        if (fileInput.files && fileInput.files.length > 0) {
            const file = fileInput.files[0];

            if (selectedFileName) selectedFileName.textContent = file.name;
            if (selectedFileSize) selectedFileSize.textContent = formatBytes(file.size);

            if (file.type.startsWith("image/")) {
                const reader = new FileReader();
                reader.onload = function (e) {
                    if (imagePreview) {
                        imagePreview.src = e.target.result;
                        imagePreview.style.display = "block";
                    }
                    if (documentIcon) documentIcon.style.display = "none";
                    if (previewContainer) previewContainer.style.display = "block";
                };
                reader.readAsDataURL(file);
            } else {
                if (imagePreview) {
                    imagePreview.src = "";
                    imagePreview.style.display = "none";
                }
                
                const ext = file.name.split('.').pop().toLowerCase();
                let iconClass = "bi-file-earmark-text-fill";
                if (ext === "pdf") iconClass = "bi-file-earmark-pdf-fill";
                else if (["doc", "docx"].includes(ext)) iconClass = "bi-file-earmark-word-fill";
                else if (["xls", "xlsx"].includes(ext)) iconClass = "bi-file-earmark-excel-fill";
                else if (["ppt", "pptx"].includes(ext)) iconClass = "bi-file-earmark-ppt-fill";

                if (documentIcon) {
                    documentIcon.innerHTML = `<i class="bi ${iconClass}"></i>`;
                    documentIcon.style.display = "flex";
                }
                if (previewContainer) previewContainer.style.display = "block";
            }

            if (selectedFileCard) selectedFileCard.style.display = "flex";
            if (uploadActions) uploadActions.style.display = "block";
            if (uploadContent) uploadContent.classList.add("file-selected");

            if (uploadStatus) {
                uploadStatus.style.display = "none";
                uploadStatus.textContent = "";
                uploadStatus.className = "upload-status";
            }
        } else {
            resetFileSelection();
        }
    }

    function resetFileSelection() {
        fileInput.value = "";
        if (selectedFileCard) selectedFileCard.style.display = "none";
        if (uploadActions) uploadActions.style.display = "none";
        if (uploadContent) uploadContent.classList.remove("file-selected");
        
        if (previewContainer) previewContainer.style.display = "none";
        if (imagePreview) {
            imagePreview.src = "";
            imagePreview.style.display = "none";
        }
        if (documentIcon) documentIcon.style.display = "none";

        if (uploadStatus) {
            uploadStatus.style.display = "none";
            uploadStatus.textContent = "";
            uploadStatus.className = "upload-status";
        }
    }

    // Remove file button handler
    if (removeFileBtn) {
        removeFileBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            resetFileSelection();
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

    uploadBox.addEventListener("dragenter", (e) => {
        dragCounter++;
        uploadBox.classList.add("drag-over");
    });

    uploadBox.addEventListener("dragover", (e) => {
        e.dataTransfer.dropEffect = "copy";
        if (!uploadBox.classList.contains("drag-over")) {
            uploadBox.classList.add("drag-over");
        }
    });

    uploadBox.addEventListener("dragleave", (e) => {
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
        const files = dt.files;

        if (files && files.length > 0) {
            fileInput.files = files;
            handleFileSelection();
        }
    });

    // Upload Form Submission Handler
    uploadForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        if (!fileInput.files || fileInput.files.length === 0) {
            if (uploadStatus) {
                uploadStatus.style.display = "block";
                uploadStatus.textContent = "⚠ Please choose a file first.";
                uploadStatus.className = "upload-status upload-error";
            }
            return;
        }

        const formData = new FormData();
        formData.append("file", fileInput.files[0]);

        if (uploadBtn) {
            uploadBtn.disabled = true;
            uploadBtn.innerHTML = `<i class="bi bi-arrow-repeat spin"></i> Uploading & Converting...`;
        }

        if (uploadStatus) {
            uploadStatus.style.display = "block";
            uploadStatus.textContent = "Uploading file, please wait...";
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
                if (selectedFileCard) selectedFileCard.style.display = "none";
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