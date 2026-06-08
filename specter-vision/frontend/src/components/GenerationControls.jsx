import React from 'react';
import DirectorsMenu from './DirectorsMenu.jsx';
import './GenerationControls.css';

/* ── Directed Motion slider ─────────────────────────────────────── */
function DirectedMotion({ value, onChange }) {
  const pct = Math.round((value / 255) * 100);
  const label = pct < 20 ? 'SUBTLE' : pct < 50 ? 'FLUID' : pct < 78 ? 'DYNAMIC' : 'CINEMATIC';

  return (
    <div className="sv-motion">
      <div className="sv-motion__header">
        <span className="sv-eyebrow">Directed Motion</span>
        <div className="sv-motion__value-wrap">
          <span className="sv-motion__value">{pct}</span>
          <span className="sv-motion__value-unit">%</span>
        </div>
      </div>

      <div className="sv-motion__label-row">
        <span className="sv-motion__scale-label">SUBTLE</span>
        <span className="sv-motion__mode-badge">{label}</span>
        <span className="sv-motion__scale-label">CINEMATIC</span>
      </div>

      <div className="sv-motion__track-wrap">
        <input
          type="range"
          min={0}
          max={255}
          value={value}
          onChange={e => onChange(Number(e.target.value))}
          className="sv-motion__range"
          style={{ '--pct': `${pct}%` }}
        />
        {/* Tick marks */}
        <div className="sv-motion__ticks" aria-hidden>
          {[0, 64, 128, 192, 255].map(v => (
            <div key={v} className={`sv-motion__tick${v <= value ? ' sv-motion__tick--lit' : ''}`} />
          ))}
        </div>
      </div>

      <p className="sv-motion__hint">
        Controls Wan 2.1 motion_bucket_id — higher values produce more dramatic camera movement
      </p>
    </div>
  );
}

/* ── Compact param row ──────────────────────────────────────────── */
function ParamRow({ label, value, min, max, step = 1, onChange }) {
  return (
    <div className="sv-ctrl__param-row">
      <span className="sv-ctrl__param-label">{label}</span>
      <div className="sv-ctrl__param-input-wrap">
        <button
          className="sv-ctrl__param-step"
          onClick={() => onChange(Math.max(min, value - step))}
        >−</button>
        <span className="sv-ctrl__param-val">{value}</span>
        <button
          className="sv-ctrl__param-step"
          onClick={() => onChange(Math.min(max, value + step))}
        >+</button>
      </div>
    </div>
  );
}

/* ── Main controls panel ────────────────────────────────────────── */
export default function GenerationControls({ state, dispatch, onGenerate, canGenerate }) {
  const {
    modelMode, motionBucket, steps, guidanceScale, numFrames, fps,
    canvasMode, jobStatus, progress,
  } = state;

  const isGenerating = canvasMode === 'generating';

  const setParam = (k, v) => dispatch({ type: 'SET_PARAM', k, v });

  return (
    <aside className="sv-ctrl">
      <div className="sv-ctrl__header">
        <span className="sv-eyebrow">Generation Engine</span>
      </div>
      <div className="sv-divider" />

      {/* Mode toggle */}
      <div className="sv-ctrl__section">
        <span className="sv-label sv-ctrl__section-label">Model Mode</span>
        <div className="sv-ctrl__mode-toggle">
          <button
            className={`sv-ctrl__mode-btn${modelMode === 'i2v' ? ' sv-ctrl__mode-btn--active' : ''}`}
            onClick={() => setParam('modelMode', 'i2v')}
          >
            I2V
            <span className="sv-ctrl__mode-sub">Image → Video</span>
          </button>
          <button
            className={`sv-ctrl__mode-btn${modelMode === 't2v' ? ' sv-ctrl__mode-btn--active' : ''}`}
            onClick={() => setParam('modelMode', 't2v')}
          >
            T2V
            <span className="sv-ctrl__mode-sub">Text → Video</span>
          </button>
        </div>
      </div>

      <div className="sv-divider" />

      {/* Directed motion */}
      <div className="sv-ctrl__section">
        <DirectedMotion
          value={motionBucket}
          onChange={v => dispatch({ type: 'SET_MOTION', v })}
        />
      </div>

      <div className="sv-divider" />

      {/* Director's Menu */}
      <div className="sv-ctrl__section">
        <DirectorsMenu state={state} dispatch={dispatch} />
      </div>

      <div className="sv-divider" />

      {/* Advanced params */}
      <div className="sv-ctrl__section sv-ctrl__section--params">
        <span className="sv-label sv-ctrl__section-label">Render Parameters</span>
        <div className="sv-ctrl__params-grid">
          <ParamRow label="STEPS"    value={steps}         min={10} max={50}  step={1}    onChange={v => setParam('steps', v)} />
          <ParamRow label="CFG"      value={guidanceScale} min={1}  max={15}  step={0.5}  onChange={v => setParam('guidanceScale', v)} />
          <ParamRow label="FRAMES"   value={numFrames}     min={25} max={121} step={4}    onChange={v => setParam('numFrames', v)} />
          <ParamRow label="FPS"      value={fps}           min={8}  max={30}  step={1}    onChange={v => setParam('fps', v)} />
        </div>

        {/* Duration readout */}
        <div className="sv-ctrl__duration">
          <span className="sv-ctrl__duration-label">DURATION</span>
          <span className="sv-ctrl__duration-val">
            {(numFrames / fps).toFixed(1)}
            <span className="sv-ctrl__duration-unit">s</span>
          </span>
        </div>
      </div>

      <div className="sv-ctrl__spacer" />
      <div className="sv-divider" />

      {/* Generate button */}
      <div className="sv-ctrl__generate-wrap">
        {isGenerating ? (
          <div className="sv-ctrl__generating-state">
            <div className="sv-ctrl__gen-bar-track">
              <div className="sv-ctrl__gen-bar-fill" style={{ width: `${progress}%` }} />
            </div>
            <div className="sv-ctrl__gen-status">
              <span className="sv-ctrl__gen-spinner" />
              <span className="sv-ctrl__gen-status-text">RENDERING — {Math.round(progress)}%</span>
            </div>
          </div>
        ) : (
          <button
            className={`sv-ctrl__generate-btn${canGenerate ? '' : ' sv-ctrl__generate-btn--disabled'}`}
            onClick={onGenerate}
            disabled={!canGenerate}
          >
            <span className="sv-ctrl__gen-glyph">◈</span>
            <span className="sv-ctrl__gen-label">GENERATE SEQUENCE</span>
            <span className="sv-ctrl__gen-sub">
              {modelMode === 'i2v' ? 'Image-to-Video · Wan 2.1' : 'Text-to-Video · Wan 2.1'}
            </span>
          </button>
        )}

        {/* Validation hint */}
        {!canGenerate && !isGenerating && (
          <p className="sv-ctrl__hint">
            {state.prompt.trim().length === 0
              ? '↑ Enter a prompt to continue'
              : modelMode === 'i2v' ? '← Select or upload a CAD render'
              : ''}
          </p>
        )}
      </div>
    </aside>
  );
}
