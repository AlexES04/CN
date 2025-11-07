@echo OFF
setlocal

REM
cd /d "%~dp0"
echo --- Directorio de trabajo establecido en: %cd% ---

REM
SET AWS_ACCOUNT_ID=339713111309
SET AWS_REGION=us-east-1
SET REPOSITORY_NAME=products-app-lambdas
SET ECR_BASE=%AWS_ACCOUNT_ID%.dkr.ecr.%AWS_REGION%.amazonaws.com/%REPOSITORY_NAME%

REM
echo --- Iniciando sesion en ECR (%AWS_REGION%) ---
aws ecr get-login-password --region %AWS_REGION% | docker login --username AWS --password-stdin %AWS_ACCOUNT_ID%.dkr.ecr.%AWS_REGION%.amazonaws.com
IF %ERRORLEVEL% NEQ 0 (
    echo *** ERROR: Fallo en el login de ECR. ***
    goto :error
)
echo --- Login de ECR exitoso. ---
echo.

REM
    
echo ----------------------------------------------------
echo --- Procesando post-item ---
echo ----------------------------------------------------
REM
docker build --platform linux/amd64 --provenance=false -f "lambdas/postItem/Dockerfile" -t "%ECR_BASE%:post-item" .
IF %ERRORLEVEL% NEQ 0 ( echo *** ERROR: Fallo en BUILD de post-item *** & goto :error )
docker push "%ECR_BASE%:post-item"
IF %ERRORLEVEL% NEQ 0 ( echo *** ERROR: Fallo en PUSH de post-item *** & goto :error )
echo.

echo ----------------------------------------------------
echo --- Procesando get-items ---
echo ----------------------------------------------------
REM
docker build --platform linux/amd64 --provenance=false -f "lambdas/getItems/Dockerfile" -t "%ECR_BASE%:get-items" .
IF %ERRORLEVEL% NEQ 0 ( echo *** ERROR: Fallo en BUILD de get-items *** & goto :error )
docker push "%ECR_BASE%:get-items"
IF %ERRORLEVEL% NEQ 0 ( echo *** ERROR: Fallo en PUSH de get-items *** & goto :error )
echo.

echo ----------------------------------------------------
echo --- Procesando get-item ---
echo ----------------------------------------------------
REM
docker build --platform linux/amd64 --provenance=false -f "lambdas/getItem/Dockerfile" -t "%ECR_BASE%:get-item" .
IF %ERRORLEVEL% NEQ 0 ( echo *** ERROR: Fallo en BUILD de get-item *** & goto :error )
docker push "%ECR_BASE%:get-item"
IF %ERRORLEVEL% NEQ 0 ( echo *** ERROR: Fallo en PUSH de get-item *** & goto :error )
echo.

echo ----------------------------------------------------
echo --- Procesando put-item ---
echo ----------------------------------------------------
REM
docker build --platform linux/amd64 --provenance=false -f "lambdas/putItem/Dockerfile" -t "%ECR_BASE%:put-item" .
IF %ERRORLEVEL% NEQ 0 ( echo *** ERROR: Fallo en BUILD de put-item *** & goto :error )
docker push "%ECR_BASE%:put-item"
IF %ERRORLEVEL% NEQ 0 ( echo *** ERROR: Fallo en PUSH de put-item *** & goto :error )
echo.

echo ----------------------------------------------------
echo --- Procesando delete-item ---
echo ----------------------------------------------------
REM
docker build --platform linux/amd64 --provenance=false -f "lambdas/deleteItem/Dockerfile" -t "%ECR_BASE%:delete-item" .
IF %ERRORLEVEL% NEQ 0 ( echo *** ERROR: Fallo en BUILD de delete-item *** & goto :error )
docker push "%ECR_BASE%:delete-item"
IF %ERRORLEVEL% NEQ 0 ( echo *** ERROR: Fallo en PUSH de delete-item *** & goto :error )
echo.

echo ----------------------------------------------------
echo --- SCRIPT COMPLETADO ---
echo --- Todas las 5 imagenes han sido subidas a ECR (para linux/amd64). ---
echo ----------------------------------------------------
goto :EOF

:error
echo *** SCRIPT FALLIDO DEBIDO A UN ERROR ANTERIOR. ***

endlocal