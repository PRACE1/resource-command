import React, { useState } from 'react';
import './PromptTerminal.css';

const TEMPLATES = [
  {
    id: 'anamorphic',
    label: 'ANAMORPHIC',
    prompt: 'Anamorphic lens flare, 8K RAW, slow cinematic reveal, volumetric industrial fog, precision-engineered metal surfaces, golden investment-grade documentary lighting, shallow depth-of-field, film grain',
  },
  {
    id: 'aerial',
    label: 'AERIAL PULL',
    prompt: 'Overhead drone pullback reveal, golden-hour industrial lighting, heat distortion shimmer, machined titanium textures, facility-scale establishing shot, National Geographic documentary quality, ultra-wide anamorphic',
  },
  {
    id: 'macro',
    label: 'MACRO SPEC',
    prompt: 'Extreme macro lens close-up, V8 combustion cycle, thermal imaging overlay, aerospace-grade tolerances, IMAX 4K resolution, BBC Nature documentary pacing, cinematic rack focus, chromatic depth',
  },
  {
    id: 'orbit',
    label: 'NIGHT ORBIT',
    prompt: 'Cinematic 360-degree orbit, night-time industrial complex, volumetric light shafts, rain-slicked polished concrete, moody Forbes industrial documentary grading, HDR lens bloom, fog machine atmosphere',
  },
  {
    id: 'timelapse',
    label: 'ASSEMBLY',
    prompt: 'Time-lapse precision manufacturing sequence, ultra-clean assembly choreography, hyperreal industrial aesthetic, Senna-era documentary grading, 8K anamorphic widescreen, spotlit component reveal, silent reverence',
  },
];

export default function PromptTerminal({ state, dispatch }) {
  const [showNeg, setShowNeg] = useState(false);
  const { prompt, negativePrompt } = state;

  const injectTemplate = (t) => {
    dispatch({ type: 'SET_PROMPT', v: t.prompt });
  };

  return (
    <div className="sv-prompt">
      <div className="sv-prompt__header">
        <span className="sv-eyebrow">Directed Intelligence</span>
        <span className="sv-prompt__terminal-label">// PROMPT TERMINAL</span>
        <div className="sv-prompt__header-actions">
          <button
            className={`sv-prompt__neg-toggle${showNeg ? ' sv-prompt__neg-toggle--active' : ''}`}
            onClick={() => setShowNeg(v => !v)}
          >
            NEG PROMPT
          </button>
          {prompt && (
            <button
              className="sv-prompt__clear-btn"
              onClick={() => dispatch({ type: 'SET_PROMPT', v: '' })}
            >
              CLEAR
            </button>
          )}
        </div>
      </div>

      <div className="sv-divider" />

      {/* Template rail */}
      <div className="sv-prompt__templates">
        {TEMPLATES.map(t => (
          <button
            key={t.id}
            className={`sv-prompt__template-btn${prompt === t.prompt ? ' sv-prompt__template-btn--active' : ''}`}
            onClick={() => injectTemplate(t)}
            title={t.prompt}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* Positive prompt */}
      <div className="sv-prompt__input-wrap">
        <textarea
          className="sv-prompt__textarea"
          value={prompt}
          onChange={e => dispatch({ type: 'SET_PROMPT', v: e.target.value })}
          placeholder="Describe the cinematic sequence… or inject a template above."
          rows={3}
          spellCheck={false}
        />
        <span className="sv-prompt__char-count">{prompt.length}</span>
      </div>

      {/* Negative prompt (collapsible) */}
      {showNeg && (
        <div className="sv-prompt__neg-wrap">
          <span className="sv-label sv-prompt__neg-label">Negative</span>
          <textarea
            className="sv-prompt__textarea sv-prompt__textarea--neg"
            value={negativePrompt}
            onChange={e => dispatch({ type: 'SET_NEG_PROMPT', v: e.target.value })}
            placeholder="Exclusions…"
            rows={2}
            spellCheck={false}
          />
        </div>
      )}
    </div>
  );
}
