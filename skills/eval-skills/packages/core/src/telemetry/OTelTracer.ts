import { trace, SpanStatusCode, type Span } from "@opentelemetry/api";

const tracer = trace.getTracer("eval-skills", "0.1.0");

export function withSpan<T>(
  name: string,
  attributes: Record<string, string | number | boolean>,
  fn: (span: Span) => Promise<T>
): Promise<T> {
  return tracer.startActiveSpan(name, async (span) => {
    try {
      // Set initial attributes
      for (const [key, value] of Object.entries(attributes)) {
        span.setAttribute(key, value);
      }
      
      // Execute function
      const result = await fn(span);
      
      // Set status to OK
      span.setStatus({ code: SpanStatusCode.OK });
      return result;
    } catch (error) {
      // Set status to ERROR and record exception
      span.setStatus({
          code: SpanStatusCode.ERROR,
          message: error instanceof Error ? error.message : String(error)
      });
      span.recordException(error instanceof Error ? error : new Error(String(error)));
      throw error;
    } finally {
      span.end();
    }
  });
}
