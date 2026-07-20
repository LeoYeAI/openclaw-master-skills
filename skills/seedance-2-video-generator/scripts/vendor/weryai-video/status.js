import { executeStatus } from '../weryai-core/status.js';

export function execute(input, ctx) {
  return executeStatus(input, ctx, {
    outputKey: 'videos',
    outputLabel: 'video',
    allowBatch: true,
  });
}

export default execute;
