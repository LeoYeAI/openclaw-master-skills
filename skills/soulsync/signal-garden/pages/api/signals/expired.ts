import type { NextApiRequest, NextApiResponse } from 'next';
import { deleteExpiredSignals } from '@/lib/db';

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'DELETE') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const deleted = deleteExpiredSignals();

  return res.status(200).json({
    success: true,
    deleted,
  });
}
