# Checkpoint: Der echte Einbürgerungstest

## Goal
Static quiz website (12 humorous German culture questions), hosted cheaply on AWS. Questions maintained in `fragen.md`; push to `main` deploys via GitHub Actions.

## Decisions
- Hosting: private S3 bucket + CloudFront (OAC, HTTPS, `PriceClass_100`, managed SecurityHeadersPolicy). No custom domain for now.
- IaC: CloudFormation (`infra/template.yaml`).
- CI/CD auth: GitHub OIDC -> IAM role restricted to `repo:vvkorz/einbuergerung_de:ref:refs/heads/main`. No AWS keys in GitHub.
- Quiz UX: fixed question order, explanation shown after each answer, score + restart at end. German UI, "Sie" form.
- Build: `scripts/build.py` (stdlib only) parses + validates `fragen.md` -> `dist/questions.json`, copies `site/` -> `dist/`. Fails on malformed questions. Answer-key table in `fragen.md` is ignored.

## Repo structure (all created, build verified locally)
- `fragen.md` – questions (renamed from `echter_einbuergerungstest_fragen.md`)
- `site/index.html`, `site/app.js`, `site/style.css` – quiz UI (uses `textContent`, no innerHTML)
- `scripts/build.py`
- `infra/template.yaml` – S3, OAC, CloudFront, bucket policy, optional OIDC provider (param `ExistingOidcProviderArn`), DeployRole (S3 put/delete/list + CloudFront invalidation). Outputs: BucketName, DistributionId, WebsiteUrl, DeployRoleArn
- `.github/workflows/deploy.yml` – build on push/PR, deploy on push to main. Uses repo **variables**: `AWS_REGION`, `AWS_ROLE_ARN`, `S3_BUCKET`, `CLOUDFRONT_DISTRIBUTION_ID`
- `README.md`, `.gitignore` (`dist/`, `__pycache__/`)

Local test: `python scripts/build.py; python -m http.server 8000 -d dist`

## AWS setup state
- GitHub repo: `vvkorz/einbuergerung_de`
- CLI profile `einbuergerung` = IAM user `einbuergerung` with access key, region `eu-north-1` (Stockholm). User has admin-level permissions.
- Target (member) account: `<member-account-id>` (shown as "Project einbuergerung" on settings.aws.com, linked to an IAM Identity Center instance).
- AWS Organization with management account `<management-account-id>` (owned by user), feature set ALL. Check IDs with `aws organizations describe-organization --profile einbuergerung`.
- Account upgraded from free plan to paid.

## Current blocker
Deploy fails: an SCP in the user's own org explicitly denies `iam:CreateOpenIDConnectProvider` and `iam:ListOpenIDConnectProviders` in the member account (SCP ID is shown in the error message). Stack rolls back to `ROLLBACK_COMPLETE` (must be deleted before retry).

## Next steps
1. Sign in to the management account -> AWS Organizations -> Policies -> the blocking SCP: inspect content/targets. Then either narrow the deny (remove OIDC provider actions), detach it from the member account (keep `FullAWSAccess`), or use an exempt role if the SCP has an exception condition. Beware: the "Projects" feature may manage/restore this SCP.
2. Delete failed stack and redeploy:
   ```powershell
   aws cloudformation delete-stack --stack-name einbuergerungstest --profile einbuergerung
   aws cloudformation wait stack-delete-complete --stack-name einbuergerungstest --profile einbuergerung
   aws cloudformation deploy --stack-name einbuergerungstest --template-file infra/template.yaml --capabilities CAPABILITY_IAM --parameter-overrides GitHubRepo=vvkorz/einbuergerung_de --profile einbuergerung
   ```
3. Read outputs (`aws cloudformation describe-stacks --stack-name einbuergerungstest --query "Stacks[0].Outputs" --output table --profile einbuergerung`) and set GitHub repo variables (`AWS_REGION=eu-north-1`).
4. Push to main; site at `WebsiteUrl`.

Fallback (option B) if SCP can't be changed: remove IAM resources from template (S3 + CloudFront only), workflow authenticates with a least-privilege access key stored as GitHub **secrets** `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY`.
