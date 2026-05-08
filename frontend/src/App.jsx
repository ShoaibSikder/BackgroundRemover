import { useEffect, useState } from "react";

const API_URL = "/api/images/";

function formatFileSize(size) {
  if (!size) return "";
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`;
  return `${(size / (1024 * 1024)).toFixed(2)} MB`;
}

function extractFilename(contentDisposition, fallback = "background-removed.png") {
  const match = contentDisposition?.match(/filename="?([^"]+)"?/i);
  return match?.[1] || fallback;
}

function App() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    if (!file) {
      setPreview("");
      return undefined;
    }

    const previewUrl = URL.createObjectURL(file);
    setPreview(previewUrl);

    return () => URL.revokeObjectURL(previewUrl);
  }, [file]);

  const handleFileChange = (event) => {
    const selectedFile = event.target.files?.[0];
    if (!selectedFile) return;

    setFile(selectedFile);
    setResult(null);
    setError("");
    setMessage("");
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");
    setMessage("");

    if (!file) {
      setError("Choose an image first.");
      return;
    }

    const formData = new FormData();
    formData.append("original", file);

    setLoading(true);
    setResult(null);
    setMessage("Removing background and preparing your PNG...");

    try {
      const response = await fetch(API_URL, {
        method: "POST",
        body: formData,
      });

      const data = await response.json().catch(() => null);
      if (!response.ok) {
        throw new Error(
          data?.original?.[0] ||
            data?.detail ||
            data?.error ||
            "Image processing failed.",
        );
      }

      setResult({
        id: data.id,
        processed: data.processed,
        downloadUrl: data.download_url,
      });
      setMessage("Your image is ready.");
    } catch (uploadError) {
      setError(uploadError.message);
      setMessage("");
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async () => {
    if (!result?.downloadUrl) return;

    setDownloading(true);
    setError("");

    try {
      const response = await fetch(result.downloadUrl);
      if (!response.ok) {
        throw new Error("Download failed. Please try again.");
      }

      const blob = await response.blob();
      const filename = extractFilename(response.headers.get("content-disposition"));
      const blobUrl = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = blobUrl;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(blobUrl);
    } catch (downloadError) {
      setError(downloadError.message);
    } finally {
      setDownloading(false);
    }
  };

  return (
    <div className="page">
      <div className="aurora aurora-one" />
      <div className="aurora aurora-two" />

      <main className="layout">
        <section className="hero-panel">
          <p className="eyebrow">AI background remover</p>
          <h1>Remove the background in one click.</h1>
          <p className="hero-copy">
            Upload a photo, preview the result, and download a transparent PNG
            when it is ready.
          </p>

          <div className="hero-stats">
            <div className="stat-card">
              <span>Input</span>
              <strong>JPG, PNG, WEBP</strong>
            </div>
            <div className="stat-card">
              <span>Output</span>
              <strong>Transparent PNG</strong>
            </div>
            <div className="stat-card">
              <span>Status</span>
              <strong>{loading ? "Processing" : "Ready"}</strong>
            </div>
          </div>
        </section>

        <section className="workspace">
          <form className="glass-card uploader" onSubmit={handleSubmit}>
            <div className="card-heading">
              <div>
                <p className="section-label">Upload</p>
                <h2>Start with your image</h2>
                <p className="card-copy">
                  Pick a JPG, PNG, or WEBP file. Photos with one clear subject
                  usually give the best result.
                </p>
              </div>
              {file && (
                <span className="file-pill">
                  {file.name} {formatFileSize(file.size)}
                </span>
              )}
            </div>

            <label className="dropzone">
              <input type="file" accept="image/*" onChange={handleFileChange} />
              <span className="dropzone-kicker">Step 1</span>
              <strong>Click here to choose an image</strong>
              <p>Supported formats: JPG, PNG, WEBP</p>
              <ul className="dropzone-tips">
                <li>Use a photo where the subject is centered</li>
                <li>A simple background gives cleaner cutouts</li>
                <li>After upload, click Remove Background</li>
              </ul>
            </label>

            <button className="primary-button" type="submit" disabled={loading}>
              {loading ? "Removing background..." : "Step 2: Remove Background"}
            </button>

            {message && <p className="feedback success">{message}</p>}
            {error && <p className="feedback error">{error}</p>}
          </form>

          <div className="results-grid">
            <article className="glass-card preview-panel">
              <div className="card-heading">
                <div>
                  <p className="section-label">Original</p>
                  <h2>Before</h2>
                </div>
              </div>

              {preview ? (
                <div className="image-stage checkerboard">
                  <img src={preview} alt="Selected preview" />
                </div>
              ) : (
                <div className="empty-state">
                  <p>No image selected yet.</p>
                </div>
              )}
            </article>

            <article className="glass-card preview-panel">
              <div className="card-heading">
                <div>
                  <p className="section-label">Result</p>
                  <h2>After</h2>
                </div>
                {result && <span className="status-chip">PNG ready</span>}
              </div>

              {result?.processed ? (
                <>
                  <div className="image-stage checkerboard">
                    <img src={result.processed} alt="Processed result" />
                  </div>

                  <button
                    className="secondary-button"
                    type="button"
                    onClick={handleDownload}
                    disabled={downloading}
                  >
                    {downloading ? "Downloading..." : "Download PNG"}
                  </button>
                </>
              ) : (
                <div className="empty-state">
                  <p>Your transparent preview will appear here.</p>
                </div>
              )}
            </article>
          </div>
        </section>
      </main>

      <footer className="site-footer glass-card">
        <div className="footer-top">
          <div>
            <p className="section-label">Connect</p>
            <h2 className="footer-title">Background Remover</h2>
            <p className="footer-copy">
              Upload, remove, preview, and download with a cleaner interface.
            </p>
          </div>

          <div className="footer-links">
            <a
              href="https://github.com/ShoaibSikder"
              target="_blank"
              rel="noopener noreferrer"
            >
              GitHub
            </a>
            <a
              href="https://www.instagram.com/shoaibsikder0"
              target="_blank"
              rel="noopener noreferrer"
            >
              Instagram
            </a>
            <a
              href="https://www.facebook.com/shoaib.sikder.35?mibextid=ZbWKwL"
              target="_blank"
              rel="noopener noreferrer"
            >
              Facebook
            </a>
            <a href="/api/images/" target="_blank" rel="noopener noreferrer">
              API
            </a>
          </div>
        </div>

        <div className="footer-bottom">
          <p>Copyright © 2026 by @shoaibsikder | All Rights Reserved.</p>
        </div>
      </footer>
    </div>
  );
}

export default App;
