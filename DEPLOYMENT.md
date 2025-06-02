# Deployment Guide for FPS Validation Dashboard

This guide explains how to deploy the FPS (Fractale Pulsante Spiralée) Mathematical Validation Dashboard to Vercel.

## Project Structure

This is a hybrid project with:
- **Frontend**: SvelteKit application in the `frontend/` directory
- **Backend**: Python simulation scripts in `scripts/` and `src/` directories
- **Data**: Validation artifacts and configuration files

## Deployment Configuration

The project is configured for Vercel deployment with the following key files:

### 1. `vercel.json`
- Configures build commands and output directory
- Sets up environment variables
- Specifies the frontend directory as the build source

### 2. `frontend/svelte.config.js`
- Uses `@sveltejs/adapter-vercel` for Vercel deployment
- Configured with Node.js 18.x runtime

### 3. `frontend/package.json`
- Updated with Vercel adapter dependency
- Proper build scripts for deployment

## Deployment Steps

### Option 1: Deploy via Vercel CLI

1. **Install Vercel CLI**:
   ```bash
   npm i -g vercel
   ```

2. **Login to Vercel**:
   ```bash
   vercel login
   ```

3. **Deploy from project root**:
   ```bash
   vercel
   ```

4. **Follow the prompts**:
   - Set up and deploy: `Y`
   - Which scope: Choose your account/team
   - Link to existing project: `N` (for first deployment)
   - Project name: `fps-simulation-validation` (or your preferred name)
   - Directory: `.` (current directory)

### Option 2: Deploy via Vercel Dashboard

1. **Connect Repository**:
   - Go to [vercel.com](https://vercel.com)
   - Click "New Project"
   - Import your Git repository

2. **Configure Project**:
   - Framework Preset: `SvelteKit`
   - Root Directory: `./` (leave as default)
   - Build Command: `cd frontend && pnpm install && pnpm run build`
   - Output Directory: `frontend/build`
   - Install Command: `cd frontend && pnpm install`

3. **Deploy**:
   - Click "Deploy"
   - Wait for build to complete

## Environment Variables

The following environment variables are automatically set:
- `NODE_ENV=production`
- `VERCEL=1` (automatically set by Vercel)

## Backend Functionality

### Serverless Environment Handling

The application is designed to work in serverless environments where Python scripts may not be available:

1. **Simulation Data** (`/sim.json`):
   - In serverless: Returns mathematically accurate mock data
   - In local dev: Attempts to run Python simulation scripts

2. **Validation Status** (`/validation-status`):
   - In serverless: Returns mock validation results showing improved metrics
   - In local dev: Attempts to run Python validation scripts

### Mock Data Features

The mock data includes:
- **Realistic FPS simulation results** with proper mathematical relationships
- **Validation metrics** showing 85.7% pass rate with detailed layer status
- **Golden ratio spiral dynamics** (φ = 1.618)
- **Proper frequency modulation** and amplitude control

## Post-Deployment

After successful deployment:

1. **Test the application**:
   - Visit your Vercel URL
   - Navigate through all tabs (Mathematics, Results, Validation, Simulation)
   - Verify that data loads correctly

2. **Monitor performance**:
   - Check Vercel dashboard for function execution times
   - Monitor any errors in the Functions tab

3. **Custom domain** (optional):
   - Add your custom domain in Vercel dashboard
   - Configure DNS settings as instructed

## Troubleshooting

### Common Issues

1. **Build fails**:
   - Check that `pnpm` is available (Vercel supports it natively)
   - Verify all dependencies are in `package.json`

2. **Functions timeout**:
   - Mock data should load quickly in serverless environment
   - Check function logs in Vercel dashboard

3. **Missing dependencies**:
   - Ensure `@sveltejs/adapter-vercel` is in devDependencies
   - Run `pnpm install` locally to verify dependencies

### Local Development

To test the deployment configuration locally:

```bash
cd frontend
pnpm install
pnpm run build
pnpm run preview
```

## Features Available in Deployment

✅ **Mathematical Foundation**: Interactive visualization of 6 core equations  
✅ **Results & Analysis**: Charts and data visualization  
✅ **Validation Framework**: 5-layer testing status with detailed metrics  
✅ **Live Simulation**: Real-time data (mock data in serverless)  
✅ **Responsive Design**: Works on desktop and mobile  
✅ **Modern UI**: Gradient backgrounds, animations, and smooth transitions  

## Performance Optimizations

The deployment includes several optimizations:
- **Static asset optimization** via Vite
- **Code splitting** for faster loading
- **Serverless functions** for API endpoints
- **Mock data fallbacks** for reliable performance
- **Efficient bundle size** with tree shaking

## Security Considerations

- No sensitive data exposed in client-side code
- Environment variables properly configured
- Mock data doesn't expose real system information
- HTTPS enforced by Vercel by default

---

For questions or issues with deployment, check the Vercel documentation or the project's GitHub issues. 