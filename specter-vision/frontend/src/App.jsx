import React, { useReducer, useCallback, useEffect } from 'react';
import StatusBar from './components/StatusBar.jsx';
import BrandVault from './components/BrandVault.jsx';
import Canvas from './components/Canvas.jsx';
import PromptTerminal from './components/PromptTerminal.jsx';
import GenerationControls from './components/GenerationControls.jsx';
import { CINEMATIC_PRESETS } from './components/DirectorsMenu.jsx';
import './App.css';

/* ── Cinematic preset suffix map (keyed by id) ───────────────────── */
const PRESET_SUFFIX_MAP = Object.fromEntries(
  CINEMATIC_PRESETS.map(p => [p.id, p.suffix])
);

/* ── Seed assets for the Brand Vault ─────────────────────────────── */
const VAULT_SEED = [
  { id: 'oracle-front',  name: 'ORACLE 250V8',  sub: 'Front Quarter',  angle: 'front',  file: null, thumb: null },
  { id: 'oracle-rear',   name: 'ORACLE 250V8',  sub: 'Rear Quarter',   angle: 'rear',   file: null, thumb: null },
  { id: 'oracle-side',   name: 'ORACLE 250V8',  sub: 'Side Profile',   angle: 'side',   file: null, thumb: null },
  { id: 'oracle-engine', name: 'ORACLE 250V8',  sub: 'Engine Bay',     angle: 'engine', file: null, thumb: null },
];

/* ── State ────────────────────────────────────────────────────────── */
const initialState = {
  vaultAssets:    VAULT_SEED,
  selectedAsset:  null,
  uploadedFile:   null,
  uploadedUrl:    null,

  canvasMode:     'idle',   // idle | image | generating | video | error
  videoUrl:       null,
  progress:       0,
  progressMsg:    '',

  prompt:         '',
  negativePrompt: 'blurry, distorted, low quality, amateur, shaky, noise, watermark',
  motionBucket:   110,
  numFrames:      81,
  fps:            24,
  guidanceScale:  6.0,
  steps:          25,
  modelMode:      'i2v',    // i2v | t2v

  // ── Elite: Director's Menu ──────────────────────────────────────
  activePresets:            [],     // array of CINEMATIC_PRESETS ids
  geometryLock:             false,
  geometryLockDepthStrength: 0.80,
  geometryLockCannyStrength: 0.60,
  temporalMaster:           true,   // on by default — always deliver 24fps cinematic

  currentJobId:   null,
  jobStatus:      null,     // null | queued | running | complete | failed

  comfyStatus:    'checking',
  gpuVram:        null,
  queueDepth:     0,
};

function reducer(state, action) {
  switch (action.type) {

    case 'SELECT_ASSET':
      return {
        ...state,
        selectedAsset: action.asset,
        canvasMode: action.asset?.thumb || action.asset?.file ? 'image' : state.canvasMode,
        uploadedUrl:  action.asset?.thumb  ?? action.asset?.url ?? state.uploadedUrl,
        uploadedFile: action.asset?.file   ?? state.uploadedFile,
      };

    case 'UPLOAD_CUSTOM': {
      const url = URL.createObjectURL(action.file);
      const newAsset = {
        id: `custom-${Date.now()}`,
        name: 'CUSTOM RENDER',
        sub: action.file.name.replace(/\.[^.]+$/, '').toUpperCase(),
        angle: 'custom',
        file: action.file,
        thumb: url,
      };
      return {
        ...state,
        vaultAssets:   [...state.vaultAssets, newAsset],
        selectedAsset: newAsset,
        uploadedFile:  action.file,
        uploadedUrl:   url,
        canvasMode:    'image',
      };
    }

    case 'SET_PROMPT':         return { ...state, prompt: action.v };
    case 'SET_NEG_PROMPT':     return { ...state, negativePrompt: action.v };
    case 'SET_MOTION':         return { ...state, motionBucket: action.v };
    case 'SET_PARAM':          return { ...state, [action.k]: action.v };

    case 'TOGGLE_PRESET':
      return {
        ...state,
        activePresets: state.activePresets.includes(action.id)
          ? state.activePresets.filter(id => id !== action.id)
          : [...state.activePresets, action.id],
      };

    case 'JOB_START':
      return { ...state, currentJobId: action.jobId, jobStatus: 'queued', canvasMode: 'generating', progress: 0, progressMsg: 'Submitting to render queue…', videoUrl: null };

    case 'JOB_PROGRESS':
      return { ...state, progress: action.progress, progressMsg: action.msg, jobStatus: 'running' };

    case 'JOB_COMPLETE':
      return { ...state, jobStatus: 'complete', canvasMode: 'video', videoUrl: action.videoUrl, progress: 100, progressMsg: 'Sequence rendered.' };

    case 'JOB_FAILED':
      return { ...state, jobStatus: 'failed', canvasMode: 'error', progressMsg: action.error };

    case 'RESET':
      return {
        ...state,
        jobStatus:    null,
        currentJobId: null,
        progress:     0,
        progressMsg:  '',
        videoUrl:     null,
        canvasMode:   state.uploadedUrl ? 'image' : 'idle',
      };

    case 'COMFY_STATUS':
      return { ...state, comfyStatus: action.status, gpuVram: action.vram ?? null, queueDepth: action.queue ?? 0 };

    default:
      return state;
  }
}

/* ── App ──────────────────────────────────────────────────────────── */
export default function App() {
  const [state, dispatch] = useReducer(reducer, initialState);

  /* ComfyUI health poll */
  useEffect(() => {
    const check = async () => {
      try {
        const r = await fetch('/api/comfyui/status', { signal: AbortSignal.timeout(4000) });
        const d = await r.json();
        dispatch({ type: 'COMFY_STATUS', status: 'online', vram: d.vram, queue: d.queue });
      } catch {
        dispatch({ type: 'COMFY_STATUS', status: 'offline', vram: null, queue: 0 });
      }
    };
    check();
    const id = setInterval(check, 6000);
    return () => clearInterval(id);
  }, []);

  /* Job poll */
  useEffect(() => {
    if (!state.currentJobId || state.jobStatus === 'complete' || state.jobStatus === 'failed') return;
    const poll = async () => {
      try {
        const r = await fetch(`/api/job/${state.currentJobId}`);
        const d = await r.json();
        if (d.status === 'complete') {
          dispatch({ type: 'JOB_COMPLETE', videoUrl: d.video_url });
        } else if (d.status === 'failed') {
          dispatch({ type: 'JOB_FAILED', error: d.error || 'Render failed — check backend logs.' });
        } else {
          dispatch({ type: 'JOB_PROGRESS', progress: d.progress ?? 0, msg: d.message ?? 'Rendering…' });
        }
      } catch { /* keep polling */ }
    };
    const id = setInterval(poll, 1800);
    return () => clearInterval(id);
  }, [state.currentJobId, state.jobStatus]);

  const handleGenerate = useCallback(async () => {
    const hasImage  = !!(state.selectedAsset?.file || state.uploadedFile);
    const hasPrompt = state.prompt.trim().length > 0;

    if (state.modelMode === 'i2v' && !hasImage) return;
    if (!hasPrompt) return;

    // Compose final prompt: user text + active cinematic preset suffixes
    const presetSuffixes = state.activePresets
      .map(id => PRESET_SUFFIX_MAP[id])
      .filter(Boolean);
    const composedPrompt = [state.prompt.trim(), ...presetSuffixes].join(', ');

    try {
      const fd = new FormData();
      fd.append('prompt',           composedPrompt);
      fd.append('negative_prompt',  state.negativePrompt);
      fd.append('motion_bucket_id', String(state.motionBucket));
      fd.append('num_frames',       String(state.numFrames));
      fd.append('fps',              String(state.fps));
      fd.append('guidance_scale',   String(state.guidanceScale));
      fd.append('steps',            String(state.steps));
      fd.append('model_mode',       state.modelMode);
      // ── Elite params ──────────────────────────────────────────────
      fd.append('geometry_lock',               String(state.geometryLock));
      fd.append('geometry_lock_depth_strength', String(state.geometryLockDepthStrength));
      fd.append('geometry_lock_canny_strength', String(state.geometryLockCannyStrength));
      fd.append('temporal_master',             String(state.temporalMaster));

      const imageFile = state.selectedAsset?.file ?? state.uploadedFile;
      if (imageFile) fd.append('image', imageFile);

      const r = await fetch('/api/generate', { method: 'POST', body: fd });
      if (!r.ok) throw new Error(await r.text());
      const d = await r.json();
      dispatch({ type: 'JOB_START', jobId: d.job_id });
    } catch (err) {
      dispatch({ type: 'JOB_FAILED', error: err.message });
    }
  }, [state]);

  const canGenerate = state.canvasMode !== 'generating' &&
    state.prompt.trim().length > 0 &&
    (state.modelMode === 't2v' || !!(state.selectedAsset?.file || state.uploadedFile));

  return (
    <div className="sv-root">
      <StatusBar state={state} />
      <div className="sv-workspace">
        <BrandVault state={state} dispatch={dispatch} />
        <div className="sv-center">
          <Canvas state={state} dispatch={dispatch} />
          <PromptTerminal state={state} dispatch={dispatch} />
        </div>
        <GenerationControls
          state={state}
          dispatch={dispatch}
          onGenerate={handleGenerate}
          canGenerate={canGenerate}
        />
      </div>
    </div>
  );
}
