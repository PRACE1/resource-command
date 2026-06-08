// Resource Command — Compliance Guest Program
// ============================================
// RISC0 zkVM guest program. This is the circuit.
//
// It receives the PRIVATE witness (satellite passes + biometric data)
// and commits only PUBLIC outputs (boolean assertions + hashes).
// No raw data ever leaves the enclave.
//
// Build:
//   cargo risczero build --manifest-path Cargo.toml
//   → Produces: target/riscv-guest/riscv32im-risc0-zkvm-elf/release/compliance_guest
//
// The IMAGE_ID from this build is what you register with Boundless.

use risc0_zkvm::guest::env;
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};

// ── Private Witness Structures ──────────────────────────────────────────────

#[derive(Deserialize)]
struct SatellitePass {
    pass_id: String,
    timestamp: String,
    displacement_m: f32,      // Ground displacement in metres (InSAR result)
    coherence: f32,           // SAR coherence 0-1 (data quality)
    area_km2: f32,
}

#[derive(Deserialize)]
struct BiometricAttestation {
    session_id: String,
    presence_ratio: f32,      // 0-1, auditor face presence fraction
    lux_level: f32,           // Ambient light in lux
    gaze_stable: bool,        // Eye tracking stability
    timestamp: f64,
    signature: String,        // HMAC-SHA256 of (session_id + timestamp)
}

#[derive(Deserialize)]
struct ComplianceWitness {
    satellite_passes: Vec<SatellitePass>,
    biometric: BiometricAttestation,
    batch_id: String,
    mine_lat: f32,            // Bounding box check (not revealed)
    mine_lon: f32,
    audit_timestamp: f64,
}

// ── Public Journal Structures (committed to receipt) ────────────────────────

#[derive(Serialize)]
struct ComplianceJournal {
    // Committed public statements — verifier sees ONLY these
    batch_id: String,
    pass_count: u32,
    max_displacement_below_threshold: bool,   // all passes < 3mm
    presence_ratio_satisfied: bool,           // ratio >= 0.85
    lux_satisfied: bool,                      // lux >= 50.0
    gaze_stable: bool,
    biometric_session: String,               // session_id (not raw biometric)
    mine_region_hash: String,                // SHA256 of (lat, lon), not raw coords
    audit_timestamp: u64,
    max_observed_displacement_mm: u32,       // rounded, not exact (privacy-preserving)
}

// ── Compliance Thresholds ───────────────────────────────────────────────────
const MAX_DISPLACEMENT_M: f32    = 0.003;   // 3mm Kamoa-Kakula threshold
const MIN_PRESENCE_RATIO: f32    = 0.85;    // 85% face presence required
const MIN_LUX: f32               = 50.0;    // Minimum lighting
const MIN_COHERENCE: f32         = 0.65;    // Data quality floor

// Kamoa-Kakula bounding box (DRC Copperbelt)
const MINE_LAT_MIN: f32 = -10.80;
const MINE_LAT_MAX: f32 = -10.70;
const MINE_LON_MIN: f32 =  25.80;
const MINE_LON_MAX: f32 =  26.00;

fn main() {
    // ── READ PRIVATE WITNESS ─────────────────────────────────────────────────
    let witness: ComplianceWitness = env::read();

    // ── ASSERTION 1: Geographic bounding box ────────────────────────────────
    // Proves audit occurred at Kamoa-Kakula coordinates
    // Exact coordinates are NOT committed — only a hash
    assert!(
        witness.mine_lat >= MINE_LAT_MIN && witness.mine_lat <= MINE_LAT_MAX,
        "Mine latitude outside Kamoa-Kakula bounding box"
    );
    assert!(
        witness.mine_lon >= MINE_LON_MIN && witness.mine_lon <= MINE_LON_MAX,
        "Mine longitude outside Kamoa-Kakula bounding box"
    );

    // ── ASSERTION 2: Satellite data quality ─────────────────────────────────
    // All passes must have coherence above floor (ensures real SAR data)
    for pass in &witness.satellite_passes {
        assert!(
            pass.coherence >= MIN_COHERENCE,
            "SAR coherence below minimum: {} (pass {})",
            pass.coherence,
            pass.pass_id
        );
    }

    // ── ASSERTION 3: Displacement threshold ─────────────────────────────────
    // No ground displacement exceeds 3mm (compliance threshold)
    let mut max_displacement = 0.0f32;
    for pass in &witness.satellite_passes {
        assert!(
            pass.displacement_m < MAX_DISPLACEMENT_M,
            "Ground displacement {} m exceeds 3mm threshold at {}",
            pass.displacement_m,
            pass.timestamp
        );
        if pass.displacement_m > max_displacement {
            max_displacement = pass.displacement_m;
        }
    }

    // ── ASSERTION 4: Biometric presence ─────────────────────────────────────
    assert!(
        witness.biometric.presence_ratio >= MIN_PRESENCE_RATIO,
        "Auditor presence ratio {} below 0.85 minimum",
        witness.biometric.presence_ratio
    );

    // ── ASSERTION 5: Lighting standard ──────────────────────────────────────
    assert!(
        witness.biometric.lux_level >= MIN_LUX,
        "Ambient lux {} below 50.0 minimum for valid audit",
        witness.biometric.lux_level
    );

    // ── BUILD PRIVACY-PRESERVING JOURNAL ────────────────────────────────────
    // Hash coordinates — proves location without revealing exact lat/lon
    let mut hasher = Sha256::new();
    hasher.update(format!("{:.4},{:.4}", witness.mine_lat, witness.mine_lon).as_bytes());
    let mine_region_hash = format!("{:x}", hasher.finalize())[..16].to_string();

    // Round max displacement to nearest 0.1mm — enough to prove compliance
    // without leaking precise geological data
    let max_mm_rounded = (max_displacement * 10_000.0).round() as u32; // in 0.1mm units

    let journal = ComplianceJournal {
        batch_id: witness.batch_id.clone(),
        pass_count: witness.satellite_passes.len() as u32,
        max_displacement_below_threshold: true,  // only reachable if assertion passed
        presence_ratio_satisfied: true,
        lux_satisfied: true,
        gaze_stable: witness.biometric.gaze_stable,
        biometric_session: witness.biometric.session_id.clone(),
        mine_region_hash,
        audit_timestamp: witness.audit_timestamp as u64,
        max_observed_displacement_mm: max_mm_rounded,
    };

    // ── COMMIT PUBLIC OUTPUTS ────────────────────────────────────────────────
    env::commit(&journal);
}
