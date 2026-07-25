const uploadForm = document.querySelector(".upload-box");
const chooseButton = document.getElementById("chooseFileBtn");
const fileInput = document.getElementById("fileInput");
const selectedFile = document.getElementById("selectedFile");
const uploadStatus = document.getElementById("uploadStatus");

// Open File Explorer
chooseButton.addEventListener("click", () => {
    fileInput.click();
});

// Show Selected Filename
fileInput.addEventListener("change", () => {

    if (fileInput.files.length > 0) {

        selectedFile.textContent = fileInput.files[0].name;

        // Clear any previous status message
        uploadStatus.textContent = "";
        uploadStatus.className = "upload-status";

    } else {

        selectedFile.textContent = "No file selected";

    }

});

// Upload File
uploadForm.addEventListener("submit", async (event) => {

    event.preventDefault();

    // No file selected
    if (fileInput.files.length === 0) {

        uploadStatus.textContent = "⚠ Please choose a file first.";
        uploadStatus.className = "upload-status upload-error";

        return;
    }

    const formData = new FormData();

    formData.append("file", fileInput.files[0]);

    try {

        // Uploading...
        uploadStatus.textContent = "Uploading...";
        uploadStatus.className = "upload-status upload-loading";

        const response = await fetch("/upload", {

            method: "POST",

            body: formData

        });

        const data = await response.json();
        if (data.success) {

            uploadStatus.innerHTML = `
        ✅ Upload Successful!<br><br>
        <a href="${data.download_url}" class="btn btn-primary">
            Download PDF
        </a>
    `;

            uploadStatus.className = "upload-status upload-success";

            uploadForm.reset();
            selectedFile.textContent = "No file selected";

        } else {

            uploadStatus.textContent = data.message;
            uploadStatus.className = "upload-status upload-error";

        }

    } catch (error) {

        console.error(error);

        uploadStatus.textContent = "❌ Upload failed. Please try again.";
        uploadStatus.className = "upload-status upload-error";

    }

});