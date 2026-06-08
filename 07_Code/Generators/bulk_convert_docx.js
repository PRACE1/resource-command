const fs = require('fs');
const { Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType } = require('docx');

async function createDoc(title, contentFile, outputFile) {
    const content = fs.readFileSync(contentFile, 'utf8');
    const lines = content.split('\n');
    
    const children = [
        new Paragraph({
            text: title,
            heading: HeadingLevel.HEADING_1,
            alignment: AlignmentType.CENTER,
        }),
        new Paragraph({ text: "" }),
    ];

    lines.forEach(line => {
        if (line.startsWith('# ')) {
            children.push(new Paragraph({ text: line.replace('# ', ''), heading: HeadingLevel.HEADING_1 }));
        } else if (line.startsWith('## ')) {
            children.push(new Paragraph({ text: line.replace('## ', ''), heading: HeadingLevel.HEADING_2 }));
        } else if (line.startsWith('### ')) {
            children.push(new Paragraph({ text: line.replace('### ', ''), heading: HeadingLevel.HEADING_3 }));
        } else if (line.trim() !== "") {
            children.push(new Paragraph({ text: line.trim() }));
        }
    });

    const doc = new Document({ sections: [{ children }] });
    const buffer = await Packer.toBuffer(doc);
    fs.writeFileSync(outputFile, buffer);
    console.log(`${outputFile} created successfully.`);
}

(async () => {
    await createDoc("RESOURCE COMMAND: TECHNICAL PRE-READ", "Resource_Command_Technical_Pre-Read.md", "Resource_Command_Technical_Pre-Read.docx");
    await createDoc("TRIPARTITE SOVEREIGN MOU", "Tripartite_Sovereign_MOU.md", "Tripartite_Sovereign_MOU.docx");
})();
