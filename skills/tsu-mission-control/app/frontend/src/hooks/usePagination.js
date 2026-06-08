/**
 * usePagination — reusable pagination hook for list views
 *
 * Handles offset-based pagination with "Load More" pattern.
 * Tracks total count, loading state, and whether more items exist.
 *
 * Usage:
 *   const { items, loading, hasMore, loadMore, reset, total } = usePagination(
 *     (offset, limit) => api.getDocuments({ offset, limit, ...filters }),
 *     { pageSize: 25 }
 *   );
 */
import { useState, useCallback, useEffect, useRef } from "react";

export default function usePagination(fetchFn, options = {}) {
  const { pageSize = 25, deps = [] } = options;

  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  const [total, setTotal] = useState(null);
  const offsetRef = useRef(0);

  const load = useCallback(async (reset = false) => {
    if (loading) return;
    setLoading(true);

    try {
      const offset = reset ? 0 : offsetRef.current;
      const data = await fetchFn(offset, pageSize);

      // Handle two response shapes:
      // 1. Array directly: [item, item, ...]
      // 2. Object with items and total: { items: [...], total: N }
      const newItems = Array.isArray(data) ? data : (data?.items || data || []);
      const newTotal = data?.total ?? null;

      if (reset) {
        setItems(newItems);
        offsetRef.current = newItems.length;
      } else {
        setItems(prev => [...prev, ...newItems]);
        offsetRef.current += newItems.length;
      }

      setHasMore(newItems.length >= pageSize);
      if (newTotal !== null) setTotal(newTotal);
    } catch (err) {
      console.error("Pagination load failed:", err);
      setHasMore(false);
    } finally {
      setLoading(false);
    }
  }, [fetchFn, pageSize, loading]);

  // Reset and reload when dependencies change
  useEffect(() => {
    offsetRef.current = 0;
    setItems([]);
    setHasMore(true);
    setTotal(null);

    // Small delay to batch rapid filter changes
    const timer = setTimeout(() => load(true), 50);
    return () => clearTimeout(timer);
  }, deps); // eslint-disable-line react-hooks/exhaustive-deps

  const loadMore = useCallback(() => {
    if (!loading && hasMore) load(false);
  }, [load, loading, hasMore]);

  const reset = useCallback(() => {
    offsetRef.current = 0;
    setItems([]);
    setHasMore(true);
    load(true);
  }, [load]);

  return { items, loading, hasMore, loadMore, reset, total };
}
