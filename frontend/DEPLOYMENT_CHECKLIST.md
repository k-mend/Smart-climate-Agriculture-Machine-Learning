# Deployment Checklist

## Pre-Deployment

- [ ] Test locally with `npm run dev`
- [ ] Test build with `npm run build`
- [ ] Push code to GitHub
- [ ] Ensure `.env.example` is committed (not `.env`)
- [ ] Review `vercel.json` configuration

## Vercel Setup

- [ ] Create Vercel account (if needed)
- [ ] Connect GitHub account to Vercel
- [ ] Import repository
- [ ] Set root directory to `frontend`
- [ ] Verify build settings:
  - Build Command: `npm run build`
  - Output Directory: `dist`
  - Install Command: `npm install`

## Environment Variables

- [ ] Add `VITE_API_URL`:
  - Production: `https://smart-climate-agriculture-machine.onrender.com`
  - Development: `http://localhost:8000`

## Post-Deployment

- [ ] Test all features:
  - [ ] Location Analysis
  - [ ] Crop Analysis
  - [ ] Smart Route
  - [ ] AI Assistant
  - [ ] Disease Detection
- [ ] Check browser console for errors
- [ ] Test on mobile device
- [ ] Update backend CORS_ORIGINS with Vercel domain
- [ ] Redeploy backend on Render

## Backend CORS Update

Add your Vercel domain to backend `.env`:
```
CORS_ORIGINS=["https://your-app.vercel.app", "http://localhost:5173"]
```

## Verification

- [ ] Frontend loads without errors
- [ ] API calls succeed
- [ ] All images load correctly
- [ ] Forms submit successfully
- [ ] Loading states display properly
- [ ] Error messages show when needed
- [ ] Mobile responsive layout works

## Troubleshooting

### Build Fails
1. Check TypeScript errors: `npm run build`
2. Verify all dependencies are installed
3. Check root directory is set to `frontend`

### API Connection Issues
1. Verify `VITE_API_URL` in Vercel settings
2. Test backend: https://smart-climate-agriculture-machine.onrender.com/docs
3. Check browser network tab for errors
4. Verify CORS settings in backend

### CORS Errors
1. Add Vercel domain to backend CORS_ORIGINS
2. Redeploy backend
3. Clear browser cache
4. Test in incognito mode

## Custom Domain (Optional)

- [ ] Purchase domain
- [ ] Add domain in Vercel project settings
- [ ] Configure DNS records
- [ ] Update CORS_ORIGINS with custom domain
- [ ] Test with custom domain

## Monitoring

- [ ] Enable Vercel Analytics
- [ ] Set up error tracking
- [ ] Monitor API usage
- [ ] Check performance metrics

## Done!

Your AgriBricks frontend is now live and helping farmers worldwide!

Share your deployment: ____________________________

Next steps:
- Get user feedback
- Monitor performance
- Plan feature updates
- Share with community
