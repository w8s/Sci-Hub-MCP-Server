# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.3.x   | ✅        |
| < 0.3   | ❌        |

## Reporting a Vulnerability

Please **do not** open a public GitHub issue for security vulnerabilities.

Instead, report them privately via [GitHub's private vulnerability reporting](https://github.com/w8s/scihub-mcp/security/advisories/new).

I'll acknowledge within a few days and aim to release a fix within 30 days depending on severity.

## Notes

This server makes outbound network requests to CrossRef and Sci-Hub mirror endpoints. It does not store credentials or personal data. The `download_scihub_pdf` tool writes files to paths specified by the caller — ensure your MCP client is configured to restrict output paths appropriately.
