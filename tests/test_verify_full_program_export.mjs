#!/usr/bin/env node
// CPU-only integration tests. GLBs are generated in an owned temporary folder
// and removed afterward; no asset payloads or external downloads are required.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';

const usage = 'Usage: node tests/test_verify_full_program_export.mjs --repo PATH\n';
if (process.argv.includes('--help')) { process.stdout.write(usage); process.exit(0); }
assert.equal(process.argv.length, 4, usage);
assert.equal(process.argv[2], '--repo', usage);
const repo = path.resolve(process.argv[3]);
const verifier = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../scripts/verify_full_program_export.mjs');
const temporary = fs.mkdtempSync(path.join(os.tmpdir(), 'full-program-export-test-'));
const results = [];

function floats(values) {
  const buffer = Buffer.alloc(values.length * 4);
  values.forEach((value, index) => buffer.writeFloatLE(value, index * 4));
  return buffer;
}

function fixture({ capturedTranslation = 0, movingRotation = false, staticTranslation = 2, curveHeight = 1 } = {}) {
  // One triangle, two mesh instances and a translation clip provide enough
  // structure to distinguish a captured animation pose from a static change.
  const positions = floats([0, 0, 0, 1, 0, 0, 0, 1, 0]);
  const indices = Buffer.alloc(8); [0, 1, 2].forEach((value, index) => indices.writeUInt16LE(value, index * 2));
  const times = floats([0, 1, 2]);
  const translations = floats([0, 0, 0, 0, 0, curveHeight, 0, 0, 0]);
  const binary = Buffer.concat([positions, indices, times, translations]);
  const moving = { name: 'Moving', mesh: 0, translation: [0, 0, capturedTranslation] };
  if (movingRotation) moving.rotation = [0, Math.sin(0.1), 0, Math.cos(0.1)];
  const document = {
    asset: { version: '2.0', generator: 'CPU verification fixture' },
    scene: 0, scenes: [{ nodes: [0] }],
    nodes: [
      { name: 'Root', children: [1, 2] }, moving,
      { name: 'Static', mesh: 0, translation: [staticTranslation, 0, 0] }
    ],
    meshes: [{ primitives: [{ attributes: { POSITION: 0 }, indices: 1, material: 0 }] }],
    materials: [{ pbrMetallicRoughness: { baseColorFactor: [0.5, 0.7, 0.8, 1], metallicFactor: 0, roughnessFactor: 1 } }],
    buffers: [{ byteLength: binary.length }],
    bufferViews: [
      { buffer: 0, byteOffset: 0, byteLength: 36, target: 34962 },
      { buffer: 0, byteOffset: 36, byteLength: 6, target: 34963 },
      { buffer: 0, byteOffset: 44, byteLength: 12 },
      { buffer: 0, byteOffset: 56, byteLength: 36 }
    ],
    accessors: [
      { bufferView: 0, componentType: 5126, count: 3, type: 'VEC3', min: [0, 0, 0], max: [1, 1, 0] },
      { bufferView: 1, componentType: 5123, count: 3, type: 'SCALAR' },
      { bufferView: 2, componentType: 5126, count: 3, type: 'SCALAR', min: [0], max: [2] },
      { bufferView: 3, componentType: 5126, count: 3, type: 'VEC3' }
    ],
    animations: [{ name: 'Slide', samplers: [{ input: 2, output: 3, interpolation: 'LINEAR' }], channels: [{ sampler: 0, target: { node: 1, path: 'translation' } }] }]
  };
  const json = Buffer.from(JSON.stringify(document));
  const paddedJson = Buffer.concat([json, Buffer.alloc((4 - json.length % 4) % 4, 0x20)]);
  const header = Buffer.alloc(12), jsonHeader = Buffer.alloc(8), binaryHeader = Buffer.alloc(8);
  header.writeUInt32LE(0x46546c67, 0); header.writeUInt32LE(2, 4); header.writeUInt32LE(28 + paddedJson.length + binary.length, 8);
  jsonHeader.writeUInt32LE(paddedJson.length, 0); jsonHeader.writeUInt32LE(0x4e4f534a, 4);
  binaryHeader.writeUInt32LE(binary.length, 0); binaryHeader.writeUInt32LE(0x004e4942, 4);
  return Buffer.concat([header, jsonHeader, paddedJson, binaryHeader, binary]);
}

function execute(name, actual, expectedExit, failureKind = null, expectPoseAllowance = false) {
  const actualName = actual === null ? 'missing.glb' : `${name}.glb`;
  if (actual !== null) fs.writeFileSync(path.join(temporary, actualName), actual);
  const outputName = `${name}.json`;
  const processResult = spawnSync(process.execPath, [verifier, '--repo', repo, '--workspace', temporary,
    '--reference', 'reference.glb', '--actual', actualName, '--out', outputName], { encoding: 'utf8' });
  assert.equal(processResult.status, expectedExit, `${name}: ${processResult.stdout}\n${processResult.stderr}`);
  const report = JSON.parse(fs.readFileSync(path.join(temporary, outputName), 'utf8'));
  assert.deepEqual(report.tolerance, { absolute: 1e-5, relative: 1e-6 });
  assert.equal(report.status, expectedExit === 0 ? 'PASS' : 'FAIL');
  if (failureKind) assert(report.failures.some(failure => failure.kind === failureKind), `${name}: expected ${failureKind}`);
  const allowances = report.checks.captured_pose_differences?.filter(value => value.accepted) || [];
  assert.equal(allowances.length > 0, expectPoseAllowance, `${name}: unexpected captured-pose allowance`);
  if (expectPoseAllowance) {
    assert.deepEqual(allowances[0].differences.map(value => value.property), ['translation']);
    assert.equal(allowances[0].proof.all_clip_bindings_and_curves_match, true);
    assert.equal(allowances[0].proof.canonical_world_samples_match, true);
    assert.equal(allowances[0].proof.reference_and_actual_validator_errors_zero, true);
  }
  results.push({ name, passed: true, expected_exit: expectedExit });
}

try {
  const help = spawnSync(process.execPath, [verifier, '--help', '--repo', path.join(temporary, 'nonexistent-repository')], { encoding: 'utf8', cwd: temporary });
  assert.equal(help.status, 0, help.stderr);
  assert.match(help.stdout, /--repo PATH/);
  assert.deepEqual(fs.readdirSync(temporary), [], 'Help must not create any files or load missing dependencies');
  results.push({ name: 'help-without-dependencies-or-file-writes', passed: true });

  const noRepo = spawnSync(process.execPath, [verifier, '--reference', 'reference.glb', '--actual', 'actual.glb', '--out', 'missing-repo-report.json'], { encoding: 'utf8', cwd: temporary });
  assert.notEqual(noRepo.status, 0);
  assert.match(noRepo.stderr, /--repo.*required/);
  assert.deepEqual(fs.readdirSync(temporary), [], 'Missing required repo must not create output');
  results.push({ name: 'explicit-repository-required', passed: true });

  fs.writeFileSync(path.join(temporary, 'reference.glb'), fixture());
  execute('identity', fixture(), 0);
  execute('animated-translation-pose', fixture({ capturedTranslation: 0.6 }), 0, null, true);
  execute('nonanimated-rotation', fixture({ movingRotation: true }), 1, 'local_transform_unanimated_component');
  execute('static-translation', fixture({ staticTranslation: 2.4 }), 1, 'local_transform_unanimated_component');
  execute('changed-curve', fixture({ capturedTranslation: 0.6, curveHeight: 1.3 }), 1, 'clip_channels_or_curves');
  execute('missing-actual', null, 1, 'exception_or_unsupported_input');
  console.log(JSON.stringify({ status: 'PASS', tests: results.length, results, scope: 'Generated temporary fixtures; CPU only; no browser, GPU, models or external asset files.' }, null, 2));
} finally {
  fs.rmSync(temporary, { recursive: true, force: true });
}
