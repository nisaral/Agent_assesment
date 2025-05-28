let mediaRecorder = null;
let audioChunks = [];
let storedPortfolio = '';
let voiceHistory = [];

async function checkService(port, service) {
    try {
        const response = await fetch(`http://localhost:${port}/health`);
        if (!response.ok) throw new Error(`Service returned status: ${response.status}`);
        const data = await response.json();
        return data.status === "healthy";
    } catch (e) {
        console.error(`${service} is not running on port ${port}: ${e.message}`);
        return false;
    }
}

async function checkAllServices() {
    const services = [
        { port: 6007, name: "Orchestrator" },
        { port: 8001, name: "API Agent" },
        { port: 6002, name: "Scraping Agent" },
        { port: 6003, name: "Retriever Agent" },
        { port: 6004, name: "Analysis Agent" },
        { port: 6005, name: "Language Agent" },
        { port: 6006, name: "Voice Agent" }
    ];

    const results = await Promise.all(services.map(s => checkService(s.port, s.name)));
    const failedServices = services.filter((s, i) => !results[i]);
    
    if (failedServices.length > 0) {
        const message = `Some services are not running: ${failedServices.map(s => s.name).join(', ')}`;
        showError(message);
        return false;
    }
    return true;
}

function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    document.querySelector('.response-section').prepend(errorDiv);
    setTimeout(() => errorDiv.remove(), 5000);
}

function updateVoiceHistory(text) {
    voiceHistory.unshift({ text, timestamp: new Date() });
    if (voiceHistory.length > 10) voiceHistory.pop();
    
    const list = document.getElementById('voice-history-list');
    list.innerHTML = voiceHistory.map(item => 
        `<li>${item.text} <small>(${item.timestamp.toLocaleTimeString()})</small></li>`
    ).join('');
}

async function startRecording() {
    const recordButton = document.querySelector('button[onclick="startRecording()"]');
    const stopButton = document.querySelector('button[onclick="stopRecording()"]');
    
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];

        mediaRecorder.ondataavailable = e => {
            if (e.data.size > 0) {
                audioChunks.push(e.data);
            }
        };

        mediaRecorder.start();
        document.getElementById('record-status').textContent = 'Recording...';
        recordButton.disabled = true;
        stopButton.disabled = false;
    } catch (err) {
        document.getElementById('record-status').textContent = 'Error: ' + err.message;
        showError('Failed to start recording: ' + err.message);
    }
}

function stopRecording() {
    return new Promise(resolve => {
        const recordButton = document.querySelector('button[onclick="startRecording()"]');
        const stopButton = document.querySelector('button[onclick="stopRecording()"]');
        
        if (!mediaRecorder || mediaRecorder.state !== 'recording') {
            document.getElementById('record-status').textContent = 'Recorder not active';
            recordButton.disabled = false;
            stopButton.disabled = true;
            resolve(null);
            return;
        }

        mediaRecorder.onstop = () => {
            const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
            const reader = new FileReader();
            reader.onloadend = () => {
                document.getElementById('record-status').textContent = 'Stopped';
                recordButton.disabled = false;
                stopButton.disabled = true;
                resolve(reader.result);
            };
            reader.readAsDataURL(audioBlob);
        };

        mediaRecorder.stop();
    });
}

function savePortfolio() {
    const portfolioInput = document.getElementById('portfolio-input').value;
    try {
        const entries = portfolioInput.split(',').map(s => s.trim()).filter(s => s);
        for (const entry of entries) {
            const [symbol, qty] = entry.split(':').map(x => x.trim());
            if (!symbol || !/^\d+$/.test(qty)) {
                throw new Error('Invalid format');
            }
        }
        storedPortfolio = portfolioInput;
        alert('Portfolio saved!');
        updateLiveTracking();
    } catch (e) {
        showError('Invalid portfolio format. Use "AAPL:100, MSFT:50"');
    }
}

async function submitQuery() {
    let queryText = document.getElementById('query-input-text').value.trim();
    document.getElementById('written-response').textContent = 'Processing your request...';
    document.getElementById('audio-output').style.display = 'none';

    if (!await checkAllServices()) {
        document.getElementById('written-response').textContent = '';
        return;
    }

    if (audioChunks.length > 0) {
        const audioData = await stopRecording();
        if (!audioData) {
            document.getElementById('written-response').textContent = '';
            return;
        }

        try {
            const response = await fetch('http://localhost:6006/run', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ action: 'stt', audio: audioData })
            });
            
            if (!response.ok) {
                throw new Error(`Voice service error: ${response.status}`);
            }
            
            const result = await response.json();
            if (result.error) {
                throw new Error(result.error);
            }
            
            queryText = result.text;
            document.getElementById('query-input-text').value = queryText;
            updateVoiceHistory(queryText);
        } catch (e) {
            showError('Error transcribing audio: ' + e.message);
            document.getElementById('written-response').textContent = '';
            return;
        }
    }

    if (!queryText || !storedPortfolio) {
        showError('Please enter a query and save a portfolio.');
        document.getElementById('written-response').textContent = '';
        return;
    }

    try {
        const response = await fetch('http://localhost:6007/run', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: queryText, portfolio: storedPortfolio })
        });
        
        if (!response.ok) {
            throw new Error(`Server responded with status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }

        document.getElementById('written-response').textContent = data.narrative || 'No response generated';

        const audioElement = document.getElementById('audio-output');
        if (data.audio_file) {
            audioElement.src = `data:audio/mp3;base64,${data.audio_file}`;
            audioElement.style.display = 'block';
        } else {
            audioElement.style.display = 'none';
        }

        const lowerQuery = queryText.toLowerCase();
        if (lowerQuery.includes('visualize') || lowerQuery.includes('chart') || lowerQuery.includes('plot')) {
            await renderVisualizations();
        }

    } catch (e) {
        showError('Error processing query: ' + e.message);
        document.getElementById('written-response').textContent = 'Error: ' + e.message;
        document.getElementById('audio-output').style.display = 'none';
    }
}

async function renderVisualizations() {
    try {
        const stocks = storedPortfolio.split(',').map(s => s.split(':')[0].trim()).filter(Boolean);
        if (!stocks.length) {
            throw new Error('No stocks in portfolio');
        }

        const marketResponse = await fetch('http://localhost:8001/run', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ticker: stocks.join(',') })
        });
        
        if (!marketResponse.ok) {
            throw new Error(`Market data service error: ${marketResponse.status}`);
        }
        
        const marketData = await marketResponse.json();
        if (marketData.error) {
            throw new Error(marketData.error);
        }

        const stockPrices = Object.entries(marketData.stocks || {})
            .filter(([s, d]) => stocks.includes(s) && d.price > 0)
            .map(([s, d]) => ({ Stock: s, Price: d.price }));

        if (stockPrices.length > 0) {
            await Plotly.newPlot('stock-chart', [{
                x: stockPrices.map(d => d.Stock),
                y: stockPrices.map(d => d.Price),
                type: 'scatter',
                mode: 'lines+markers',
                name: 'Stock Prices'
            }], {
                title: 'Portfolio Stock Prices',
                xaxis: { title: 'Stock' },
                yaxis: { title: 'Price ($)' }
            });
        }

        const sectors = { Semiconductors: 35.2, Software: 28.8, Hardware: 22.1, Services: 13.9 };
        await Plotly.newPlot('sector-chart', [{
            labels: Object.keys(sectors),
            values: Object.values(sectors),
            type: 'pie',
            name: 'Sector Allocation'
        }], {
            title: 'Portfolio Sector Allocation'
        });

        const newsPromises = stocks.map(symbol =>
            fetch('http://localhost:6002/run', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ company: symbol })
            }).then(res => {
                if (!res.ok) throw new Error(`News service error: ${res.status}`);
                return res.json();
            })
        );

        const newsResponses = await Promise.allSettled(newsPromises);
        const news = newsResponses
            .filter(r => r.status === 'fulfilled')
            .flatMap(r => r.value.news || []);

        if (news.length > 0) {
            const sentiments = news.map(n => {
                const match = n.match(/Sentiment: (positive|negative|neutral)/i);
                return match ? match[1].toLowerCase() : 'neutral';
            });

            const sentimentCounts = {
                positive: sentiments.filter(s => s === 'positive').length,
                neutral: sentiments.filter(s => s === 'neutral').length,
                negative: sentiments.filter(s => s === 'negative').length
            };

            await Plotly.newPlot('news-chart', [{
                labels: Object.keys(sentimentCounts),
                values: Object.values(sentimentCounts),
                type: 'pie',
                marker: {
                    colors: ['#2ecc71', '#95a5a6', '#e74c3c']
                },
                name: 'News Sentiment'
            }], {
                title: 'News Sentiment Distribution'
            });
        }

    } catch (e) {
        showError('Visualization Error: ' + e.message);
    }
}

async function updateLiveTracking() {
    try {
        if (!storedPortfolio) return;
        const stocks = storedPortfolio.split(',').map(s => s.split(':')[0].trim()).filter(Boolean);
        if (!stocks.length) return;

        const response = await fetch('http://localhost:8001/run', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ticker: stocks.join(',') })
        });
        if (!response.ok) throw new Error('Failed to fetch live data');
        const data = await response.json();
        if (data.error) throw new Error(data.error);

        const tbody = document.querySelector('#live-tracking tbody');
        tbody.innerHTML = '';
        Object.entries(data.stocks || {}).forEach(([stock, info]) => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${stock}</td>
                <td>${info.price.toFixed(2)}</td>
                <td>${info.volume}</td>
                <td>${new Date().toLocaleTimeString()}</td>
            `;
            tbody.appendChild(row);
        });
    } catch (e) {
        showError('Live tracking error: ' + e.message);
    }
}

setInterval(updateLiveTracking, 60000);