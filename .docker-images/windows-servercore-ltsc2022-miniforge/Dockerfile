FROM mcr.microsoft.com/windows/servercore:ltsc2022

ADD https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Windows-x86_64.exe miniforge_installer.exe
RUN miniforge_installer.exe /InstallationType=JustMe /RegisterPython=0 /S /D=%USERPROFILE%\Miniforge3 && \
    del miniforge_installer.exe
RUN setx /M PATH "%PATH%;%USERPROFILE%\Miniforge3\Scripts"
RUN %USERPROFILE%\Miniforge3\Scripts\activate.bat && \
    conda config --add channels conda-forge && \
    conda update --all -n base --yes && \
    conda clean --all --yes

CMD cmd.exe /k %USERPROFILE%\Miniforge3\Scripts\activate.bat