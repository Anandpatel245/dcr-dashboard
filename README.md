# Mumbai & Maharashtra DCR Dashboard

A production-safe, automated dashboard for tracking Daily Construction Rules (DCR) amendments for Mumbai DCPR 2034 and Maharashtra UDCPR.

## Features

✅ **Automated Daily Updates** – Runs every day at 9:00 AM IST via GitHub Actions  
✅ **Verified Amendments Only** – Only displays entries marked as verified=true  
✅ **Idempotent** – Safe repeated runs; no duplicate entries  
✅ **Email Notifications** – SMTP integration for daily status emails  
✅ **Structured Data** – JSON-based updates for easy maintenance  
✅ **GitHub Pages** – Permanent, no-rebuild dashboard URL  
✅ **Validation** – JSON schema validation before processing  
✅ **Production-Ready** – Minimal, safe, well-commented code  

## Setup

### 1. Enable GitHub Pages
- Go to Settings → Pages
- Source: Deploy from a branch
- Branch: main, Folder: / (root)

### 2. Configure GitHub Secrets
Add these to your repository settings (Settings → Secrets and variables → Actions):

```
SMTP_HOST           # e.g., smtp.gmail.com
SMTP_PORT           # e.g., 587
SMTP_USERNAME       # Your email
SMTP_PASSWORD       # App password (not regular password)
SMTP_FROM           # From address for emails
DASHBOARD_URL       # Your GitHub Pages URL
```

**Gmail Example:**
- SMTP_HOST: `smtp.gmail.com`
- SMTP_PORT: `587`
- SMTP_USERNAME: `your-email@gmail.com`
- SMTP_PASSWORD: [Create App Password](https://myaccount.google.com/apppasswords)
- SMTP_FROM: `your-email@gmail.com`
- DASHBOARD_URL: `https://Anandpatel245.github.io/dcr-dashboard/`

### 3. Add a New Amendment

Edit `data/updates.json` and add a new entry:

```json
{
  "date": "DD Mon YYYY",
  "regulation": "Mumbai DCPR 2034 or Maharashtra UDCPR",
  "status": "One-line summary of the amendment",
  "verified_link": "https://official-source-url",
  "source_type": "news|article|official|circular",
  "verified": true
}
```

**Required fields:**
- `date` – Date of amendment (format: DD Mon YYYY)
- `regulation` – Which regulation was amended
- `status` – Summary of the amendment
- `verified_link` – Link to official source (must start with http/https)
- `source_type` – Type of source (news, article, official, circular)
- `verified` – Boolean (true = appears in dashboard, false = hidden)

### 4. Manual Test

1. Go to your repository
2. Click **Actions** → **DCR Dashboard Update** → **Run workflow**
3. Check the logs to verify it ran successfully

## Files

| File | Purpose |
|------|----------|
| `.github/workflows/dcr-dashboard.yml` | GitHub Actions workflow (scheduled daily + manual trigger) |
| `scripts/validate_json.py` | JSON validation before processing |
| `scripts/update_dcr_dashboard.py` | Main update logic (HTML + email) |
| `data/updates.json` | Amendment data (add new entries here) |
| `data/state.json` | Workflow state (last run, last verified date) |
| `mumbai-maharashtra-dcr-dashboard.html` | Published dashboard (auto-updated) |
| `index.html` | Legacy dashboard |
| `todo.html` | To-do app (separate from dashboard) |

## How It Works

```
9:00 AM IST Daily (or manual trigger)
         ↓
    Checkout repo
         ↓
    Validate JSON files
         ↓
    Find new verified entries
         ↓
    Update HTML dashboard
         ↓
    Update state.json
         ↓
    Commit changes (only if changed)
         ↓
    Deploy to GitHub Pages
         ↓
    Send email notification
         ↓
    Dashboard live at: https://...
```

## Email Format

### If new amendment found:
```
Subject: DCR update: verified amendment

DCR Dashboard Update

Amendment Date: 6 May 2026
Regulation: Mumbai DCPR 2034
Status: Higher FSI-free space...

Verified Link: https://...

View full dashboard: https://Anandpatel245.github.io/dcr-dashboard/
```

### If no update:
```
Subject: DCR update: no update
Body: No update today
```

## Idempotency & Safety

✅ Uses `state.json` to track last processed date  
✅ Never creates duplicate rows or log entries  
✅ Only commits if actual changes made  
✅ Validates JSON structure before any processing  
✅ Graceful email failures (non-blocking)  
✅ Preserves all prior verified entries  
✅ Reverse chronological order (newest first)  

## Maintenance

### Add a verified amendment:
1. Edit `data/updates.json`
2. Add new entry with `"verified": true`
3. Commit and push
4. Workflow runs next cycle (or trigger manually)
5. Dashboard updates automatically
6. Email notification sent

### Mark an entry as unverified:
1. Set `"verified": false` for that entry
2. Commit and push
3. Next workflow run removes it from dashboard

### Disable email temporarily:
- Remove all `SMTP_*` secrets
- Workflow will skip email (no error)

### Manual workflow run:
1. Go to Actions → DCR Dashboard Update
2. Click "Run workflow"
3. Check logs for results

## Troubleshooting

### Workflow fails on validation:
- Check `data/updates.json` structure
- Verify all required fields are present
- Ensure `verified` is `true` or `false` (not string)
- Ensure URLs start with `http://` or `https://`

### Dashboard not updating:
1. Check workflow logs: Actions → DCR Dashboard Update
2. Verify `mumbai-maharashtra-dcr-dashboard.html` exists
3. Run validation: `python scripts/validate_json.py`

### Email not sending:
1. Verify SMTP secrets are set correctly
2. Check GitHub Actions logs for SMTP errors
3. Try using an app-specific password (Gmail)
4. Email errors don't block workflow (by design)

## Dashboard URL

🌐 **https://Anandpatel245.github.io/dcr-dashboard/mumbai-maharashtra-dcr-dashboard.html**

The URL remains permanent. Never changes, never rebuilds.

## Support

For questions:
1. Check GitHub Actions logs for errors
2. Verify `data/updates.json` has correct structure
3. Test locally: `python scripts/update_dcr_dashboard.py`
4. Review the inline code comments for details

---

**Last Updated:** 20 May 2026  
**Automation Setup:** Production-ready DCR tracking  
**Next Run:** Daily at 9:00 AM IST  
