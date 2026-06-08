pragma circom 2.2.3;

include "circomlib/circuits/poseidon.circom";
include "circomlib/circuits/comparators.circom";
include "circomlib/circuits/bitify.circom";
include "./ExponentialDecay.circom";

template ComplianceCircuit() {
    // ==============================================================================
    // PUBLIC INPUTS
    // ==============================================================================
    signal input volume_commitment_hash;
    signal input tax_paid_usd;
    signal input royalty_rate_bps;
    signal input min_token_threshold; // PoP Minimum authentication threshold

    // ==============================================================================
    // PRIVATE INPUTS (The "Sovereign Witnesses")
    // ==============================================================================
    signal input volume_v;
    signal input density_d;
    signal input grade_g;
    signal input volume_nonce;
    
    // Biometric presence witnesses
    signal input initial_token;
    signal input decay_constant_kt;
    signal input k_shift;
    signal input reduced_x;
    signal input rem_decay;

    // MULTIPLICATIVE INVERSE WITNESSES (For RC-01/02 Hardening)
    signal input inv_density_d;
    signal input inv_grade_g;

    // REMAINDER WITNESSES (For Fixed-Point Precision)
    signal input rem_tonnage;
    signal input rem_mineral;
    signal input rem_royalty;

    // ==============================================================================
    // 0. INPUT RANGE CHECKS (Rationalized Bit-Widths)
    // ==============================================================================
    component vRange = Num2Bits(40); // Max 10^12 m3
    vRange.in <== volume_v;
    component dRange = Num2Bits(26); // Max ~67 t/m3
    dRange.in <== density_d;
    component gRange = Num2Bits(20); // Max 100% (1,000,000)
    gRange.in <== grade_g;

    // 0.1 SEMANTIC PHYSICS CHECK: grade_g <= 1,000,000 (100% grade)
    component gMax = LessThan(20);
    gMax.in[0] <== grade_g;
    gMax.in[1] <== 1000001; 
    gMax.out === 1;

    // 0.2 RC-01 & RC-02: MULTIPLICATIVE INVERSE LOCK
    density_d * inv_density_d === 1;
    grade_g * inv_grade_g === 1;

    // 0.3 RC-04: tax_paid_usd range constraint (Derived: < 2^44)
    component taxRange = Num2Bits(44);
    taxRange.in <== tax_paid_usd;

    // 0.4 ROYALTY RATE BOUNDS CHECK: 1 bps <= royalty_rate_bps <= 5000 bps
    component rateMin = GreaterThan(13);
    rateMin.in[0] <== royalty_rate_bps;
    rateMin.in[1] <== 0;
    rateMin.out === 1;

    component rateMax = LessThan(13);
    rateMax.in[0] <== royalty_rate_bps;
    rateMax.in[1] <== 5001;
    rateMax.out === 1;

    // ==============================================================================
    // 1. ZK CRYPTOKINETICS (TEMPORAL PRESENCE DECAY INTEGRATION)
    // ==============================================================================
    // 1.1 In-Circuit Range Reduction
    component rangeRed = RangeReduction(32);
    rangeRed.raw_kt <== decay_constant_kt;
    rangeRed.k_shift <== k_shift;
    rangeRed.reduced_x <== reduced_x;

    // 1.2 Calculate Exponential Decay using [3/3] Padé Rational Approximation
    component decay = ExponentialDecayPade3(32);
    decay.x <== reduced_x;

    // 1.3 Calculate Decayed Biometric Token: (initial_token * decay_multiplier) / 10^6
    // Since circom doesn't support division in standard constraints, we assert multiplication balance
    signal current_token;
    current_token <-- (initial_token * decay.out) \ 1000000;

    // Scale balance constraint with remainder
    signal decay_mult;
    decay_mult <== initial_token * decay.out;
    decay_mult === (current_token * 1000000) + rem_decay;

    // Soundness check: 0 <= rem_decay < 1000000 (20 bits)
    component ltDecay = LessThan(20);
    ltDecay.in[0] <== rem_decay;
    ltDecay.in[1] <== 1000000;
    ltDecay.out === 1;

    // Enforce that decayed presence level exceeds the statutory threshold
    component presenceCheck = GreaterEqThan(32);
    presenceCheck.in[0] <== current_token;
    presenceCheck.in[1] <== min_token_threshold;
    presenceCheck.out === 1;

    // ==============================================================================
    // 2. TRUTH ANCHOR BINDING (Constraint 0)
    // ==============================================================================
    component pos = Poseidon(2);
    pos.inputs[0] <== volume_v;
    pos.inputs[1] <== volume_nonce;
    pos.out === volume_commitment_hash;

    // ==============================================================================
    // 3. TONNAGE CALCULATION (volume * density = tonnage * 10^6 + rem)
    // ==============================================================================
    signal tonnage_t;
    tonnage_t <-- (volume_v * density_d) \ 1000000;
    
    component tRange = Num2Bits(47);
    tRange.in <== tonnage_t;

    signal vol_dens;
    vol_dens <== volume_v * density_d;
    vol_dens === (tonnage_t * 1000000) + rem_tonnage;
    
    component lt1 = LessThan(20);
    lt1.in[0] <== rem_tonnage;
    lt1.in[1] <== 1000000;
    lt1.out === 1;

    // ==============================================================================
    // 4. MINERAL CONTENT CALCULATION (tonnage * grade = mineral * 10^6 + rem)
    // ==============================================================================
    signal mineral_content_m;
    mineral_content_m <-- (tonnage_t * grade_g) \ 1000000;

    component mRange = Num2Bits(47);
    mRange.in <== mineral_content_m;

    signal ton_grad;
    ton_grad <== tonnage_t * grade_g;
    ton_grad === (mineral_content_m * 1000000) + rem_mineral;

    component lt2 = LessThan(20);
    lt2.in[0] <== rem_mineral;
    lt2.in[1] <== 1000000;
    lt2.out === 1;

    // ==============================================================================
    // 5. ROYALTY ATTESTATION (mineral * royalty_rate_bps = tax_paid * 10000 + rem)
    // ==============================================================================
    signal lhs;
    lhs <== mineral_content_m * royalty_rate_bps;
    signal rhs;
    rhs <== tax_paid_usd * 10000;
    lhs === rhs + rem_royalty;

    component lt3 = LessThan(14);
    lt3.in[0] <== rem_royalty;
    lt3.in[1] <== 10000;
    lt3.out === 1;
}

component main {public [volume_commitment_hash, tax_paid_usd, royalty_rate_bps, min_token_threshold]} = ComplianceCircuit();
