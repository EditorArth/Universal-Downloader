# Universal Downloader

Windows desktop media downloader built with Python, PySide6, and yt-dlp.

## Build locally on Windows

Install Python 3.12 (64-bit), then run in this folder:

```bat
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt pyinstaller
pyinstaller --noconfirm --clean --windowed --onefile --name UniversalDownloader --icon universal_downloader_logo.ico --add-data "universal_downloader_logo.png;." --add-data "universal_downloader_logo.ico;." --collect-all yt_dlp universal_downloader.py
```

The executable is created at `dist\UniversalDownloader.exe`.

## Build via GitHub Actions

1. Create a GitHub repository and push the project files.
2. Open **Actions** and run **Build Windows EXE** to build an artifact.
3. To publish a downloadable release, create and push a version tag, for example:
   ```bat
   git tag v1.0.0
   git push origin v1.0.0
   ```
4. The workflow builds the EXE and attaches it to a GitHub Release.

## Publish the website with GitHub Pages

1. In `docs/index.html`, replace `YOUR_GITHUB_USERNAME` with your GitHub username.
2. Push the repository to GitHub.
3. Open **Settings → Pages**, choose **Deploy from a branch**, select branch `main` and folder `/docs`, then save.
4. The site URL will be `https://YOUR_GITHUB_USERNAME.github.io/Universal-Downloader/`.

## Notes

- The download button works after a tagged release publishes `UniversalDownloader.exe`.
- Build on Windows for a Windows EXE.
- Test on a clean Windows PC before sharing. Unsigned one-file Python apps may trigger antivirus warnings.
- Only download content you have permission to access and use.
