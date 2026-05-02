document.addEventListener('DOMContentLoaded', () => {
    const startBtn = document.getElementById('startBtn');
    const stopBtn = document.getElementById('stopBtn');
    const botStatus = document.getElementById('botStatus');
    const statusText = botStatus.querySelector('.status-text');
    const settingsContainer = document.getElementById('settingsContainer');
    const settingsForm = document.getElementById('settingsForm');
    const saveSettingsBtn = document.getElementById('saveSettingsBtn');
    const saveStatus = document.getElementById('saveStatus');

    let currentSettings = {};
    let isBotRunning = false;

    // Fetch initial status and settings
    fetchStatus();
    fetchSettings();

    // Poll status every 3 seconds
    setInterval(fetchStatus, 3000);

    // Event Listeners
    startBtn.addEventListener('click', startBot);
    stopBtn.addEventListener('click', stopBot);
    settingsForm.addEventListener('submit', saveSettings);

    async function fetchStatus() {
        try {
            const res = await fetch('/api/bot/status');
            const data = await res.json();
            updateStatusUI(data.running);
        } catch (error) {
            console.error('Error fetching status:', error);
            statusText.textContent = 'Connection Error';
            botStatus.className = 'status-badge stopped';
        }
    }

    function updateStatusUI(running) {
        isBotRunning = running;
        if (running) {
            botStatus.className = 'status-badge running';
            statusText.textContent = 'Running';
            startBtn.disabled = true;
            stopBtn.disabled = false;
        } else {
            botStatus.className = 'status-badge stopped';
            statusText.textContent = 'Stopped';
            startBtn.disabled = false;
            stopBtn.disabled = true;
        }
    }

    async function startBot() {
        startBtn.disabled = true;
        startBtn.textContent = 'Starting...';
        try {
            const res = await fetch('/api/bot/start', { method: 'POST' });
            if (!res.ok) throw new Error('Failed to start');
            await fetchStatus();
        } catch (error) {
            console.error(error);
            alert('Failed to start bot. Check server logs.');
        } finally {
            startBtn.textContent = 'Start Bot';
        }
    }

    async function stopBot() {
        stopBtn.disabled = true;
        stopBtn.textContent = 'Stopping...';
        try {
            const res = await fetch('/api/bot/stop', { method: 'POST' });
            if (!res.ok) throw new Error('Failed to stop');
            await fetchStatus();
        } catch (error) {
            console.error(error);
            alert('Failed to stop bot. Check server logs.');
        } finally {
            stopBtn.textContent = 'Stop Bot';
        }
    }

    async function fetchSettings() {
        try {
            const res = await fetch('/api/settings');
            const data = await res.json();
            currentSettings = data.settings || {};
            renderSettingsForm(currentSettings);
        } catch (error) {
            console.error('Error fetching settings:', error);
            settingsContainer.innerHTML = '<p class="error-msg">Failed to load settings. Check connection.</p>';
        }
    }

    function renderSettingsForm(settings) {
        settingsContainer.innerHTML = '';
        
        let delay = 0;
        for (const [key, value] of Object.entries(settings)) {
            const formGroup = document.createElement('div');
            formGroup.className = 'form-group';
            formGroup.style.animationDelay = `${delay}s`;
            
            const label = document.createElement('label');
            label.htmlFor = `setting_${key}`;
            label.textContent = key;
            
            // Try to infer type
            const input = document.createElement('input');
            input.id = `setting_${key}`;
            input.name = key;
            
            if (value && (value.toLowerCase() === 'true' || value.toLowerCase() === 'false')) {
                // It's a boolean, use a select dropdown
                const select = document.createElement('select');
                select.id = `setting_${key}`;
                select.name = key;
                
                const optTrue = document.createElement('option');
                optTrue.value = 'True';
                optTrue.textContent = 'True';
                
                const optFalse = document.createElement('option');
                optFalse.value = 'False';
                optFalse.textContent = 'False';
                
                if (value.toLowerCase() === 'true') optTrue.selected = true;
                else optFalse.selected = true;
                
                select.appendChild(optTrue);
                select.appendChild(optFalse);
                
                formGroup.appendChild(label);
                formGroup.appendChild(select);
            } else {
                // Regular text input
                input.type = key.toLowerCase().includes('token') || key.toLowerCase().includes('key') ? 'password' : 'text';
                input.value = value || '';
                
                formGroup.appendChild(label);
                formGroup.appendChild(input);
            }
            
            settingsContainer.appendChild(formGroup);
            delay += 0.05;
        }
    }

    async function saveSettings(e) {
        e.preventDefault();
        saveSettingsBtn.disabled = true;
        saveSettingsBtn.textContent = 'Saving...';
        
        const formData = new FormData(settingsForm);
        const newSettings = {};
        for (const [key, value] of formData.entries()) {
            newSettings[key] = value;
        }
        
        try {
            const res = await fetch('/api/settings', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ settings: newSettings })
            });
            
            if (!res.ok) throw new Error('Failed to save settings');
            
            showSaveStatus('Settings saved successfully! Restart bot to apply.', 'success');
        } catch (error) {
            console.error(error);
            showSaveStatus('Failed to save settings.', 'error');
        } finally {
            saveSettingsBtn.disabled = false;
            saveSettingsBtn.textContent = 'Save Settings';
        }
    }

    function showSaveStatus(message, type) {
        saveStatus.textContent = message;
        saveStatus.className = `save-status show ${type}`;
        
        setTimeout(() => {
            saveStatus.classList.remove('show');
        }, 5000);
    }
});
