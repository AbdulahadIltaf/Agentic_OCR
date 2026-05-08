document.addEventListener('DOMContentLoaded', () => {
    const screens = {
        upload: document.getElementById('screen-upload'),
        processing: document.getElementById('screen-processing'),
        confidence: document.getElementById('screen-confidence'),
        output: document.getElementById('screen-output'),
        history: document.getElementById('screen-history'),
    };

    const steps = {
        upload: document.querySelector('.step-upload'),
        processing: document.querySelector('.step-processing'),
        confidence: document.querySelector('.step-confidence'),
        output: document.querySelector('.step-output'),
    };

    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const feedTerminal = document.getElementById('feed-terminal');
    const confValue = document.getElementById('conf-value');
    const confBar = document.getElementById('conf-bar');
    const btnApprove = document.getElementById('btn-approve');
    const btnReupload = document.getElementById('btn-reupload');
    const riskNote = document.getElementById('risk-note');
    const riskAckWrap = document.getElementById('risk-ack-wrap');
    const ackRisk = document.getElementById('ack-risk');
    const outputImgSrc = document.getElementById('output-img-src');
    const docxCanvas = document.getElementById('docx-canvas');
    const auditLogContent = document.getElementById('audit-log-content');
    const btnStartNew = document.getElementById('btn-start-new');
    const btnDownload = document.getElementById('btn-download');
    const btnHistory = document.getElementById('history-btn');
    const btnCloseHistory = document.getElementById('btn-close-history');
    const historyList = document.getElementById('history-list');

    let currentSessionId = null;
    let currentBlocks = null;
    let currentXaiTrace = null;
    let currentOutFilename = null;
    let complianceDB = {};
    let lastMeanConf = 0;

    function loadComplianceDB() {
        fetch('/api/compliance')
            .then((res) => res.json())
            .then((data) => {
                complianceDB = data;
                const sidebarContent = document.getElementById('compliance-content');
                if (!sidebarContent) return;
                sidebarContent.innerHTML = '';
                Object.keys(data).forEach((key) => {
                    const item = data[key];
                    const card = document.createElement('div');
                    card.className = 'law-card';
                    card.innerHTML = `
                        <h4>${item.framework}</h4>
                        <h5>${item.title}</h5>
                        <p>"${item.text}"</p>
                        <div class="rationale">Rationale: ${item.rationale}</div>
                    `;
                    sidebarContent.appendChild(card);
                });
            })
            .catch((err) => console.error('Compliance load failed:', err));
    }
    loadComplianceDB();

    function showScreen(screenName) {
        Object.values(screens).forEach((s) => {
            s.classList.remove('screen--active');
        });
        const target = screens[screenName];
        if (target) target.classList.add('screen--active');

        document.querySelectorAll('.phases__item').forEach((btn) => {
            btn.classList.toggle('active', btn.dataset.screen === screenName);
        });
    }

    document.querySelectorAll('.phases__item').forEach((btn) => {
        btn.addEventListener('click', () => showScreen(btn.dataset.screen));
    });

    dropZone.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            fileInput.click();
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length) handleUpload(e.target.files[0]);
    });

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('drop-tile--drag');
    });
    dropZone.addEventListener('dragleave', () => dropZone.classList.remove('drop-tile--drag'));
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('drop-tile--drag');
        if (e.dataTransfer.files.length) handleUpload(e.dataTransfer.files[0]);
    });

    function handleUpload(file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            outputImgSrc.src = e.target.result;
        };
        reader.readAsDataURL(file);

        ackRisk.checked = false;
        showScreen('processing');
        feedTerminal.innerHTML = '';
        runAgentPerceiveDecide(file);
    }

    function runAgentPerceiveDecide(file) {
        const formData = new FormData();
        formData.append('image', file);

        fetch('/api/agent/perceive_decide', { method: 'POST', body: formData })
            .then((res) => {
                if (!res.ok) throw new Error(`HTTP ${res.status}`);
                return res.json();
            })
            .then((data) => {
                if (data.error) throw new Error(data.error);
                currentSessionId = data.session_id;
                currentBlocks = data.blocks || [];
                currentXaiTrace = data.xai_trace || [];
                simulateReasoningFeed(data.xai_trace, data.decision.mean_conf);
            })
            .catch((err) => {
                showToast('Pipeline error: ' + err.message, true);
                showScreen('upload');
            });
    }

    function simulateReasoningFeed(traceList, conf) {
        if (!traceList || traceList.length === 0) {
            showConfidenceGate(conf);
            return;
        }
        let i = 0;
        const interval = setInterval(() => {
            if (i < traceList.length) {
                const line = document.createElement('div');
                line.className = 'feed-line';
                let citationHtml = '';
                if (traceList[i].citation_key && complianceDB[traceList[i].citation_key]) {
                    const ref = complianceDB[traceList[i].citation_key];
                    citationHtml = `<span class="citation-badge" title="${ref.text.replace(/"/g, '&quot;')}">[Ref: ${ref.title}]</span>`;
                }
                line.innerHTML = `<span class="feed-tag">[${traceList[i].step}]</span> ${traceList[i].message} ${citationHtml}`;
                feedTerminal.appendChild(line);
                i++;
            } else {
                clearInterval(interval);
                setTimeout(() => showConfidenceGate(conf), 900);
            }
        }, 700);
    }

    function showConfidenceGate(conf) {
        lastMeanConf = typeof conf === 'number' ? conf : 0;
        showScreen('confidence');

        riskNote.classList.remove('risk-note--ok', 'risk-note--mid', 'risk-note--bad');
        btnApprove.disabled = conf < 18;

        if (conf >= 80) {
            riskNote.classList.add('risk-note--ok');
            riskNote.innerHTML =
                '<strong>Assessment:</strong> Structure looks healthy. Export is allowed without extra acknowledgement.';
            confBar.style.background = 'linear-gradient(90deg, #34d399, #22d3ee)';
            confValue.style.color = '#6ee7b7';
            riskAckWrap.classList.add('hidden');
        } else if (conf >= 55) {
            riskNote.classList.add('risk-note--mid');
            riskNote.innerHTML =
                '<strong>Assessment:</strong> Mixed signal quality. Review preview carefully; server requires explicit acknowledgement under 80%.';
            confBar.style.background = 'linear-gradient(90deg, #fbbf24, #f97316)';
            confValue.style.color = '#fde68a';
            riskAckWrap.classList.remove('hidden');
        } else {
            riskNote.classList.add('risk-note--bad');
            riskNote.innerHTML =
                '<strong>Assessment:</strong> Low structural confidence — possible empty OCR, malformed JSON, or prompt-injection pattern in text.';
            confBar.style.background = 'linear-gradient(90deg, #f87171, #fb7185)';
            confValue.style.color = '#fecaca';
            riskAckWrap.classList.remove('hidden');
        }

        let startTs = null;
        const duration = 1000;
        const stepAnim = (ts) => {
            if (!startTs) startTs = ts;
            const p = Math.min((ts - startTs) / duration, 1);
            const ease = 1 - Math.pow(1 - p, 3);
            confValue.textContent = Math.floor(ease * conf);
            confBar.style.width = `${ease * Math.min(conf, 100)}%`;
            if (p < 1) requestAnimationFrame(stepAnim);
            else confValue.textContent = Math.round(conf);
        };
        requestAnimationFrame(stepAnim);
    }

    btnReupload.addEventListener('click', () => {
        if (currentSessionId) {
            fetch('/api/agent/abort', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ session_id: currentSessionId }),
            }).catch(console.error);
        }
        resetPipeline();
    });

    btnApprove.addEventListener('click', () => {
        if (!currentSessionId) return;

        const conf = lastMeanConf;
        if (conf < 18) {
            showToast('Confidence too low for export — pipeline aborted. Re-upload a clearer image.', true);
            return;
        }
        if (conf < 80 && !ackRisk.checked) {
            showToast('Check the acknowledgement box to export below 80% confidence.', true);
            return;
        }

        btnApprove.disabled = true;
        const prevLabel = btnApprove.textContent;
        btnApprove.textContent = 'Authorizing…';

        const body = { session_id: currentSessionId };
        if (conf < 80) body.acknowledge_risk = true;

        fetch('/api/agent/act', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
        })
            .then((res) => res.json().then((j) => ({ ok: res.ok, j })))
            .then(({ ok, j }) => {
                if (!ok || j.error) throw new Error(j.error || `HTTP error`);
                currentOutFilename = j.filename;
                renderOutput(currentBlocks, j.conf ?? conf, currentXaiTrace);
            })
            .catch((err) => showToast('Export failed: ' + err.message, true))
            .finally(() => {
                btnApprove.disabled = false;
                btnApprove.textContent = prevLabel;
            });
    });

    function renderOutput(blocks, conf, trace) {
        showScreen('output');
        if (trace && trace.length > 0) {
            const enriched = trace.map((t) => {
                if (t.citation_key && complianceDB[t.citation_key]) {
                    return {
                        ...t,
                        citation: complianceDB[t.citation_key].title,
                        citation_text: complianceDB[t.citation_key].text,
                    };
                }
                return t;
            });
            auditLogContent.textContent = JSON.stringify(enriched, null, 2);
        } else {
            auditLogContent.textContent = 'No audit data.';
        }

        docxCanvas.innerHTML = '';
        if (!blocks || blocks.length === 0) {
            docxCanvas.innerHTML =
                '<p style="color:#64748b;text-align:center;padding:2rem;">No blocks returned — verify API key and image clarity.</p>';
            return;
        }

        const alignMap = { 0: 'left', 1: 'center', 2: 'right', 3: 'justify' };
        blocks.forEach((block) => {
            const div = document.createElement('div');
            div.style.textAlign = alignMap[block.align] || 'left';
            div.style.fontWeight = block.bold ? 'bold' : 'normal';
            div.textContent = block.text;
            div.style.marginBottom = '8px';
            if (block.style && block.style.includes('Heading 1')) {
                div.style.fontSize = '22px';
                div.style.marginTop = '12px';
            } else if (block.style && block.style.includes('Heading 2')) {
                div.style.fontSize = '18px';
            } else div.style.fontSize = '15px';
            docxCanvas.appendChild(div);
        });
        showToast('Export complete');
    }

    btnDownload.addEventListener('click', () => {
        if (currentOutFilename) window.location.href = `/api/download/${currentOutFilename}`;
        else showToast('No file yet', true);
    });

    btnStartNew.addEventListener('click', resetPipeline);

    function resetPipeline() {
        currentSessionId = null;
        currentOutFilename = null;
        fileInput.value = '';
        ackRisk.checked = false;
        riskAckWrap.classList.add('hidden');
        showScreen('upload');
    }

    btnHistory.addEventListener('click', () => {
        showScreen('history');
        loadHistory();
    });

    btnCloseHistory.addEventListener('click', () => resetPipeline());

    function loadHistory() {
        fetch('/api/agent/history')
            .then((res) => res.json())
            .then((data) => {
                historyList.innerHTML = '';
                if (!data || data.length === 0) {
                    historyList.innerHTML = '<div class="empty-history">No sessions logged yet.</div>';
                    return;
                }
                data.reverse().forEach((item) => {
                    const c = item.mean_conf || 0;
                    const pillClass = c >= 80 ? 'pill--ok' : c >= 55 ? 'pill--mid' : 'pill--bad';
                    const card = document.createElement('article');
                    card.className = 'history-card';
                    card.setAttribute('role', 'listitem');
                    card.innerHTML = `
                        <div>
                            <h4>Run #${item.attempt || 1}</h4>
                            <span class="meta">${item.out || 'n/a'}</span>
                        </div>
                        <div style="display:flex;gap:10px;align-items:center;">
                            <span class="pill ${pillClass}">${Math.round(c)}%</span>
                            <span class="pill pill--neutral">${(item.action || '').toUpperCase()}</span>
                        </div>
                    `;
                    historyList.appendChild(card);
                });
            })
            .catch(() => {
                historyList.innerHTML = '<div class="empty-history">Could not read memory file.</div>';
            });
    }

    function showToast(msg, isError = false) {
        const toast = document.getElementById('toast');
        toast.textContent = msg;
        toast.classList.toggle('toast--err', isError);
        toast.classList.remove('toast--hidden');
        setTimeout(() => toast.classList.add('toast--hidden'), 4200);
    }
});
