import test from 'node:test';
import assert from 'node:assert/strict';
import { assertFlowTopology } from '../scripts/d2-flow-policy.mjs';

const flow = '# @flow\n# scenarios:\n# @endflow\n';

test('sequence and lifeline diagrams cannot opt into flow playback', () => {
  for (const source of [
    'shape: sequence_diagram\na -> b: Request',
    flow + 'shape: sequence_diagram # ordered messages\na -> b',
    'group: {\n  shape: sequence_diagram\n  a -> b\n}',
  ]) {
    assert.throws(() => assertFlowTopology(source, 'lesson.mdx:12'),
      /lesson\.mdx:12: sequence\/lifeline diagrams must not use mode=flow/);
  }
});

test('fixed topology remains eligible without mistaking labels or comments for shapes', () => {
  for (const source of [
    flow + 'direction: right\nclient -> api\napi -> cache',
    '# shape: sequence_diagram\nclient -> api',
    'note: "shape: sequence_diagram"\nclient -> api',
  ]) assert.doesNotThrow(() => assertFlowTopology(source));
});
