FROM mcr.microsoft.com/windows/servercore:ltsc2022

ADD https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Windows-x86_64.exe miniforge_installer.exe
RUN miniforge_installer.exe /InstallationType=JustMe /RegisterPython=0 /S /D=%USERPROFILE%\Miniforge3

ENV PATH="%USERPROFILE%\Miniforge3;%PATH%"

CMD ["conda.exe"]