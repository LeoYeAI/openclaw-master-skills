import type { NextApiRequest, NextApiResponse } from 'next';
import { getRandomSignal } from '@/lib/db';

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const signal = getRandomSignal();

  if (!signal) {
    return res.status(404).json({
      success: false,
      error: 'No signals available',
    });
  }

  return res.status(200).json(signal);
}
