import assert from 'node:assert/strict';

/** Sequence/lifeline diagrams already show ordering; reserve playback for topology views. */
export function assertFlowTopology(source, where = 'D2 flow') {
  assert.doesNotMatch(source, /^\s*shape:\s*sequence_diagram\b/m,
    `${where}: sequence/lifeline diagrams must not use mode=flow; keep the normal D2 viewer`);
}
