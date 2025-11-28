# AgriBricks Frontend - Deployment Guide

Clean, user-friendly frontend for the Smart Climate Agriculture ML platform.

## Features

- Location Analysis - Best crops and planting times
- Crop Analysis - Detailed crop suitability assessment
- Smart Route - Weather-aware routing
- AI Assistant - Expert agricultural advice
- Disease Detection - AI-powered plant pathology

## Tech Stack

- React 18 + TypeScript
- Vite
- Axios
- Lucide Icons

## Local Development

```bash
npm install
npm run dev
```

## Deploy to Vercel

### Option 1: Via Vercel Dashboard (Easiest)

1. Go to [vercel.com](https://vercel.com) and sign in with GitHub
2. Click "Add New Project"
3. Import your GitHub repository
4. **Important:** Set the root directory to `frontend`
5. Add environment variable:
   - Name: `VITE_API_URL`
   - Value: `https://smart-climate-agriculture-machine.onrender.com`
6. Click "Deploy"

### Option 2: Via Vercel CLI

```bash
# Install Vercel CLI globally
npm install -g vercel

# Login to Vercel
vercel login

# Navigate to frontend directory
cd frontend

# Deploy to production
vercel --prod
```

When prompted:
- Set up and deploy? **Y**
- Which scope? Select your account
- Link to existing project? **N**
- Project name: `agribricks` (or your preferred name)
- Directory: `./` (current directory)
- Override settings? **N**

Add environment variable after deployment:
```bash
vercel env add VITE_API_URL production
# When prompted, enter: https://smart-climate-agriculture-machine.onrender.com
```

Redeploy with environment variable:
```bash
vercel --prod
```

## Environment Variables

Create a `.env` file in the frontend directory:

```
VITE_API_URL=https://smart-climate-agriculture-machine.onrender.com
```

## Color Scheme

The app uses earth tones that match the agricultural theme:
- Earth Brown: `#6B4423`
- Leaf Green: `#4A7C59`
- Wheat Gold: `#D4A574`
- Cream: `#F5F1E8`
- Light Green: `#E8F5E9`

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── LocationAnalysis.tsx
│   │   ├── CropAnalysis.tsx
│   │   ├── SmartRoute.tsx
│   │   ├── AIAssistant.tsx
│   │   └── DiseaseDetection.tsx
│   ├── App.tsx
│   ├── App.css
│   ├── config.ts
│   ├── main.tsx
│   └── index.css
├── index.html
├── vercel.json
├── package.json
└── vite.config.ts
```

## API Integration

The frontend connects to the backend API hosted on Render. All API calls are handled through Axios with proper error handling and loading states.

## Build Command

```bash
npm run build
```

This creates an optimized production build in the `dist` directory.

## Troubleshooting

### CORS Issues
If you encounter CORS errors, ensure your backend API has the frontend domain added to CORS_ORIGINS.

### API Connection Failed
- Verify `VITE_API_URL` is set correctly
- Check that the backend API is running on Render
- Test the API endpoint directly in your browser

### Build Fails
- Clear node_modules and reinstall: `rm -rf node_modules package-lock.json && npm install`
- Check for TypeScript errors: `npm run build`

## Support

For issues, check the main project README or create an issue on GitHub.
