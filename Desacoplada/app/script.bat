@ECHO OFF
SETLOCAL

REM --- Configuración ---
REM Reemplaza esto con tus valores si son diferentes
SET "AWS_ACCOUNT_ID=339713111309"
SET "AWS_REGION=us-east-1"
SET "REPOSITORY_NAME=products-app-lambdas"

REM --- Variables Calculadas ---
SET "ECR_URI=%AWS_ACCOUNT_ID%.dkr.ecr.%AWS_REGION%.amazonaws.com"
SET "FULL_REPO_URI=%ECR_URI%/%REPOSITORY_NAME%"

REM --- Paso 1: Iniciar sesión en ECR ---
ECHO Iniciando sesion en ECR...
aws ecr get-login-password --region %AWS_REGION% | docker login --username AWS --password-stdin %ECR_URI%
IF %ERRORLEVEL% NEQ 0 (
    ECHO *** ERROR: Fallo al iniciar sesion en ECR. Abortando. ***
    GOTO :eof
)
ECHO ¡Inicio de sesion exitoso!

REM --- Paso 2: Definir la función de ayuda ---
GOTO :main

REM Define una "función" (subrutina) para construir y subir
:build_and_push
    SET "FOLDER_NAME=%~1"
    SET "IMAGE_TAG=%~2"
    SET "DOCKERFILE_PATH=lambdas\%FOLDER_NAME%\Dockerfile"
    SET "FULL_IMAGE_NAME=%FULL_REPO_URI%:%IMAGE_TAG%"

    ECHO --------------------------------------------------
    ECHO Construyendo: %FULL_IMAGE_NAME%
    ECHO Dockerfile: %DOCKERFILE_PATH%
    ECHO --------------------------------------------------
    
    REM El '.' al final es CRUCIAL. Usa la carpeta actual (raíz) como contexto.
    docker build -t "%FULL_IMAGE_NAME%" -f "%DOCKERFILE_PATH%" .
    IF %ERRORLEVEL% NEQ 0 (
        ECHO *** ERROR: Fallo en BUILD de %IMAGE_TAG% ***
        EXIT /B 1
    )
    
    ECHO Subiendo: %FULL_IMAGE_NAME%
    docker push "%FULL_IMAGE_NAME%"
    IF %ERRORLEVEL% NEQ 0 (
        ECHO *** ERROR: Fallo en PUSH de %IMAGE_TAG% ***
        EXIT /B 1
    )
    
    ECHO ¡Exito para %IMAGE_TAG%!
    EXIT /B 0

:main
    REM --- Paso 3: Construir y Subir cada Lambda ---
    ECHO.
    CALL :build_and_push postItem post-item
    IF %ERRORLEVEL% NEQ 0 GOTO :error

    ECHO.
    CALL :build_and_push getItems get-items
    IF %ERRORLEVEL% NEQ 0 GOTO :error

    ECHO.
    CALL :build_and_push getItem get-item
    IF %ERRORLEVEL% NEQ 0 GOTO :error

    ECHO.
    CALL :build_and_push putItem put-item
    IF %ERRORLEVEL% NEQ 0 GOTO :error

    ECHO.
    CALL :build_and_push deleteItem delete-item
    IF %ERRORLEVEL% NEQ 0 GOTO :error

    ECHO --------------------------------------------------
    ECHO ¡PROCESO COMPLETADO!
    ECHO Todas las 5 imagenes han sido subidas a ECR.
    ECHO --------------------------------------------------
    GOTO :end

:error
    ECHO *** SCRIPT FALLIDO DEBIDO A UN ERROR ANTERIOR. ***

:end
ENDLOCAL