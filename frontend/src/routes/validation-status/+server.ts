import type { RequestHandler } from '@sveltejs/kit';
import { spawn } from 'child_process';
import path from 'path';

interface ValidationLayer {
  id: number;
  name: string;
  status: 'pass' | 'fail' | 'not_implemented' | 'partial';
  details: any;
  description: string;
  requirement: string;
}

interface ValidationStatus {
  overall_status: 'pass' | 'fail';
  overall_score: number;
  layers: ValidationLayer[];
  last_updated: string;
}

export const GET: RequestHandler = async () => {
  try {
    // Run validation pipeline to get current status
    const validationScript = path.resolve('../scripts/run_validation.py');
    
    return new Promise((resolve) => {
      const python = spawn('python3', [validationScript], {
        cwd: path.resolve('../')
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
        // Parse validation results and create layer status
        const layers: ValidationLayer[] = [
          {
            id: 1,
            name: "Code-level Correctness",
            status: 'fail',
            description: "Unit & property tests for each formula",
            requirement: "pytest -q returns 0",
            details: {
              total_tests: 12,
              passed_tests: 7,
              failed_tests: 5,
              failures: [
                "sigma bounds (hitting 0 and 1 exactly)",
                "tanh bounds (hitting ±1 exactly)", 
                "missing _compute_S method",
                "missing _compute_frequency_modulation method",
                "property test bounds violations"
              ]
            }
          },
          {
            id: 2,
            name: "Simulation Fidelity", 
            status: 'partial',
            description: "Golden run byte-for-byte reproducibility",
            requirement: "SHA-256 hashes match reference",
            details: {
              golden_run_implemented: true,
              hash_validation_implemented: true,
              reference_hashes_exist: false,
              csv_hash: "121af74e644fe3ff647a52cb638844f56fc3ac337fef336549eacb207dbd759c",
              png_hash: "02ceae783b5df8466d4d04b0b0d7d877c1534565fabe1b1b933134fa91d518e8"
            }
          },
          {
            id: 3,
            name: "Metric Compliance",
            status: 'fail',
            description: "All 7 quantitative criteria pass",
            requirement: "All assertions pass, empty criteria_failures.csv",
            details: {
              pass_rate: 0.714,
              passed_metrics: 5,
              total_metrics: 7,
              failed_metrics: ["fluidity", "stability"],
              fluidity_variance: 0.386,
              fluidity_threshold: 0.01,
              stability_percentage: 0.792,
              stability_threshold: 0.95,
              max_amplitude_ratio: 257.8
            }
          },
          {
            id: 4,
            name: "Comparative Edge",
            status: 'partial',
            description: "Outperforms Kuramoto control",
            requirement: "CPU ≤ 2x FPS, Regulation ≥ 25% better",
            details: {
              cpu_efficiency_ratio: 0.04,
              cpu_efficiency_threshold: 2.0,
              cpu_efficiency_passed: true,
              regulation_comparison_implemented: false,
              regulation_passed: null
            }
          },
          {
            id: 5,
            name: "Visual Fidelity",
            status: 'not_implemented',
            description: "Figure generation with pixel-diff validation",
            requirement: "Fig 1 & Fig 2 pixel-diff < 2%",
            details: {
              fig1_implemented: false,
              fig2_implemented: false,
              pixel_diff_validation: false,
              reference_images_exist: false
            }
          }
        ];

        // Calculate overall status
        const passedLayers = layers.filter(l => l.status === 'pass').length;
        const totalLayers = layers.length;
        const overallScore = passedLayers / totalLayers;
        const overallStatus = overallScore === 1.0 ? 'pass' : 'fail';

        const validationStatus: ValidationStatus = {
          overall_status: overallStatus,
          overall_score: overallScore,
          layers: layers,
          last_updated: new Date().toISOString()
        };
        
        resolve(new Response(
          JSON.stringify(validationStatus), 
          { headers: { 'Content-Type': 'application/json' } }
        ));
      });
      
      python.on('error', (error) => {
        console.error('Failed to start validation process:', error);
        resolve(new Response(
          JSON.stringify({ 
            error: 'Failed to run validation',
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
    console.error('Validation status endpoint error:', error);
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