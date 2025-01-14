@echo off
:: Navigate to the directory
cd /d %~dp0

:: Initialize a new Git repository with main branch if not already initialized
if not exist .git (
    git init -b main
)

:: Remove any nested .git directories to prevent conflicts
for /d %%d in (*) do (
    if exist "%%d\.git" (
        rd /s /q "%%d\.git"
    )
)

:: Add all files to the repository
git add -A

:: Commit the changes if any
git commit -m "Initial commit" || echo No changes to commit

:: Check if remote origin exists
git remote | find "origin" >nul 2>&1
if errorlevel 1 (
    git remote add origin https://github.com/DangAW2002/Project1_14.git
) else (
    echo Remote 'origin' already exists.
)

:: Ensure the main branch has commits before pushing
git rev-parse main >/dev/null 2>&1
if %errorlevel% equ 0 (
    git push -u origin main
) else (
    echo "No commits on main branch to push."
)