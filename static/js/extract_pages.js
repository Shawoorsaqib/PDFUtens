/**
 * Extract Pages Tool Client Script
 * Configures tool_uploader for extracting PDF pages.
 */
createToolUploader({
    formId: "extractPagesForm",
    fileInputId: "extractPagesFileInput",
    chooseBtnId: "chooseExtractPagesBtn",
    uploadEndpoint: "/extract-pages/upload",
    allowedExtensions: ["pdf"],
    invalidExtensionMsg: "Please select a valid PDF file (.pdf).",
    loadingMsg: "Extracting selected pages, please wait...",
    buttonIconClass: "bi-box-arrow-up-right",
    buttonText: "Extract Selected Pages",
    downloadBtnText: "Download Extracted PDF",
    defaultOutputFilename: "extracted_pages.pdf"
});
