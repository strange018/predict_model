@echo off
REM Cluster Integration Setup Script for Windows
REM This script helps set up KUBECONFIG and validate cluster connection

setlocal enabledelayedexpansion

echo.
echo =========================================
echo Predictive Infrastructure - Cluster Setup
echo =========================================
echo.

REM Check if kubeconfig path provided
if "%1"=="" (
    echo Usage: setup_cluster.bat "C:\path\to\kubeconfig"
    echo.
    echo Example:
    echo   setup_cluster.bat "C:\Users\Username\.kube\config"
    echo.
    echo Or set KUBECONFIG manually:
    echo   set KUBECONFIG=C:\path\to\kubeconfig
    echo   python app.py
    echo.
    exit /b 1
)

set KUBECONFIG=%1

if not exist "%KUBECONFIG%" (
    echo Error: Kubeconfig file not found: %KUBECONFIG%
    exit /b 1
)

echo Found kubeconfig: %KUBECONFIG%
echo.

REM Set environment variable for this session
set KUBECONFIG=%1

echo Setting KUBECONFIG for this session...
echo KUBECONFIG=%KUBECONFIG%
echo.

REM Run validation
echo Running validation...
C:/Python314/python.exe validate_cluster.py

if errorlevel 1 (
    echo.
    echo Validation failed. Please check the errors above.
    exit /b 1
)

echo.
echo =========================================
echo Setup Complete! Starting application...
echo =========================================
echo.

REM Start the application
C:/Python314/python.exe app.py
