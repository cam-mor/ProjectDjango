-- import_to_sqlserver.sql
-- Script generado para importar los CSVs del proyecto a SQL Server
-- Flujo recomendado:
-- 1) Ejecutar el script de PowerShell `convert_csvs_to_tsv.ps1` en la carpeta de exports para generar .tsv limpias.
--    En PowerShell (ejecutar desde la ruta del proyecto o con ruta absoluta):
--      cd C:\Users\iamxa\Desktop\ProjectDjango\project1\exports
--      .\convert_csvs_to_tsv.ps1
-- 2) Abrir este archivo en SSMS, seleccionar la conexión y ejecutar por secciones.
-- 3) Ejecutar las BULK INSERT sobre los archivos .tsv (el script usa rutas absolutas a la carpeta exports).
-- 4) Verificar conteos y activar constraints/índices finales.

SET NOCOUNT ON;

-- 0) Parámetros (ajusta si tu instancia tiene otra ruta)
DECLARE @exportsPath NVARCHAR(4000) = N'C:\Users\iamxa\Desktop\ProjectDjango\project1\exports\';

-- 1) Crear base de datos (opcional)
IF DB_ID(N'StudyGroupsMVP') IS NULL
BEGIN
    PRINT 'Creating database StudyGroupsMVP...';
    CREATE DATABASE StudyGroupsMVP;
END
GO

USE StudyGroupsMVP;
GO

-- 2) Crear tablas finales (diseño estilo "AdventureWorks-lite": IDENTITY PKs, FK constraints, índices)
-- Nota: Creamos una tabla Subjects mínima porque groups.subject_id hace referencia a ella.
-- Asegurar DROP seguro de Subjects (eliminar FKs que lo referencian primero)
IF OBJECT_ID('dbo.Subjects','U') IS NOT NULL
BEGIN
    DECLARE @dropFkOnSubjects NVARCHAR(MAX) = N'';
    SELECT @dropFkOnSubjects += N'ALTER TABLE ' + QUOTENAME(OBJECT_SCHEMA_NAME(parent_object_id)) + N'.' + QUOTENAME(OBJECT_NAME(parent_object_id))
        + N' DROP CONSTRAINT ' + QUOTENAME(name) + N';' + CHAR(13)
    FROM sys.foreign_keys
    WHERE referenced_object_id = OBJECT_ID(N'dbo.Subjects');

    IF LEN(@dropFkOnSubjects) > 0
        EXEC sp_executesql @dropFkOnSubjects;

    DROP TABLE dbo.Subjects;
END
CREATE TABLE dbo.Subjects (
    SubjectID INT IDENTITY(1,1) PRIMARY KEY,
    Name NVARCHAR(255) NOT NULL,
    Description NVARCHAR(MAX) NULL
);

IF OBJECT_ID('dbo.Users','U') IS NOT NULL DROP TABLE dbo.Users;
CREATE TABLE dbo.Users (
    UserID INT IDENTITY(1,1) PRIMARY KEY,
    LegacyID INT NULL, -- mantendremos el id original en LegacyID
    Username NVARCHAR(150) NOT NULL UNIQUE,
    Email NVARCHAR(254) NULL,
    FirstName NVARCHAR(150) NULL,
    LastName NVARCHAR(150) NULL,
    IsStaff BIT NOT NULL DEFAULT(0),
    IsSuperuser BIT NOT NULL DEFAULT(0),
    IsActive BIT NOT NULL DEFAULT(1),
    DateJoined DATETIME2 NULL
);
CREATE INDEX IX_Users_Email ON dbo.Users(Email);

IF OBJECT_ID('dbo.Profiles','U') IS NOT NULL DROP TABLE dbo.Profiles;
CREATE TABLE dbo.Profiles (
    ProfileID INT IDENTITY(1,1) PRIMARY KEY,
    LegacyID INT NULL,
    UserID INT NOT NULL,
    Major NVARCHAR(200) NULL,
    Bio NVARCHAR(MAX) NULL,
    Interests NVARCHAR(MAX) NULL,
    CreatedAt DATETIME2 NULL,
    CONSTRAINT FK_Profiles_Users FOREIGN KEY (UserID) REFERENCES dbo.Users(UserID)
);
CREATE INDEX IX_Profiles_UserID ON dbo.Profiles(UserID);

IF OBJECT_ID('dbo.Groups','U') IS NOT NULL DROP TABLE dbo.Groups;
CREATE TABLE dbo.Groups (
    GroupID INT IDENTITY(1,1) PRIMARY KEY,
    LegacyID INT NULL,
    Name NVARCHAR(255) NOT NULL,
    Description NVARCHAR(MAX) NULL,
    SubjectID INT NULL,
    CreatedByID INT NULL,
    MaxMembers INT NULL,
    IsActive BIT NULL,
    CreatedAt DATETIME2 NULL,
    CONSTRAINT FK_Groups_Subjects FOREIGN KEY (SubjectID) REFERENCES dbo.Subjects(SubjectID),
    CONSTRAINT FK_Groups_CreatedBy FOREIGN KEY (CreatedByID) REFERENCES dbo.Users(UserID)
);
CREATE INDEX IX_Groups_CreatedBy ON dbo.Groups(CreatedByID);

IF OBJECT_ID('dbo.Memberships','U') IS NOT NULL DROP TABLE dbo.Memberships;
CREATE TABLE dbo.Memberships (
    MembershipID INT IDENTITY(1,1) PRIMARY KEY,
    LegacyID INT NULL,
    UserID INT NOT NULL,
    GroupID INT NOT NULL,
    Role NVARCHAR(50) NULL,
    JoinedAt DATETIME2 NULL,
    CONSTRAINT FK_Memberships_Users FOREIGN KEY (UserID) REFERENCES dbo.Users(UserID),
    CONSTRAINT FK_Memberships_Groups FOREIGN KEY (GroupID) REFERENCES dbo.Groups(GroupID)
);
CREATE INDEX IX_Memberships_UserID ON dbo.Memberships(UserID);
CREATE INDEX IX_Memberships_GroupID ON dbo.Memberships(GroupID);

IF OBJECT_ID('dbo.Sessions','U') IS NOT NULL DROP TABLE dbo.Sessions;
CREATE TABLE dbo.Sessions (
    SessionID INT IDENTITY(1,1) PRIMARY KEY,
    LegacyID INT NULL,
    GroupID INT NULL,
    Title NVARCHAR(255) NULL,
    Description NVARCHAR(MAX) NULL,
    [Date] DATE NULL,
    StartTime TIME NULL,
    EndTime TIME NULL,
    Location NVARCHAR(255) NULL,
    IsOnline BIT NULL,
    MeetingLink NVARCHAR(512) NULL,
    [Status] NVARCHAR(50) NULL,
    CreatedByID INT NULL,
    CreatedAt DATETIME2 NULL,
    CONSTRAINT FK_Sessions_Groups FOREIGN KEY (GroupID) REFERENCES dbo.Groups(GroupID),
    CONSTRAINT FK_Sessions_CreatedBy FOREIGN KEY (CreatedByID) REFERENCES dbo.Users(UserID)
);
CREATE INDEX IX_Sessions_GroupID ON dbo.Sessions(GroupID);

IF OBJECT_ID('dbo.Materials','U') IS NOT NULL DROP TABLE dbo.Materials;
CREATE TABLE dbo.Materials (
    MaterialID INT IDENTITY(1,1) PRIMARY KEY,
    LegacyID INT NULL,
    GroupID INT NULL,
    Title NVARCHAR(255) NULL,
    Description NVARCHAR(MAX) NULL,
    FilePath NVARCHAR(512) NULL,
    Link NVARCHAR(512) NULL,
    UploadedByID INT NULL,
    CreatedAt DATETIME2 NULL,
    CONSTRAINT FK_Materials_Groups FOREIGN KEY (GroupID) REFERENCES dbo.Groups(GroupID),
    CONSTRAINT FK_Materials_UploadedBy FOREIGN KEY (UploadedByID) REFERENCES dbo.Users(UserID)
);
CREATE INDEX IX_Materials_GroupID ON dbo.Materials(GroupID);

IF OBJECT_ID('dbo.Comments','U') IS NOT NULL DROP TABLE dbo.Comments;
CREATE TABLE dbo.Comments (
    CommentID INT IDENTITY(1,1) PRIMARY KEY,
    LegacyID INT NULL,
    GroupID INT NULL,
    AuthorID INT NULL,
    Content NVARCHAR(MAX) NULL,
    ParentLegacyID INT NULL,
    CreatedAt DATETIME2 NULL,
    CONSTRAINT FK_Comments_Groups FOREIGN KEY (GroupID) REFERENCES dbo.Groups(GroupID),
    CONSTRAINT FK_Comments_Author FOREIGN KEY (AuthorID) REFERENCES dbo.Users(UserID)
);
CREATE INDEX IX_Comments_GroupID ON dbo.Comments(GroupID);
CREATE INDEX IX_Comments_AuthorID ON dbo.Comments(AuthorID);

PRINT 'Final tables (with IDENTITY PKs) created.';

-- 3) Crear tablas STAGING (todas como NVARCHAR para evitar problemas de parseo inicial)
-- Se importarán los .tsv generados por el PowerShell helper para respetar comillas internas.
-- Asegurarse de que el schema 'stg' existe antes de crear tablas staging
IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'stg')
    EXEC('CREATE SCHEMA stg');

-- Eliminar tablas staging si existen (se recrearán a continuación)
IF OBJECT_ID('stg.users_staging','U') IS NOT NULL DROP TABLE stg.users_staging;
IF OBJECT_ID('stg.profiles_staging','U') IS NOT NULL DROP TABLE stg.profiles_staging;
IF OBJECT_ID('stg.groups_staging','U') IS NOT NULL DROP TABLE stg.groups_staging;
IF OBJECT_ID('stg.memberships_staging','U') IS NOT NULL DROP TABLE stg.memberships_staging;
IF OBJECT_ID('stg.sessions_staging','U') IS NOT NULL DROP TABLE stg.sessions_staging;
IF OBJECT_ID('stg.materials_staging','U') IS NOT NULL DROP TABLE stg.materials_staging;
IF OBJECT_ID('stg.comments_staging','U') IS NOT NULL DROP TABLE stg.comments_staging;

CREATE TABLE stg.users_staging (
    id NVARCHAR(100),
    username NVARCHAR(200),
    email NVARCHAR(300),
    first_name NVARCHAR(200),
    last_name NVARCHAR(200),
    is_staff NVARCHAR(50),
    is_superuser NVARCHAR(50),
    is_active NVARCHAR(50),
    date_joined NVARCHAR(200)
);

CREATE TABLE stg.profiles_staging (
    id NVARCHAR(100),
    user_id NVARCHAR(100),
    major NVARCHAR(MAX),
    bio NVARCHAR(MAX),
    interests NVARCHAR(MAX),
    created_at NVARCHAR(200)
);

CREATE TABLE stg.groups_staging (
    id NVARCHAR(100),
    name NVARCHAR(MAX),
    description NVARCHAR(MAX),
    subject_id NVARCHAR(100),
    created_by_id NVARCHAR(100),
    max_members NVARCHAR(100),
    is_active NVARCHAR(50),
    created_at NVARCHAR(200)
);

CREATE TABLE stg.memberships_staging (
    id NVARCHAR(100),
    user_id NVARCHAR(100),
    group_id NVARCHAR(100),
    role NVARCHAR(100),
    joined_at NVARCHAR(200)
);

CREATE TABLE stg.sessions_staging (
    id NVARCHAR(100),
    group_id NVARCHAR(100),
    title NVARCHAR(MAX),
    description NVARCHAR(MAX),
    date NVARCHAR(100),
    start_time NVARCHAR(50),
    end_time NVARCHAR(50),
    location NVARCHAR(255),
    is_online NVARCHAR(50),
    meeting_link NVARCHAR(512),
    status NVARCHAR(100),
    created_by_id NVARCHAR(100),
    created_at NVARCHAR(200)
);

CREATE TABLE stg.materials_staging (
    id NVARCHAR(100),
    group_id NVARCHAR(100),
    title NVARCHAR(MAX),
    description NVARCHAR(MAX),
    file_path NVARCHAR(512),
    link NVARCHAR(512),
    uploaded_by_id NVARCHAR(100),
    created_at NVARCHAR(200)
);

CREATE TABLE stg.comments_staging (
    id NVARCHAR(100),
    group_id NVARCHAR(100),
    author_id NVARCHAR(100),
    content NVARCHAR(MAX),
    parent_id NVARCHAR(100),
    created_at NVARCHAR(200)
);

PRINT 'Staging tables created.';

-- 4) BULK INSERT desde los .tsv generados (recomendado) -- ajusta si no usas .tsv
-- Asegúrate de ejecutar convert_csvs_to_tsv.ps1 antes de estos BULK INSERTs.

BULK INSERT stg.users_staging
FROM 'C:\Users\iamxa\Desktop\ProjectDjango\project1\exports\users.tsv'
WITH (FIRSTROW = 2, FIELDTERMINATOR = '\t', ROWTERMINATOR = '\n', CODEPAGE = '65001');

BULK INSERT stg.profiles_staging
FROM 'C:\Users\iamxa\Desktop\ProjectDjango\project1\exports\profiles.tsv'
WITH (FIRSTROW = 2, FIELDTERMINATOR = '\t', ROWTERMINATOR = '\n', CODEPAGE = '65001');

BULK INSERT stg.groups_staging
FROM 'C:\Users\iamxa\Desktop\ProjectDjango\project1\exports\groups.tsv'
WITH (FIRSTROW = 2, FIELDTERMINATOR = '\t', ROWTERMINATOR = '\n', CODEPAGE = '65001');

BULK INSERT stg.memberships_staging
FROM 'C:\Users\iamxa\Desktop\ProjectDjango\project1\exports\memberships.tsv'
WITH (FIRSTROW = 2, FIELDTERMINATOR = '\t', ROWTERMINATOR = '\n', CODEPAGE = '65001');

BULK INSERT stg.sessions_staging
FROM 'C:\Users\iamxa\Desktop\ProjectDjango\project1\exports\sessions.tsv'
WITH (FIRSTROW = 2, FIELDTERMINATOR = '\t', ROWTERMINATOR = '\n', CODEPAGE = '65001');

BULK INSERT stg.materials_staging
FROM 'C:\Users\iamxa\Desktop\ProjectDjango\project1\exports\materials.tsv'
WITH (FIRSTROW = 2, FIELDTERMINATOR = '\t', ROWTERMINATOR = '\n', CODEPAGE = '65001');

BULK INSERT stg.comments_staging
FROM 'C:\Users\iamxa\Desktop\ProjectDjango\project1\exports\comments.tsv'
WITH (FIRSTROW = 2, FIELDTERMINATOR = '\t', ROWTERMINATOR = '\n', CODEPAGE = '65001');

PRINT 'Bulk insert to staging complete.';

-- 5) Transferir datos de STAGING a tablas finales
-- Usuarios: convertir booleans y fechas
SET XACT_ABORT ON;
BEGIN TRANSACTION;

-- Users: preserve legacy id into LegacyID and populate UserID via IDENTITY (or use IDENTITY_INSERT if prefieres mantener ids)
INSERT INTO dbo.Users (LegacyID, Username, Email, FirstName, LastName, IsStaff, IsSuperuser, IsActive, DateJoined)
SELECT
    TRY_CAST(id AS INT) AS LegacyID,
    username,
    NULLIF(email,'') AS Email,
    NULLIF(first_name,'') AS FirstName,
    NULLIF(last_name,'') AS LastName,
    CASE WHEN LOWER(is_staff) IN ('true','1','yes') THEN 1 ELSE 0 END,
    CASE WHEN LOWER(is_superuser) IN ('true','1','yes') THEN 1 ELSE 0 END,
    CASE WHEN LOWER(is_active) IN ('true','1','yes') THEN 1 ELSE 0 END,
    TRY_CONVERT(datetime2, TRY_CONVERT(datetimeoffset, date_joined))
FROM stg.users_staging;

-- Profiles: map user via legacy id -> new UserID
INSERT INTO dbo.Profiles (LegacyID, UserID, Major, Bio, Interests, CreatedAt)
SELECT
    TRY_CAST(s.id AS INT) AS LegacyID,
    u.UserID,
    s.major,
    s.bio,
    s.interests,
    TRY_CONVERT(datetime2, TRY_CONVERT(datetimeoffset, s.created_at))
FROM stg.profiles_staging s
LEFT JOIN dbo.Users u ON u.LegacyID = TRY_CAST(s.user_id AS INT);

-- Groups
INSERT INTO dbo.Groups (LegacyID, Name, Description, SubjectID, CreatedByID, MaxMembers, IsActive, CreatedAt)
SELECT
    TRY_CAST(s.id AS INT),
    s.name,
    s.description,
    CASE WHEN TRY_CAST(s.subject_id AS INT) IS NULL THEN NULL ELSE TRY_CAST(s.subject_id AS INT) END,
    u.UserID,
    TRY_CAST(NULLIF(s.max_members,'') AS INT),
    CASE WHEN LOWER(s.is_active) IN ('true','1','yes') THEN 1 ELSE 0 END,
    TRY_CONVERT(datetime2, TRY_CONVERT(datetimeoffset, s.created_at))
FROM stg.groups_staging s
LEFT JOIN dbo.Users u ON u.LegacyID = TRY_CAST(s.created_by_id AS INT);

-- Memberships
INSERT INTO dbo.Memberships (LegacyID, UserID, GroupID, Role, JoinedAt)
SELECT
    TRY_CAST(s.id AS INT),
    u.UserID,
    g.GroupID,
    s.role,
    TRY_CONVERT(datetime2, TRY_CONVERT(datetimeoffset, s.joined_at))
FROM stg.memberships_staging s
LEFT JOIN dbo.Users u ON u.LegacyID = TRY_CAST(s.user_id AS INT)
LEFT JOIN dbo.Groups g ON g.LegacyID = TRY_CAST(s.group_id AS INT);

-- Sessions
INSERT INTO dbo.Sessions (LegacyID, GroupID, Title, Description, [Date], StartTime, EndTime, Location, IsOnline, MeetingLink, [Status], CreatedByID, CreatedAt)
SELECT
    TRY_CAST(s.id AS INT),
    g.GroupID,
    s.title,
    s.description,
    TRY_CONVERT(date, s.date),
    TRY_CONVERT(time, s.start_time),
    TRY_CONVERT(time, s.end_time),
    s.location,
    CASE WHEN LOWER(s.is_online) IN ('true','1','yes') THEN 1 ELSE 0 END,
    NULLIF(s.meeting_link,''),
    s.status,
    u.UserID,
    TRY_CONVERT(datetime2, TRY_CONVERT(datetimeoffset, s.created_at))
FROM stg.sessions_staging s
LEFT JOIN dbo.Groups g ON g.LegacyID = TRY_CAST(s.group_id AS INT)
LEFT JOIN dbo.Users u ON u.LegacyID = TRY_CAST(s.created_by_id AS INT);

-- Materials
INSERT INTO dbo.Materials (LegacyID, GroupID, Title, Description, FilePath, Link, UploadedByID, CreatedAt)
SELECT
    TRY_CAST(s.id AS INT),
    g.GroupID,
    s.title,
    s.description,
    s.file_path,
    s.link,
    u.UserID,
    TRY_CONVERT(datetime2, TRY_CONVERT(datetimeoffset, s.created_at))
FROM stg.materials_staging s
LEFT JOIN dbo.Groups g ON g.LegacyID = TRY_CAST(s.group_id AS INT)
LEFT JOIN dbo.Users u ON u.LegacyID = TRY_CAST(s.uploaded_by_id AS INT);

-- Comments (preserve parent relationship via Legacy IDs; ParentLegacyID stored to resolve later)
INSERT INTO dbo.Comments (LegacyID, GroupID, AuthorID, Content, ParentLegacyID, CreatedAt)
SELECT
    TRY_CAST(s.id AS INT),
    g.GroupID,
    u.UserID,
    s.content,
    TRY_CAST(NULLIF(s.parent_id,'') AS INT),
    TRY_CONVERT(datetime2, TRY_CONVERT(datetimeoffset, s.created_at))
FROM stg.comments_staging s
LEFT JOIN dbo.Groups g ON g.LegacyID = TRY_CAST(s.group_id AS INT)
LEFT JOIN dbo.Users u ON u.LegacyID = TRY_CAST(s.author_id AS INT);

COMMIT TRANSACTION;

PRINT 'Data transfer from staging complete.';

-- 6) Resolver relaciones de respuesta: NO sobreescribir ParentLegacyID (preserva el id legado)
-- En su lugar, crea ParentCommentID y rellénalo con el CommentID real del padre.
-- Nota: si ejecutas por partes, asegúrate de correr el bloque de ADD COLUMN antes del UPDATE que lo usa.

-- 7) Opcional: crear ParentCommentID y FK
-- 7) Opcional: crear ParentCommentID y FK
-- Separar en batches para evitar problemas de resolución de nombres en la misma ejecución
IF COL_LENGTH('dbo.Comments','ParentCommentID') IS NULL
BEGIN
    ALTER TABLE dbo.Comments ADD ParentCommentID INT NULL;
END
GO

-- Actualizar ParentCommentID usando JOIN (mejor rendimiento y menos ambigüedad)
UPDATE c
SET ParentCommentID = p.CommentID
FROM dbo.Comments c
INNER JOIN dbo.Comments p ON p.LegacyID = c.ParentLegacyID
WHERE c.ParentLegacyID IS NOT NULL;
GO

-- Crear la FK si no existe
IF NOT EXISTS (
    SELECT 1 FROM sys.foreign_keys fk WHERE fk.parent_object_id = OBJECT_ID('dbo.Comments') AND fk.name = 'FK_Comments_Parent'
)
BEGIN
    ALTER TABLE dbo.Comments ADD CONSTRAINT FK_Comments_Parent FOREIGN KEY (ParentCommentID) REFERENCES dbo.Comments(CommentID);
END
GO

PRINT 'Parent comment IDs resolved.';

-- 8) Limpieza: (opcional) eliminar tablas staging
-- DROP SCHEMA stg CASCADE; -- usar con cuidado

PRINT 'Import script finished. Revise resultados y cree índices adicionales según necesidad.';
