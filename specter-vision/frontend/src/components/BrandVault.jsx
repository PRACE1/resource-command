import React, { useRef } from 'react';
import './BrandVault.css';

const ANGLE_PALETTES = {
  front:  ['#0d1a2e', '#1b3d5c', '#00d5f2'],
  rear:   ['#1a0d2e', '#3d1b5c', '#b060ff'],
  side:   ['#1a1d0a', '#3d4a10', '#c8e040'],
  engine: ['#2e0d0d', '#5c1b1b', '#ff4060'],
  custom: ['#0a1a1a', '#1a3a3a', '#00f2c8'],
};

function AssetPlaceholder({ angle }) {
  const [a, b, c] = ANGLE_PALETTES[angle] ?? ANGLE_PALETTES.custom;
  return (
    <svg viewBox="0 0 120 80" className="sv-vault__placeholder-svg" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id={`g-${angle}`} x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%"   stopColor={a} />
          <stop offset="100%" stopColor={b} />
        </linearGradient>
      </defs>
      <rect width="120" height="80" fill={`url(#g-${angle})`} />
      {/* chassis silhouette */}
      <rect x="18" y="46" width="84" height="14" rx="2" fill={c} opacity="0.18" />
      <rect x="28" y="30" width="64" height="22" rx="4" fill={c} opacity="0.14" />
      <ellipse cx="36" cy="62" rx="10" ry="6" fill={c} opacity="0.22" />
      <ellipse cx="84" cy="62" rx="10" ry="6" fill={c} opacity="0.22" />
      {/* grill / detail */}
      {[0,1,2,3].map(i => (
        <rect key={i} x={22 + i*8} y={34} width="4" height="10" rx="1" fill={c} opacity="0.20" />
      ))}
      {/* accent line */}
      <line x1="20" y1="44" x2="100" y2="44" stroke={c} strokeWidth="0.8" opacity="0.35" />
      {/* corner bracket decoration */}
      <polyline points="4,4 4,14 14,14" fill="none" stroke={c} strokeWidth="1" opacity="0.4" />
      <polyline points="116,4 116,14 106,14" fill="none" stroke={c} strokeWidth="1" opacity="0.4" />
      <polyline points="4,76 4,66 14,66" fill="none" stroke={c} strokeWidth="1" opacity="0.4" />
      <polyline points="116,76 116,66 106,66" fill="none" stroke={c} strokeWidth="1" opacity="0.4" />
    </svg>
  );
}

export default function BrandVault({ state, dispatch }) {
  const fileRef = useRef(null);
  const { vaultAssets, selectedAsset } = state;

  const handleSelect = (asset) => {
    dispatch({ type: 'SELECT_ASSET', asset });
  };

  const handleUpload = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    dispatch({ type: 'UPLOAD_CUSTOM', file });
    e.target.value = '';
  };

  return (
    <aside className="sv-vault">
      <div className="sv-vault__header">
        <span className="sv-eyebrow">Brand Vault</span>
        <span className="sv-vault__asset-count">{vaultAssets.length} ASSETS</span>
      </div>
      <div className="sv-divider" />

      <div className="sv-vault__grid">
        {vaultAssets.map((asset) => {
          const isSelected = selectedAsset?.id === asset.id;
          return (
            <button
              key={asset.id}
              className={`sv-vault__card${isSelected ? ' sv-vault__card--selected' : ''}`}
              onClick={() => handleSelect(asset)}
              title={`${asset.name} — ${asset.sub}`}
            >
              <div className="sv-vault__thumb">
                {asset.thumb
                  ? <img src={asset.thumb} alt={asset.sub} className="sv-vault__thumb-img" />
                  : <AssetPlaceholder angle={asset.angle} />
                }
                {isSelected && <div className="sv-vault__selected-overlay">◈</div>}
              </div>
              <div className="sv-vault__card-label">
                <span className="sv-vault__card-name">{asset.name}</span>
                <span className="sv-vault__card-sub">{asset.sub}</span>
              </div>
            </button>
          );
        })}
      </div>

      <div className="sv-divider" />
      <div className="sv-vault__footer">
        <button className="sv-vault__upload-btn" onClick={() => fileRef.current?.click()}>
          <span className="sv-vault__upload-icon">+</span>
          UPLOAD CAD RENDER
        </button>
        <input
          ref={fileRef}
          type="file"
          accept="image/*"
          style={{ display: 'none' }}
          onChange={handleUpload}
        />
        <p className="sv-vault__hint">PNG · JPG · WEBP · TIFF</p>
      </div>
    </aside>
  );
}
