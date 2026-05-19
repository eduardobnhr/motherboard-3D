import { useCallback, useEffect, useMemo, useState } from "react";
import { FileRejection, useDropzone } from "react-dropzone";

import { analyzeMotherboardImage } from "../api/motherboardAnalysis";
import type { MotherboardAnalysisResponse } from "../types/analysis";

const ACCEPTED_IMAGE_TYPES = {
  "image/png": [".png"],
  "image/jpeg": [".jpg", ".jpeg"],
};

interface MotherboardUploadProps {
  onAnalysisComplete: (analysis: MotherboardAnalysisResponse) => void;
}

export function MotherboardUpload({
  onAnalysisComplete,
}: MotherboardUploadProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
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

  const handleAcceptedFiles = useCallback((files: File[]) => {
    const nextFile = files[0];
    if (!nextFile) {
      return;
    }

    setSelectedFile(nextFile);
    setErrorMessage(null);
  }, []);

  const handleRejectedFiles = useCallback((rejections: FileRejection[]) => {
    setSelectedFile(null);
    setErrorMessage(buildDropzoneError(rejections));
  }, []);

  const { getRootProps, getInputProps, isDragActive, open } = useDropzone({
    accept: ACCEPTED_IMAGE_TYPES,
    maxFiles: 1,
    multiple: false,
    noClick: true,
    onDropAccepted: handleAcceptedFiles,
    onDropRejected: handleRejectedFiles,
  });

  const canAnalyze = Boolean(selectedFile) && !isAnalyzing;

  const fileSummary = useMemo(() => {
    if (!selectedFile) {
      return "PNG, JPG ou JPEG";
    }

    return `${selectedFile.name} - ${formatFileSize(selectedFile.size)}`;
  }, [selectedFile]);

  async function handleAnalyzeClick() {
    if (!selectedFile) {
      setErrorMessage("Selecione uma imagem antes de iniciar a analise.");
      return;
    }

    setIsAnalyzing(true);
    setErrorMessage(null);

    try {
      const analysis = await analyzeMotherboardImage(selectedFile);
      onAnalysisComplete(analysis);
    } catch (error) {
      setErrorMessage(toFriendlyErrorMessage(error));
    } finally {
      setIsAnalyzing(false);
    }
  }

  return (
    <section className="upload-panel" aria-labelledby="upload-title">
      <div className="panel-heading">
        <div>
          <p className="eyebrow">Fase 1</p>
          <h1 id="upload-title">Upload da placa-mae</h1>
        </div>
        <span className="status-pill">Mock backend</span>
      </div>

      <div
        {...getRootProps({
          className: `dropzone ${isDragActive ? "dropzone-active" : ""}`,
        })}
      >
        <input {...getInputProps()} />
        <div className="dropzone-content">
          <span className="dropzone-icon" aria-hidden="true">
            +
          </span>
          <div>
            <p className="dropzone-title">
              {isDragActive ? "Solte a imagem aqui" : "Arraste a imagem aqui"}
            </p>
            <p className="dropzone-subtitle">{fileSummary}</p>
          </div>
          <button className="secondary-button" type="button" onClick={open}>
            Selecionar arquivo
          </button>
        </div>
      </div>

      {previewUrl ? (
        <div className="preview-frame">
          <img src={previewUrl} alt="Preview da placa-mae selecionada" />
        </div>
      ) : (
        <div className="preview-empty">Preview da imagem</div>
      )}

      {errorMessage ? (
        <p className="error-message" role="alert">
          {errorMessage}
        </p>
      ) : null}

      <button
        className="primary-button"
        type="button"
        disabled={!canAnalyze}
        onClick={handleAnalyzeClick}
      >
        {isAnalyzing ? "Analisando..." : "Analisar placa"}
      </button>
    </section>
  );
}

function buildDropzoneError(rejections: FileRejection[]): string {
  const firstError = rejections[0]?.errors[0];
  if (firstError?.code === "file-invalid-type") {
    return "Use uma imagem PNG, JPG ou JPEG.";
  }

  if (firstError?.code === "too-many-files") {
    return "Envie apenas uma imagem por vez.";
  }

  return "Nao foi possivel carregar esse arquivo.";
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

