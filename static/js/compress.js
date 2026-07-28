/**
 * Compress PDF Tool Client Script
 * Configures tool_uploader for PDF compression.
 */
createToolUploader({
    formId: "compressPdfForm",
    fileInputId: "compressPdfFileInput",
    chooseBtnId: "chooseCompressBtn",
    uploadEndpoint: "/compress-pdf/upload",
    allowedExtensions: ["pdf"],
    invalidExtensionMsg: "Please select a valid PDF file (.pdf).",
    loadingMsg: "Compressing PDF file, please wait...",
    buttonIconClass: "bi-file-earmark-zip-fill",
    buttonText: "Compress PDF",
    downloadBtnText: "Download Compressed PDF",
    defaultOutputFilename: "compressed.pdf"
});
