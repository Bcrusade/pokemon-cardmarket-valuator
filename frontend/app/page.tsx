'use client';

import { FormEvent, useState } from 'react';

import {
  createJob,
  fetchHtmlProvided,
  ingestCandidates,
  runFullEvaluation,
  type CandidateInputPayload
} from '../lib/api';

const LANGUAGE_OPTIONS = ['English', 'German', 'French', 'Spanish', 'Italian', 'Japanese'];
const CONDITION_OPTIONS = ['NM', 'EX', 'GD', 'LP', 'PL'];

export default function HomePage() {
  const [jobId, setJobId] = useState('');
  const [targetLanguage, setTargetLanguage] = useState('English');
  const [minimumCondition, setMinimumCondition] = useState('NM');

  const [candidateTitle, setCandidateTitle] = useState('');
  const [candidateUrlInput, setCandidateUrlInput] = useState('');
  const [candidateSource, setCandidateSource] = useState('manual');
  const [candidateSetName, setCandidateSetName] = useState('');
  const [candidateCardNumber, setCandidateCardNumber] = useState('');

  const [selectedCandidateUrl, setSelectedCandidateUrl] = useState('');
  const [activeCandidateUrl, setActiveCandidateUrl] = useState('');

  const [htmlInput, setHtmlInput] = useState('');
  const [evaluationResult, setEvaluationResult] = useState<unknown>(null);
  const [status, setStatus] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function withAction(action: () => Promise<void>) {
    setError('');
    setStatus('');
    setLoading(true);
    try {
      await action();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  }

  async function onCreateJob(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await withAction(async () => {
      const created = await createJob({
        target_language: targetLanguage,
        minimum_condition: minimumCondition
      });
      setJobId(created.job_id);
      setEvaluationResult(null);
      setSelectedCandidateUrl('');
      setActiveCandidateUrl('');
      setHtmlInput('');
      setStatus(`Created job ${created.job_id}`);
    });
  }

  async function onIngestCandidate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!jobId) {
      setError('Create a job first.');
      return;
    }

    await withAction(async () => {
      const payload: CandidateInputPayload = {
        title: candidateTitle,
        url: candidateUrlInput,
        source: candidateSource
      };
      if (candidateSetName) payload.extracted_set_name = candidateSetName;
      if (candidateCardNumber) payload.extracted_card_number = candidateCardNumber;

      await ingestCandidates(jobId, [payload]);
      setSelectedCandidateUrl(candidateUrlInput);
      setActiveCandidateUrl(candidateUrlInput);
      setStatus(`Candidate ingested and activated: ${candidateUrlInput}`);
    });
  }

  function ensureActiveCandidateUrl(): string | null {
    if (!activeCandidateUrl) {
      setError('No active candidate URL. Ingest/select a candidate first.');
      return null;
    }
    return activeCandidateUrl;
  }

  async function onProvideHtml(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!jobId) {
      setError('Create a job first.');
      return;
    }

    const url = ensureActiveCandidateUrl();
    if (!url) return;

    await withAction(async () => {
      await fetchHtmlProvided(jobId, url, htmlInput);
      setStatus(`Stored HTML for ${url}`);
    });
  }

  async function onRunEvaluation() {
    if (!jobId) {
      setError('Create a job first.');
      return;
    }

    const url = ensureActiveCandidateUrl();
    if (!url) return;

    await withAction(async () => {
      const result = await runFullEvaluation(jobId, url);
      setEvaluationResult(result);
      setStatus(`Evaluation completed for ${url}`);
    });
  }

  return (
    <main style={{ maxWidth: 900, margin: '1rem auto', fontFamily: 'sans-serif', padding: '0 1rem' }}>
      <h1>Pokemon Cardmarket Valuator</h1>
      <p>Candidate-driven deterministic MVP workflow.</p>

      <section>
        <h2>1) Create Job</h2>
        <form onSubmit={onCreateJob}>
          <label>
            Target language{' '}
            <select value={targetLanguage} onChange={(e) => setTargetLanguage(e.target.value)}>
              {LANGUAGE_OPTIONS.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </label>{' '}
          <label>
            Minimum condition{' '}
            <select value={minimumCondition} onChange={(e) => setMinimumCondition(e.target.value)}>
              {CONDITION_OPTIONS.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </label>{' '}
          <button type="submit" disabled={loading}>Create Job</button>
        </form>
        <p>
          <strong>Job ID:</strong> {jobId || '(none)'}
        </p>
      </section>

      <section>
        <h2>2) Ingest Candidate</h2>
        <form onSubmit={onIngestCandidate}>
          <div>
            <input placeholder="title" value={candidateTitle} onChange={(e) => setCandidateTitle(e.target.value)} required />
          </div>
          <div>
            <input
              placeholder="url"
              value={candidateUrlInput}
              onChange={(e) => {
                setCandidateUrlInput(e.target.value);
                setSelectedCandidateUrl(e.target.value);
              }}
              required
            />
          </div>
          <div>
            <input placeholder="source" value={candidateSource} onChange={(e) => setCandidateSource(e.target.value)} required />
          </div>
          <div>
            <input
              placeholder="optional extracted set name"
              value={candidateSetName}
              onChange={(e) => setCandidateSetName(e.target.value)}
            />
          </div>
          <div>
            <input
              placeholder="optional extracted card number"
              value={candidateCardNumber}
              onChange={(e) => setCandidateCardNumber(e.target.value)}
            />
          </div>
          <button type="submit" disabled={loading}>Submit Candidate</button>
        </form>
        <p>
          <strong>Selected Candidate URL:</strong> {selectedCandidateUrl || '(none)'}
        </p>
        <p>
          <strong>Active Candidate URL:</strong> {activeCandidateUrl || '(none)'}
        </p>
      </section>

      <section>
        <h2>3) Provide Candidate HTML</h2>
        <form onSubmit={onProvideHtml}>
          <textarea
            placeholder="Paste product page HTML"
            value={htmlInput}
            onChange={(e) => setHtmlInput(e.target.value)}
            rows={10}
            cols={100}
            required
          />
          <div>
            <button type="submit" disabled={loading}>Store HTML</button>
          </div>
        </form>
      </section>

      <section>
        <h2>4) Run Full Evaluation</h2>
        <button type="button" onClick={onRunEvaluation} disabled={loading}>Run Full Evaluation</button>
      </section>

      <section>
        <h2>5) Results</h2>
        {loading && <p>Loading...</p>}
        {status && <p style={{ color: 'green' }}>{status}</p>}
        {error && <p style={{ color: 'red' }}>{error}</p>}
        {evaluationResult ? <pre>{JSON.stringify(evaluationResult, null, 2)}</pre> : <p>No evaluation result yet.</p>}
      </section>
    </main>
  );
}
