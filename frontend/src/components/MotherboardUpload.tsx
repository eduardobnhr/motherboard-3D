import { useCallback, useMemo } from "react";
import type { FileRejection } from "react-dropzone";
import { useDropzone } from "react-dropzone";

import type { PhaseOneStatus } from "../pages/PhaseOnePage";

const ACCEPTED_IMAGE_TYPES = {
  "image/png": [".png"],
  "image/jpeg": [".jpg", ".jpeg"],
};

interface MotherboardUploadProps {
  errorMessage: string | null;
  previewUrl: string | null;
  selectedFile: File | null;
  status: PhaseOneStatus;
  onAnalyze: () => void;
  onFileRejected: (message: string) => void;
  onFileSelected: (file: File) => void;
}

export function MotherboardUpload({
  errorMessage,
  previewUrl,
  selectedFile,
  status,
  onAnalyze,
  onFileRejected,
  onFileSelected,
}: MotherboardUploadProps) {
  const handleAcceptedFiles = useCallback((files: File[]) => {
    const nextFile = files[0];
    if (!nextFile) {
      return;
    }

    onFileSelected(nextFile);
  }, [onFileSelected]);

  const handleRejectedFiles = useCallback((rejections: FileRejection[]) => {
    onFileRejected(buildDropzoneError(rejections));
  }, [onFileRejected]);

  const { getRootProps, getInputProps, isDragActive, open } = useDropzone({
    accept: ACCEPTED_IMAGE_TYPES,
    maxFiles: 1,
    multiple: false,
    noClick: true,
    onDropAccepted: handleAcceptedFiles,
    onDropRejected: handleRejectedFiles,
  });

  const isAnalyzing = status === "analyzing";
  const canAnalyze = Boolean(selectedFile) && !isAnalyzing;

  const fileSummary = useMemo(() => {
    if (!selectedFile) {
      return "PNG, JPG ou JPEG";
    }

    return `${selectedFile.name} - ${formatFileSize(selectedFile.size)}`;
  }, [selectedFile]);

  return (
    <section className="upload-panel" aria-labelledby="upload-title">
      <div className="panel-heading">
        <div>
          <p className="eyebrow">Fase 1</p>
          <h1 id="upload-title">Upload da placa-mae</h1>
        </div>
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
        onClick={onAnalyze}
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
