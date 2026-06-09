# Hashcloak Meeting Cheat Sheet (The "Baby Words" Version)

**Goal of the Call:** 
You are NOT selling them the project. You are hiring them as mathematical mechanics to look under the hood of your zero-knowledge engine. Speak to them peer-to-peer.

---

### 1. The Opening Pitch (1 Minute)
"We are building a cryptographic verification layer for sovereign mineral royalties. Our core infrastructure takes satellite/LiDAR production data, hashes it on-site before the mining operator can alter it, and uses a Zero-Knowledge circuit to prove the operator's tax declarations match the physical reality."

### 2. The Tech Stack (What we used)
If they ask what you are building with, say:
*   **Proof System:** Groth16 (Industry standard, highly efficient)
*   **Elliptic Curve:** BN254 (Standard Ethereum/Web3 curve)
*   **Circuit Language:** Circom (839 constraints currently)
*   **Hash Function:** Poseidon (Highly optimized for ZK circuits)

### 3. The Magic Move (The Poseidon Truth Anchor)
They will ask how you stop mines from lying about the data before it enters the ZK proof.

**Your Answer:**
"We bind the physical reality to the math using a Poseidon Truth Anchor. The raw satellite/sensor data is converted into a Poseidon hash at the edge. The mining operator never sees the raw satellite data calculation. Our Circom circuit enforces that the operator's declared production volume *must* perfectly hash to that exact same Poseidon commitment, or the proof fails."

### 4. What You Did Already (The Flex)
"We have run internal adversarial reviews and passed our code through **Circomspect** (Trail of Bits' static analyzer). We've resolved the basic constraints, including enforcing upper bounds on the `royalty_rate_bps` to prevent overflow manipulation."

### 5. What You Want Hashcloak to Do (The Scope)
When they ask how they can help, read this exact list:
1.  **Fixed-Point Arithmetic Review:** Circom doesn't support decimals. We use custom bit-width constraints for percentages (like the 6% royalty rate). We need you to verify we didn't leave any overflow/underflow vulnerabilities in our math.
2.  **Side-Channel & Constant-Time Analysis:** We want to ensure our ZK circuit doesn't leak any of the operator's commercial data through timing attacks during the proof generation.
3.  **Poseidon Implementation Integrity:** Verify that our Poseidon hash binding is cryptographically sound and cannot be bypassed by an operator trying to forge a collision.

---

### Cheat Codes / Keywords to Drop:
*   **"BFT Consensus Topology"**: If they ask about the network, say you are using a PBFT (Practical Byzantine Fault Tolerance) network involving 5 institutional nodes (AfDB, World Bank, ZRA, etc.).
*   **"Soundness & Completeness"**: Use these words when asking them to verify your circuit. (e.g., "We need you to verify the soundness of the arithmetic.")
*   **"We are also engaging Trail of Bits"**: Drop this casually. It shows you are serious, well-funded, and playing in the absolute top tier of security auditing.
