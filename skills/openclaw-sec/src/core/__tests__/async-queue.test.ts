import { describe, it, expect, beforeEach, afterEach, jest } from '@jest/globals';
import { AsyncQueue, AsyncQueueOptions } from '../async-queue';

describe('AsyncQueue', () => {
  let queue: AsyncQueue;

  afterEach(() => {
    if (queue) {
      queue.stop();
    }
  });

  describe('Basic functionality', () => {
    it('should create a queue with default options', () => {
      queue = new AsyncQueue({
        onBatch: jest.fn() as any,
      });

      expect(queue.size()).toBe(0);
    });

    it('should create a queue with custom options', () => {
      const options: AsyncQueueOptions = {
        batchSize: 10,
        flushInterval: 50,
        maxQueueSize: 100,
        onBatch: jest.fn() as any,
      };

      queue = new AsyncQueue(options);
      expect(queue.size()).toBe(0);
    });

    it('should throw error if onBatch is not provided', () => {
      expect(() => {
        // @ts-expect-error - Testing missing required option
        queue = new AsyncQueue({});
      }).toThrow('onBatch callback is required');
    });

    it('should throw error if onBatch is not a function', () => {
      expect(() => {
        // @ts-expect-error - Testing invalid onBatch type
        queue = new AsyncQueue({ onBatch: 'not-a-function' });
      }).toThrow('onBatch must be a function');
    });

    it('should validate batchSize is positive', () => {
      expect(() => {
        queue = new AsyncQueue({
          batchSize: 0,
          onBatch: jest.fn() as any,
        });
      }).toThrow('batchSize must be greater than 0');
    });

    it('should validate flushInterval is positive', () => {
      expect(() => {
        queue = new AsyncQueue({
          flushInterval: -1,
          onBatch: jest.fn() as any,
        });
      }).toThrow('flushInterval must be greater than 0');
    });

    it('should validate maxQueueSize is positive', () => {
      expect(() => {
        queue = new AsyncQueue({
          maxQueueSize: 0,
          onBatch: jest.fn() as any,
        });
      }).toThrow('maxQueueSize must be greater than 0');
    });
  });

  describe('Enqueue and size', () => {
    it('should enqueue tasks and track size', () => {
      const onBatch = jest.fn() as any;
      queue = new AsyncQueue({
        batchSize: 10,
        onBatch,
      });

      queue.enqueue({ id: 1 });
      expect(queue.size()).toBe(1);

      queue.enqueue({ id: 2 });
      queue.enqueue({ id: 3 });
      expect(queue.size()).toBe(3);
    });

    it('should return queue size after processing', async () => {
      const onBatch = (jest.fn() as any).mockResolvedValue(undefined);
      queue = new AsyncQueue({
        batchSize: 2,
        onBatch,
      });

      queue.enqueue({ id: 1 });
      queue.enqueue({ id: 2 });

      // Wait for batch to process
      await new Promise((resolve) => setTimeout(resolve, 10));

      expect(queue.size()).toBe(0);
    });
  });

  describe('Batch processing', () => {
    it('should process batch when batch size is reached', async () => {
      const onBatch = (jest.fn() as any).mockResolvedValue(undefined);
      queue = new AsyncQueue({
        batchSize: 3,
        onBatch,
      });

      queue.enqueue({ id: 1 });
      queue.enqueue({ id: 2 });
      expect(onBatch).not.toHaveBeenCalled();

      queue.enqueue({ id: 3 });

      // Wait for async processing
      await new Promise((resolve) => setTimeout(resolve, 10));

      expect(onBatch).toHaveBeenCalledTimes(1);
      expect(onBatch).toHaveBeenCalledWith([{ id: 1 }, { id: 2 }, { id: 3 }]);
      expect(queue.size()).toBe(0);
    });

    it('should process multiple batches', async () => {
      const onBatch = (jest.fn() as any).mockResolvedValue(undefined);
      queue = new AsyncQueue({
        batchSize: 2,
        onBatch,
      });

      // First batch
      queue.enqueue({ id: 1 });
      queue.enqueue({ id: 2 });

      await new Promise((resolve) => setTimeout(resolve, 10));

      // Second batch
      queue.enqueue({ id: 3 });
      queue.enqueue({ id: 4 });

      await new Promise((resolve) => setTimeout(resolve, 10));

      expect(onBatch).toHaveBeenCalledTimes(2);
      expect(onBatch).toHaveBeenNthCalledWith(1, [{ id: 1 }, { id: 2 }]);
      expect(onBatch).toHaveBeenNthCalledWith(2, [{ id: 3 }, { id: 4 }]);
    });

    it('should process tasks asynchronously without blocking', async () => {
      const processedTasks: number[] = [];
      const onBatch = (jest.fn() as any).mockImplementation(async (tasks: any[]) => {
        await new Promise((resolve) => setTimeout(resolve, 20));
        tasks.forEach((task) => processedTasks.push(task.id));
      });

      queue = new AsyncQueue({
        batchSize: 2,
        onBatch,
      });

      queue.enqueue({ id: 1 });
      queue.enqueue({ id: 2 });

      // Should not block
      expect(processedTasks).toEqual([]);

      // Wait for processing
      await new Promise((resolve) => setTimeout(resolve, 50));

      expect(processedTasks).toEqual([1, 2]);
    });
  });

  describe('Flush interval', () => {
    it('should process tasks after flush interval', async () => {
      jest.useFakeTimers();

      const onBatch = (jest.fn() as any).mockResolvedValue(undefined);
      queue = new AsyncQueue({
        batchSize: 10,
        flushInterval: 100,
        onBatch,
      });

      queue.enqueue({ id: 1 });
      queue.enqueue({ id: 2 });

      expect(onBatch).not.toHaveBeenCalled();

      // Advance timers to trigger one interval
      jest.advanceTimersByTime(100);
      await Promise.resolve(); // Let microtasks run

      expect(onBatch).toHaveBeenCalledWith([{ id: 1 }, { id: 2 }]);

      queue.stop();
      jest.useRealTimers();
    });

    it('should continue processing at intervals', async () => {
      // Use real timers for this test since we need actual async behavior
      const onBatch = (jest.fn() as any).mockResolvedValue(undefined);
      queue = new AsyncQueue({
        batchSize: 10,
        flushInterval: 50,
        onBatch,
      });

      queue.enqueue({ id: 1 });
      await new Promise((resolve) => setTimeout(resolve, 60));

      expect(onBatch).toHaveBeenCalledTimes(1);
      expect(onBatch).toHaveBeenNthCalledWith(1, [{ id: 1 }]);

      queue.enqueue({ id: 2 });
      await new Promise((resolve) => setTimeout(resolve, 60));

      expect(onBatch).toHaveBeenCalledTimes(2);
      expect(onBatch).toHaveBeenNthCalledWith(2, [{ id: 2 }]);
    });

    it('should not process empty queue on interval', async () => {
      jest.useFakeTimers();

      const onBatch = (jest.fn() as any).mockResolvedValue(undefined);
      queue = new AsyncQueue({
        batchSize: 10,
        flushInterval: 100,
        onBatch,
      });

      jest.advanceTimersByTime(100);
      await Promise.resolve(); // Let microtasks run

      expect(onBatch).not.toHaveBeenCalled();

      queue.stop();
      jest.useRealTimers();
    });
  });

  describe('Manual flush', () => {
    it('should flush all remaining tasks', async () => {
      const onBatch = (jest.fn() as any).mockResolvedValue(undefined);
      queue = new AsyncQueue({
        batchSize: 10,
        onBatch,
      });

      queue.enqueue({ id: 1 });
      queue.enqueue({ id: 2 });
      queue.enqueue({ id: 3 });

      await queue.flush();

      expect(onBatch).toHaveBeenCalledWith([{ id: 1 }, { id: 2 }, { id: 3 }]);
      expect(queue.size()).toBe(0);
    });

    it('should not process if queue is empty', async () => {
      const onBatch = (jest.fn() as any).mockResolvedValue(undefined);
      queue = new AsyncQueue({
        batchSize: 10,
        onBatch,
      });

      await queue.flush();

      expect(onBatch).not.toHaveBeenCalled();
    });

    it('should wait for flush to complete', async () => {
      const processedTasks: number[] = [];
      const onBatch = (jest.fn() as any).mockImplementation(async (tasks: any[]) => {
        await new Promise((resolve) => setTimeout(resolve, 20));
        tasks.forEach((task) => processedTasks.push(task.id));
      });

      queue = new AsyncQueue({
        batchSize: 10,
        onBatch,
      });

      queue.enqueue({ id: 1 });
      queue.enqueue({ id: 2 });

      await queue.flush();

      expect(processedTasks).toEqual([1, 2]);
    });
  });

  describe('Queue overflow', () => {
    it('should drop oldest tasks when max queue size is exceeded', async () => {
      const onBatch = (jest.fn() as any).mockResolvedValue(undefined);
      queue = new AsyncQueue({
        batchSize: 100,
        maxQueueSize: 5,
        onBatch,
      });

      queue.enqueue({ id: 1 });
      queue.enqueue({ id: 2 });
      queue.enqueue({ id: 3 });
      queue.enqueue({ id: 4 });
      queue.enqueue({ id: 5 });

      expect(queue.size()).toBe(5);

      // This should drop task 1
      queue.enqueue({ id: 6 });
      expect(queue.size()).toBe(5);

      // This should drop task 2
      queue.enqueue({ id: 7 });
      expect(queue.size()).toBe(5);

      await queue.flush();

      expect(onBatch).toHaveBeenCalledWith([
        { id: 3 },
        { id: 4 },
        { id: 5 },
        { id: 6 },
        { id: 7 },
      ]);
    });

    it('should handle overflow with batch processing', async () => {
      const onBatch = (jest.fn() as any).mockResolvedValue(undefined);
      queue = new AsyncQueue({
        batchSize: 3,
        maxQueueSize: 5,
        onBatch,
      });

      // Fill queue
      queue.enqueue({ id: 1 });
      queue.enqueue({ id: 2 });
      queue.enqueue({ id: 3 });

      // This triggers batch processing
      await new Promise((resolve) => setTimeout(resolve, 10));

      // Now add more to test overflow
      // When we add these 5, the 3rd one triggers another batch
      queue.enqueue({ id: 4 }); // size=1
      queue.enqueue({ id: 5 }); // size=2
      queue.enqueue({ id: 6 }); // size=3, triggers batch processing
      queue.enqueue({ id: 7 }); // size=1
      queue.enqueue({ id: 8 }); // size=2

      // After second batch triggered on id:6, only 7,8 remain
      await new Promise((resolve) => setTimeout(resolve, 10));
      expect(queue.size()).toBe(2);

      await queue.flush();

      expect(onBatch).toHaveBeenCalledTimes(3);
      expect(onBatch).toHaveBeenNthCalledWith(1, [{ id: 1 }, { id: 2 }, { id: 3 }]);
      expect(onBatch).toHaveBeenNthCalledWith(2, [{ id: 4 }, { id: 5 }, { id: 6 }]);
      expect(onBatch).toHaveBeenNthCalledWith(3, [{ id: 7 }, { id: 8 }]);
    });
  });

  describe('Error handling', () => {
    it('should handle errors in onBatch callback', async () => {
      const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
      const onBatch = (jest.fn() as any).mockRejectedValue(new Error('Batch processing failed'));

      queue = new AsyncQueue({
        batchSize: 2,
        onBatch,
      });

      queue.enqueue({ id: 1 });
      queue.enqueue({ id: 2 });

      await new Promise((resolve) => setTimeout(resolve, 10));

      expect(onBatch).toHaveBeenCalled();
      expect(consoleErrorSpy).toHaveBeenCalledWith(
        'Error processing batch:',
        expect.any(Error)
      );

      consoleErrorSpy.mockRestore();
    });

    it('should continue processing after error', async () => {
      const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
      let callCount = 0;
      const onBatch = (jest.fn() as any).mockImplementation(() => {
        callCount++;
        if (callCount === 1) {
          return Promise.reject(new Error('First batch failed'));
        }
        return Promise.resolve();
      });

      queue = new AsyncQueue({
        batchSize: 2,
        onBatch,
      });

      // First batch - will fail
      queue.enqueue({ id: 1 });
      queue.enqueue({ id: 2 });

      await new Promise((resolve) => setTimeout(resolve, 10));

      // Second batch - should succeed
      queue.enqueue({ id: 3 });
      queue.enqueue({ id: 4 });

      await new Promise((resolve) => setTimeout(resolve, 10));

      expect(onBatch).toHaveBeenCalledTimes(2);
      expect(consoleErrorSpy).toHaveBeenCalledTimes(1);

      consoleErrorSpy.mockRestore();
    });

    it('should handle errors during flush', async () => {
      const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
      const onBatch = (jest.fn() as any).mockRejectedValue(new Error('Flush failed'));

      queue = new AsyncQueue({
        batchSize: 10,
        onBatch,
      });

      queue.enqueue({ id: 1 });

      await expect(queue.flush()).rejects.toThrow('Flush failed');

      consoleErrorSpy.mockRestore();
    });
  });

  describe('Stop and cleanup', () => {
    it('should stop the timer', () => {
      const onBatch = jest.fn() as any;
      queue = new AsyncQueue({
        batchSize: 10,
        flushInterval: 100,
        onBatch,
      });

      queue.enqueue({ id: 1 });
      queue.stop();

      // Timer should be stopped, so this should not trigger processing
      // (difficult to test directly, but stop should clear the interval)
      expect(queue.size()).toBe(1);
    });

    it('should allow stop to be called multiple times', () => {
      const onBatch = jest.fn() as any;
      queue = new AsyncQueue({
        batchSize: 10,
        onBatch,
      });

      expect(() => {
        queue.stop();
        queue.stop();
        queue.stop();
      }).not.toThrow();
    });

    it('should not process after stop is called', async () => {
      jest.useFakeTimers();

      const onBatch = (jest.fn() as any).mockResolvedValue(undefined);
      queue = new AsyncQueue({
        batchSize: 10,
        flushInterval: 100,
        onBatch,
      });

      queue.enqueue({ id: 1 });
      queue.stop();

      jest.advanceTimersByTime(200);
      await jest.runAllTimersAsync();

      expect(onBatch).not.toHaveBeenCalled();

      jest.useRealTimers();
    });
  });

  describe('Edge cases', () => {
    it('should handle tasks with undefined or null values', async () => {
      const onBatch = (jest.fn() as any).mockResolvedValue(undefined);
      queue = new AsyncQueue({
        batchSize: 3,
        onBatch,
      });

      queue.enqueue(null);
      queue.enqueue(undefined);
      queue.enqueue({ id: 1 });

      await queue.flush();

      expect(onBatch).toHaveBeenCalledWith([null, undefined, { id: 1 }]);
    });

    it('should handle complex task objects', async () => {
      const onBatch = (jest.fn() as any).mockResolvedValue(undefined);
      queue = new AsyncQueue({
        batchSize: 2,
        onBatch,
      });

      const complexTask = {
        id: 1,
        nested: { data: { value: 'test' } },
        array: [1, 2, 3],
        fn: () => 'test',
      };

      queue.enqueue(complexTask);
      queue.enqueue({ id: 2 });

      await queue.flush();

      expect(onBatch).toHaveBeenCalledWith([complexTask, { id: 2 }]);
    });

    it('should handle rapid enqueuing', async () => {
      const onBatch = (jest.fn() as any).mockResolvedValue(undefined);
      queue = new AsyncQueue({
        batchSize: 100,
        onBatch,
      });

      // Rapidly enqueue 1000 tasks
      for (let i = 0; i < 1000; i++) {
        queue.enqueue({ id: i });
      }

      await queue.flush();

      expect(onBatch).toHaveBeenCalled();
      // Should have processed all tasks in one batch (or multiple if batch size is hit)
    });
  });
});
