# Merge Instructions

This document outlines how to merge the `feature/certification-challenge` branch, containing the Qdrant retrieval and RAGAS evaluation implementation, back into the `main` branch.

## Option 1: GitHub Pull Request (Recommended)

1.  **Push the Branch:** Ensure your local `feature/certification-challenge` branch is pushed to GitHub:
    ```bash
    git push origin feature/certification-challenge
    ```

2.  **Create Pull Request:** Go to your repository on GitHub. You should see a prompt to create a new pull request from `feature/certification-challenge` to `main`. If not, navigate to the "Pull requests" tab and click "New pull request".

3.  **Review and Merge:**
    *   Set the base branch to `main` and the compare branch to `feature/certification-challenge`.
    *   Provide a clear title and description for your pull request, summarizing the changes.
    *   Request reviews from relevant team members (if applicable).
    *   Address any feedback or conflicts.
    *   Once approved and all checks pass, merge the pull request. Choose an appropriate merge method (e.g., "Squash and merge" for a cleaner history).

## Option 2: GitHub CLI

1.  **Ensure Latest Main:** Ensure your local `main` branch is up-to-date:
    ```bash
    git checkout main
    git pull origin main
    ```

2.  **Checkout Feature Branch:** Switch to your feature branch:
    ```bash
    git checkout feature/certification-challenge
    ```

3.  **Push the Branch:** Ensure your local `feature/certification-challenge` branch is pushed to GitHub:
    ```bash
    git push origin feature/certification-challenge
    ```

4.  **Create Pull Request:** Use the GitHub CLI to create a pull request:
    ```bash
    gh pr create --base main --head feature/certification-challenge --title "feat: Implemented Qdrant retrieval and RAGAS evaluation" --body "This PR integrates the Qdrant-based retrieval mechanism and the RAGAS evaluation script."
    ```
    *   You can customize the `--title` and `--body` as needed.

5.  **Merge Pull Request (after review):** After the pull request has been reviewed and approved on GitHub, you can merge it using the CLI:
    ```bash
    gh pr merge <PR_NUMBER> --squash --delete-branch
    ```
    *   Replace `<PR_NUMBER>` with the actual pull request number.
    *   The `--squash` flag will squash all commits into a single commit on `main`.
    *   The `--delete-branch` flag will delete the feature branch after merging.
