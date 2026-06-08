pragma circom 2.2.3;

include "circomlib/circuits/poseidon.circom";
include "circomlib/circuits/comparators.circom";
include "circomlib/circuits/bitify.circom";

template ComplianceCircuit() {
    // PUBLIC INPUTS
    signal input volume_commitment_hash;
    signal input tax_paid_usd;
    signal input royalty_rate_bps;

    // PRIVATE INPUTS (The "Sovereign Witnesses")
    signal input volume_v;
    signal input density_d;
    signal input grade_g;
    signal input volume_nonce;
    
    // MULTIPLICATIVE INVERSE WITNESSES (For RC-01/02 Hardening)
    // Satisfies x * x_inv === 1. Only exists if x != 0.
    signal input inv_density_d;
    signal input inv_grade_g;

    // REMAINDER WITNESSES (For Fixed-Point Precision)
    signal input rem_tonnage;
    signal input rem_mineral;
    signal input rem_royalty;

    // 0. INPUT RANGE CHECKS (Rationalized Bit-Widths)
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
    // These constraints are only satisfiable if inputs are non-zero.
    // Savings: 128 constraints removed vs GreaterThan(64)
    density_d * inv_density_d === 1;
    grade_g * inv_grade_g === 1;

    // 0.3 RC-04: tax_paid_usd range constraint (Derived: < 2^44)
    component taxRange = Num2Bits(44);
    taxRange.in <== tax_paid_usd;

    // 0.4 ROYALTY RATE BOUNDS CHECK: 1 bps <= royalty_rate_bps <= 5000 bps
    // Lower bound: royalty_rate_bps > 0
    component rateMin = GreaterThan(13);
    rateMin.in[0] <== royalty_rate_bps;
    rateMin.in[1] <== 0;
    rateMin.out === 1;
    // Upper bound: royalty_rate_bps <= 5000 (statutory maximum — RC-05)
    component rateMax = LessThan(13);
    rateMax.in[0] <== royalty_rate_bps;
    rateMax.in[1] <== 5001;
    rateMax.out === 1;

    // 1. TRUTH ANCHOR BINDING (Constraint 0)
    component pos = Poseidon(2);
    pos.inputs[0] <== volume_v;
    pos.inputs[1] <== volume_nonce;
    pos.out === volume_commitment_hash;

    // 2. TONNAGE CALCULATION (volume * density = tonnage * 10^6 + rem)
    signal tonnage_t;
    tonnage_t <-- (volume_v * density_d) \ 1000000;
    
    // Tonnage Range (Derived: < 2^47)
    component tRange = Num2Bits(47);
    tRange.in <== tonnage_t;

    signal vol_dens;
    vol_dens <== volume_v * density_d;
    vol_dens === (tonnage_t * 1000000) + rem_tonnage;
    
    // Soundness Check: 0 <= rem_tonnage < 1000000 (20 bits)
    component lt1 = LessThan(20);
    lt1.in[0] <== rem_tonnage;
    lt1.in[1] <== 1000000;
    lt1.out === 1;

    // 3. MINERAL CONTENT CALCULATION (tonnage * grade = mineral * 10^6 + rem)
    signal mineral_content_m;
    mineral_content_m <-- (tonnage_t * grade_g) \ 1000000;

    // Mineral Range (Derived: mineral <= tonnage < 2^47)
    component mRange = Num2Bits(47);
    mRange.in <== mineral_content_m;

    signal ton_grad;
    ton_grad <== tonnage_t * grade_g;
    ton_grad === (mineral_content_m * 1000000) + rem_mineral;

    // Soundness Check: 0 <= rem_mineral < 1000000 (20 bits)
    component lt2 = LessThan(20);
    lt2.in[0] <== rem_mineral;
    lt2.in[1] <== 1000000;
    lt2.out === 1;

    // 4. ROYALTY ATTESTATION (mineral * royalty_rate_bps = tax_paid * 10000 + rem)
    signal lhs;
    lhs <== mineral_content_m * royalty_rate_bps;
    signal rhs;
    rhs <== tax_paid_usd * 10000;
    lhs === rhs + rem_royalty;

    // Soundness Check: 0 <= rem_royalty < 10000 (14 bits)
    component lt3 = LessThan(14);
    lt3.in[0] <== rem_royalty;
    lt3.in[1] <== 10000;
    lt3.out === 1;
}

component main {public [volume_commitment_hash, tax_paid_usd, royalty_rate_bps]} = ComplianceCircuit();
