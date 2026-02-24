document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const fileNameDisplay = document.getElementById('file-name');
    const generateBtn = document.getElementById('generate-btn');
    const apiKeyInput = document.getElementById('api-key');
    const btnText = document.querySelector('.btn-text');
    const loader = document.querySelector('.loader');
    const browseBtn = document.querySelector('.browse-btn');

    let selectedFile = null;

    // Trigger file input
    browseBtn.addEventListener('click', () => fileInput.click());
    dropZone.addEventListener('click', (e) => {
        if (e.target !== browseBtn) fileInput.click();
    });

    fileInput.addEventListener('change', (e) => handleFileSelect(e.target.files[0]));

    // Drag and Drop
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        handleFileSelect(e.dataTransfer.files[0]);
    });

    function handleFileSelect(file) {
        if (file && file.type.startsWith('image/')) {
            selectedFile = file;
            fileNameDisplay.textContent = file.name;
            checkFormValidity();
        } else {
            alert('Please upload a valid image file.');
        }
    }

    apiKeyInput.addEventListener('input', checkFormValidity);

    function checkFormValidity() {
        // If API key input is disabled (hidden/server-side), we don't need value
        const isApiKeyNeeded = !apiKeyInput.disabled && apiKeyInput.offsetParent !== null;
        const hasApiKey = apiKeyInput.value.trim().length > 0;

        if (selectedFile && (!isApiKeyNeeded || hasApiKey)) {
            generateBtn.disabled = false;
        } else {
            generateBtn.disabled = true;
        }
    }

    generateBtn.addEventListener('click', async () => {
        const isApiKeyNeeded = !apiKeyInput.disabled && apiKeyInput.offsetParent !== null;
        if (!selectedFile || (isApiKeyNeeded && !apiKeyInput.value)) return;

        setLoading(true);

        const formData = new FormData();
        formData.append('image', selectedFile);

        if (apiKeyInput.value.trim()) {
            formData.append('api_key', apiKeyInput.value.trim());
        }

        try {
            const response = await fetch('/process', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (response.ok && data.success) {
                // 1. Prepare ZIP download from base64
                const binaryString = window.atob(data.zip_base64);
                const bytes = new Uint8Array(binaryString.length);
                for (let i = 0; i < binaryString.length; i++) {
                    bytes[i] = binaryString.charCodeAt(i);
                }
                const blob = new Blob([bytes], { type: 'application/zip' });
                const url = window.URL.createObjectURL(blob);

                // Set up the download button in results
                const downloadBtn = document.getElementById('download-zip-btn');
                downloadBtn.onclick = () => {
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = 'tia_portal_assets.zip';
                    document.body.appendChild(a);
                    a.click();
                    a.remove();
                };

                // 2. Populate Code Preview
                const resultsSection = document.getElementById('results-section');
                const sclPreview = document.getElementById('scl-preview');
                const blockDisplay = document.getElementById('block-name-display');
                const copyBtn = document.getElementById('copy-scl-btn');

                blockDisplay.textContent = data.block_name;
                sclPreview.textContent = data.scl_raw;

                copyBtn.onclick = () => {
                    navigator.clipboard.writeText(data.scl_raw);
                    const originalText = copyBtn.textContent;
                    copyBtn.textContent = 'Copied!';
                    setTimeout(() => copyBtn.textContent = originalText, 2000);
                };

                // 3. Show Results
                resultsSection.classList.remove('hidden');
                resultsSection.scrollIntoView({ behavior: 'smooth' });

                // Also trigger download automatically once
                downloadBtn.click();

                showToast('Assets generated successfully!');
            } else {
                alert(`Error: ${data.error || 'Unknown error occurred'}`);
            }
        } catch (error) {
            console.error(error);
            alert('An unexpected network error occurred.');
        } finally {
            setLoading(false);
        }
    });

    function setLoading(isLoading) {
        generateBtn.disabled = isLoading;
        if (isLoading) {
            btnText.style.opacity = '0';
            loader.hidden = false;
        } else {
            btnText.style.opacity = '1';
            loader.hidden = true;
        }
    }

    function showToast(message) {
        const toast = document.getElementById('toast');
        toast.textContent = message;
        toast.classList.remove('hidden');
        toast.classList.add('show');
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.classList.add('hidden'), 300);
        }, 3000);
    }
});
