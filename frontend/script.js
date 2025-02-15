document.addEventListener("DOMContentLoaded", () => {
  const navLinks = document.querySelectorAll(".nav-link");
  const sections = document.querySelectorAll(".container");

  navLinks.forEach((link) => {
    link.addEventListener("click", (e) => {
      e.preventDefault();
      sections.forEach((section) => (section.style.display = "none"));
      const targetId = e.target.getAttribute("data-target");
      document.getElementById(targetId).style.display = "block";
    });
  });
});

async function uploadFile(endpoint, inputSelector, messageSelector) {
  const input = document.querySelector(inputSelector);
  const files = input.files;
  if (files.length === 0) {
    alert("Please select a file.");
    return;
  }

  const formData = new FormData();
  for (let i = 0; i < files.length; i++) {
    // Check the file type and append to the correct field name
    const file = files[i];

    if (file.type === "application/pdf") {
      const fieldName = endpoint === "merge-pdfs" ? "pdfs" : "pdf";
      formData.append(fieldName, file); // Append PDF under "pdf" field
    } else if (file.type.startsWith("image/")) {
      formData.append("images", file); // Append image under "images" field
    } else {
      console.error("Unsupported file type:", file.type);
    }
  }

  const message = document.querySelector(messageSelector);
  message.textContent = "Processing...";

  try {
    const response = await fetch(
      `https://imagetopdf-3nph.onrender.com/${endpoint}`,
      {
        method: "POST",
        body: formData,
      }
    );

    const data = await response.json();
    console.log(response);
    if (response.ok) {
      const fileUrl = data.pdf_url || data.word_url; // Handle different responses
      if (fileUrl) {
        message.innerHTML = `Download your file: <a href="${fileUrl}" target="_blank">Click Here</a>`;
      } else {
        message.textContent = "Error: " + data.error;
      }
    }
  } catch (error) {
    message.textContent = "Failed to connect to server.";
  }
}

// Image to PDF
document
  .querySelector("#uploadBtn")
  .addEventListener("click", () =>
    uploadFile("upload", "#imageInputImageToPdf", "#message")
  );

// PDF to Word
document
  .querySelector("#convertWordBtn")
  .addEventListener("click", () =>
    uploadFile("convert-pdf-to-word", "#imageInputPdfToWord", "#wordMessage")
  );

// Merge PDFs
document
  .querySelector("#mergeBtn")
  .addEventListener("click", () =>
    uploadFile("merge-pdfs", "#imageInputMergePdfs", "#mergeMessage")
  );

// Compress PDF
document
  .querySelector("#compressBtn")
  .addEventListener("click", () =>
    uploadFile("compress-pdf", "#imageInputCompressPdf", "#compressMessage")
  );
