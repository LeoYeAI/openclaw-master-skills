/**
 * Options for configuring the AsyncQueue
 */
export interface AsyncQueueOptions {
  /**
   * Number of tasks to batch together before processing
   * @default 50
   */
  batchSize?: number;

  /**
   * Interval in milliseconds to flush pending tasks
   * @default 100
   */
  flushInterval?: number;

  /**
   * Maximum number of tasks to keep in queue
   * When exceeded, oldest tasks are dropped
   * @default 10000
   */
  maxQueueSize?: number;

  /**
   * Callback function to process a batch of tasks
   * @param tasks - Array of tasks to process
   */
  onBatch: (tasks: any[]) => Promise<void>;
}

/**
 * AsyncQueue provides non-blocking batch processing of tasks
 *
 * Features:
 * - Automatic batching when batch size is reached
 * - Periodic flushing based on time interval
 * - Queue overflow protection (drops oldest tasks)
 * - Error handling for batch processing failures
 * - Manual flush support
 *
 * @example
 * ```typescript
 * const queue = new AsyncQueue({
 *   batchSize: 50,
 *   flushInterval: 100,
 *   onBatch: async (tasks) => {
 *     await database.insertMany(tasks);
 *   }
 * });
 *
 * queue.enqueue({ type: 'event', data: {...} });
 * await queue.flush(); // Manual flush
 * queue.stop(); // Cleanup
 * ```
 */
export class AsyncQueue {
  private queue: any[] = [];
  private readonly batchSize: number;
  private readonly flushInterval: number;
  private readonly maxQueueSize: number;
  private readonly onBatch: (tasks: any[]) => Promise<void>;
  private timer: NodeJS.Timeout | null = null;
  private isProcessing = false;

  /**
   * Creates a new AsyncQueue instance
   * @param options - Configuration options
   * @throws Error if options are invalid
   */
  constructor(options: AsyncQueueOptions) {
    // Validate required options
    if (!options.onBatch) {
      throw new Error('onBatch callback is required');
    }

    if (typeof options.onBatch !== 'function') {
      throw new Error('onBatch must be a function');
    }

    // Set defaults
    this.batchSize = options.batchSize ?? 50;
    this.flushInterval = options.flushInterval ?? 100;
    this.maxQueueSize = options.maxQueueSize ?? 10000;
    this.onBatch = options.onBatch;

    // Validate options
    if (this.batchSize <= 0) {
      throw new Error('batchSize must be greater than 0');
    }

    if (this.flushInterval <= 0) {
      throw new Error('flushInterval must be greater than 0');
    }

    if (this.maxQueueSize <= 0) {
      throw new Error('maxQueueSize must be greater than 0');
    }

    // Start the periodic flush timer
    this.startTimer();
  }

  /**
   * Add a task to the queue
   * Automatically processes batch when batch size is reached
   * @param task - Task to enqueue
   */
  enqueue(task: any): void {
    // Add task to queue
    this.queue.push(task);

    // Handle queue overflow - drop oldest tasks
    while (this.queue.length > this.maxQueueSize) {
      this.queue.shift();
    }

    // Process batch if batch size is reached
    if (this.queue.length >= this.batchSize) {
      this.processBatch();
    }
  }

  /**
   * Returns the current number of tasks in the queue
   * @returns Queue size
   */
  size(): number {
    return this.queue.length;
  }

  /**
   * Process all remaining tasks in the queue
   * Waits for processing to complete
   * @returns Promise that resolves when all tasks are processed
   */
  async flush(): Promise<void> {
    if (this.queue.length === 0) {
      return;
    }

    const batch = this.queue.splice(0, this.queue.length);
    await this.onBatch(batch);
  }

  /**
   * Stop the periodic flush timer and cleanup
   * Does not flush remaining tasks - call flush() first if needed
   */
  stop(): void {
    if (this.timer) {
      clearInterval(this.timer);
      this.timer = null;
    }
  }

  /**
   * Start the periodic flush timer
   * @private
   */
  private startTimer(): void {
    this.timer = setInterval(() => {
      if (this.queue.length > 0 && !this.isProcessing) {
        this.processBatch();
      }
    }, this.flushInterval) as any; // Cast to any for compatibility with both Node.js and fake timers
  }

  /**
   * Process a batch of tasks asynchronously
   * Handles errors without throwing
   * @private
   */
  private processBatch(): void {
    // Prevent concurrent batch processing
    if (this.isProcessing || this.queue.length === 0) {
      return;
    }

    this.isProcessing = true;

    // Extract batch
    const batchCount = Math.min(this.batchSize, this.queue.length);
    const batch = this.queue.splice(0, batchCount);

    // Process asynchronously
    this.onBatch(batch)
      .catch((error) => {
        console.error('Error processing batch:', error);
      })
      .finally(() => {
        this.isProcessing = false;
      });
  }
}
