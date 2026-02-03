# Audio & Voice System

How the voice/audio system works and how to integrate it.

---

## Quick Facts

**Architecture:** REST API (not streaming)
**Audio Input:** ✅ Yes (MP3, WAV, WebM, M4A, FLAC)
**Audio Output:** ❌ No (returns text only)
**Real-time:** No (turn-based, ~2-5 sec per request)

---

## How It Works

```
User Mic → Browser Records → Upload File →
Whisper Transcribes → RAG Processes →
Returns Text Response
```

**Flow:**
1. User clicks "Record"
2. User speaks (5-30 seconds)
3. User clicks "Stop"
4. Audio uploads to `/process` endpoint
5. Backend transcribes with Whisper
6. RAG finds relevant documents
7. LLM generates response
8. Returns JSON with text

**Not streaming** - it's turn-based like a walkie-talkie.

---

## Browser Implementation

### Recording Audio

```javascript
// 1. Get microphone
const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

// 2. Create recorder
const mediaRecorder = new MediaRecorder(stream);

// 3. Collect chunks
let audioChunks = [];
mediaRecorder.ondataavailable = (e) => {
  audioChunks.push(e.data);
};

// 4. Start
mediaRecorder.start();

// 5. Stop and upload
mediaRecorder.onstop = async () => {
  const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
  await uploadAudio(audioBlob);
};
```

### Uploading Audio

```javascript
async function uploadAudio(audioBlob) {
  const formData = new FormData();
  formData.append('audio', audioBlob, 'recording.webm');

  const response = await fetch('http://localhost:8000/process', {
    method: 'POST',
    body: formData
  });

  const data = await response.json();

  console.log('Transcript:', data.transcript);
  console.log('Response:', data.response);
  console.log('Confidence:', data.confidence);
}
```

**No base64 encoding needed!** Just standard file upload.

---

## Working Example

```bash
open examples/simple-voice-chat.html
```

Features:
- Click-to-record button
- Visual feedback
- Auto-upload
- Displays transcript + response
- Error handling

---

## Audio Formats

**Supported:**
- MP3
- WAV
- WebM (browser default)
- M4A
- FLAC

**Browser outputs:** WebM (works fine!)

**File size limits:**
- Max: 25MB
- Max duration: 600 seconds (10 min)

**Typical sizes:**
- 10 seconds ≈ 100KB
- 30 seconds ≈ 300KB
- 1 minute ≈ 600KB

---

## Processing Time

| Audio Length | Transcription | RAG | Total |
|--------------|---------------|-----|-------|
| 5 seconds    | ~800ms        | ~1s | ~2s   |
| 15 seconds   | ~1.5s         | ~1s | ~2.5s |
| 30 seconds   | ~2.2s         | ~1s | ~3.2s |
| 60 seconds   | ~3.5s         | ~1s | ~4.5s |

---

## Adding Voice Responses (TTS)

The API returns text only. To get voice responses, add client-side TTS:

### Option 1: Web Speech API (Free)

```javascript
const utterance = new SpeechSynthesisUtterance(response.response);
window.speechSynthesis.speak(utterance);
```

**Pros:** Free, built-in
**Cons:** Robotic voice

### Option 2: ElevenLabs (Best Quality)

```javascript
const response = await fetch('https://api.elevenlabs.io/v1/text-to-speech/...', {
  method: 'POST',
  headers: { 'xi-api-key': 'YOUR_KEY' },
  body: JSON.stringify({ text: response.response })
});

const audioBlob = await response.blob();
const audio = new Audio(URL.createObjectURL(audioBlob));
audio.play();
```

**Pros:** Natural voice
**Cons:** Costs money

### Option 3: Google Cloud TTS

Similar to ElevenLabs but different API.

---

## CORS

Already configured. Requests from browser work out of the box.

---

## Browser Support

**MediaRecorder:**
- ✅ Chrome 47+
- ✅ Firefox 25+
- ✅ Edge 79+
- ✅ Safari 14.1+
- ❌ IE

**getUserMedia:**
- ✅ All modern browsers
- ⚠️ Requires HTTPS (except localhost)

---

## Mobile Support

**iOS Safari:** ✅ Works
**Android Chrome:** ✅ Works
**Both require:** User interaction to start recording

---

## Common Issues

### "Permission denied"

User needs to allow microphone access.

### "NotSupportedError"

Browser doesn't support MediaRecorder. Update browser.

### "Audio file too large"

Limit recordings to <10 minutes. Or increase `MAX_AUDIO_SIZE_MB` in `.env`.

### "Low quality transcription"

- Check microphone quality
- Reduce background noise
- Speak clearly
- Use better audio format (WAV > WebM > MP3)

---

## Advanced: Streaming (Future)

Current system is turn-based. For streaming:

**Would need:**
- WebSocket endpoint
- Streaming transcription
- Partial results
- Backend changes

**Complexity:** High
**Benefit:** Lower perceived latency

Not implemented yet.

---

## Complete Example Code

See: `examples/simple-voice-chat.html`

- Full recording UI
- Error handling
- Visual feedback
- Transcript display
- Response with confidence
- ~200 lines of code
- No dependencies

---

## Next Steps

1. **Try example:** `open examples/simple-voice-chat.html`
2. **Read code:** See implementation details
3. **Customize:** Modify for your needs
4. **Deploy:** Add HTTPS for production

---

## Reference

- **Endpoint:** [API.md](API.md#post-process)
- **Examples:** [../examples/](../examples/)
- **OpenAPI:** [OPENAPI.md](OPENAPI.md)
