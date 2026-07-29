/**
 * Reorder Pages Tool Client Script
 * Configures tool_uploader for reordering PDF pages.
 */
createToolUploader({
    formId: "reorderPagesForm",
    fileInputId: "reorderPagesFileInput",
    chooseBtnId: "chooseReorderPagesBtn",
    uploadEndpoint: "/reorder-pages/upload",
    allowedExtensions: ["pdf"],
    invalidExtensionMsg: "Please select a valid PDF file (.pdf).",
    loadingMsg: "Reordering PDF pages, please wait...",
    buttonIconClass: "bi-arrow-down-up",
    buttonText: "Save New Page Order",
    downloadBtnText: "Download Reordered PDF",
    defaultOutputFilename: "reordered.pdf"
});
