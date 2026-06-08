import React, { useState, useEffect } from 'react';
import './StatusBar.css';

export default function StatusBar({ state }) {
  const [time, setTime] = useState(new Date());

  useEffect(() => {
    const id = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(id);
  }, []);

  const { comfyStatus, gpuVram, queueDepth, jobStatus, currentJobId } = state;

  const statusColor = {
    online:   'var(--green)',
    offline:  'var(--red)',
    checking: 'var(--amber)',
  }[comfyStatus] ?? 'var(--amber)';

  const vramPct = gpuVram ? gpuVram.pct : null;

  return (
    <header className="sv-statusbar">
      {/* Identity */}
      <div className="sv-statusbar__brand">
        <span className="sv-statusbar__glyph">◈</span>
        <span className="sv-statusbar__name">SPECTER-VISION</span>
        <span className="sv-statusbar__divider">|</span>
        <span className="sv-statusbar__sub">WAN 2.1 ENGINE</span>
      </div>

      {/* Center — active job */}
      <div className="sv-statusbar__center">
        {jobStatus === 'running' && (
          <span className="sv-statusbar__job-pill sv-statusbar__job-pill--running">
            <span className="sv-statusbar__spinner" />
            RENDERING — {Math.round(state.progress)}%
          </span>
        )}
        {jobStatus === 'complete' && (
          <span className="sv-statusbar__job-pill sv-statusbar__job-pill--done">
            ✓ SEQUENCE COMPLETE
          </span>
        )}
        {jobStatus === 'failed' && (
          <span className="sv-statusbar__job-pill sv-statusbar__job-pill--failed">
            ✕ RENDER FAILED
          </span>
        )}
        {jobStatus === 'queued' && (
          <span className="sv-statusbar__job-pill sv-statusbar__job-pill--queued">
            <span className="sv-statusbar__dot" />
            IN QUEUE
          </span>
        )}
      </div>

      {/* Right — system stats */}
      <div className="sv-statusbar__stats">
        {/* ComfyUI */}
        <div className="sv-statusbar__stat">
          <span className="sv-statusbar__dot-status" style={{ background: statusColor }} />
          <span className="sv-statusbar__stat-label">COMFYUI</span>
          <span className="sv-statusbar__stat-val">{comfyStatus.toUpperCase()}</span>
        </div>

        {/* VRAM */}
        {gpuVram && (
          <div className="sv-statusbar__stat">
            <span className="sv-statusbar__stat-label">VRAM</span>
            <span className="sv-statusbar__stat-val">
              {gpuVram.used_gb}
              <span className="sv-statusbar__stat-unit">GB</span>
              &nbsp;/&nbsp;
              {gpuVram.total_gb}
              <span className="sv-statusbar__stat-unit">GB</span>
            </span>
            <div className="sv-statusbar__vram-bar">
              <div
                className="sv-statusbar__vram-fill"
                style={{ width: `${vramPct}%`, background: vramPct > 85 ? 'var(--red)' : 'var(--cyan)' }}
              />
            </div>
          </div>
        )}

        {/* Queue */}
        <div className="sv-statusbar__stat">
          <span className="sv-statusbar__stat-label">QUEUE</span>
          <span className="sv-statusbar__stat-val">{queueDepth}</span>
        </div>

        {/* Clock */}
        <div className="sv-statusbar__clock">
          {time.toLocaleTimeString('en-ZA', { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false })}
        </div>
      </div>
    </header>
  );
}
