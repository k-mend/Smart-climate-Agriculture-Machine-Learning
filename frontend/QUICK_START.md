# Quick Start Guide - AgriBricks Frontend

## Prerequisites

- Node.js 18+ installed
- A GitHub account
- A Vercel account (free tier works)

## Step 1: Test Locally

```bash
cd frontend
npm install
npm run dev
```

Visit http://localhost:5173 to see the app running locally.

## Step 2: Deploy to Vercel (2 Minutes)

### Using Vercel Dashboard (Recommended)

1. Push your code to GitHub
2. Go to https://vercel.com
3. Click "Add New Project"
4. Import your GitHub repository
5. Configure:
   - **Root Directory**: `frontend`
   - **Framework Preset**: Vite
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
6. Add Environment Variable:
   - **Name**: `VITE_API_URL`
   - **Value**: `https://smart-climate-agriculture-machine.onrender.com`
7. Click "Deploy"

That's it! Your app will be live in about 1 minute.

## Step 3: Update Backend CORS

After deployment, update your backend's `.env` file to include your Vercel domain:

```
CORS_ORIGINS=["https://your-app.vercel.app"]
```

Redeploy the backend on Render.

## Common Issues

### Build Fails
- Make sure you set the root directory to `frontend` in Vercel
- Check that all dependencies are in package.json

### API Not Connecting
- Verify `VITE_API_URL` is set in Vercel environment variables
- Check that the backend is running on Render
- Test the API directly: https://smart-climate-agriculture-machine.onrender.com/docs

### CORS Errors
- Add your Vercel domain to backend CORS_ORIGINS
- Redeploy the backend after updating

## Need Help?

Check the full DEPLOYMENT.md guide or the main project README.
