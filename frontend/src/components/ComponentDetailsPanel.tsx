import type { ComponentDetection } from "../types/analysis";

interface ComponentDetailsPanelProps {
  component: ComponentDetection | null;
  onClearSelection: () => void;
}

export function ComponentDetailsPanel({
  component,
  onClearSelection,
}: ComponentDetailsPanelProps) {
  if (!component) {
    return (
      <section
        className="component-details-panel component-details-empty"
        aria-labelledby="component-details-title"
      >
        <div>
          <p className="eyebrow">Inspecao</p>
          <h3 id="component-details-title">Detalhes do componente</h3>
        </div>
        <p>Clique em um componente da placa para visualizar detalhes.</p>
      </section>
    );
  }

  return (
    <section
      className="component-details-panel"
      aria-labelledby="component-details-title"
    >
      <div className="details-heading">
        <div>
          <p className="eyebrow">Inspecao</p>
          <h3 id="component-details-title">{component.label}</h3>
        </div>
        <button
          className="clear-selection-button"
          type="button"
          onClick={onClearSelection}
        >
          Limpar
        </button>
      </div>

      <p className="component-description">{component.description}</p>

      <dl className="component-details-grid">
        <DetailItem label="ID" value={component.id} />
        <DetailItem label="Type" value={component.type} />
        <DetailItem
          label="Confidence"
          value={formatConfidence(component.confidence)}
        />
        <DetailItem
          label="Estimated height"
          value={component.estimatedHeight.toFixed(2)}
        />
      </dl>

      <div className="bbox-panel">
        <h4>Bbox original</h4>
        <dl className="bbox-grid">
          <DetailItem label="x" value={formatNumber(component.bbox.x)} />
          <DetailItem label="y" value={formatNumber(component.bbox.y)} />
          <DetailItem label="width" value={formatNumber(component.bbox.width)} />
          <DetailItem label="height" value={formatNumber(component.bbox.height)} />
        </dl>
      </div>
    </section>
  );
}

function DetailItem({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt>{label}</dt>
      <dd>{value}</dd>
    </div>
  );
}

function formatConfidence(confidence: number): string {
  return `${Math.round(confidence * 100)}%`;
}

function formatNumber(value: number): string {
  return Number.isInteger(value) ? String(value) : value.toFixed(2);
}
