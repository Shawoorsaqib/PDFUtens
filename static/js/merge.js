document.addEventListener("DOMContentLoaded", () => {
    const mergeForm = document.getElementById("mergeForm");
    const mergeFileInput = document.getElementById("mergeFileInput");
    const chooseMergeFilesBtn = document.getElementById("chooseMergeFilesBtn");
    const addMorePdfsBtn = document.getElementById("addMorePdfsBtn");
    const uploadContent = document.getElementById("uploadContent");
    const selectedFilesContainer = document.getElementById("selectedFilesContainer");
    const uploadActions = document.getElementById("uploadActions");
    const mergeSubmitBtn = document.getElementById("mergeSubmitBtn");
    const uploadStatus = document.getElementById("uploadStatus");
    const successCard = document.getElementById("successCard");
    const downloadMergedBtn = document.getElementById("downloadMergedBtn");
    const mergeAnotherBtn = document.getElementById("mergeAnotherBtn");
    const uploadBox = document.querySelector(".upload-box");

    if (!mergeForm || !mergeFileInput || !uploadBox) return;

    let selectedFiles = [];

    // Helper: Format file size
    function formatBytes(bytes, decimals = 2) {
        if (!bytes || bytes === 0) return '0 Bytes';
        const k = 1024;
        const dm = decimals < 0 ? 0 : decimals;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
    }

    // Open File Explorer when clicking Choose PDFs button
    if (chooseMergeFilesBtn) {
        chooseMergeFilesBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            mergeFileInput.value = "";
            mergeFileInput.click();
        });
    }

    // Open File Explorer when clicking + Add More PDFs button
    if (addMorePdfsBtn) {
        addMorePdfsBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            mergeFileInput.value = "";
            mergeFileInput.click();
        });
    }

    // Open File Explorer when clicking drop zone (outside of buttons/cards)
    uploadBox.addEventListener("click", (e) => {
        if (
            e.target.closest("button") ||
            e.target.closest("a") ||
            e.target.closest(".remove-file-btn") ||
            e.target.closest(".reorder-btn") ||
            e.target.closest(".selected-file-card") ||
            (successCard && successCard.style.display !== "none")
        ) {
            return;
        }
        mergeFileInput.value = "";
        mergeFileInput.click();
    });

    // Handle File Selection
    mergeFileInput.addEventListener("change", () => {
        if (mergeFileInput.files && mergeFileInput.files.length > 0) {
            addFiles(Array.from(mergeFileInput.files));
        }
    });

    function addFiles(newFiles) {
        const pdfFiles = newFiles.filter(file => 
            file.name.toLowerCase().endsWith(".pdf") || file.type === "application/pdf"
        );

        pdfFiles.forEach(file => {
            const isDuplicate = selectedFiles.some(
                f => f.name === file.name && f.size === file.size && f.lastModified === file.lastModified
            );
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

    function moveFile(index, direction) {
        const targetIndex = index + direction;
        if (targetIndex < 0 || targetIndex >= selectedFiles.length) return;
        const temp = selectedFiles[index];
        selectedFiles[index] = selectedFiles[targetIndex];
        selectedFiles[targetIndex] = temp;
        renderSelectedFiles();
    }

    function resetFileSelection() {
        selectedFiles = [];
        mergeFileInput.value = "";
        renderSelectedFiles();
    }

    function renderSelectedFiles() {
        if (!selectedFilesContainer) return;
        selectedFilesContainer.innerHTML = "";

        if (selectedFiles.length === 0) {
            selectedFilesContainer.style.display = "none";
            if (uploadActions) uploadActions.style.display = "none";
            if (uploadContent) uploadContent.classList.remove("file-selected");
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

        if (uploadStatus) {
            uploadStatus.style.display = "none";
            uploadStatus.textContent = "";
            uploadStatus.className = "upload-status";
        }

        selectedFiles.forEach((file, index) => {
            const card = document.createElement("div");
            card.className = "selected-file-card";

            // Position Order Badge
            const badge = document.createElement("div");
            badge.className = "file-order-badge";
            badge.textContent = index + 1;

            // Icon & Thumbnail Preview Container
            const previewContainer = document.createElement("div");
            previewContainer.className = "preview-container active";

            if (typeof renderFilePreview === "function") {
                renderFilePreview(file, previewContainer);
            }

            // File Info
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

            // Actions Group (Move Up, Move Down, Remove)
            const actionsGroup = document.createElement("div");
            actionsGroup.className = "file-actions-group";

            // Move Up Button
            const moveUpBtn = document.createElement("button");
            moveUpBtn.type = "button";
            moveUpBtn.className = "reorder-btn";
            moveUpBtn.title = "Move Up";
            moveUpBtn.disabled = index === 0;
            moveUpBtn.innerHTML = `<i class="bi bi-arrow-up"></i>`;
            moveUpBtn.addEventListener("click", (e) => {
                e.stopPropagation();
                moveFile(index, -1);
            });

            // Move Down Button
            const moveDownBtn = document.createElement("button");
            moveDownBtn.type = "button";
            moveDownBtn.className = "reorder-btn";
            moveDownBtn.title = "Move Down";
            moveDownBtn.disabled = index === selectedFiles.length - 1;
            moveDownBtn.innerHTML = `<i class="bi bi-arrow-down"></i>`;
            moveDownBtn.addEventListener("click", (e) => {
                e.stopPropagation();
                moveFile(index, 1);
            });

            // Remove Button
            const removeBtn = document.createElement("button");
            removeBtn.type = "button";
            removeBtn.className = "remove-file-btn";
            removeBtn.title = "Remove selected file";
            removeBtn.innerHTML = `<i class="bi bi-x-lg"></i>`;
            removeBtn.addEventListener("click", (e) => {
                e.stopPropagation();
                removeFile(index);
            });

            actionsGroup.appendChild(moveUpBtn);
            actionsGroup.appendChild(moveDownBtn);
            actionsGroup.appendChild(removeBtn);

            card.appendChild(badge);
            card.appendChild(previewContainer);
            card.appendChild(fileInfo);
            card.appendChild(actionsGroup);

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

    // Merge Form Submission
    mergeForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        if (selectedFiles.length < 2) {
            if (uploadStatus) {
                uploadStatus.style.display = "block";
                uploadStatus.textContent = "⚠ Please select at least two PDF files to merge.";
                uploadStatus.className = "upload-status upload-error";
            }
            return;
        }

        const formData = new FormData();
        selectedFiles.forEach(file => {
            formData.append("file", file);
        });

        if (mergeSubmitBtn) {
            mergeSubmitBtn.disabled = true;
            mergeSubmitBtn.innerHTML = `<i class="bi bi-arrow-repeat spin"></i> Merging PDFs...`;
        }

        if (uploadStatus) {
            uploadStatus.style.display = "block";
            uploadStatus.textContent = "Merging PDF files, please wait...";
            uploadStatus.className = "upload-status upload-loading";
        }

        try {
            const response = await fetch("/merge-pdf/upload", {
                method: "POST",
                body: formData
            });

            const data = await response.json();

            if (response.ok && data.success) {
                if (uploadStatus) uploadStatus.style.display = "none";

                if (downloadMergedBtn) {
                    downloadMergedBtn.href = data.download_url;
                    downloadMergedBtn.setAttribute("download", data.filename || "merged.pdf");
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
                    uploadStatus.textContent = data.message || "❌ Failed to merge PDFs. Please try again.";
                    uploadStatus.className = "upload-status upload-error";
                }
                if (mergeSubmitBtn) {
                    mergeSubmitBtn.disabled = false;
                    mergeSubmitBtn.innerHTML = `<i class="bi bi-files"></i> Merge PDFs`;
                }
            }
        } catch (error) {
            console.error("Merge error:", error);
            if (uploadStatus) {
                uploadStatus.style.display = "block";
                uploadStatus.textContent = "❌ Network error. Please check your connection and try again.";
                uploadStatus.className = "upload-status upload-error";
            }
            if (mergeSubmitBtn) {
                mergeSubmitBtn.disabled = false;
                mergeSubmitBtn.innerHTML = `<i class="bi bi-files"></i> Merge PDFs`;
            }
        }
    });

    // Merge Another Button Handler
    if (mergeAnotherBtn) {
        mergeAnotherBtn.addEventListener("click", (e) => {
            e.stopPropagation();

            mergeForm.reset();
            resetFileSelection();

            if (uploadContent) uploadContent.style.display = "block";
            if (successCard) {
                successCard.style.display = "none";
                successCard.classList.remove("show");
            }

            if (mergeSubmitBtn) {
                mergeSubmitBtn.disabled = false;
                mergeSubmitBtn.innerHTML = `<i class="bi bi-files"></i> Merge PDFs`;
            }
        });
    }
});