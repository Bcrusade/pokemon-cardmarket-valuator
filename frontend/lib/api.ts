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

async function postJson<T>(path: string, payload: unknown): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(payload)
  });

  const rawBody = await response.text();

  if (!response.ok) {
    throw new Error(`Request failed (${response.status}) ${path}: ${rawBody || 'No response body'}`);
  }

  return rawBody ? (JSON.parse(rawBody) as T) : ({} as T);
}

export async function createJob(payload: CreateJobPayload) {
  return postJson<CreateJobResponse>('/jobs', payload);
}

export async function ingestCandidates(jobId: string, results: CandidateInputPayload[]) {
  return postJson<{ ingested_count: number }>(`/jobs/${jobId}/candidates`, { results });
}

export async function fetchHtmlProvided(jobId: string, candidateUrl: string, providedHtml: string) {
  return postJson<FetchHtmlResponse>(`/jobs/${jobId}/candidates/fetch-html`, {
    candidate_url: candidateUrl,
    retrieval_mode: 'provided',
    provided_html: providedHtml
  });
}

export async function runFullEvaluation(jobId: string, candidateUrl: string) {
  return postJson<unknown>(`/jobs/${jobId}/candidates/run-full-evaluation`, {
    candidate_url: candidateUrl
  });
}
