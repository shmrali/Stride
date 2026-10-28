# Stride — website and chatbot

Submission project. Original source folders remain untouched.

- `frontend/`: Original Stride website, packaged with Vite. Vercel root: `frontend`; build: `npm run build`; output: `dist`.
- `backend/`: FastAPI chatbot. Render root: `backend`; build: `pip install -r requirements.txt`; start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
- `frontend-legacy/`: original backend-served interface, required by the existing server. The submission website is `frontend/`.
- `docs/`: chatbot policies.

## Deployment

1. Push this directory as its own GitHub repository on `main`.
2. Create a Render Python web service using `render.yaml` or the settings above. Configure `OPENAI_API_KEY` privately, `OPENAI_MODEL` to a model available to your account, and `ALLOWED_ORIGINS` to the final Vercel origin. Never upload the local `.env`. Health endpoint: `/health`.
3. Import the repository in Vercel, choose root `frontend`, Vite, and deploy. `frontend/vercel.json` forwards `/api` requests to the Render backend; no frontend API environment variable is required.
4. Update Render `ALLOWED_ORIGINS` to the exact Vercel production origin and redeploy.
5. Test a membership question and a safety question on the public website. A greeting or health check alone does not verify OpenAI. Check `writer_status` on a fully specified FAQ answer: `used` confirms an OpenAI response; `fallback` means the approved FAQ was used after an API failure.

The chatbot uses approved FAQs and may use OpenAI to rewrite complete answers. Missing business details are acknowledged rather than invented. This is a student demonstration; sample business details need verification for real use.

## Submission links

- GitHub: pending
- Render API: pending
- Vercel website: pending
