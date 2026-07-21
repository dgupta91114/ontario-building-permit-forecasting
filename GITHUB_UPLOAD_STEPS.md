# GitHub Upload Steps

1. The public repository has been created at <https://github.com/dgupta91114/ontario-building-permit-forecasting>.
2. Open a terminal inside this project folder.
3. Confirm the remote with `git remote -v`.
4. Run:

```bash
git add .
git commit -m "Update capstone repository"
git push
```

5. After the official data pipeline runs successfully, add the small processed dataset and analysis evidence:

```bash
git add data/processed docs outputs/tables outputs/figures
git commit -m "Add reproducible data pipeline outputs"
git push
```

Do not commit passwords, access tokens, `.venv`, raw full-table ZIP files, or synthetic demo results as if they were real findings. GitHub authentication should be handled through GitHub Desktop, SSH, or a credential manager; no credential is needed inside the source code.
