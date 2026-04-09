const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? 'http://localhost:8000';

export type CreateJobPayload = {
  target_language: string;
  minimum_condition: string;
};

export type CreateJobResponse = {
  job_id: string;
  status: string;
};

export type CandidateInputPayload = {
  title: string;
  url: string;
  source: string;
  extracted_set_name?: string;
  extracted_card_number?: string;
};

export type FetchHtmlResponse = {
  candidate_url: string;
  retrieval_mode: 'provided' | 'fetched';
  stored: boolean;
  html_length: number;
};

async function requestJson<T>(path: string, payload: unknown): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  let bodyText = '';
  try {
    bodyText = await res.text();
  } catch {
    bodyText = '';
  }

  if (!res.ok) {
    throw new Error(`Request failed (${res.status}) ${path}: ${bodyText || 'No error body returned'}`);
  }

  return bodyText ? (JSON.parse(bodyText) as T) : ({} as T);
}

export async function createJob(payload: CreateJobPayload) {
  return requestJson<CreateJobResponse>('/jobs', payload);
}

export async function ingestCandidates(jobId: string, results: CandidateInputPayload[]) {
  return requestJson<{ ingested_count: number }>(`/jobs/${jobId}/candidates`, { results });
}

export async function fetchHtmlProvided(jobId: string, candidateUrl: string, providedHtml: string) {
  return requestJson<FetchHtmlResponse>(`/jobs/${jobId}/candidates/fetch-html`, {
    candidate_url: candidateUrl,
    retrieval_mode: 'provided',
    provided_html: providedHtml
  });
}

export async function runFullEvaluation(jobId: string, candidateUrl: string) {
  return requestJson<unknown>(`/jobs/${jobId}/candidates/run-full-evaluation`, {
    candidate_url: candidateUrl
  });
}
