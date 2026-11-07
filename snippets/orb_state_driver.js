// Illustrative snippet — emotion/activity -> orb uniforms
// Shows the mapping layer between backend state and the renderer.
// Generic patterns only; no proprietary logic.

const ORB_PRESETS = {
  happy:     { colorA: [0.35, 0.85, 1.00], colorB: [0.65, 0.95, 1.00], turbulence: 0.35, glow: 0.85 },
  excited:   { colorA: [1.00, 0.55, 0.20], colorB: [1.00, 0.85, 0.35], turbulence: 0.90, glow: 1.00 },
  surprised: { colorA: [0.80, 0.70, 1.00], colorB: [1.00, 1.00, 1.00], turbulence: 0.75, glow: 1.00 },
  thinking:  { colorA: [0.30, 0.55, 0.90], colorB: [0.45, 0.75, 1.00], turbulence: 0.20, glow: 0.55 },
  sad:       { colorA: [0.25, 0.35, 0.60], colorB: [0.40, 0.50, 0.75], turbulence: 0.10, glow: 0.40 },
  angry:     { colorA: [0.95, 0.20, 0.25], colorB: [1.00, 0.45, 0.30], turbulence: 0.85, glow: 1.00 },
  neutral:   { colorA: [0.30, 0.75, 0.95], colorB: [0.55, 0.90, 1.00], turbulence: 0.25, glow: 0.65 },
};

const ACTIVITY_GAIN = {
  idle:         0.15,
  listening:    0.45,
  tool_running: 0.80,
  speaking:     0.60,
};

export function applyState(orb, { emotion, activity, audioLevel }) {
  const preset = ORB_PRESETS[emotion] ?? ORB_PRESETS.neutral;
  const gain = ACTIVITY_GAIN[activity] ?? ACTIVITY_GAIN.idle;

  // smooth transitions: never snap, always lerp toward target
  orb.target.colorA = preset.colorA;
  orb.target.colorB = preset.colorB;
  orb.target.turbulence = preset.turbulence * (0.4 + gain);
  orb.target.glow = preset.glow * (0.5 + gain);
  orb.target.pulse = audioLevel * gain;
}
