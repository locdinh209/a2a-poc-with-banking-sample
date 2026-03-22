from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
# Optional: OTLP exporter
# from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

def setup_tracing(service_name: str, app=None):
    """Sets up OpenTelemetry tracing for a service."""
    from opentelemetry.sdk.resources import Resource
    
    resource = Resource(attributes={
        "service.name": service_name
    })

    provider = TracerProvider(resource=resource)
    
    # Use console exporter for POC (could switch to OTLP for Jaeger etc.)
    processor = BatchSpanProcessor(ConsoleSpanExporter())
    provider.add_span_processor(processor)
    
    trace.set_tracer_provider(provider)

    # Instrument HTTP clients globally
    HTTPXClientInstrumentor().instrument()

    # Instrument FastAPI app if provided
    if app:
        FastAPIInstrumentor.instrument_app(app)

    return trace.get_tracer(service_name)
