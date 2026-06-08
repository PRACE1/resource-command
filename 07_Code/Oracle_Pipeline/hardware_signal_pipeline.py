import math
import json
import random
import time
import os

# ==============================================================================
# RESOURCE COMMAND: HARDWARE SIGNAL PIPELINE (v1.0)
# Embedded Simulation Environment for AR Visor Biometric Capture
# ==============================================================================

class HardwareSignalPipeline:
    def __init__(self, scale_factor=1000000):
        self.scale_factor = scale_factor
        # ML Linear Regression coefficients for ambient light calibration (Pre-trained, fixed-point scaled by 10^6)
        # Formula: calibrated_response = W0 + W1 * raw_pupil + W2 * lux_reading
        self.w0 = int(2.5 * scale_factor)
        self.w1 = int(0.8 * scale_factor)
        self.w2 = int(-0.01 * scale_factor)

    def fixed_point_ml_regression(self, raw_pupil, lux_reading):
        """
        Computes the ambient light regression using strict fixed-point arithmetic.
        Simulates low-power integer units on the AR Visor edge hardware.
        """
        # All inputs must be integer scaled
        p_scaled = int(raw_pupil * self.scale_factor)
        l_scaled = int(lux_reading * self.scale_factor)

        # Term 1: W1 * Raw Pupil -> intermediate scaled by scale_factor^2
        t1 = (self.w1 * p_scaled) // self.scale_factor
        # Term 2: W2 * Lux Reading -> intermediate scaled by scale_factor^2
        t2 = (self.w2 * l_scaled) // self.scale_factor

        # Sum terms and divide to get final scaled calibrated pupil size
        calibrated = self.w0 + t1 + t2
        return max(0, calibrated)

    def savitzky_golay_filter(self, window_data):
        """
        Savitzky-Golay local quadratic smoothing filter (Window size = 5).
        Coefficients derived for quadratic/cubic fit:
        y[i] = (-3*x[i-2] + 12*x[i-1] + 17*x[i] + 12*x[i+1] - 3*x[i+2]) / 35
        """
        if len(window_data) < 5:
            return window_data[-1]

        # Use the last 5 readings
        x = window_data[-5:]
        smoothed = (-3*x[0] + 12*x[1] + 17*x[2] + 12*x[3] - 3*x[4]) // 35
        return smoothed

    def normalize_biometric(self, smoothed_signal, baseline_signal):
        """
        Normalizes the response against the user's base calibration.
        Returns a deterministic fixed-point scalar representing Pupil Response Ratio.
        """
        if baseline_signal == 0:
            return 0
        # Ratio = (smoothed_signal * scale_factor) / baseline_signal
        ratio = (smoothed_signal * self.scale_factor) // baseline_signal
        return ratio

    def generate_witness_commitment(self, presence_ratio, timestamp, mine_id="KAMO_01"):
        """
        Generates deterministic commitments ready for the ZK-circuit input.
        """
        commitment_payload = {
            "presence_ratio": str(presence_ratio),
            "timestamp": str(int(timestamp)),
            "mine_id": mine_id
        }
        # In a real environment, this payload is signed by the AR visor's HSM
        return commitment_payload

    def run_simulation(self, duration_sec=3, frequency_hz=10):
        """
        Runs the real-time simulation producing raw noisy sensor inputs 
        and processing them through the pipeline.
        """
        print("\n" + "="*80)
        print(" RESOURCE COMMAND: HARDWARE SIGNAL PIPELINE RUNNING")
        print("="*80)
        print(f"Sampling frequency: {frequency_hz} Hz | Duration: {duration_sec}s")
        
        signal_window = []
        baseline_pupil = int(4.2 * self.scale_factor)
        
        # Simulate active physiological response curve (event-related pupillary response)
        start_time = time.time()
        readings_count = 0
        
        while time.time() - start_time < duration_sec:
            current_time = time.time() - start_time
            
            # 1. Simulate physical environment telemetry with micro-vibrations (noise)
            # Simulating micro-vibrations via high-frequency sine wave + random head jitters
            vibration_noise = math.sin(current_time * 50) * 0.15 + random.uniform(-0.05, 0.05)
            
            # Simulate actual pupil reflex (physiological signal)
            reflex_signal = 4.5 + math.sin(current_time * 2.5) * 0.4
            raw_pupil = reflex_signal + vibration_noise
            
            # Ambient light reading (lux) simulating mine shaft dynamic illumination
            lux_reading = 150.0 + math.cos(current_time * 0.5) * 50.0
            
            # 2. Step 1: Fixed-Point ML Regression for Light Calibration
            calibrated_val = self.fixed_point_ml_regression(raw_pupil, lux_reading)
            signal_window.append(calibrated_val)
            
            # 3. Step 2: Savitzky-Golay Vibration Filtering
            smoothed_val = self.savitzky_golay_filter(signal_window)
            
            # 4. Step 3: Normalize output against user baseline
            presence_ratio = self.normalize_biometric(smoothed_val, baseline_pupil)
            
            readings_count += 1
            if readings_count % 10 == 0:
                print(f"[t={current_time:.2f}s] Raw Pupil: {raw_pupil:.3f} mm | Lux: {lux_reading:.1f} lx | Calibrated: {calibrated_val/self.scale_factor:.4f} | Smoothed: {smoothed_val/self.scale_factor:.4f} | PoP Ratio: {presence_ratio/self.scale_factor:.4f}")
                
            time.sleep(1.0 / frequency_hz)

        # Generate the final deterministic witness commitment package
        final_payload = self.generate_witness_commitment(presence_ratio, time.time())
        print("\n" + "="*80)
        print(" PIPELINE EXECUTION SUCCESSFUL - FINAL WITNESS COMMITTED")
        print("="*80)
        print(json.dumps(final_payload, indent=4))
        
        # Save final witness to file in a completely platform-agnostic manner
        output_dir = os.path.dirname(os.path.abspath(__file__))
        output_path = os.path.join(output_dir, "hardware_witness.json")
        with open(output_path, "w") as f:
            json.dump(final_payload, f, indent=4)
        print(f"Witness successfully exported to: {output_path}")

if __name__ == "__main__":
    pipeline = HardwareSignalPipeline()
    pipeline.run_simulation(duration_sec=3, frequency_hz=10)
