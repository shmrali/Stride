# Chatbot deployment guide — GitHub, Render, and Vercel

Based on the educator’s 16-step walkthrough shared in this chat. This is a reference guide for the **separate chatbot project**, not the orchestration case study. The chatbot files have not yet been inspected, so all example paths and commands must be checked against that project before use.

Place this file in the chatbot project’s top-level folder, beside its README. Ask Codex to inspect that folder and fill in the project worksheet below before deployment. This guide does not require moving or renaming existing folders.

## 1. Understand the folder structure first

The educator’s example has this layout:

```text
chatbot-project/                 ← Project root: open this folder in Codex
├── CHATBOT-DEPLOYMENT-GUIDE.md   ← This guide
├── README.md
├── .gitignore
├── .env.example                ← Placeholder values only; optional
├── frontend/                   ← Browser interface; deployed to Vercel
│   ├── package.json
│   ├── angular.json             ← Present if this is an Angular project
│   └── src/
│       └── environments/
│           └── environment.production.ts
└── backend/                    ← Server; deployed to Render
    ├── requirements.txt
    └── app/
        └── main.py             ← Example FastAPI entry point
```

**This is an example, not your confirmed folder structure.** Your interface might be in `client/`, your server in `server/`, or they might be in separate repositories. Your project may also use a different framework.

| Term | What it means | How to identify it |
| --- | --- | --- |
| Project root | Top-level folder containing the chatbot project | Usually contains README and frontend/backend folders |
| Git repository root | Folder Git tracks | Run `git rev-parse --show-toplevel` inside the project |
| Frontend | Pages and controls the visitor sees | Often contains `package.json`, UI source, and framework configuration |
| Backend | Server code that calls the AI provider | Look for API routes, Python requirements, and environment-variable reads |
| Build output | Generated files published by the host | Determine from framework configuration and a successful build |

Do not select a folder solely because of its name. Inspect its contents. A `dist/` folder commonly contains generated output, not the editable source.

The orchestration case study was static and needed no Render backend. Do not reuse that assumption for this chatbot.

## 2. Fill in this worksheet after inspection

| Setting | Confirmed value |
| --- | --- |
| Chatbot project root on this computer | To inspect |
| Git repository root | To inspect |
| GitHub repository URL | To create or confirm |
| Deployment branch | To confirm; educator uses `main` |
| Frontend folder relative to repository root | To inspect |
| Frontend framework | To inspect |
| Frontend production build command | To inspect |
| Frontend output directory relative to frontend folder | To inspect |
| Production API URL configuration location | To inspect |
| Does frontend code append `/api` or `/api/chat`? | To inspect |
| Backend folder relative to repository root | To inspect |
| Backend runtime and compatible version | To inspect |
| Backend dependency installation command | To inspect |
| Backend start command and app entry point | To inspect |
| Health endpoint | To inspect |
| Required backend environment variable names | To inspect; never record secret values here |
| Render backend origin | Fill after deployment |
| Vercel production origin | Fill after deployment |

## 3. Before you begin

- Keep the chatbot in its own repository and hosting project, separate from the case study.
- Keep real API keys and `.env` files out of GitHub. Enter backend secrets privately in Render.
- Confirm `.gitignore` excludes `.env`, secret-bearing environment variants, dependency folders, and local-only files before staging code. A safe `.env.example` may contain placeholders.
- Never put a secret into frontend code or a public frontend environment variable.
- Review the files to be committed before uploading. If a secret is already tracked, adding `.gitignore` does not remove it from Git history.
- Use your actual repository branch and paths in every command below.

## 4. Follow the educator’s 16 steps

### Step 01 — Create or choose the chatbot GitHub repository

Create a separate repository for the complete chatbot project. Include source code, README, dependency manifests, and safe example configuration.

For a new repository receiving existing local code, leave GitHub’s README, license, and `.gitignore` initialization unchecked to avoid creating separate histories.

### Step 02 — Open Terminal in the correct project folder

On Mac, use Finder’s **New Terminal at Folder**, or type `cd` followed by the quoted absolute folder path. On Windows, use **Open in Terminal** inside the project folder.

Check:

```bash
git status
git remote -v
git rev-parse --show-toplevel
```

If this is not yet a repository, ask Codex to initialize the correct project root, add the intended remote, review files, and create the initial commit. Do not initialize an unrelated parent folder or blindly stage everything.

### Step 03 — Resolve existing GitHub history only if needed, then push

If Git reports unrelated histories because GitHub already contains an independently created README or license, inspect both histories before deciding to merge. The educator’s one-time command is:

```bash
git pull origin main --allow-unrelated-histories --no-rebase --no-edit
```

Use this only for the verified situation; resolve any conflicts before continuing. It is not a routine update command.

Once the intended files are committed:

```bash
git push -u origin main
```

If authentication fails, use a supported GitHub sign-in method. A normal account password does not authenticate HTTPS Git pushes. Never paste a token into chat or put it in a command URL.

### Step 04 — Create a Render Web Service

Sign in to Render and choose **New → Web Service**. Connect the chatbot repository, not the orchestration repository.

### Step 05 — Configure the backend location and commands

Use the worksheet’s confirmed backend runtime, branch, and root directory. Root Directory is relative to the Git repository root; Render runs the commands from that selected folder.

The educator’s Python/FastAPI example is:

```text
Runtime: Python 3
Branch: main
Root Directory: backend
Build Command: pip install -r requirements.txt
Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

`app.main:app` assumes `backend/app/main.py` exports a FastAPI object named `app`. If your files differ, the command must differ. Do not paste the `backend/ $` prompt shown in screenshots into the command field.

### Step 06 — Add backend environment variables privately

Inspect the server code and example configuration to identify required variables. The educator’s example contains:

```text
OPENAI_API_KEY = enter privately in Render
MODEL_NAME = a model supported by the app and available to your API account
ALLOWED_ORIGINS = http://localhost:4200
ENABLE_LIVE_CREWAI = false
```

These names and values are example-specific. The local origin must match your frontend’s actual development address. Confirm what `ENABLE_LIVE_CREWAI` does before choosing its value; do not assume a disabled setting runs a live agent workflow.

Save and deploy. If the build fails, inspect the actual error logs before changing anything.

### Step 07 — Pin a compatible Python version

For a Python backend, select a runtime version supported by the project’s dependencies. The educator resolved their example’s compatibility issue with:

```text
PYTHON_VERSION = 3.12.11
```

This is the educator’s example version, not a confirmed requirement for your chatbot. Check local runtime and dependencies, then save, rebuild, and deploy with the selected compatible version.

### Step 08 — Confirm the backend is live

Wait for Render’s successful build and live service status. Open the confirmed health route, for example:

```text
https://YOUR-BACKEND.onrender.com/health
```

The educator’s expected response is:

```json
{"status":"ok"}
```

Your endpoint must actually exist. A 404 at `/` does not necessarily mean the backend failed. Check the configured health route and logs. A health response verifies the server is responding; the final chatbot test must also verify the AI interaction.

### Step 09 — Point the frontend to the Render backend

Find the production API configuration in the actual frontend. The educator’s Angular project uses:

```text
frontend/src/environments/environment.production.ts
```

Example:

```typescript
export const environment = {
  production: true,
  apiBaseUrl: 'https://YOUR-BACKEND.onrender.com',
};
```

In that example, frontend code appends the API path, so the setting contains the origin only—no `/api`, `/api/chat`, or `/health`. Inspect your request-building code before applying this rule. Other frameworks may configure the public API origin through a different file or build-time variable.

### Step 10 — Save, commit, and push the frontend configuration

Save the actual changed file. Review the diff, stage that file, commit, and push. For the educator’s exact Angular layout:

```bash
git add frontend/src/environments/environment.production.ts
git commit -m "Configure production API URL"
git push
```

Use your project’s actual file path. Confirm the production build uses that configuration.

### Step 11 — Import the chatbot repository into Vercel

Sign in to Vercel and choose **Add New → Project → Import** for the chatbot repository.

### Step 12 — Select the frontend root directory

Set Root Directory to the confirmed frontend source folder relative to the repository root. The educator uses `frontend` with the Angular preset. Select the framework that matches your actual application.

Vercel should deploy the frontend; the backend in this architecture runs on Render. No OpenAI API key belongs in this browser application.

### Step 13 — Set the correct frontend output directory

Confirm the production build command and generated output. The educator’s Angular example uses:

```text
dist/octakidz-faq-assistant/browser
```

Do not copy that project name. Determine the output from your own configuration and build. Vercel’s output path is relative to the selected frontend root directory. Other frameworks may need different settings or their preset defaults.

### Step 14 — Deploy or redeploy with the saved settings

Deploy the frontend. If you changed output or build settings after a deployment, open **Deployments → latest deployment → three-dot menu → Redeploy** so a new build uses them.

Record the stable production domain from the project, not a temporary deployment URL.

### Step 15 — Allow the production frontend origin on Render

In Render’s environment settings, update the backend’s confirmed CORS variable to the exact Vercel production origin, without a path or trailing slash. The educator uses:

```text
ALLOWED_ORIGINS = https://YOUR-CHATBOT.vercel.app
```

Confirm the format expected by your backend if multiple origins are needed. Save, rebuild, and deploy.

CORS controls which browser origins can read responses; it is not authentication and does not prevent direct API requests.

### Step 16 — Test the complete live chatbot

Open the stable Vercel production URL, ideally also in a signed-out or private browser window, and submit a harmless example question appropriate to the chatbot.

Confirm the request reaches Render, returns the expected response, and displays correctly. If using an instance that sleeps after inactivity, allow it to wake before retrying. Check browser errors and Render logs for failures without exposing secrets.

Confirm whether the response uses the intended live AI path or an explicitly configured demo/fallback mode.

## 5. Final handover checklist

- [ ] Chatbot source is in its own GitHub repository on the deployment branch.
- [ ] Real API keys and secret-bearing `.env` files are absent from committed code.
- [ ] Render uses the correct backend folder, runtime, install command, and start command.
- [ ] Required backend environment variables are configured privately.
- [ ] Backend health route responds as expected.
- [ ] Frontend production configuration targets the correct backend URL.
- [ ] Vercel uses the correct frontend root, framework, build command, and output settings.
- [ ] Backend CORS configuration includes the exact stable frontend origin.
- [ ] The public production URL opens for a signed-out visitor.
- [ ] A complete chatbot interaction succeeds in the intended live or clearly labeled demo mode.
- [ ] GitHub, Render, and Vercel URLs are recorded in the project README.

## 6. Prompt to use with Codex in the chatbot folder

> Read CHATBOT-DEPLOYMENT-GUIDE.md and inspect this chatbot project before making deployment changes. Identify the Git root, frontend and backend folders, frameworks, runtime versions, dependency manifests, API entry point, health endpoint, production API URL configuration, and CORS handling. Fill in the worksheet with verified values and explain the folder structure in plain language. Follow the educator’s GitHub → Render → frontend configuration → Vercel → CORS → end-to-end test sequence, adapting every setting to this codebase. Guide me one screen at a time. Never ask me to paste an API key or token into chat, and keep secret-bearing .env files out of GitHub. Keep this chatbot separate from the deployed orchestration case study.

## 7. If a step fails

Share the step number and an error screenshot or relevant log excerpt with credentials hidden. Ask for the next smallest action based on that evidence. Do not repeatedly change settings without identifying the cause.

The platform screens and defaults may change. Verify current platform documentation when executing these steps; this file records the educator’s process, not a guarantee that every label or example value remains current.
