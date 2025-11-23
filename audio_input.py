"""Utility helpers for capturing microphone input inside Streamlit.

The module exposes a single helper, ``render_audio_input_panel`` which renders a
client-side audio recorder based on the browser's Web Speech API. The widget
streams interim transcription results back into a target Streamlit ``textarea``
so the existing text-based workflow keeps working while enabling a microphone
workflow.

Limitations:
    * Works only in browsers that implement ``SpeechRecognition`` (Chrome,
      Edge, most Chromium variants). Safari/Firefox users will see a graceful
      fallback message.
    * Transcription runs entirely in the browser; no audio data leaves the
      user's device.
"""
from __future__ import annotations

import json
from textwrap import dedent

from streamlit.components.v1 import html


def render_audio_input_panel(
    target_container_id: str,
    *,
    language: str = "en-US",
    height: int = 240,
    title: str | None = None,
    initial_text: str = "",
) -> None:
    """Render a lightweight audio recorder bound to ``target_container_id``.

    Args:
        target_container_id: The DOM ``id`` of the Streamlit container that wraps
            the ``textarea`` to be updated. We expect ``<div id="..."><textarea /></div>``.
        language: BCP-47 locale code used by the Web Speech recognizer.
        height: Pixel height reserved for the iframe.
        title: Optional heading text rendered above the controls.
    """

    component_id = f"{target_container_id}-audio-panel"
    heading = title or "Speak your answer"
    serialized_initial = json.dumps(initial_text)
    component_id_js = json.dumps(component_id)
    target_container_js = json.dumps(target_container_id)
    language_js = json.dumps(language)

    html_content = dedent(
        """
        <style>
            .audio-panel {
                font-family: 'Source Sans Pro', 'Segoe UI', system-ui;
                border: 1px solid #e5e7eb;
                border-radius: 12px;
                padding: 16px;
                background: #ffffff;
                box-shadow: 0 4px 12px rgba(15, 23, 42, 0.08);
            }
            .audio-panel h4 {
                margin: 0 0 12px;
                font-size: 1rem;
                font-weight: 600;
                color: #111827;
            }
            .audio-panel__buttons {
                display: flex;
                gap: 8px;
                margin-bottom: 12px;
            }
            .audio-panel button {
                border: none;
                border-radius: 999px;
                padding: 10px 18px;
                font-weight: 600;
                cursor: pointer;
                font-size: 0.95rem;
                transition: transform 120ms ease, box-shadow 120ms ease;
            }
            .audio-panel button:disabled {
                cursor: not-allowed;
                opacity: 0.6;
                box-shadow: none;
            }
            .audio-panel__start {
                background: #7c3aed;
                color: #fff;
                box-shadow: 0 6px 14px rgba(124, 58, 237, 0.25);
            }
            .audio-panel__stop {
                background: #e5e7eb;
                color: #111827;
            }
            .audio-panel__status {
                font-size: 0.9rem;
                color: #6b7280;
                margin-bottom: 4px;
            }
            .audio-panel__transcript {
                min-height: 40px;
                font-size: 0.95rem;
                color: #1f2937;
                line-height: 1.4;
                background: #f9fafb;
                border-radius: 8px;
                padding: 8px 10px;
                border: 1px dashed #d1d5db;
            }
        </style>
        <div class="audio-panel" id="%(component_id)s">
            <h4>%(heading)s</h4>
            <div class="audio-panel__buttons">
                <button type="button" class="audio-panel__start" data-action="start">🎙️ Start</button>
                <button type="button" class="audio-panel__stop" data-action="stop" disabled>■ Stop</button>
            </div>
            <div class="audio-panel__status" data-role="status">Idle</div>
            <div class="audio-panel__transcript" data-role="transcript">—</div>
        </div>
        <script>
            (function() {
                const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                const root = document.getElementById(%(component_id_js)s);
                const statusEl = root.querySelector('[data-role="status"]');
                const transcriptEl = root.querySelector('[data-role="transcript"]');
                const startBtn = root.querySelector('[data-action="start"]');
                const stopBtn = root.querySelector('[data-action="stop"]');
                const targetId = %(target_container_js)s;
                const initialText = %(serialized_initial)s;

                if (!SpeechRecognition) {
                    statusEl.textContent = 'Microphone transcription not supported in this browser.';
                    startBtn.disabled = true;
                    stopBtn.disabled = true;
                    transcriptEl.textContent = 'Try Chrome / Edge for live captions.';
                    return;
                }

                let recognition = null;
                let isListening = false;
                let committedText = initialText || '';

                const setButtons = (listening) => {
                    startBtn.disabled = listening;
                    stopBtn.disabled = !listening;
                };

                const setStatus = (text) => {
                    statusEl.textContent = text;
                };

                const updateTranscript = (value) => {
                    transcriptEl.textContent = value || '—';
                };

                const broadcast = (value, { final = false } = {}) => {
                    const payload = {
                        type: 'audio-transcript',
                        targetId,
                        value,
                        final,
                    };
                    if (window.parent) {
                        window.parent.postMessage(payload, '*');
                    } else {
                        window.postMessage(payload, '*');
                    }
                };

                const stopListening = () => {
                    isListening = false;
                    if (recognition) {
                        recognition.onend = null;
                        recognition.stop();
                        recognition = null;
                    }
                    setButtons(false);
                    setStatus('Idle');
                    broadcast(committedText, { final: true });
                };

                const handleResults = (event) => {
                    let interim = '';
                    for (let i = event.resultIndex; i < event.results.length; i += 1) {
                        const result = event.results[i];
                        if (result.isFinal) {
                            committedText = (committedText + ' ' + result[0].transcript).trim();
                        } else {
                            interim = result[0].transcript;
                        }
                    }
                    const combined = (committedText + ' ' + interim).trim();
                    updateTranscript(combined);
                    broadcast(combined);
                };

                const startListening = () => {
                    if (isListening) return;
                    recognition = new SpeechRecognition();
                    recognition.lang = %(language_js)s;
                    recognition.interimResults = true;
                    recognition.continuous = true;
                    committedText = initialText || '';
                    updateTranscript(committedText);
                    recognition.onresult = handleResults;
                    recognition.onerror = (event) => {
                        setStatus(`Error: ${event.error}`);
                        stopListening();
                    };
                    recognition.onend = () => {
                        if (isListening) {
                            recognition.start();
                        } else {
                            stopListening();
                        }
                    };
                    recognition.start();
                    isListening = true;
                    setButtons(true);
                    setStatus('Listening…');
                };

                startBtn.addEventListener('click', startListening);
                stopBtn.addEventListener('click', stopListening);

                window.addEventListener('message', (event) => {
                    if (event?.data?.type === 'timer-lock') {
                        stopListening();
                    }
                });

                updateTranscript(committedText);
            })();
        </script>
        """
    ) % {
        "component_id": component_id,
        "heading": heading,
        "component_id_js": component_id_js,
        "target_container_js": target_container_js,
        "serialized_initial": serialized_initial,
        "language_js": language_js,
    }

    html(html_content, height=height)
