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

export const GET: RequestHandler = async () => {
  try {
    // Run the FPS simulation using the Python backend
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
          resolve(new Response(
            JSON.stringify({ 
              error: 'Simulation failed', 
              details: errorOutput 
            }), 
            { 
              status: 500, 
              headers: { 'Content-Type': 'application/json' } 
            }
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
          resolve(new Response(
            JSON.stringify({ 
              error: 'Failed to parse simulation results' 
            }), 
            { 
              status: 500, 
              headers: { 'Content-Type': 'application/json' } 
            }
          ));
        }
      });
      
      python.on('error', (error) => {
        console.error('Failed to start Python process:', error);
        resolve(new Response(
          JSON.stringify({ 
            error: 'Failed to start simulation',
            details: error.message 
          }), 
          { 
            status: 500, 
            headers: { 'Content-Type': 'application/json' } 
          }
        ));
      });
    });
    
  } catch (error) {
    console.error('Simulation endpoint error:', error);
    return new Response(
      JSON.stringify({ 
        error: 'Internal server error',
        details: error instanceof Error ? error.message : 'Unknown error'
      }), 
      { 
        status: 500, 
        headers: { 'Content-Type': 'application/json' } 
      }
    );
  }
}; 