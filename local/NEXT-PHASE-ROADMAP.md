# Next-Phase Roadmap: Sealed Secrets & GHCR Image Promotion

This roadmap adds **Bitnami Sealed Secrets** and **automated GHCR image promotion** to `innovate-inc-aws-infra`, eliminating plain-text database passwords in Git and manual `local/deploy-local.ps1` runs.

---

## Phase 1: Bitnami Sealed Secrets (Encrypting DB Credentials in Git)

- **Step 1 — Install the Sealed Secrets Controller & `kubeseal` CLI**
  - Install `kubeseal` on Windows via `winget install Bitnami.Kubeseal`.
  - Deploy the Sealed Secrets controller into the `kube-system` namespace on the `innovate` Kind cluster:
    `kubectl apply -f https://github.com/bitnami-labs/sealed-secrets/releases/download/v0.27.2/controller.yaml`
  - *Verification:* `kubectl get pods -n kube-system -l name=sealed-secrets-controller` shows `1/1 Running`.

- **Step 2 — Generate Namespace-Scoped `SealedSecret` Manifests**
  - For each environment (`dev`, `staging`, `prod`), create a dry-run Kubernetes `Secret` containing `POSTGRES_USER`, `POSTGRES_PASSWORD`, and `DATABASE_URL`, then pipe it directly into `kubeseal --format yaml > local/apps/<env>/sealed-db-secret.yaml`.
  - Back up the cluster's master sealing key (`kubectl get secret -n kube-system -l sealedsecrets.bitnami.com/sealed-secrets-key -o yaml`) outside the repository.
  - *Verification:* `sealed-db-secret.yaml` contains encrypted `encryptedData:` blocks with zero plain-text passwords.

- **Step 3 — Swap Plain Secrets & Sync via ArgoCD**
  - Remove plain-text secret manifests from `local/apps/dev/`, `local/apps/staging/`, and `local/apps/prod/`, commit the new `sealed-db-secret.yaml` files, and push to `main`.
  - *Verification:* ArgoCD syncs the `SealedSecret` resources, the controller generates native `Secret` objects in each namespace, and `.\local\verify-project.ps1` passes `/db-test`.

---

## Phase 2: Automated GHCR Image Promotion (Hands-Free GitOps CI/CD)

- **Step 1 — Publish Scanned Images to `ghcr.io` in GitHub Actions**
  - Update `.mithub/workflows/build-and-push.yml` (`.github/workflows/build-and-push.yml`) with `permissions: contents: write` and `packages: write`, then log in to `ghcr.io` using `${{ secrets.GITHUB_TOKEN }}`.
  - After the Trivy vulnerability scan passes, build and push `ghcr.io/charanprathi/innovate-app:${{ github.sha }}` (and `:latest`).
  - *Verification:* The `Packages` tab on GitHub displays the `innovate-app` container image tagged with the commit SHA.

- **Step 2 — Automate `dev` Manifest Updates & Add Environment Promotion**
  - At the end of `.github/workflows/build-and-push.yml` (on pushes to `main`), update the image tag in `local/apps/dev/` to `ghcr.io/charanprathi/innovate-app:${{ github.sha }}` and commit `[skip ci] Bump dev image to <sha>`.
  - Add a `workflow_dispatch` promotion workflow (`.github/workflows/promote.yml`) accepting `image_tag` and `target_env` (`staging` or `prod`) inputs to update `local/apps/<target_env>/` via Git commit.
  - *Verification:* Pushing a change to `app/app.py` updates `local/apps/dev/` automatically, and ArgoCD (`selfHeal: true`) rolls out the new pod in `dev` without running `local/deploy-local.ps1`.

- **Step 3 — Configure Kind Image Pull & `imagePullPolicy`**
  - Set the `ghcr.io/charanprathi/innovate-app` package visibility to **Public** (or create a `ragcred` `imagePullSecret` in `dev`, `staging`, and `prod`), and update `imagePullPolicy` from `Never` to `IfNotPresent` in `local/apps/*`.
  - *Verification:* `kubectl describe pod -n dev -l app=innovate-app` shows `Successfully pulled image "ghcr.io/charanprathi/innovate-app:<sha>"`.
