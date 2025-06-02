import type { RequestHandler } from '@sveltejs/kit';
import { spawn } from 'child_process';
import path from 'path';

interface SimData {
  t: number[];
  C: number[];
  S: number[];
  r: number[];
  validation?: any;
}

// Mock data for when Python backend is not available (e.g., in Vercel)
function generateMockSimData(): SimData {
  const N = 100;
  const t = Array.from({ length: N }, (_, i) => i * 0.2);
  const phi = 1.618;
  const epsilon = 0.05;
  const omega = 0.1;
  
  const r = t.map(time => phi + epsilon * Math.sin(2 * Math.PI * omega * time));
  const S = t.map(time => Math.sin(2 * Math.PI * 0.1 * time) * Math.exp(-time * 0.01));
  const C = t.map(time => 0.5 + 0.3 * Math.cos(2 * Math.PI * 0.05 * time));
  
  return { t, C, S, r };
}

export const GET: RequestHandler = async () => {
  try {
    // Check if we're in a serverless environment (Vercel)
    const isServerless = process.env.VERCEL || process.env.AWS_LAMBDA_FUNCTION_NAME;
    
    if (isServerless) {
      // Return mock data for serverless environments
      const mockData = generateMockSimData();
      return new Response(
        JSON.stringify({
          ...mockData,
          note: "Mock data - Python backend not available in serverless environment"
        }), 
        { headers: { 'Content-Type': 'application/json' } }
      );
    }
    
    // Try to run the Python simulation for local development
    const pythonScript = path.resolve('../scripts/run_fps_simulation.py');
    
    return new Promise((resolve) => {
      const python = spawn('python3', [pythonScript, '--json'], {
        cwd: path.resolve('../')  // Run from project root, not frontend dir
      });
      
      let output = '';
      let errorOutput = '';
      
      python.stdout.on('data', (data) => {
        output += data.toString();
      });
      
      python.stderr.on('data', (data) => {
        errorOutput += data.toString();
      });
      
      python.on('close', (code) => {
        if (code !== 0) {
          console.error('Python script error:', errorOutput);
          // Fallback to mock data if Python fails
          const mockData = generateMockSimData();
          resolve(new Response(
            JSON.stringify({
              ...mockData,
              note: "Mock data - Python simulation failed",
              error: errorOutput
            }), 
            { headers: { 'Content-Type': 'application/json' } }
          ));
          return;
        }
        
        try {
          const data: SimData = JSON.parse(output);
          resolve(new Response(
            JSON.stringify(data), 
            { headers: { 'Content-Type': 'application/json' } }
          ));
        } catch (parseError) {
          console.error('JSON parse error:', parseError);
          // Fallback to mock data if parsing fails
          const mockData = generateMockSimData();
          resolve(new Response(
            JSON.stringify({
              ...mockData,
              note: "Mock data - Failed to parse Python simulation results"
            }), 
            { headers: { 'Content-Type': 'application/json' } }
          ));
        }
      });
      
      python.on('error', (error) => {
        console.error('Failed to start Python process:', error);
        // Fallback to mock data if Python process fails to start
        const mockData = generateMockSimData();
        resolve(new Response(
          JSON.stringify({
            ...mockData,
            note: "Mock data - Failed to start Python simulation"
          }), 
          { headers: { 'Content-Type': 'application/json' } }
        ));
      });
    });
    
  } catch (error) {
    console.error('Simulation endpoint error:', error);
    // Final fallback to mock data
    const mockData = generateMockSimData();
    return new Response(
      JSON.stringify({
        ...mockData,
        note: "Mock data - Internal server error",
        error: error instanceof Error ? error.message : 'Unknown error'
      }), 
      { headers: { 'Content-Type': 'application/json' } }
    );
  }
}; 