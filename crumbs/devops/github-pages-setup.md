---
title: "GitHub Pages Setup with GitHub Actions"
description: "Step-by-step guide for configuring GitHub Pages deployment from GitHub Actions workflows"
category: "devops"
tags: ["github", "github-pages", "github-actions", "deployment", "documentation", "ci-cd"]
difficulty: "beginner"
created: "2025-12-29"
updated: "2025-12-29"
author: "Claude Sonnet 4.5"
related: []
prerequisites:
  - "GitHub repository with admin access"
  - "GitHub Actions workflow that builds static site"
  - "Workflow uses actions/upload-pages-artifact and actions/deploy-pages"
applies_to:
  - "MkDocs documentation sites"
  - "Jekyll static sites"
  - "Hugo static sites"
  - "Any static site generator"
---

# GitHub Pages Setup with GitHub Actions

This guide documents how to configure GitHub Pages to deploy from GitHub Actions workflows rather than from a branch.

## Use Case

When you have a GitHub Actions workflow that builds and deploys documentation or a static site to GitHub Pages, you need to configure the repository settings to accept deployments from Actions.

**Symptoms that you need this:**
- Build job succeeds but deploy job shows "skipped"
- Workflow has both build and deploy jobs, but only build runs
- Site artifact is created but never deployed

## Prerequisites

Your GitHub Actions workflow must include:

1. **Required permissions** in workflow file:
   ```yaml
   permissions:
     contents: read
     pages: write
     id-token: write
   ```

2. **Build job** that creates artifact:
   ```yaml
   - name: Upload artifact
     uses: actions/upload-pages-artifact@v3
     with:
       path: ./site
   ```

3. **Deploy job** that deploys artifact:
   ```yaml
   - name: Deploy to GitHub Pages
     uses: actions/deploy-pages@v4
   ```

## Setup Steps

### 1. Navigate to Repository Settings

1. Go to your repository on GitHub: `https://github.com/YOUR_USERNAME/YOUR_REPO`
2. Click the **Settings** tab (requires admin access)
3. In the left sidebar, scroll down to **Pages** under "Code and automation"

### 2. Configure Build and Deployment Source

> **This is the critical step that's often missed!**

1. Under the **Build and deployment** section
2. Find the **Source** dropdown
3. Change from **"Deploy from a branch"** to **"GitHub Actions"**
4. Changes auto-save when you select

![GitHub Pages Source Selection](https://docs.github.com/assets/cb-48480/mw-1440/images/help/pages/pages-source-none-or-github-actions.webp)

### 3. Verify Environment Settings (Optional)

1. Still in Settings, go to **Environments** in the left sidebar
2. You should see an environment named `github-pages` (auto-created when you first deploy)
3. Click on it to configure deployment protection rules if needed
4. For public repos, this is usually ready to use as-is

### 4. Trigger Deployment

1. Push a commit to your main branch (or configured trigger branch)
2. Go to the **Actions** tab
3. Watch the workflow run:
   - ✅ **Build** job completes first (creates artifact)
   - ✅ **Deploy** job runs after build succeeds (deploys to Pages)
4. Check deployment URL in the deploy job output or in Pages settings

## Common Issues and Solutions

### Issue: Deploy Job Skipped

**Symptom:** Build job succeeds but deploy job shows "skipped"

**Cause:** Repository not configured to accept GitHub Actions deployments (still set to "Deploy from a branch")

**Solution:** Follow Step 2 above to change Source to "GitHub Actions"

### Issue: Permission Denied Errors

**Symptom:** Deploy job fails with permission errors like:
```
Error: HttpError: Resource not accessible by integration
```

**Cause:** Workflow doesn't have required permissions

**Solution:** Add permissions block at workflow level:
```yaml
permissions:
  contents: read
  pages: write
  id-token: write
```

### Issue: Wrong Branch Deploying

**Symptom:** Deployments not happening on main branch pushes

**Cause:** Workflow condition filtering wrong branch

**Solution:** Check workflow's deploy job condition:
```yaml
deploy:
  needs: build
  if: github.event_name == 'push' && github.ref == 'refs/heads/main'
```

### Issue: Environment Not Found

**Symptom:** Deploy fails with "Environment github-pages not found"

**Cause:** Environment hasn't been created yet (happens on first run)

**Solution:**
1. Go to Settings > Environments
2. Click "New environment"
3. Name it `github-pages`
4. Save (no special settings needed)
5. Re-run the workflow

## Complete Example Workflow

```yaml
name: Deploy Documentation

on:
  push:
    branches: [main]
  workflow_dispatch:

# Required permissions for Pages deployment
permissions:
  contents: read
  pages: write
  id-token: write

# Allow only one concurrent deployment
concurrency:
  group: "pages"
  cancel-in-progress: false

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
          cache: 'pip'
          cache-dependency-path: 'docs/requirements.txt'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r docs/requirements.txt

      - name: Build documentation
        run: mkdocs build --clean --strict

      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: ./site

  deploy:
    needs: build
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

## Verification Steps

After setup, verify the deployment:

1. **Check Pages Settings:**
   - Go to Settings > Pages
   - See "Your site is live at https://username.github.io/repo/"
   - Click the link to view deployed site

2. **Check Actions Tab:**
   - Both build and deploy jobs should show green checkmarks
   - Deploy job should show the deployment URL

3. **Check Deployments:**
   - In repository main page, click "Deployments" on right sidebar
   - Should see recent "github-pages" deployments

4. **Verify Site Content:**
   - Visit the Pages URL
   - Check that theme/styling is correctly applied
   - Test navigation and links

## Key Differences from Branch Deployment

| Aspect | Deploy from Branch | Deploy from Actions |
|--------|-------------------|---------------------|
| **Build** | GitHub's built-in Jekyll build | Custom build in Actions workflow |
| **Control** | Limited (Jekyll only) | Full control over build process |
| **Frameworks** | Jekyll only | Any static site generator |
| **Caching** | Limited | Full control via Actions cache |
| **Dependencies** | GitHub-managed | Self-managed in workflow |
| **Customization** | Minimal | Complete flexibility |

## Related Resources

- [GitHub Pages Documentation](https://docs.github.com/en/pages)
- [Configuring a publishing source](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)
- [Using custom workflows with GitHub Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)
- [actions/upload-pages-artifact](https://github.com/actions/upload-pages-artifact)
- [actions/deploy-pages](https://github.com/actions/deploy-pages)

## Notes

- This setup is required **once per repository**
- Subsequent pushes automatically trigger build + deploy
- No need to configure branch-based deployment when using Actions
- Custom domains can be configured in the Pages settings
- HTTPS is automatically enabled for github.io domains
- Free for public repositories, requires GitHub Pro/Team for private repos
