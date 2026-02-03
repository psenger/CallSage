# CallSage Frontend Examples

This folder contains example frontend implementations using the CallSage API.

## 📁 Files

### 1. `swagger-ui-standalone.html`
**Interactive API Documentation**

A standalone Swagger UI that displays the complete API documentation.

**Features:**
- 📖 Browse all endpoints
- 🧪 Test API calls directly in browser
- 📝 View request/response schemas
- 💡 See examples for each endpoint

**How to use:**
```bash
# Option 1: Open directly in browser
open examples/swagger-ui-standalone.html

# Option 2: Serve with Python
cd examples
python3 -m http.server 8080
# Then open: http://localhost:8080/swagger-ui-standalone.html
```

**Note:** Change `?local` in the URL to use the local `openapi.yaml` file instead of the live API endpoint.

---

### 2. `vanilla-js-chat.html`
**Pure JavaScript Chat Interface**

A complete chat interface built with vanilla JavaScript - no frameworks required!

**Features:**
- ✅ Text queries
- 🎤 Audio upload
- 📊 Confidence scoring
- 📚 Source attribution
- 💡 Example queries

**How to use:**
```bash
# Start the CallSage API first
cd ..
make start

# Then open the HTML file
open examples/vanilla-js-chat.html

# Or serve it
cd examples
python3 -m http.server 8080
# Open: http://localhost:8080/vanilla-js-chat.html
```

**Perfect for:**
- Quick prototypes
- Learning the API
- No-build setups
- Static hosting

---

### 3. `react-chat-component.tsx`
**React + TypeScript Component**

A production-ready React component with TypeScript.

**Features:**
- ⚛️ React hooks
- 📘 TypeScript types
- 🎤 Audio + text support
- 🎨 Styled component
- ♿ Accessible

**How to use:**

**Option 1: Copy into existing React app**
```bash
# Copy the component
cp examples/react-chat-component.tsx src/components/

# Install dependencies
npm install axios

# Use in your app
import { insurance documentationChatComponent } from './components/react-chat-component';

function App() {
  return <insurance documentationChatComponent />;
}
```

**Option 2: Generate typed client first**
```bash
# Generate TypeScript client from OpenAPI spec
npx openapi-typescript-codegen \
  --input openapi.yaml \
  --output ./src/api \
  --client axios

# Then use the generated types/services in your component
import { QueryService } from './api/services/QueryService';
```

**Perfect for:**
- React applications
- TypeScript projects
- Production apps
- Component libraries

---

## 🚀 Quick Start

### 1. Start the API

```bash
cd /Users/psenger/Developer/CallSage
make start
make ingest-insurance documentation  # Prime the database
```

### 2. Choose Your Frontend

**Just want to test?** → Use `vanilla-js-chat.html`

**Building a React app?** → Use `react-chat-component.tsx`

**Want to explore the API?** → Use `swagger-ui-standalone.html`

### 3. Test It

Open the example in your browser and try queries like:
- "What does the insurance documentation say about love?"
- "Tell me about the creation story"
- "What are the ten commandments?"

---

## 🛠️ Customization

### Change API URL

All examples use `http://localhost:8000` by default.

**Vanilla JS:**
```javascript
const API_BASE_URL = 'https://your-api.com';
```

**React:**
```typescript
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
```

### Add Authentication

If you enable API keys in CallSage:

**Vanilla JS:**
```javascript
const response = await fetch(`${API_BASE_URL}/query`, {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-API-Key': 'your-api-key'
    },
    body: JSON.stringify({ text: query })
});
```

**React:**
```typescript
axios.defaults.headers.common['X-API-Key'] = 'your-api-key';
```

### Customize Styling

**Vanilla JS:**
Edit the `<style>` section in the HTML file.

**React:**
The component uses inline styles - easily replace with:
- CSS Modules
- Styled Components
- Tailwind CSS
- Material-UI
- Chakra UI

---

## 📚 More Examples

### Generate Clients for Other Frameworks

**Vue.js:**
```bash
npx openapi-typescript-codegen \
  --input openapi.yaml \
  --output ./src/api \
  --client axios
```

**Angular:**
```bash
npx @openapitools/openapi-generator-cli generate \
  -i openapi.yaml \
  -g typescript-angular \
  -o ./src/app/api
```

**Svelte:**
```bash
npx openapi-typescript-codegen \
  --input openapi.yaml \
  --output ./src/lib/api \
  --client fetch
```

**React Native:**
```bash
npx openapi-typescript-codegen \
  --input openapi.yaml \
  --output ./src/api \
  --client axios
```

---

## 🎯 Production Checklist

Before deploying to production:

- [ ] **Environment variables** - Don't hardcode API URLs
- [ ] **Error handling** - Add proper error messages
- [ ] **Loading states** - Show spinners/skeletons
- [ ] **Retry logic** - Handle network failures
- [ ] **Rate limiting** - Debounce user input
- [ ] **Validation** - Check inputs before sending
- [ ] **Security** - Sanitize user inputs
- [ ] **Analytics** - Track usage metrics
- [ ] **Accessibility** - Test with screen readers
- [ ] **Mobile** - Test responsive design

---

## 🐛 Troubleshooting

### CORS Errors

If you see CORS errors in the browser console:

1. Check that the API is running: `make health`
2. Verify CORS is enabled in FastAPI (it should be by default)
3. If serving examples locally, use `python3 -m http.server` instead of `file://`

### API Not Responding

```bash
# Check API health
curl http://localhost:8000/health

# Check Docker services
docker compose ps

# View logs
docker compose logs app
```

### Low Confidence Scores

```bash
# Check knowledge base
make stats

# If empty, ingest documents
make ingest-insurance documentation
```

---

## 📖 Documentation

- **API Reference**: See `openapi.yaml`
- **OpenAPI Usage Guide**: See `OPENAPI_USAGE.md`
- **Testing Guide**: See `TESTING_GUIDE.md`
- **Quick Start**: See `QUICKSTART.md`

---

## 🎨 UI/UX Inspiration

Looking for design inspiration? Check out:

- [ChatGPT UI](https://chat.openai.com/) - Clean chat interface
- [Perplexity](https://www.perplexity.ai/) - Source citations
- [Claude](https://claude.ai/) - Markdown rendering
- [Vercel AI Playground](https://sdk.vercel.ai/) - Multiple model support

---

## 🤝 Contributing

Have a cool example? PRs welcome!

Ideas for new examples:
- [ ] Next.js 14 app
- [ ] Vue 3 composition API
- [ ] Svelte 5 component
- [ ] Flutter mobile app
- [ ] Electron desktop app
- [ ] Chrome extension

---

## 📝 License

These examples are provided as-is for educational purposes.

**Happy building!** 🎉
