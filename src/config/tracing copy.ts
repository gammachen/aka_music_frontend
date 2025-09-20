import { WebTracerProvider } from '@opentelemetry/sdk-trace-web';
import { SimpleSpanProcessor, BatchSpanProcessor } from '@opentelemetry/sdk-trace-base';
import { OTLPTraceExporter } from '@opentelemetry/exporter-trace-otlp-http';
import { FetchInstrumentation } from '@opentelemetry/instrumentation-fetch';
import { registerInstrumentations } from '@opentelemetry/instrumentation';
import { Resource } from '@opentelemetry/resources';
import { SemanticResourceAttributes } from '@opentelemetry/semantic-conventions';
import { SamplingDecision } from '@opentelemetry/sdk-trace-base';

// 创建资源信息
const resource = new Resource({
  [SemanticResourceAttributes.SERVICE_NAME]: 'aka-music-frontend',
  [SemanticResourceAttributes.SERVICE_VERSION]: '1.0.0',
});

// 创建导出器
const exporter = new OTLPTraceExporter({
  url: 'http://127.0.0.1:11800/v1/traces', // SkyWalking OAP 服务地址
  concurrencyLimit: 10, // 最大并发请求数
  headers: {
    'Content-Type': 'application/x-protobuf'
  },
  timeoutMillis: 3000, // 请求超时时间
});

// 创建并配置 TracerProvider
export function initTracing() {
  const provider = new WebTracerProvider({
    resource: resource,
    sampler: {
      shouldSample: () => ({
        decision: SamplingDecision.RECORD_AND_SAMPLED, // 始终采样
        attributes: {}
      }) // 始终采样
    }
  });

  // 使用 BatchSpanProcessor 来批量处理和发送追踪数据
  provider.addSpanProcessor(new BatchSpanProcessor(exporter, {
    maxQueueSize: 100, // 最大队列大小
    maxExportBatchSize: 10, // 每批发送的最大span数量
    scheduledDelayMillis: 500, // 定期发送间隔(毫秒)
  }));

  // 注册 FetchInstrumentation 用于自动追踪 fetch 请求
  registerInstrumentations({
    instrumentations: [
      new FetchInstrumentation({
        clearTimingResources: true, // 清理timing资源
        applyCustomAttributesOnSpan: (span) => {
          span.setAttribute('app.version', '1.0.0');
        }
      })
    ],
  });

  // 注册 TracerProvider
  provider.register();

  return provider;
}