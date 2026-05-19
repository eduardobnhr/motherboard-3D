import type { MotherboardAnalysisResponse } from "../types/analysis";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "";
const ANALYZE_ENDPOINT = "/api/motherboard/analyze";

export class MotherboardAnalysisError extends Error {
  status?: number;

  constructor(message: string, status?: number) {
    super(message);
    this.name = "MotherboardAnalysisError";
    this.status = status;
  }
}

export async function analyzeMotherboardImage(
  file: File,
): Promise<MotherboardAnalysisResponse> {
  const formData = new FormData();
  formData.append("file", file);

  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${ANALYZE_ENDPOINT}`, {
      method: "POST",
      body: formData,
    });
  } catch {
    throw new MotherboardAnalysisError(
      "Nao foi possivel conectar ao backend de analise.",
    );
  }

  if (!response.ok) {
    throw new MotherboardAnalysisError(
      await readErrorMessage(response),
      response.status,
    );
  }

  return response.json() as Promise<MotherboardAnalysisResponse>;
}

async function readErrorMessage(response: Response): Promise<string> {
  try {
    const body = (await response.json()) as { detail?: unknown };
    if (typeof body.detail === "string" && body.detail.trim()) {
      return body.detail;
    }
  } catch {
    // Fall through to the generic message below.
  }

  if (response.status === 413) {
    return "A imagem selecionada e maior que o limite permitido.";
  }

  return "Nao foi possivel analisar a imagem agora.";
}
