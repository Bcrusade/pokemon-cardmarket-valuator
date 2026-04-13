'use client';

import { FormEvent, useState } from 'react';

import {
  type CandidateInputPayload,
  createJob,
  fetchHtmlProvided,
  ingestCandidates,
  runFullEvaluation
} from '../lib/api';

const LANGUAGE_OPTIONS = ['English', 'German', 'French', 'Spanish', 'Italian', 'Japanese'];
const CONDITION_OPTIONS = ['NM', 'EX', 'GD', 'LP', 'PL'];

export default function HomePage() {
  const [jobId, setJobId] = useState('');
  const [targetLanguage, setTargetLanguage] = useState('English');
  const [minimumCondition, setMinimumCondition] = useState('NM');

  const [candidateTitle, setCandidateTitle] = useState('');
  const [candidateUrl, setCandidateUrl] = useState('');
  const [candidateSource, setCandidateSource] = useState('manual');
  const [candidateSetName, setCandidateSetName] = useState('');
  const [candidateCardNumber, setCandidateCardNumber] = useState('');

  const [htmlInput, setHtmlInput] = useState('');
  const [result, setResult] = useState<unknown>(null);
  const [status, setStatus] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function runAction(action: () => Promise<void>) {
    setStatus('');
    setError('');
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
    await runAction(async () => {
      const created = await createJob({
        target_language: targetLanguage,
        minimum_condition: minimumCondition
      });
      setJobId(created.job_id);
      setResult(null);
      setCandidateUrl('');
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

    await runAction(async () => {
      const payload: CandidateInputPayload = {
        title: candidateTitle,
        url: candidateUrl,
        source: candidateSource
      };
      if (candidateSetName) payload.extracted_set_name = candidateSetName;
      if (candidateCardNumber) payload.extracted_card_number = candidateCardNumber;

      await ingestCandidates(jobId, [payload]);
      setStatus(`Candidate ingested: ${candidateUrl}`);
    });
  }

  async function onProvideHtml(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!jobId) {
      setError('Create a job first.');
      return;
    }
    if (!candidateUrl) {
      setError('Enter or ingest a candidate URL first.');
      return;
    }

    await runAction(async () => {
      await fetchHtmlProvided(jobId, candidateUrl, htmlInput);
      setStatus(`Stored HTML for ${candidateUrl}`);
    });
  }

  async function onRunFullEvaluation() {
    if (!jobId) {
      setError('Create a job first.');
      return;
    }
    if (!candidateUrl) {
      setError('Enter or ingest a candidate URL first.');
      return;
    }

    await runAction(async () => {
      const evaluation = await runFullEvaluation(jobId, candidateUrl);
      setResult(evaluation);
      setStatus(`Evaluation completed for ${candidateUrl}`);
    });
  }

  return (
    <main style={{ fontFamily: 'sans-serif', margin: '1rem auto', maxWidth: 900, padding: '0 1rem' }}>
      <h1>Pokemon Cardmarket Valuator</h1>
      <p>Minimal candidate-driven MVP workflow.</p>

      <section>
        <h2>1) Create Job</h2>
        <form onSubmit={onCreateJob}>
          <label>
            Target language{' '}
            <select value={targetLanguage} onChange={(event) => setTargetLanguage(event.target.value)}>
              {LANGUAGE_OPTIONS.map((language) => (
                <option key={language} value={language}>
                  {language}
                </option>
              ))}
            </select>
          </label>{' '}
          <label>
            Minimum condition{' '}
            <select value={minimumCondition} onChange={(event) => setMinimumCondition(event.target.value)}>
              {CONDITION_OPTIONS.map((condition) => (
                <option key={condition} value={condition}>
                  {condition}
                </option>
              ))}
            </select>
          </label>{' '}
          <button type="submit" disabled={loading}>
            Create Job
          </button>
        </form>
        <p>
          <strong>Job ID:</strong> {jobId || '(none)'}
        </p>
      </section>

      <section>
        <h2>2) Ingest Candidate</h2>
        <form onSubmit={onIngestCandidate}>
          <div>
            <input
              placeholder="title"
              value={candidateTitle}
              onChange={(event) => setCandidateTitle(event.target.value)}
              required
            />
          </div>
          <div>
            <input
              placeholder="url"
              value={candidateUrl}
              onChange={(event) => setCandidateUrl(event.target.value)}
              required
            />
          </div>
          <div>
            <input
              placeholder="source"
              value={candidateSource}
              onChange={(event) => setCandidateSource(event.target.value)}
              required
            />
          </div>
          <div>
            <input
              placeholder="optional extracted set name"
              value={candidateSetName}
              onChange={(event) => setCandidateSetName(event.target.value)}
            />
          </div>
          <div>
            <input
              placeholder="optional extracted card number"
              value={candidateCardNumber}
              onChange={(event) => setCandidateCardNumber(event.target.value)}
            />
          </div>
          <button type="submit" disabled={loading}>
            Submit Candidate
          </button>
        </form>
      </section>

      <section>
        <h2>3) Provide Candidate HTML</h2>
        <form onSubmit={onProvideHtml}>
          <textarea
            placeholder="Paste product page HTML"
            value={htmlInput}
            onChange={(event) => setHtmlInput(event.target.value)}
            rows={10}
            cols={100}
            required
          />
          <div>
            <button type="submit" disabled={loading}>
              Store HTML
            </button>
          </div>
        </form>
      </section>

      <section>
        <h2>4) Run Full Evaluation</h2>
        <button type="button" onClick={onRunFullEvaluation} disabled={loading}>
          Run Full Evaluation
        </button>
      </section>

      <section>
        <h2>5) Results</h2>
        {loading && <p>Loading...</p>}
        {status && <p style={{ color: 'green' }}>{status}</p>}
        {error && <p style={{ color: 'red' }}>{error}</p>}
        {result ? <pre>{JSON.stringify(result, null, 2)}</pre> : <p>No evaluation result yet.</p>}
      </section>
    </main>
  );
}
