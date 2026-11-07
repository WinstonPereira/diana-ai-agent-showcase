// Illustrative snippet — reactive energy orb (WebGL / GLSL)
// This is a simplified, generic version of the pattern used in DIANA's
// desktop frontend. The orb is driven by three inputs coming from the
// backend: emotion (enum), activity (idle | tool_running | speaking)
// and an audio envelope sampled from the TTS playback.

uniform float uTime;
uniform vec3  uColorA;      // emotion base color
uniform vec3  uColorB;      // emotion accent color
uniform float uPulse;       // 0..1 — audio envelope from TTS
uniform float uTurbulence;  // 0..1 — excitement / activity level
uniform float uGlow;        // 0..1 — overall glow strength

varying vec2 vUv;

// cheap 2D noise for surface distortion
float hash(vec2 p) {
    return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}

float noise(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    vec2 u = f * f * (3.0 - 2.0 * f);
    return mix(mix(hash(i), hash(i + vec2(1.0, 0.0)), u.x),
               mix(hash(i + vec2(0.0, 1.0)), hash(i + vec2(1.0, 1.0)), u.x), u.y);
}

void main() {
    vec2 p = vUv * 2.0 - 1.0;
    float r = length(p);
    float angle = atan(p.y, p.x);

    // radial falloff = sphere silhouette
    float sphere = smoothstep(1.0, 0.55, r);

    // animated surface: turbulence scales with excitement
    float n = noise(p * 4.0 + vec2(uTime * 0.4, -uTime * 0.3));
    float surface = sin(angle * 6.0 + uTime * (1.0 + uTurbulence * 2.0)) * 0.5 + 0.5;
    surface = mix(surface, n, uTurbulence);

    // audio pulse contracts and expands the core
    float core = sphere * (1.0 + uPulse * 0.35);

    vec3 color = mix(uColorA, uColorB, surface);
    color += uGlow * pow(sphere, 3.0);

    float alpha = core * (0.65 + 0.35 * surface);
    gl_FragColor = vec4(color, clamp(alpha, 0.0, 1.0));
}
