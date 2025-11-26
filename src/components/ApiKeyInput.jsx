export default function ApiKeyInput({ apiKey, onApiKeyChange, disabled }) {
  return (
    <div className="api-key-input-container">
      <label htmlFor="api-key-input">
        Enter Your API Key:
      </label>
      <input
        id="api-key-input"
        type="password"
        value={apiKey}
        onChange={(e) => onApiKeyChange(e.target.value)}
        placeholder="Paste your API key here"
        disabled={disabled}
        className="api-key-input"
      />
      <p className="api-key-hint">Your API key is stored locally and never sent to our servers.</p>
    </div>
  );
}
