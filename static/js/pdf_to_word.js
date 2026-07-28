/**
 * PDF to Word Tool Client Script
 * Configures tool_uploader for PDF to Word conversion.
 */
createToolUploader({
    formId: "pdfToWordForm",
    fileInputId: "pdfToWordFileInput",
    chooseBtnId: "choosePdfBtn",
    uploadEndpoint: "/pdf-to-word/upload",
    allowedExtensions: ["pdf"],
    invalidExtensionMsg: "Please select a valid PDF file (.pdf).",
    loadingMsg: "Converting PDF to Word, please wait...",
    buttonIconClass: "bi-file-earmark-word-fill",
    buttonText: "Convert to Word",
    downloadBtnText: "Download Word",
    defaultOutputFilename: "converted.docx"
});