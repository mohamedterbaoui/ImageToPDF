// getting the upload button 
const uploadBtn = document.querySelector('#uploadBtn');

// Adding the onClick function for the upload button

uploadBtn.addEventListener('click', async () => {
    const input = document.querySelector('#imageInput');
    const files = input.files;

    if (files.length === 0) {
        alert("Please select at least one image.");
        return;
    }

    // Creating a FormData Objet and adding the images to it, to send it in a 
    // HTTP request
    const formData = new FormData();
    for (let i = 0; i < files.length; i++){
        console.log(i);
        formData.append("images", files[i]);
    }

    const progressMessage = document.querySelector('#message');
    progressMessage.textContent = "Uploading...";

    try {
        // Sending the files to the backend
        const response = await fetch('http://127.0.0.1:5000/upload', {
            method: 'POST',
            body: formData
        });

        // Handling the backend's response
        const data = await response.json();

        if (response.ok) {
            progressMessage.textContent = "Download your PDF at this link:";

            const divBlock = document.querySelector('.container');
            const link = document.createElement('a');

            link.href = `${data.pdf_url}`;
            link.target = "_blank";
            link.textContent = "Click Here";

            divBlock.appendChild(link);

        } else {
            progressMessage.textContent = "Error: " + data.error;
        } 
    } catch (error) {
        console.log(error);
        progressMessage.textContent = "Failed to connect to server.";
    }
});