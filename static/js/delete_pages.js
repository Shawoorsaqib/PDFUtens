/**
 * Delete Pages Tool Client Script
 * Configures tool_uploader for deleting PDF pages.
 */
createToolUploader({
    formId: "deletePagesForm",
    fileInputId: "deletePagesFileInput",
    chooseBtnId: "chooseDeletePagesBtn",
    uploadEndpoint: "/delete-pages/upload",
    allowedExtensions: ["pdf"],
    invalidExtensionMsg: "Please select a valid PDF file (.pdf).",
    loadingMsg: "Deleting selected pages, please wait...",
    buttonIconClass: "bi-trash-fill",
    buttonText: "Delete Selected Pages",
    downloadBtnText: "Download PDF",
    defaultOutputFilename: "deleted_pages.pdf"
});
