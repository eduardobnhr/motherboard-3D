import { useEffect, useMemo, useState } from "react";

import { analyzeMotherboardImage } from "../api/motherboardAnalysis";
import { ComponentDetailsPanel } from "../components/ComponentDetailsPanel";
import { MotherboardScene } from "../components/MotherboardScene";
import { MotherboardUpload } from "../components/MotherboardUpload";
import type {
  ComponentDetection,
  MotherboardAnalysisResponse,
} from "../types/analysis";

export type PhaseOneStatus =
  | "idle"
  | "fileSelected"
  | "analyzing"
  | "success"
  | "error";

export function PhaseOnePage() {
  const [status, setStatus] = useState<PhaseOneStatus>("idle");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [analysisResult, setAnalysisResult] =
    useState<MotherboardAnalysisResponse | null>(null);
  const [selectedComponent, setSelectedComponent] =
    useState<ComponentDetection | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    if (!selectedFile) {
      setPreviewUrl(null);
      return;
    }

    const objectUrl = URL.createObjectURL(selectedFile);
    setPreviewUrl(objectUrl);

    return () => URL.revokeObjectURL(objectUrl);
  }, [selectedFile]);

  const canShowViewer = status === "success" && analysisResult;

  const previewSummary = useMemo(() => {
    if (!selectedFile) {
      return null;
    }

    return {
      name: selectedFile.name,
      size: formatFileSize(selectedFile.size),
      type: selectedFile.type || "image",
    };
  }, [selectedFile]);

  function handleFileSelected(file: File) {
    setSelectedFile(file);
    setAnalysisResult(null);
    setSelectedComponent(null);
    setErrorMessage(null);
    setStatus("fileSelected");
  }

  function handleFileRejected(message: string) {
    setSelectedFile(null);
    setAnalysisResult(null);
    setSelectedComponent(null);
    setErrorMessage(message);
    setStatus("error");
  }

  async function handleAnalyze() {
    if (!selectedFile) {
      setErrorMessage("Selecione uma imagem antes de iniciar a analise.");
      setStatus("error");
      return;
    }

    setStatus("analyzing");
    setErrorMessage(null);
    setSelectedComponent(null);

    try {
      const analysis = await analyzeMotherboardImage(selectedFile);
      setAnalysisResult(analysis);
      setStatus("success");
    } catch (error) {
      setAnalysisResult(null);
      setErrorMessage(toFriendlyErrorMessage(error));
      setStatus("error");
    }
  }

  return (
    <main className="app-shell">
      <section className="workflow-column" aria-label="Fluxo de analise">
        <MotherboardUpload
          errorMessage={errorMessage}
          previewUrl={previewUrl}
          selectedFile={selectedFile}
          status={status}
          onAnalyze={handleAnalyze}
          onFileRejected={handleFileRejected}
          onFileSelected={handleFileSelected}
        />

        {previewSummary ? (
          <ImagePreviewSummary
            analysis={analysisResult}
            previewSummary={previewSummary}
            status={status}
          />
        ) : null}
      </section>

      <section className="viewer-column" aria-labelledby="viewer-title">
        <div className="panel-heading">
          <div>
            <p className="eyebrow">Viewer 3D</p>
            <h2 id="viewer-title">Cena procedural</h2>
          </div>
          <StatusBadge status={status} />
        </div>

        {canShowViewer ? (
          <>
            <MotherboardScene
              analysis={analysisResult}
              selectedComponentId={selectedComponent?.id}
              onSelectComponent={setSelectedComponent}
            />
            <div className="viewer-sidecar">
              <AnalysisSummary
                analysis={analysisResult}
                selectedComponent={selectedComponent}
              />
              <ComponentDetailsPanel
                component={selectedComponent}
                onClearSelection={() => setSelectedComponent(null)}
              />
            </div>
          </>
        ) : (
          <EmptyViewerState status={status} />
        )}
      </section>
    </main>
  );
}

function ImagePreviewSummary({
  analysis,
  previewSummary,
  status,
}: {
  analysis: MotherboardAnalysisResponse | null;
  previewSummary: { name: string; size: string; type: string };
  status: PhaseOneStatus;
}) {
  return (
    <section className="preview-summary" aria-label="Resumo da imagem original">
      <div>
        <p className="eyebrow">Imagem original</p>
        <h2>{previewSummary.name}</h2>
      </div>
      <dl className="summary-grid">
        <div>
          <dt>Arquivo</dt>
          <dd>{previewSummary.size}</dd>
        </div>
        <div>
          <dt>Formato</dt>
          <dd>{previewSummary.type}</dd>
        </div>
        {analysis ? (
          <div>
            <dt>Dimensoes</dt>
            <dd>
              {analysis.image.width} x {analysis.image.height}px
            </dd>
          </div>
        ) : null}
        <div>
          <dt>Status</dt>
          <dd>{getStatusLabel(status)}</dd>
        </div>
      </dl>
    </section>
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

function EmptyViewerState({ status }: { status: PhaseOneStatus }) {
  const message =
    status === "analyzing"
      ? "Analisando imagem e preparando a cena 3D..."
      : "Envie uma imagem para reconstruir a placa em 3D.";

  return (
    <div className="analysis-empty">
      {status === "analyzing" ? <span className="loading-spinner" /> : null}
      <p>{message}</p>
    </div>
  );
}

function StatusBadge({ status }: { status: PhaseOneStatus }) {
  return <span className="status-pill">{getStatusLabel(status)}</span>;
}

function getStatusLabel(status: PhaseOneStatus): string {
  const labels: Record<PhaseOneStatus, string> = {
    idle: "Aguardando",
    fileSelected: "Imagem pronta",
    analyzing: "Analisando",
    success: "Concluido",
    error: "Erro",
  };

  return labels[status];
}

function formatFileSize(size: number): string {
  if (size < 1024 * 1024) {
    return `${Math.max(1, Math.round(size / 1024))} KB`;
  }

  return `${(size / (1024 * 1024)).toFixed(1)} MB`;
}

function toFriendlyErrorMessage(error: unknown): string {
  if (error instanceof Error && error.message.trim()) {
    return error.message;
  }

  return "Nao foi possivel analisar a imagem. Tente novamente.";
}

