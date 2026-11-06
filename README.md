# Der echte Einbürgerungstest

A static website with a humorous, unofficial quiz about German everyday culture, habits and regional quirks – the things no textbook teaches you.

> **Note:** This is a fun, unofficial quiz and **not** the official German naturalization test (Einbürgerungstest). Some customs vary by region.

## Overview

The quiz contains 12 multiple-choice questions (in German) covering topics such as the *Weißwurstäquator*, Bavarian beer garden etiquette, the Swabian *Kehrwoche*, *Moin* and *Stoßlüften*. Each question has four answer options, one correct answer and a short explanation.

The website is fully static (HTML, CSS, JavaScript) and requires no backend, which makes it cheap and simple to host on AWS.

## Project Structure

| Path | Description |
|------|-------------|
| `fragen.md` | Source of all quiz questions, answers and explanations |
| `README.md` | This file |

## Local Development

Since the site is static, any local web server works:

```bash
# Python
python -m http.server 8000

# or Node.js
npx serve .
```

Then open http://localhost:8000 in your browser.

## Deployment on AWS

The recommended setup is **Amazon S3** for storage and **Amazon CloudFront** for HTTPS and caching.

1. **Create an S3 bucket** (keep *Block all public access* enabled).
2. **Upload the site files:**

   ```bash
   aws s3 sync ./ s3://<your-bucket-name> --delete --exclude ".git/*" --exclude "README.md"
   ```

3. **Create a CloudFront distribution** with the S3 bucket as origin, using **Origin Access Control (OAC)** so the bucket stays private. Set `index.html` as the default root object.
4. *(Optional)* **Custom domain:** request a certificate in **AWS Certificate Manager** (region `us-east-1`) and add a DNS record in **Route 53** pointing to the CloudFront distribution.
5. **Invalidate the cache** after each deployment:

   ```bash
   aws cloudfront create-invalidation --distribution-id <distribution-id> --paths "/*"
   ```

Alternatively, **AWS Amplify Hosting** can deploy the site directly from the Git repository with HTTPS and CI/CD included.

## Adding or Editing Questions

Questions are maintained in [fragen.md](fragen.md). Each question follows this format:

```markdown
### N. Question text?

- A) Option
- B) Option
- C) Option
- D) Option

**Richtige Antwort:** B

**Erklärung:** Short explanation.
```
