FROM mcr.microsoft.com/windows/servercore:ltsc2022
USER ContainerAdministrator
RUN powershell -Command Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://vcredist.com/install.ps1'))
USER ContainerUser
ADD https://github.com/mamba-org/micromamba-releases/releases/download/2.1.0-0/micromamba-win-64 micromamba.exe
RUN mkdir %USERPROFILE%\micromamba && \
    copy micromamba.exe %USERPROFILE%\micromamba && \
    del micromamba.exe && \
    powershell -Command \
        [Environment]::SetEnvironmentVariable('PATH', $env:Path + ';' + $env:USERPROFILE + '\micromamba', 'User') && \
    powershell -Command \
        [Environment]::SetEnvironmentVariable('MAMBA_ROOT_PREFIX', $env:USERPROFILE + '\micromambaenv', 'User')
CMD powershell
