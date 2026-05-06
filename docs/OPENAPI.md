# OpenAPI & API Clients

How to use the OpenAPI specification to build frontends and generate API clients.

---

## Quick Start

### View Interactive Docs

```bash
make docs
```

Opens: `http://localhost:8000/docs`

- Try endpoints in browser
- See request/response formats
- Test with real data

---

## OpenAPI Specification File

**Location:** `openapi.yaml` (in project root)

**What it contains:**
- All 8 REST endpoints
- Request/response schemas
- Examples
- Error handling

---

## Generate API Clients

### TypeScript (React, Vue, Angular)

```bash
npx openapi-typescript-codegen \
  --input openapi.yaml \
  --output ./src/api \
  --client axios
```

**Use it:**
```typescript
import { QueryApi } from './api';

const api = new QueryApi();
const result = await api.queryText({ text: 'Your question' });
console.log(result.response);
```

### Python

```bash
pip install openapi-generator-cli

openapi-generator-cli generate \
  -i openapi.yaml \
  -g python \
  -o ./python-client
```

**Use it:**
```python
from callsage_client import ApiClient, QueryApi

api = QueryApi(ApiClient(host="http://localhost:8000"))
result = api.query_text({"text": "Your question"})
print(result.response)
```

### Other Languages

**Available generators:**
- Java, Kotlin, Swift, Go, Ruby, PHP, C#, Dart, Rust
- 50+ languages supported

```bash
openapi-generator-cli list
```

---

## API Endpoints

### Text Query (Chat)

**POST /query**

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"text": "What does the insurance documentation say about love?"}'
```

**Response:**
```json
{
  "success": true,
  "response": "The insurance documentation teaches...",
  "confidence": 0.87,
  "sources": [...]
}
```

### Audio Processing (Voice)

**POST /process**

```bash
curl -X POST http://localhost:8000/process \
  -F "audio=@recording.mp3"
```

**Response:**
```json
{
  "success": true,
  "transcript": "What does the insurance documentation say about faith?",
  "response": "The insurance documentation defines faith as...",
  "confidence": 0.85,
  "sources": [...]
}
```

### Health Check

**GET /health**

```bash
curl http://localhost:8000/health
```

### Database Stats

**GET /knowledge/stats**

```bash
curl http://localhost:8000/knowledge/stats
```

### Load Documents

**POST /knowledge/ingest**

```bash
curl -X POST http://localhost:8000/knowledge/ingest \
  -F "clear_existing=true"
```

**See [API.md](API.md) for complete endpoint reference.**

---

## Frontend Frameworks

### React Example

```typescript
import { useState } from 'react';

function ChatComponent() {
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState('');

  const handleSubmit = async () => {
    const res = await fetch('http://localhost:8000/query', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: query })
    });

    const data = await res.json();
    setResponse(data.response);
  };

  return (
    <div>
      <input value={query} onChange={e => setQuery(e.target.value)} />
      <button onClick={handleSubmit}>Ask</button>
      <p>{response}</p>
    </div>
  );
}
```

### Vue Example

```vue
<script setup>
import { ref } from 'vue';

const query = ref('');
const response = ref('');

const ask = async () => {
  const res = await fetch('http://localhost:8000/query', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text: query.value })
  });

  const data = await res.json();
  response.value = data.response;
};
</script>

<template>
  <div>
    <input v-model="query" />
    <button @click="ask">Ask</button>
    <p>{{ response }}</p>
  </div>
</template>
```

### Vanilla JavaScript

See: `examples/vanilla-js-chat.html`

---

## Import into Tools

### Postman

1. Open Postman
2. Click **Import**
3. Select `openapi.yaml`
4. Done!

### Insomnia

1. Open Insomnia
2. Click **Import**
3. Select `openapi.yaml`

### Hoppscotch

1. Open https://hoppscotch.io/
2. Import `openapi.yaml`

---

## Low-Code Platforms

### Retool

1. Add **REST API** resource
2. Import `openapi.yaml`
3. Auto-generates UI components

### Appsmith

1. Add **REST API**
2. Import spec
3. Use in widgets

### Budibase

1. Import OpenAPI spec
2. Auto-generates forms & tables

---

## Validation

```bash
# Install validator
npm install -g @apidevtools/swagger-cli

# Validate spec
swagger-cli validate openapi.yaml
```

---

## Complete Examples

See `examples/` folder:
- `vanilla-js-chat.html` - Pure JavaScript
- `simple-voice-chat.html` - Voice + text
- `react-chat-component.tsx` - React + TypeScript

---

## Next Steps

1. **View docs:** `make docs`
2. **Generate client:** Choose your language above
3. **Build UI:** See [examples](../examples/README.md)
4. **Deploy:** See [SETUP.md](SETUP.md)
