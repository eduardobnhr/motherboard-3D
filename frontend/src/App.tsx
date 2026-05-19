import { useState } from "react";

import { ComponentDetailsPanel } from "./components/ComponentDetailsPanel";
import { MotherboardUpload } from "./components/MotherboardUpload";
import { MotherboardScene } from "./components/MotherboardScene";
import type {
  ComponentDetection,
  MotherboardAnalysisResponse,
} from "./types/analysis";

function App() {
  const [analysisResult, setAnalysisResult] =
    useState<MotherboardAnalysisResponse | null>(null);
  const [selectedComponent, setSelectedComponent] =
    useState<ComponentDetection | null>(null);

  function handleAnalysisComplete(analysis: MotherboardAnalysisResponse) {
    setAnalysisResult(analysis);
    setSelectedComponent(null);
  }

  return (
    <main className="app-shell">
      <MotherboardUpload onAnalysisComplete={handleAnalysisComplete} />

      <aside className="analysis-panel" aria-labelledby="analysis-title">
        <div className="panel-heading">
          <div>
            <p className="eyebrow">Viewer 3D</p>
            <h2 id="analysis-title">Cena simplificada</h2>
          </div>
        </div>

        {analysisResult ? (
          <>
            <MotherboardScene
              analysis={analysisResult}
              selectedComponentId={selectedComponent?.id}
              onSelectComponent={setSelectedComponent}
            />
            <AnalysisSummary
              analysis={analysisResult}
              selectedComponent={selectedComponent}
            />
            <ComponentDetailsPanel
              component={selectedComponent}
              onClearSelection={() => setSelectedComponent(null)}
            />
          </>
        ) : (
          <div className="analysis-empty">
            A cena 3D aparecera aqui depois da analise.
          </div>
        )}
      </aside>
    </main>
  );
}

function AnalysisSummary({
  analysis,
  selectedComponent,
}: {
  analysis: MotherboardAnalysisResponse;
  selectedComponent: ComponentDetection | null;
}) {
  return (
    <div className="analysis-summary">
      <dl className="summary-grid">
        <div>
          <dt>Imagem</dt>
          <dd>
            {analysis.image.width} x {analysis.image.height}px
          </dd>
        </div>
        <div>
          <dt>Componentes</dt>
          <dd>{analysis.components.length}</dd>
        </div>
      </dl>

      <ul className="component-list" aria-label="Componentes detectados">
        {analysis.components.map((component) => (
          <li
            className={
              component.id === selectedComponent?.id
                ? "component-list-selected"
                : undefined
            }
            key={component.id}
          >
            <span>{component.label}</span>
            <strong>{Math.round(component.confidence * 100)}%</strong>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default App;
