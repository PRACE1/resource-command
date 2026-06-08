/**
 * RC Session Start Hook
 * Runs at the beginning of every Claude Code session.
 * Injects master context + memory + latest intel feed into the model.
 */

const fs   = require('fs');
const path = require('path');

const RC_ROOT  = 'C:\\Users\\R5 5600 GT\\.gemini\\antigravity\\scratch\\resource_command';
const MEM_ROOT = 'C:\\Users\\R5 5600 GT\\.claude\\projects\\C--Users-R5-5600-GT--gemini-antigravity-scratch-resource-command\\memory';

function safeRead(filePath, maxChars) {
  try {
    const content = fs.readFileSync(filePath, 'utf8');
    return content.length > maxChars ? content.slice(0, maxChars) + '\n[...truncated]' : content;
  } catch {
    return '[Not found: ' + path.basename(filePath) + ']';
  }
}

const masterCtx  = safeRead(path.join(RC_ROOT,  'MASTER_CONTEXT.md'),        4000);
const memIndex   = safeRead(path.join(MEM_ROOT, 'MEMORY.md'),                1500);
const intelFeed  = safeRead(path.join(RC_ROOT,  'memory', 'intelligence_feed.md'), 1200);

const context = [
  '=== RC SESSION AUTO-LOADED — ' + new Date().toISOString().slice(0,10) + ' ===',
  '',
  masterCtx,
  '',
  '--- MEMORY INDEX ---',
  memIndex,
  '',
  '--- LATEST INTELLIGENCE FEED ---',
  intelFeed,
].join('\n');

process.stdout.write(JSON.stringify({
  hookSpecificOutput: {
    hookEventName: 'SessionStart',
    additionalContext: context
  }
}));
