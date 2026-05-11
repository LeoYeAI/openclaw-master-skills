import type { NextApiRequest, NextApiResponse } from 'next';
import { getAllSignals, addSignal, generateId, type Signal } from '@/lib/db';

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method === 'GET') {
    // List all signals
    const page = parseInt(req.query.page as string) || 1;
    const limit = Math.min(parseInt(req.query.limit as string) || 20, 100);

    const allSignals = getAllSignals();
    const total = allSignals.length;
    const totalPages = Math.ceil(total / limit);
    const startIndex = (page - 1) * limit;
    const signals = allSignals.slice(startIndex, startIndex + limit);

    return res.status(200).json({
      signals,
      pagination: {
        page,
        limit,
        total,
        totalPages,
      },
    });
  }

  if (req.method === 'POST') {
    // Create new signal
    const { anonymousId, syncRate, content, timestamp } = req.body;

    // Validation
    if (!anonymousId || syncRate === undefined || syncRate === null || !content || !timestamp) {
      return res.status(400).json({
        success: false,
        error: 'Missing required fields',
      });
    }

    // Sync rate must be between 0 and 100 (inclusive)
    if (typeof syncRate !== 'number' || syncRate < 0 || syncRate > 100) {
      return res.status(400).json({
        success: false,
        error: 'Sync rate must be a number between 0 and 100',
      });
    }

    // Content length validation (50-500 chars)
    if (content.length < 50 || content.length > 500) {
      return res.status(400).json({
        success: false,
        error: 'Content must be between 50 and 500 characters',
      });
    }

    // Sync rate validation
    if (syncRate < 0 || syncRate > 100) {
      return res.status(400).json({
        success: false,
        error: 'Sync rate must be between 0 and 100',
      });
    }

    // Generate signal
    const id = generateId();
    const expiresAt = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString();

    const signal: Signal = {
      id,
      anonymousId,
      syncRate,
      content,
      timestamp,
      expiresAt,
    };

    addSignal(signal);

    return res.status(201).json({
      success: true,
      id,
      expiresAt,
    });
  }

  return res.status(405).json({ error: 'Method not allowed' });
}
