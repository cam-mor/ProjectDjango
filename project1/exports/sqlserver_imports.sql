-- SQL Server import helper
-- 1) Run the CREATE TABLE statements below in your target database (adjust schema/name if needed)
-- 2) Ensure the SQL Server service account can access the CSV path OR copy the CSV files to the SQL Server host
-- 3) Run the BULK INSERT commands to load the CSVs (adjust file paths if required)

SET NOCOUNT ON;

-- USERS
IF OBJECT_ID('dbo.users','U') IS NOT NULL DROP TABLE dbo.users;
CREATE TABLE dbo.users (
  id INT PRIMARY KEY,
  username NVARCHAR(150) NOT NULL,
  email NVARCHAR(254) NULL,
  first_name NVARCHAR(150) NULL,
  last_name NVARCHAR(150) NULL,
  is_staff BIT NOT NULL,
  is_superuser BIT NOT NULL,
  is_active BIT NOT NULL,
  date_joined DATETIME2 NULL
);

-- PROFILES
IF OBJECT_ID('dbo.profiles','U') IS NOT NULL DROP TABLE dbo.profiles;
CREATE TABLE dbo.profiles (
  id INT PRIMARY KEY,
  user_id INT NOT NULL,
  major NVARCHAR(200) NULL,
  bio NVARCHAR(MAX) NULL,
  interests NVARCHAR(MAX) NULL,
  created_at DATETIME2 NULL
);

-- GROUPS
IF OBJECT_ID('dbo.groups','U') IS NOT NULL DROP TABLE dbo.groups;
CREATE TABLE dbo.groups (
  id INT PRIMARY KEY,
  name NVARCHAR(255) NOT NULL,
  description NVARCHAR(MAX) NULL,
  subject_id INT NULL,
  created_by_id INT NULL,
  max_members INT NULL,
  is_active BIT NULL,
  created_at DATETIME2 NULL
);

-- MEMBERSHIPS
IF OBJECT_ID('dbo.memberships','U') IS NOT NULL DROP TABLE dbo.memberships;
CREATE TABLE dbo.memberships (
  id INT PRIMARY KEY,
  user_id INT NOT NULL,
  group_id INT NOT NULL,
  role NVARCHAR(50) NULL,
  joined_at DATETIME2 NULL
);

-- SESSIONS
IF OBJECT_ID('dbo.sessions','U') IS NOT NULL DROP TABLE dbo.sessions;
CREATE TABLE dbo.sessions (
  id INT PRIMARY KEY,
  group_id INT NULL,
  title NVARCHAR(255) NULL,
  description NVARCHAR(MAX) NULL,
  date DATE NULL,
  start_time TIME NULL,
  end_time TIME NULL,
  location NVARCHAR(255) NULL,
  is_online BIT NULL,
  meeting_link NVARCHAR(512) NULL,
  status NVARCHAR(50) NULL,
  created_by_id INT NULL,
  created_at DATETIME2 NULL
);

-- MATERIALS
IF OBJECT_ID('dbo.materials','U') IS NOT NULL DROP TABLE dbo.materials;
CREATE TABLE dbo.materials (
  id INT PRIMARY KEY,
  group_id INT NULL,
  title NVARCHAR(255) NULL,
  description NVARCHAR(MAX) NULL,
  file NVARCHAR(512) NULL,
  link NVARCHAR(512) NULL,
  uploaded_by_id INT NULL,
  created_at DATETIME2 NULL
);

-- COMMENTS
IF OBJECT_ID('dbo.comments','U') IS NOT NULL DROP TABLE dbo.comments;
CREATE TABLE dbo.comments (
  id INT PRIMARY KEY,
  group_id INT NULL,
  author_id INT NULL,
  content NVARCHAR(MAX) NULL,
  parent_id INT NULL,
  created_at DATETIME2 NULL
);

-- BULK INSERT templates (adjust path if SQL Server cannot access client path)
-- Make sure FIRSTROW = 2 to skip header row and CODEPAGE = '65001' for UTF-8

BULK INSERT dbo.users
FROM 'C:\\Users\\iamxa\\Desktop\\ProjectDjango\\project1\\exports\\users.csv'
WITH (FIRSTROW = 2, FIELDTERMINATOR = ',', ROWTERMINATOR = '\n', CODEPAGE = '65001');

BULK INSERT dbo.profiles
FROM 'C:\\Users\\iamxa\\Desktop\\ProjectDjango\\project1\\exports\\profiles.csv'
WITH (FIRSTROW = 2, FIELDTERMINATOR = ',', ROWTERMINATOR = '\n', CODEPAGE = '65001');

BULK INSERT dbo.groups
FROM 'C:\\Users\\iamxa\\Desktop\\ProjectDjango\\project1\\exports\\groups.csv'
WITH (FIRSTROW = 2, FIELDTERMINATOR = ',', ROWTERMINATOR = '\n', CODEPAGE = '65001');

BULK INSERT dbo.memberships
FROM 'C:\\Users\\iamxa\\Desktop\\ProjectDjango\\project1\\exports\\memberships.csv'
WITH (FIRSTROW = 2, FIELDTERMINATOR = ',', ROWTERMINATOR = '\n', CODEPAGE = '65001');

BULK INSERT dbo.sessions
FROM 'C:\\Users\\iamxa\\Desktop\\ProjectDjango\\project1\\exports\\sessions.csv'
WITH (FIRSTROW = 2, FIELDTERMINATOR = ',', ROWTERMINATOR = '\n', CODEPAGE = '65001');

BULK INSERT dbo.materials
FROM 'C:\\Users\\iamxa\\Desktop\\ProjectDjango\\project1\\exports\\materials.csv'
WITH (FIRSTROW = 2, FIELDTERMINATOR = ',', ROWTERMINATOR = '\n', CODEPAGE = '65001');

BULK INSERT dbo.comments
FROM 'C:\\Users\\iamxa\\Desktop\\ProjectDjango\\project1\\exports\\comments.csv'
WITH (FIRSTROW = 2, FIELDTERMINATOR = ',', ROWTERMINATOR = '\n', CODEPAGE = '65001');

-- After import, run any necessary conversions (dates/times) if columns were imported as text
-- Example: convert a text date column to DATE using TRY_CONVERT
-- UPDATE dbo.sessions SET date = TRY_CONVERT(date, date, 120) WHERE date IS NOT NULL;

PRINT 'Import script completed (verify row counts and types).';
