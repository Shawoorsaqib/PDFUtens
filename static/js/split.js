document.addEventListener("DOMContentLoaded", () => {
    const splitForm = document.getElementById("splitForm");
    const splitFileInput = document.getElementById("splitFileInput");
    const chooseSplitFileBtn = document.getElementById("chooseSplitFileBtn");
    const changePdfBtn = document.getElementById("changePdfBtn");
    const uploadContent = document.getElementById("uploadContent");
    const selectedFilesContainer = document.getElementById("selectedFilesContainer");
    const splitOptions = document.getElementById("splitOptions");
    const rangeSection = document.getElementById("rangeSection");
    const fromPage = document.getElementById("fromPage");
    const toPage = document.getElementById("toPage");
    const addRangeBtn = document.getElementById("addRangeBtn");
    const rangeList = document.getElementById("rangeList");
    const uploadActions = document.getElementById("uploadActions");
    const splitSubmitBtn = document.getElementById("splitSubmitBtn");
    const uploadStatus = document.getElementById("uploadStatus");
    const successCard = document.getElementById("successCard");
    const downloadSplitBtn = document.getElementById("downloadSplitBtn");
    const splitAnotherBtn = document.getElementById("splitAnotherBtn");
    const uploadBox = document.querySelector(".upload-box");
    const splitModeRadios = document.querySelectorAll('input[name="splitMode"]');

    if (!splitForm || !splitFileInput || !uploadBox) return;

    let selectedFile = null;
    let pageRanges = [];

    // Helper: format file size
    function formatBytes(bytes, decimals = 2) {
        if (!bytes || bytes === 0) return '0 Bytes';
        const k = 1024;
        const dm = decimals < 0 ? 0 : decimals;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
    }

    // Toggle Split Mode Radios
    splitModeRadios.forEach(radio => {
        radio.addEventListener("change", () => {
            if (radio.value === "range" && radio.checked) {
                if (rangeSection) rangeSection.style.display = "block";
            } else if (radio.value === "all" && radio.checked) {
                if (rangeSection) rangeSection.style.display = "none";
            }
        });
    });

    // Add Custom Range
    if (addRangeBtn) {
        addRangeBtn.addEventListener("click", () => {
            const fromVal = parseInt(fromPage.value, 10);
            const toVal = parseInt(toPage.value, 10);

            if (isNaN(fromVal) || isNaN(toVal)) {
                alert("Please enter both 'From Page' and 'To Page' numbers.");
                return;
            }

            if (fromVal < 1 || toVal < 1) {
                alert("Page numbers must be 1 or greater.");
                return;
            }

            if (fromVal > toVal) {
                alert("'From Page' cannot be greater than 'To Page'.");
                return;
            }

            // Prevent exact duplicates
            const isDuplicate = pageRanges.some(r => r.from === fromVal && r.to === toVal);
            if (!isDuplicate) {
                pageRanges.push({ from: fromVal, to: toVal });
                renderRanges();
            }

            fromPage.value = "";
            toPage.value = "";
        });
    }

    function renderRanges() {
        if (!rangeList) return;
        rangeList.innerHTML = "";

        pageRanges.forEach((range, index) => {
            const tag = document.createElement("div");
            tag.className = "range-item";
            tag.innerHTML = `
                <span>Pages ${range.from} - ${range.to}</span>
                <button type="button" class="remove-range-btn" title="Remove range">
                    <i class="bi bi-x-lg"></i>
                </button>
            `;
            tag.querySelector(".remove-range-btn").addEventListener("click", () => {
                removeRange(index);
            });
            rangeList.appendChild(tag);
        });
    }

    function removeRange(index) {
        pageRanges.splice(index, 1);
        renderRanges();
    }

    // Open File Explorer when clicking Choose PDF
    if (chooseSplitFileBtn) {
        chooseSplitFileBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            splitFileInput.value = "";
            splitFileInput.click();
        });
    }

    if (changePdfBtn) {
        changePdfBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            splitFileInput.value = "";
            splitFileInput.click();
        });
    }

    // Open File Explorer when clicking drop zone area
    uploadBox.addEventListener("click", (e) => {
        if (
            e.target.closest("button") ||
            e.target.closest("a") ||
            e.target.closest(".remove-file-btn") ||
            e.target.closest(".split-options-box") ||
            (successCard && successCard.style.display !== "none")
        ) {
            return;
        }
        splitFileInput.value = "";
        splitFileInput.click();
    });

    // Handle File Selection
    splitFileInput.addEventListener("change", () => {
        if (splitFileInput.files && splitFileInput.files.length > 0) {
            setFile(splitFileInput.files[0]);
        }
    });

    function setFile(file) {
        if (!file.name.toLowerCase().endswith?.(".pdf") && file.type !== "application/pdf" && !file.name.toLowerCase().endsWith(".pdf")) {
            alert("Only PDF files are supported.");
            return;
        }

        selectedFile = file;
        renderSelectedFile();
    }

    function renderSelectedFile() {
        if (!selectedFilesContainer) return;
        selectedFilesContainer.innerHTML = "";

        if (!selectedFile) {
            selectedFilesContainer.style.display = "none";
            if (splitOptions) splitOptions.style.display = "none";
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
        if (splitOptions) splitOptions.style.display = "block";
        if (uploadActions) uploadActions.style.display = "block";
        if (uploadContent) uploadContent.classList.add("file-selected");

        const card = document.createElement("div");
        card.className = "selected-file-card";

        const previewContainer = document.createElement("div");
        previewContainer.className = "preview-container active";

        const docIcon = document.createElement("div");
        docIcon.className = "document-icon";
        docIcon.innerHTML = `<i class="bi bi-file-earmark-pdf-fill"></i>`;
        previewContainer.appendChild(docIcon);

        const fileInfo = document.createElement("div");
        fileInfo.className = "file-info";

        const fileNameP = document.createElement("p");
        fileNameP.className = "file-name";
        fileNameP.textContent = selectedFile.name;

        const fileSizeSpan = document.createElement("span");
        fileSizeSpan.className = "file-size";
        fileSizeSpan.textContent = formatBytes(selectedFile.size);

        fileInfo.appendChild(fileNameP);
        fileInfo.appendChild(fileSizeSpan);

        const removeBtn = document.createElement("button");
        removeBtn.type = "button";
        removeBtn.className = "remove-file-btn";
        removeBtn.title = "Remove PDF";
        removeBtn.innerHTML = `<i class="bi bi-x-lg"></i>`;
        removeBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            selectedFile = null;
            splitFileInput.value = "";
            renderSelectedFile();
        });

        card.appendChild(previewContainer);
        card.appendChild(fileInfo);
        card.appendChild(removeBtn);

        selectedFilesContainer.appendChild(card);
    }

    // Drag & Drop Handling
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
            setFile(dt.files[0]);
        }
    });

    // Form Submission
    splitForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        if (!selectedFile) {
            if (uploadStatus) {
                uploadStatus.style.display = "block";
                uploadStatus.textContent = "⚠ Please select a PDF file first.";
                uploadStatus.className = "upload-status upload-error";
            }
            return;
        }

        const selectedMode = document.querySelector('input[name="splitMode"]:checked')?.value || "all";

        if (selectedMode === "range") {
            // Auto add range from input boxes if user typed but forgot to click 'Add Range'
            const fromVal = parseInt(fromPage.value, 10);
            const toVal = parseInt(toPage.value, 10);
            if (!isNaN(fromVal) && !isNaN(toVal) && fromVal >= 1 && toVal >= fromVal) {
                const isDup = pageRanges.some(r => r.from === fromVal && r.to === toVal);
                if (!isDup) {
                    pageRanges.push({ from: fromVal, to: toVal });
                    renderRanges();
                    fromPage.value = "";
                    toPage.value = "";
                }
            }

            if (pageRanges.length === 0) {
                if (uploadStatus) {
                    uploadStatus.style.display = "block";
                    uploadStatus.textContent = "⚠ Please specify at least one page range.";
                    uploadStatus.className = "upload-status upload-error";
                }
                return;
            }
        }

        const formData = new FormData();
        formData.append("file", selectedFile);
        formData.append("split_mode", selectedMode);
        if (selectedMode === "range") {
            formData.append("ranges", JSON.stringify(pageRanges));
        }

        if (splitSubmitBtn) {
            splitSubmitBtn.disabled = true;
            splitSubmitBtn.innerHTML = `<i class="bi bi-arrow-repeat spin"></i> Splitting PDF...`;
        }

        if (uploadStatus) {
            uploadStatus.style.display = "block";
            uploadStatus.textContent = "Splitting PDF file, please wait...";
            uploadStatus.className = "upload-status upload-loading";
        }

        try {
            const response = await fetch("/split-pdf/upload", {
                method: "POST",
                body: formData
            });

            const data = await response.json();

            if (response.ok && data.success) {
                if (uploadStatus) uploadStatus.style.display = "none";

                if (downloadSplitBtn) {
                    downloadSplitBtn.href = data.download_url;
                    downloadSplitBtn.setAttribute("download", data.filename || "split.zip");
                }

                if (uploadContent) uploadContent.style.display = "none";
                if (selectedFilesContainer) selectedFilesContainer.style.display = "none";
                if (splitOptions) splitOptions.style.display = "none";
                if (uploadActions) uploadActions.style.display = "none";

                if (successCard) {
                    successCard.style.display = "block";
                    successCard.classList.add("show");
                }
            } else {
                if (uploadStatus) {
                    uploadStatus.style.display = "block";
                    uploadStatus.textContent = data.message || "❌ Failed to split PDF. Please try again.";
                    uploadStatus.className = "upload-status upload-error";
                }
                if (splitSubmitBtn) {
                    splitSubmitBtn.disabled = false;
                    splitSubmitBtn.innerHTML = `<i class="bi bi-scissors"></i> Split PDF`;
                }
            }
        } catch (error) {
            console.error("Split error:", error);
            if (uploadStatus) {
                uploadStatus.style.display = "block";
                uploadStatus.textContent = "❌ Network error. Please check your connection and try again.";
                uploadStatus.className = "upload-status upload-error";
            }
            if (splitSubmitBtn) {
                splitSubmitBtn.disabled = false;
                splitSubmitBtn.innerHTML = `<i class="bi bi-scissors"></i> Split PDF`;
            }
        }
    });

    // Split Another Button Handler
    if (splitAnotherBtn) {
        splitAnotherBtn.addEventListener("click", (e) => {
            e.stopPropagation();

            splitForm.reset();
            selectedFile = null;
            pageRanges = [];
            renderRanges();
            renderSelectedFile();

            if (uploadContent) uploadContent.style.display = "block";
            if (successCard) {
                successCard.style.display = "none";
                successCard.classList.remove("show");
            }

            if (splitSubmitBtn) {
                splitSubmitBtn.disabled = false;
                splitSubmitBtn.innerHTML = `<i class="bi bi-scissors"></i> Split PDF`;
            }
        });
    }
});