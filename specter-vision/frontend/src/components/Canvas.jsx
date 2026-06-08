import React, { useRef, useCallback, useState } from 'react';
import './Canvas.css';

/* ── Institutional Export — format definitions ───────────────────── */
const EXPORT_FORMATS = [
  {
    id:      'prores422',
    label:   'PRORES 422 HQ',
    badge:   'EDIT MASTER',
    icon:    '◈',
    ext:     '.MOV',
    desc:    'DaVinci Resolve · Premiere · Avid',
    size:    '~180 MB / min',
    accent:  'gold',
    detail:  '10-bit 4:2:2 · yuv422p10le · bt709',
  },
  {
    id:      'h264_presentation',
    label:   'H.264 BOARDROOM',
    badge:   'PRESENTATION',
    icon:    '◉',
    ext:     '.MP4',
    desc:    'PowerPoint · Keynote · LinkedIn',
    size:    '~12 MB / min',
    accent:  'cyan',
    detail:  'CRF 18 · Progressive download · web-optimised',
  },
  {
    id:      'h264_web',
    label:   'H.264 WEB / MOBILE',
    badge:   'SOCIAL & WHATSAPP',
    icon:    '⬡',
    ext:     '.MP4',
    desc:    'WhatsApp · Instagram · Telegram',
    size:    '~4 MB / min',
    accent:  'purple',
    detail:  'CRF 26 · 720p cap · 4 Mbps ceiling',
  },
];

/* ── Single export format card ──────────────────────────────────── */
function ExportCard({ fmt, exportState, onExport }) {
  const st = exportState?.status ?? 'idle';
  return (
    <div className={`sv-export__card sv-export__card--${fmt.accent}${st !== 'idle' ? ` sv-export__card--${st}` : ''}`}>
      <div className="sv-export__card-top">
        <span className="sv-export__card-icon">{fmt.icon}</span>
        <div className="sv-export__card-titles">
          <span className="sv-export__card-label">{fmt.label}</span>
          <span className="sv-export__card-badge">{fmt.badge}</span>
        </div>
      </div>
      <div className="sv-export__card-meta">
        <span className="sv-export__card-desc">{fmt.desc}</span>
        <span className="sv-export__card-size">{fmt.size}</span>
      </div>
      <div className="sv-export__card-detail">{fmt.detail}</div>
      <div className="sv-export__card-action">
        {st === 'idle' && (
          <button className="sv-export__btn" onClick={onExport}>
            ↓ EXPORT {fmt.ext}
          </button>
        )}
        {st === 'processing' && (
          <div className="sv-export__progress">
            <span className="sv-export__spinner" />
            <span className="sv-export__progress-text">
              TRANSCODING {exportState.pct > 0 ? `${Math.round(exportState.pct)}%` : '…'}
            </span>
            {exportState.pct > 0 && (
              <div className="sv-export__progress-bar">
                <div className="sv-export__progress-fill" style={{ width: `${exportState.pct}%` }} />
              </div>
            )}
          </div>
        )}
        {st === 'ready' && (
          <a
            href={exportState.downloadUrl}
            download
            className="sv-export__btn sv-export__btn--ready"
          >
            ↓ DOWNLOAD {fmt.ext}
          </a>
        )}
        {st === 'error' && (
          <button className="sv-export__btn sv-export__btn--error" onClick={onExport} title={exportState.error}>
            ✕ FAILED — RETRY
          </button>
        )}
      </div>
    </div>
  );
}

/* ── Institutional Export Panel ─────────────────────────────────── */
function InstitutionalExport({ jobId, onReset }) {
  const [exportStates, setExportStates] = useState({});
  const pollRefs = useRef({});

  const handleExport = useCallback(async (formatId) => {
    if (!jobId) return;

    setExportStates(prev => ({
      ...prev,
      [formatId]: { status: 'processing', pct: 0, exportId: null, downloadUrl: null, error: null },
    }));

    try {
      const r = await fetch(`/api/export/${jobId}?format=${formatId}`, { method: 'POST' });
      if (!r.ok) throw new Error(await r.text());
      const { export_id } = await r.json();

      setExportStates(prev => ({ ...prev, [formatId]: { ...prev[formatId], exportId: export_id } }));

      // Start progress poll
      pollRefs.current[formatId] = setInterval(async () => {
        try {
          const sr = await fetch(`/api/export/status/${export_id}`);
          if (!sr.ok) return;
          const d = await sr.json();

          if (d.status === 'ready') {
            clearInterval(pollRefs.current[formatId]);
            setExportStates(prev => ({
              ...prev,
              [formatId]: { status: 'ready', pct: 100, exportId: export_id, downloadUrl: d.download_url, error: null },
            }));
          } else if (d.status === 'error') {
            clearInterval(pollRefs.current[formatId]);
            setExportStates(prev => ({
              ...prev,
              [formatId]: { status: 'error', pct: 0, exportId: export_id, downloadUrl: null, error: d.error },
            }));
          } else {
            setExportStates(prev => ({
              ...prev,
              [formatId]: { ...prev[formatId], pct: d.progress ?? 0 },
            }));
          }
        } catch { /* keep polling */ }
      }, 1200);

    } catch (err) {
      setExportStates(prev => ({
        ...prev,
        [formatId]: { status: 'error', pct: 0, exportId: null, downloadUrl: null, error: err.message },
      }));
    }
  }, [jobId]);

  return (
    <div className="sv-export">
      <div className="sv-export__header">
        <div className="sv-export__header-left">
          <span className="sv-export__title">INSTITUTIONAL EXPORT</span>
          <span className="sv-export__sub">SELECT FORMAT FOR DELIVERY</span>
        </div>
        <button className="sv-export__new-btn" onClick={onReset}>
          ◈ NEW SEQUENCE
        </button>
      </div>
      <div className="sv-export__formats">
        {EXPORT_FORMATS.map(fmt => (
          <ExportCard
            key={fmt.id}
            fmt={fmt}
            exportState={exportStates[fmt.id]}
            onExport={() => handleExport(fmt.id)}
          />
        ))}
      </div>
    </div>
  );
}

/* ── Canvas ──────────────────────────────────────────────────────── */
export default function Canvas({ state, dispatch }) {
  const dropRef = useRef(null);
  const { canvasMode, uploadedUrl, videoUrl, progress, progressMsg, currentJobId } = state;

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    dropRef.current?.classList.remove('sv-canvas--drag-over');
    const file = e.dataTransfer?.files?.[0];
    if (file && file.type.startsWith('image/')) {
      dispatch({ type: 'UPLOAD_CUSTOM', file });
    }
  }, [dispatch]);

  const handleDragOver  = (e) => { e.preventDefault(); dropRef.current?.classList.add('sv-canvas--drag-over'); };
  const handleDragLeave = ()    => { dropRef.current?.classList.remove('sv-canvas--drag-over'); };
  const handleReset     = ()    => dispatch({ type: 'RESET' });

  return (
    <div
      ref={dropRef}
      className={`sv-canvas sv-canvas--${canvasMode}`}
      onDrop={handleDrop}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
    >
      <div className="sv-canvas__scanlines" aria-hidden />

      {/* ── IDLE ──────────────────────────────────────────── */}
      {canvasMode === 'idle' && (
        <div className="sv-canvas__idle">
          <div className="sv-canvas__hex-grid" aria-hidden />
          <div className="sv-canvas__idle-content">
            <div className="sv-canvas__idle-glyph">◈</div>
            <p className="sv-canvas__idle-headline">SELECT ASSET OR DROP CAD RENDER</p>
            <p className="sv-canvas__idle-sub">PNG · JPG · WEBP · TIFF — 16:9 recommended</p>
          </div>
          <div className="sv-canvas__corner sv-canvas__corner--tl" aria-hidden />
          <div className="sv-canvas__corner sv-canvas__corner--tr" aria-hidden />
          <div className="sv-canvas__corner sv-canvas__corner--bl" aria-hidden />
          <div className="sv-canvas__corner sv-canvas__corner--br" aria-hidden />
        </div>
      )}

      {/* ── IMAGE ─────────────────────────────────────────── */}
      {canvasMode === 'image' && uploadedUrl && (
        <div className="sv-canvas__image-view">
          <img src={uploadedUrl} alt="Input frame" className="sv-canvas__preview-img" />
          <div className="sv-canvas__image-badge">INPUT FRAME</div>
        </div>
      )}

      {/* ── GENERATING ────────────────────────────────────── */}
      {canvasMode === 'generating' && (
        <div className="sv-canvas__generating">
          {uploadedUrl && (
            <img src={uploadedUrl} alt="" className="sv-canvas__preview-img sv-canvas__preview-img--dimmed" />
          )}
          <div className="sv-canvas__gen-overlay">
            <div className="sv-canvas__gen-ring" />
            <div className="sv-canvas__gen-content">
              <span className="sv-canvas__gen-pct">
                {Math.round(progress)}<span className="sv-canvas__gen-pct-unit">%</span>
              </span>
              <span className="sv-canvas__gen-msg">{progressMsg || 'Initializing…'}</span>
            </div>
            <div className="sv-canvas__progress-track">
              <div className="sv-canvas__progress-fill" style={{ width: `${progress}%` }} />
            </div>
          </div>
        </div>
      )}

      {/* ── VIDEO + EXPORT ────────────────────────────────── */}
      {canvasMode === 'video' && videoUrl && (
        <div className="sv-canvas__video-view">
          <video
            src={videoUrl}
            className="sv-canvas__video"
            controls
            autoPlay
            loop
            playsInline
          />
          <InstitutionalExport jobId={currentJobId} onReset={handleReset} />
        </div>
      )}

      {/* ── ERROR ─────────────────────────────────────────── */}
      {canvasMode === 'error' && (
        <div className="sv-canvas__error">
          <div className="sv-canvas__hex-grid" aria-hidden />
          <div className="sv-canvas__error-content">
            <span className="sv-canvas__error-icon">✕</span>
            <p className="sv-canvas__error-headline">RENDER FAILED</p>
            <p className="sv-canvas__error-msg">{progressMsg}</p>
            <button className="sv-canvas__action-btn sv-canvas__action-btn--reset" onClick={handleReset}>
              RETRY
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
