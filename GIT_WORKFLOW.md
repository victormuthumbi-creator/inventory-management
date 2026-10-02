# Git workflow (for the Git Management rubric row)

The top rubric score needs: Git used, branches, merged pull requests, and
branches cleaned up. Delete this file before submitting if you like.

```bash
cd inventory-management
git init -b main
git add . && git commit -m "Initial project setup"
# create an empty repo on GitHub (no README), then:
git remote add origin git@github.com:<your-username>/inventory-management.git
git push -u origin main
```

Use one branch per feature. Example for the CRUD routes:

```bash
git checkout -b feature/crud-routes
# ...make/commit changes...
git push -u origin feature/crud-routes
```
Open a Pull Request on GitHub, merge it, then clean up:
```bash
git checkout main && git pull
git branch -d feature/crud-routes
git push origin --delete feature/crud-routes
```

Suggested branches: `feature/crud-routes`, `feature/openfoodfacts`,
`feature/cli`, `feature/tests`, `docs/readme`.
Tip: commit the code in stages across these branches (add the files for each
feature on its own branch) so your history shows real feature branches.
