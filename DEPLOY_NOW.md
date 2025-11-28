# Deploy AgriBricks Frontend Now!

Follow these exact steps to get your frontend live in 5 minutes.

## Step 1: Test Locally (1 minute)

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 and verify everything works.

Press `Ctrl+C` to stop the dev server.

## Step 2: Build for Production (30 seconds)

```bash
npm run build
```

You should see:
```
✓ built in 5.42s
```

If there are errors, fix them before proceeding.

## Step 3: Push to GitHub (1 minute)

```bash
# From project root
git add .
git commit -m "Add AgriBricks frontend"
git push origin main
```

## Step 4: Deploy to Vercel (2 minutes)

### Option A: Vercel Dashboard (Easiest)

1. Go to https://vercel.com
2. Sign in with GitHub
3. Click "Add New" → "Project"
4. Select your repository
5. Configure:
   - **Root Directory**: `frontend`
   - **Framework Preset**: Vite (auto-detected)
   - **Build Command**: `npm run build` (auto-filled)
   - **Output Directory**: `dist` (auto-filled)
6. Click "Environment Variables" → "Add"
   - **Key**: `VITE_API_URL`
   - **Value**: `https://smart-climate-agriculture-machine.onrender.com`
7. Click "Deploy"

Wait 1-2 minutes for deployment to complete.

### Option B: Vercel CLI (Advanced)

```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy from frontend directory
cd frontend
vercel --prod

# When prompted:
# - Set up and deploy: Y
# - Link to existing project: N
# - Project name: agribricks (or your choice)
# - Directory: ./ (current)
# - Override settings: N

# Add environment variable
vercel env add VITE_API_URL production
# Enter: https://smart-climate-agriculture-machine.onrender.com

# Redeploy with env var
vercel --prod
```

## Step 5: Update Backend CORS (1 minute)

Your frontend is now live at: `https://your-app.vercel.app`

Update your backend `.env` file:

```env
CORS_ORIGINS=["https://your-app.vercel.app", "http://localhost:5173"]
```

Redeploy backend on Render:
1. Go to your Render dashboard
2. Select your service
3. Click "Manual Deploy" → "Deploy latest commit"

## Step 6: Test Production (1 minute)

Visit your Vercel URL and test each feature:
- [ ] Location Analysis
- [ ] Crop Analysis
- [ ] Smart Route
- [ ] AI Assistant
- [ ] Disease Detection

Check browser console (F12) for any errors.

## Troubleshooting

### Build Fails on Vercel
- Verify root directory is set to `frontend`
- Check that package.json is in frontend directory
- Look at build logs for specific errors

### API Not Connecting
- Check environment variable `VITE_API_URL` is set
- Test backend directly: https://smart-climate-agriculture-machine.onrender.com/docs
- Check browser network tab for failed requests

### CORS Errors
- Verify backend CORS_ORIGINS includes your Vercel domain
- Wait 1-2 minutes after redeploying backend
- Try in incognito mode to rule out cache issues

### 404 Errors on Refresh
- Verify `vercel.json` exists in frontend directory
- Check it has the rewrite rule for SPA routing
- Redeploy if needed

## Success!

Your AgriBricks frontend is now live!

Share your deployment URL with users and start helping farmers make better agricultural decisions.

## Next Steps

1. Share with farmers and get feedback
2. Monitor usage in Vercel Analytics
3. Add custom domain (optional)
4. Plan feature updates based on feedback

## Support

- QUICK_START.md - Quick reference
- DEPLOYMENT.md - Detailed guide
- DEPLOYMENT_CHECKLIST.md - Full checklist
- FEATURES_OVERVIEW.md - Feature documentation

---

**Your agricultural ML platform is now accessible to farmers worldwide!**
