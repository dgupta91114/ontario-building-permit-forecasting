# GitHub Upload Steps

1. Create a new **public** repository named `ontario-building-permit-forecasting` without adding an automatic README or license.
2. Extract this project folder and open a terminal inside it.
3. Replace `REPLACE-WITH-USERNAME` in `CITATION.cff` and in the synopsis.
4. Run:

```bash
git init
git branch -M main
git add .
git commit -m "Initialize QM640 capstone repository"
git remote add origin https://github.com/REPLACE-WITH-USERNAME/ontario-building-permit-forecasting.git
git push -u origin main
```

5. After the official data pipeline runs successfully, add the small processed dataset and analysis evidence:

```bash
git add data/processed docs outputs/tables outputs/figures
git commit -m "Add reproducible data pipeline outputs"
git push
```

Do not commit passwords, access tokens, `.venv`, raw full-table ZIP files, or synthetic demo results as if they were real findings. GitHub authentication should be handled through GitHub Desktop, SSH, or a credential manager; no credential is needed inside the source code.
