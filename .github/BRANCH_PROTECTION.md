# Branch Protection Setup

This repository enforces branch protection on `main`. The rules are:

1. **No direct pushes to `main`** — all changes must go through a Pull Request
2. **Pull request review required** — at least 1 approval from the maintainer (DIP-RO)
3. **CI checks must pass** — lint, test, and build jobs must all succeed
4. **No force pushes** — git history is preserved
5. **No branch deletion** — `main` cannot be deleted

## Setting Up Branch Protection (for repository owner)

### Via GitHub CLI

```bash
# Install GitHub CLI if not already installed
# https://cli.github.com/

# Authenticate
gh auth login

# Set branch protection rules
gh api repos/DIP-RO/MCP_Package/rulesets \
  --method POST \
  --input .github/branch-protection.json

# Or use the simpler approach:
gh api repos/DIP-RO/MCP_Package/branches/main/protection \
  --method PUT \
  --field required_pull_request_reviews[required_approving_review_count]=1 \
  --field required_status_checks[strict]=true \
  --field required_status_checks[checks][][context]=lint \
  --field required_status_checks[checks][][context]="test (ubuntu-latest, 3.12)" \
  --field enforce_admins=true \
  --field restrictions=false
```

### Via GitHub Web UI

1. Go to Settings > Branches
2. Click "Add branch protection rule"
3. Branch name pattern: `main`
4. Enable:
   - Require a pull request before merging (1 approval)
   - Require status checks to pass before merging (lint, test, build)
   - Require branches to be up to date before merging
   - Do not allow bypassing the above settings
   - Restrict who can push to matching branches (admin only)
5. Click "Create"

### Via GitHub API (curl)

```bash
curl -X PUT \
  -H "Authorization: token YOUR_GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  https://api.github.com/repos/DIP-RO/MCP_Package/branches/main/protection \
  -d '{
    "required_pull_request_reviews": {
      "required_approving_review_count": 1,
      "dismiss_stale_reviews": true
    },
    "required_status_checks": {
      "strict": true,
      "contexts": ["lint", "test (ubuntu-latest, 3.12)", "build"]
    },
    "enforce_admins": true,
    "restrictions": null,
    "allow_force_pushes": false,
    "allow_deletions": false
  }'
```

## Contributor Workflow

Contributors must:
1. Fork the repository
2. Create a feature branch
3. Submit a Pull Request
4. Get approval from DIP-RO
5. Wait for CI to pass
6. Maintainer merges the PR

No one can push directly to `main`. No one can force push. No one can delete `main`.
