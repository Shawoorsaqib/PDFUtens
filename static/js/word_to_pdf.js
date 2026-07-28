/**
 * Word to PDF Tool Client Script
 * Configures tool_uploader for Word to PDF conversion.
 */
createToolUploader({
    formId: "wordToPdfForm",
    fileInputId: "wordToPdfFileInput",
    chooseBtnId: "chooseWordBtn",
    uploadEndpoint: "/word-to-pdf/upload",
    allowedExtensions: ["doc", "docx"],
    invalidExtensionMsg: "Please select a valid Word document (.doc or .docx).",
    loadingMsg: "Converting Word document to PDF, please wait...",
    buttonIconClass: "bi-file-earmark-pdf-fill",
    buttonText: "Convert to PDF",
    downloadBtnText: "Download PDF",
    defaultOutputFilename: "converted.pdf"
});
