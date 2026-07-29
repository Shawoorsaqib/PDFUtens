/**
 * Page Numbers Tool Client Script
 * Configures tool_uploader for adding page numbers.
 */
createToolUploader({
    formId: "pageNumbersForm",
    fileInputId: "pageNumbersFileInput",
    chooseBtnId: "choosePageNumbersBtn",
    uploadEndpoint: "/add-page-numbers/upload",
    allowedExtensions: ["pdf"],
    invalidExtensionMsg: "Please select a valid PDF file (.pdf).",
    loadingMsg: "Adding page numbers to PDF, please wait...",
    buttonIconClass: "bi-123",
    buttonText: "Add Page Numbers",
    downloadBtnText: "Download Numbered PDF",
    defaultOutputFilename: "numbered.pdf"
});
