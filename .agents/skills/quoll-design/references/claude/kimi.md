# Kimi in Claude Code

This note records Kimi as an LLM provider under Claude Code. It is not about Kimi CLI or other agent harnesses and contains no credential. Keep provider-neutral Claude Code permission guidance in [permissions.md](permissions.md).

Kimi's coding endpoint does not implement Claude Code's server-side auto-mode review protocol, so `CLAUDE_CODE_AUTO_MODE_SERVER=0` selects Claude Code's own classifier requests. Without a dedicated classifier override, `ANTHROPIC_DEFAULT_SONNET_MODEL` can route those requests to the primary K3.1 model. Claude Code 2.1.302 and later supports `CLAUDE_CODE_AUTO_MODE_MODEL`; setting it to `kimi-for-coding` selects K2.8 Preview for the remaining checks while leaving the main and subagent models unchanged.

```json
{
  "env": {
    "ANTHROPIC_BASE_URL": "https://api.kimi.ai/coding/",
    "ANTHROPIC_MODEL": "kimi-k3.1-pro[1m]",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "kimi-k3.1-pro[1m]",
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "kimi-k3.1-pro[1m]",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL": "kimi-k3.1-pro[1m]",
    "CLAUDE_CODE_AUTO_MODE_SERVER": "0",
    "CLAUDE_CODE_AUTO_MODE_MODEL": "kimi-for-coding"
  }
}
```

Start a new session after changing environment values. Use a debug log to confirm that `classifier_request_started` names `kimi-for-coding`; a session using server-side review would not exercise this local model path. Make no global thinking or effort change as part of this override: Claude Code documents no classifier-only thinking switch, and Kimi's model defaults should be measured before adding another independent variable.

Kimi documents `kimi-for-coding` as K2.8 Preview and `k3.1-pro-highspeed` as the premium high-speed K3.1 variant. Check [Kimi's model configuration](https://www.kimi.ai/help/kimi-code/models) for current mappings and [Claude Code's permission modes](https://code.claude.com/docs/en/permission-modes#choose-the-classifier-model) for classifier selection and debugging.
