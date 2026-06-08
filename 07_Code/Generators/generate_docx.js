const fs = require('fs');
const { Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType } = require('docx');

const doc = new Document({
    sections: [{
        children: [
            new Paragraph({ text: "MEMORANDUM: AUDIT ENGAGEMENT SCOPING", heading: HeadingLevel.HEADING_1, alignment: AlignmentType.CENTER }),
            new Paragraph({ text: "" }),
            new Paragraph({ children: [new TextRun({ text: "TO: ", bold: true }), new TextRun("Trail of Bits (Cryptographic Services Division)")] }),
            new Paragraph({ children: [new TextRun({ text: "FROM: ", bold: true }), new TextRun("[Principal Name / Resource Command]")] }),
            new Paragraph({ children: [new TextRun({ text: "DATE: ", bold: true }), new TextRun(new Date().toLocaleDateString())] }),
            new Paragraph({ children: [new TextRun({ text: "SUBJECT: ", bold: true }), new TextRun("ZK-SNARK Protocol Review — Resource Command v1.4")] }),
            new Paragraph({ text: "" }),
            new Paragraph({ text: "---", alignment: AlignmentType.CENTER }),
            new Paragraph({ text: "" }),
            
            new Paragraph({ text: "1. PROJECT OVERVIEW", heading: HeadingLevel.HEADING_2 }),
            new Paragraph({ text: "Resource Command is an institutional-grade zero-knowledge (ZK) compliance layer for sovereign mineral revenue verification. The protocol enables mining operators to prove fiscal and volumetric compliance without disclosing underlying production telemetry." }),
            
            new Paragraph({ text: "" }),
            new Paragraph({ text: "2. TECHNICAL ARCHITECTURE", heading: HeadingLevel.HEADING_2 }),
            new Paragraph({ text: "The reference implementation is built in Circom 2.2.3, targeting the BN254 scalar field. The circuit (542 constraints) utilizes Poseidon hashing for commitment binding and implements a fixed-point (10^6) R1CS scaling gate architecture with explicit soundness-hardened range constraints and bit-width optimization." }),
            
            new Paragraph({ text: "" }),
            new Paragraph({ text: "3. KNOWN DISCLOSURES & RESOLVED ITEMS", heading: HeadingLevel.HEADING_2 }),
            new Paragraph({ text: "The following items reflect the current hardening status of the protocol:" }),
            new Paragraph({ text: "• RC-01/02 Zero-Value Exploit (FIXED): Remediated via GreaterThan(64) gates enforcing non-zero floors for density and grade inputs.", bullet: { level: 0 } }),
            new Paragraph({ text: "• RC-01/02 Deployment Parameters (PENDING): Current circuit enforces x >= 1. Final physical/economic minimums (e.g., 2.5 t/m³ for density) are pending regulatory determination by ZRA and will be hardcoded prior to Phase 2 deployment.", bullet: { level: 0 } }),
            new Paragraph({ text: "• RC-03 Oracle Architectural Gap (OPEN): Current commitment binds only to volume_v. Architectural roadmap includes extending the oracle pipeline to commit independent assay-data hashes (density and grade) or requiring MRC co-signatures.", bullet: { level: 0 } }),
            new Paragraph({ text: "• RC-04 Public Input Range (FIXED): Added Num2Bits(64) range check to the tax_paid_usd public input.", bullet: { level: 0 } }),
            
            new Paragraph({ text: "" }),
            new Paragraph({ text: "4. INTEGRITY VERIFICATION", heading: HeadingLevel.HEADING_2 }),
            new Paragraph({ text: "• compliance.circom (v1.4): 35ba1158dda62eb308a0a7a51f975d508b4e02baeab4422dbd207e3ff04bb402" }),
            new Paragraph({ text: "• resource_command_zkp.py (v2.4): f1669c3abe8bec9f3b3193778a819ed06955f435b889320e6c87ce2921c75800" }),
            new Paragraph({ text: "• Technical Pre-Read (v1.8): b4832cabc607d5c413a12f135377badbba274fdf4074fe9a11bbbd783553ca7a" }),
            
            new Paragraph({ text: "" }),
            new Paragraph({ text: "5. REQUEST FOR QUOTE", heading: HeadingLevel.HEADING_2 }),
            new Paragraph({ text: "We request a formal scoping call to discuss a comprehensive security audit of the Resource Command protocol. We are prepared to transmit the full engagement pack upon execution of a standard NDA." }),
        ],
    }],
});

Packer.toBuffer(doc).then((buffer) => {
    fs.writeFileSync("ToB_Audit_Cover_Letter.docx", buffer);
    console.log("ToB_Audit_Cover_Letter.docx (v1.5) Finalized.");
});
