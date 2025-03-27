// static/js/script.js
document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('file');
    const uploadPlaceholder = document.getElementById('upload-placeholder');
    const uploadPreview = document.getElementById('upload-preview');
    const previewImage = document.getElementById('preview-image');
    const filenameDisplay = document.getElementById('filename-display');
    const removeFileButton = document.getElementById('remove-file');

    // Handle file selection
    fileInput.addEventListener('change', function() {
        if (this.files && this.files[0]) {
            const file = this.files[0];
            
            // Check file type
            const validTypes = ['image/jpeg', 'image/jpg', 'image/png'];
            if (!validTypes.includes(file.type)) {
                alert('Please select a valid image file (JPG or PNG)');
                resetFileInput();
                return;
            }
            
            // Update preview
            const reader = new FileReader();
            reader.onload = function(e) {
                previewImage.src = e.target.result;
                filenameDisplay.textContent = file.name;
                uploadPlaceholder.style.display = 'none';
                uploadPreview.style.display = 'block';
            };
            reader.readAsDataURL(file);
        }
    });
    
    // Remove selected file
    removeFileButton.addEventListener('click', function(e) {
        e.preventDefault();
        resetFileInput();
    });
    
    function resetFileInput() {
        fileInput.value = '';
        uploadPlaceholder.style.display = 'flex';
        uploadPreview.style.display = 'none';
        previewImage.src = '';
        filenameDisplay.textContent = '';
    }
    
    // Handle drag and drop
    const dropArea = document.querySelector('.file-upload');
    
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, preventDefaults, false);
    });
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    ['dragenter', 'dragover'].forEach(eventName => {
        dropArea.addEventListener(eventName, highlight, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, unhighlight, false);
    });
    
    function highlight() {
        dropArea.classList.add('highlight');
    }
    
    function unhighlight() {
        dropArea.classList.remove('highlight');
    }
    
    dropArea.addEventListener('drop', handleDrop, false);
    
    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        
        if (files.length) {
            fileInput.files = files;
            const event = new Event('change');
            fileInput.dispatchEvent(event);
        }
    }
});
