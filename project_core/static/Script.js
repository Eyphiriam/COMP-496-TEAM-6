document.addEventListener('DOMContentLoaded', () => {
    let slideIndex = 0;

    // Show slides function
    function showSlides() {
        let slides = document.getElementsByClassName("slides");
        for (let i = 0; i < slides.length; i++) {
            slides[i].style.display = "none";
        }

        slideIndex++;
        if (slideIndex > slides.length) {
            slideIndex = 1;
        }

        slides[slideIndex - 1].style.display = "block";
        setTimeout(showSlides, 7000); // Change slide every 7 seconds
    }

    showSlides(); // Initialize slideshow

    // File input preview
    const fileInput = document.getElementById('file-input');
    const preview = document.getElementById('image-preview');
    const uploadForm = document.getElementById('upload-form');

    if (fileInput && preview) {
        fileInput.addEventListener('change', () => {
            const file = fileInput.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = (event) => {
                    preview.innerHTML = `<img src="${event.target.result}" alt="Image Preview">`;
                };
                reader.readAsDataURL(file);
            } else {
                preview.innerHTML = "";
            }
        });
    }

    // Upload button
    const uploadBtn = document.getElementById('upload-btn');
    if (uploadBtn && uploadForm) {
        uploadBtn.addEventListener('click', () => {
            const formData = new FormData(uploadForm);

            fetch('/upload_image/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                },
            })
            .then(response => {
                if (response.redirected) {
                    // If the server redirects on success, follow the redirect
                    window.location.href = response.url;
                } else {
                    // If the server returns JSON, handle it
                    return response.json();
                }
            })
            .then(data => {
                if (data) {
                    statusMessage.textContent = "Upload successful!";
                    statusMessage.style.color = "green";
                }
            })
            .catch((error) => {
                console.error('Error:', error);
                statusMessage.textContent = "Upload failed. Please try again.";
                statusMessage.style.color = "red";
            });
        });
    }


    // View history button
    const viewHistoryBtn = document.getElementById('view-history-btn');
    if (viewHistoryBtn) {
        viewHistoryBtn.addEventListener('click', () => {
            // Navigate to the history page directly
            window.location.href = '/view_history/';
        });
    }

    // Resubmit button
    const resubmitBtn = document.getElementById('resubmit-btn');
    if (resubmitBtn && uploadForm) {
        resubmitBtn.addEventListener('click', () => {
            const formData = new FormData(uploadForm);
            if (!formData.get('image')) {
                console.log('No new image selected for resubmit');
                return;
            }
            fetch('/resubmit/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                },
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    console.log(data.message);
                    window.location.href = '/results/';
                } else {
                    console.log(`Error: ${data.message}`);
                }
            })
            .catch(error => console.error(error));
        });
    }
    
    // Results button
    const resultsBtn = document.getElementById('results-btn');
    if (resultsBtn) {
        resultsBtn.addEventListener('click', () => {
            window.location.href = '/results/';
        });
    }

    // Additional dynamic elements (if needed)
    const predictionElem = document.getElementById('prediction');
    const confidenceElem = document.getElementById('confidence');
    const uploadedImageElem = document.getElementById('uploadedImage');


    // Optional navigation buttons
    const resubmitButton = document.getElementById('resubmitButton');
    if (resubmitButton) {
        resubmitButton.addEventListener('click', () => {
            window.location.href = '/upload_image/';
        });
    }

    const backButton = document.getElementById('backButton');
    if (backButton) {
        backButton.addEventListener('click', () => {
            window.location.href = '/';
        });
    }
});

// Before fetching in upload or resubmit:
statusMessage.textContent = "Uploading, please wait...";
statusMessage.style.color = "#333";

// On success or error:
statusMessage.textContent = "Upload successful!";
statusMessage.style.color = "green";
