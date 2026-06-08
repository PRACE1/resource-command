import React from 'react';
import './DirectorsMenu.css';

/* ── Cinematic prompt-suffix presets ────────────────────────────────
   These inject text into the generation prompt. They do NOT change
   the pipeline — only the conditioning text.
*/
export const CINEMATIC_PRESETS = [
  {
    id:          'anamorphic',
    label:       'ANAMORPHIC',
    icon:        '⬡',
    accent:      'cyan',
    description: '2.39:1 · Oval bokeh · Lens streak',
    suffix:      'anamorphic 2.39:1 widescreen scope lens, oval bokeh highlights, horizontal lens flare streak, anamorphic barrel distortion at frame edges, cinematic scope format',
  },
  {
    id:          'kodak5219',
    label:       'KODAK 5219',
    icon:        '◉',
    accent:      'gold',
    description: 'Vision3 film · Tungsten · Natural grain',
    suffix:      'Kodak Vision3 5219 film stock, tungsten balanced color grading, natural organic film grain, warm shadow tones with lifted blacks, slight green midtone push, analog celluloid texture, cinema verité',
  },
  {
    id:          'volumetric',
    label:       'VOLUMETRIC',
    icon:        '◈',
    accent:      'purple',
    description: 'God rays · Haze · Light shafts',
    suffix:      'volumetric god ray lighting, thick atmospheric industrial haze, cinematic light shaft diffusion, suspended metallic dust particles caught in beam, dense fog machine atmosphere, chiaroscuro industrial',
  },
];

/* ── Pipeline feature toggles ───────────────────────────────────────
   These change the ComfyUI workflow graph itself — not just the prompt.
*/
export const PIPELINE_FEATURES = [
  {
    id:          'geometryLock',
    label:       'GEOMETRY LOCK',
    icon:        '⬖',
    accent:      'amber',
    description: 'ControlNet depth + canny · Zero geometry drift',
    detail:      'Extracts depth map + edge map from your CAD render and enforces them as ControlNet conditioning across every diffusion step. Eliminates the "melting chassis" effect.',
    pipeline:    true,
  },
  {
    id:          'temporalMaster',
    label:       'TEMPORAL MASTER',
    icon:        '◫',
    accent:      'green',
    description: 'RIFE 2× interpolation · Tiled VAE · CRF 18',
    detail:      'Decodes via tiled VAE for temporal coherence, then RIFE-interpolates to double the frame count. Output is H264 CRF 18 — near-lossless. Eliminates flicker.',
    pipeline:    true,
    defaultOn:   true,
  },
];

/* ── Preset card ──────────────────────────────────────────────────── */
function PresetCard({ preset, isActive, onToggle }) {
  const accentClass = `sv-dm__card--${preset.accent}`;
  return (
    <button
      className={`sv-dm__card ${accentClass}${isActive ? ' sv-dm__card--active' : ''}`}
      onClick={() => onToggle(preset.id)}
      title={preset.suffix || preset.detail}
    >
      <div className="sv-dm__card-left">
        <span className="sv-dm__card-icon">{preset.icon}</span>
      </div>
      <div className="sv-dm__card-body">
        <span className="sv-dm__card-label">{preset.label}</span>
        <span className="sv-dm__card-desc">{preset.description}</span>
      </div>
      <div className="sv-dm__card-right">
        <div className={`sv-dm__toggle${isActive ? ' sv-dm__toggle--on' : ''}`}>
          <div className="sv-dm__toggle-knob" />
        </div>
      </div>
    </button>
  );
}

/* ── Director's Menu ─────────────────────────────────────────────── */
export default function DirectorsMenu({ state, dispatch }) {
  const { activePresets, geometryLock, temporalMaster } = state;

  const togglePreset = (id) => dispatch({ type: 'TOGGLE_PRESET', id });

  const togglePipeline = (id) => {
    if (id === 'geometryLock')   dispatch({ type: 'SET_PARAM', k: 'geometryLock',  v: !geometryLock });
    if (id === 'temporalMaster') dispatch({ type: 'SET_PARAM', k: 'temporalMaster', v: !temporalMaster });
  };

  const isPipelineActive = (id) => {
    if (id === 'geometryLock')   return geometryLock;
    if (id === 'temporalMaster') return temporalMaster;
    return false;
  };

  const activeCount = activePresets.length + (geometryLock ? 1 : 0) + (temporalMaster ? 1 : 0);

  return (
    <div className="sv-dm">
      <div className="sv-dm__header">
        <span className="sv-eyebrow">Director's Menu</span>
        {activeCount > 0 && (
          <span className="sv-dm__active-count">{activeCount} ACTIVE</span>
        )}
      </div>

      {/* Cinematic Grade — prompt suffix injectors */}
      <div className="sv-dm__group">
        <span className="sv-dm__group-label">CINEMATIC GRADE</span>
        <div className="sv-dm__cards">
          {CINEMATIC_PRESETS.map(p => (
            <PresetCard
              key={p.id}
              preset={p}
              isActive={activePresets.includes(p.id)}
              onToggle={togglePreset}
            />
          ))}
        </div>
      </div>

      {/* Pipeline Features — workflow graph changes */}
      <div className="sv-dm__group sv-dm__group--pipeline">
        <span className="sv-dm__group-label">PIPELINE FEATURES</span>
        <div className="sv-dm__cards">
          {PIPELINE_FEATURES.map(p => (
            <PresetCard
              key={p.id}
              preset={p}
              isActive={isPipelineActive(p.id)}
              onToggle={togglePipeline}
            />
          ))}
        </div>
      </div>

      {/* Active suffix preview */}
      {activePresets.length > 0 && (
        <div className="sv-dm__suffix-preview">
          <span className="sv-dm__suffix-label">INJECTING INTO PROMPT ↗</span>
          <p className="sv-dm__suffix-text">
            {activePresets
              .map(id => CINEMATIC_PRESETS.find(p => p.id === id)?.suffix)
              .filter(Boolean)
              .join(' · ')
              .slice(0, 140)}
            {activePresets.length > 1 && '…'}
          </p>
        </div>
      )}
    </div>
  );
}
