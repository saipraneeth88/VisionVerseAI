// --- SCRIPT FOR VIDEO UPLOAD ---
document.getElementById('upload-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    const formData = new FormData(this);
    const summaryDiv = document.getElementById('summary');
    const fileInput = this.querySelector('input[type="file"]');

    // Validate file size
    const maxSize = 50 * 1024 * 1024; // 50MB
    if (fileInput.files[0].size > maxSize) {
        summaryDiv.innerHTML = `<p style="color:red;">Error: File size exceeds 50MB limit</p>`;
        return;
    }

    // Show loading state
    summaryDiv.innerHTML = `
        <div class="loading-state">
            <div class="loading-spinner"></div>
            <p><i>Analyzing video, please wait...</i></p>
            <small>This may take a few moments depending on the video size</small>
        </div>
    `;

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        const result = await response.json();
        
        if (result.status === 'success') {
            // Update summary with styled headings
            summaryDiv.innerHTML = `
                <h3 style="color: #2c3e50; font-size: 24px; margin-bottom: 15px;">AI Summary</h3>
                <div class="summary-content" style="color: #ffffff;">${
                    result.summary
                        .replace(/\*\*([^*]+)\*\*/g, '<strong style="color: #2c3e50; font-size: 18px; display: block; margin-top: 15px; margin-bottom: 10px;">$1</strong>')
                        .replace(/\n•/g, '<br>• ')
                        .replace(/\n/g, '<br>')
                }</div>
            `;

            // Store session ID
            localStorage.setItem('session_id', result.session_id);
        } else {
            summaryDiv.innerHTML = `<p style="color:red;">Error: ${result.error}</p>`;
        }
    } catch (error) {
        console.error('Upload error:', error);
        summaryDiv.innerHTML = `<p style="color:red;">Error: Failed to process video</p>`;
    }
});
document.getElementById('upload-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    const formData = new FormData(this);
    const summaryDiv = document.getElementById('summary');
    const fileInput = this.querySelector('input[type="file"]');
    const fileName = fileInput.files[0]?.name || '';
    
    // Update file name display
    this.querySelector('.file-name').textContent = fileName;
    
    summaryDiv.innerHTML = `
        <h3>AI Summary</h3>
        <div class="summary-content">
            <div class="loading-spinner"></div>
            <i>Analyzing video, please wait...</i>
        </div>
    `;

    const response = await fetch('/upload', {
        method: 'POST',
        body: formData
    });
    const result = await response.json();
    
    if (result.summary) {
        // Convert **bold** to styled strong tags and format line breaks
        let formatted = result.summary
            .replace(/\*\*([^*]+)\*\*/g, '<strong style="color: #2c3e50; font-size: 18px; display: block; margin-top: 15px; margin-bottom: 10px;">$1</strong>')
            .replace(/\n•/g, '<br>• ')
            .replace(/\n/g, '<br>');
        summaryDiv.innerHTML = `<h3 style="color: #2c3e50; font-size: 24px; margin-bottom: 15px;">Analysis Summary:</h3><div class="summary-content" style="color: #ffffff;">${formatted}</div>`;
    } else {
        summaryDiv.innerHTML = `<p style="color:red;">Error: ${result.error}</p>`;
    }
});

// --- SCRIPT FOR VIDEO PREVIEW ---
document.getElementById('upload-form').video.addEventListener('change', function(e) {
    const file = e.target.files[0];
    const preview = document.getElementById('video-preview');
    if (file) {
        const url = URL.createObjectURL(file);
        preview.src = url;
        preview.style.display = 'block';
    } else {
        preview.src = '';
        preview.style.display = 'none';
    }
});

// --- SCRIPT FOR CHAT ---
document.getElementById('chat-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    const questionInput = document.getElementById('question');
    const userQuestion = questionInput.value;
    const chatHistory = document.getElementById('chat-history');

    if (!userQuestion) return;

    // Display user's question
    chatHistory.innerHTML += `<div class="user-message">${userQuestion}</div>`;
    
    // Smooth scroll to the bottom
    chatHistory.scrollTo({
        top: chatHistory.scrollHeight,
        behavior: 'smooth'
    });
    
    // Send question to the backend
    const response = await fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: userQuestion })
    });
    const result = await response.json();

        // Display AI's response with plain formatting
    const formattedResponse = result.response
        .replace(/\*\*/g, '')  // Remove bold
        .replace(/\*/g, '•');  // Replace asterisks with bullet points
    chatHistory.innerHTML += `<div class="ai-message">${formattedResponse}</div>`;

    // Clear the input and smooth scroll to the bottom
    questionInput.value = '';
    chatHistory.scrollTo({
        top: chatHistory.scrollHeight,
        behavior: 'smooth'
    });
});
