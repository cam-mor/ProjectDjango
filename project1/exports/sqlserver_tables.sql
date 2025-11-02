-- SQL Server table definitions only
-- Run this file in the target database (open in SSMS, select the database, then Execute)
-- It will DROP the table if exists, then CREATE the table schema.

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

PRINT 'Table definitions created (or replaced).';
