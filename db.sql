CREATE TABLE "pages" ("id" INTEGER PRIMARY KEY  NOT NULL ,"title" TEXT NOT NULL ,"content" TEXT,"created" INTEGER,"modified" INTEGER);
CREATE TABLE "sessions" ("session_id" TEXT NOT NULL  UNIQUE , "atime" INTEGER NOT NULL  DEFAULT CURRENT_TIMESTAMP, "data" TEXT);
CREATE TABLE "users" ("id" INTEGER PRIMARY KEY  NOT NULL , "username" TEXT NOT NULL  UNIQUE , "password" TEXT NOT NULL , "firstname" TEXT, "lastname" TEXT, "email" TEXT, "created" INTEGER DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE "versions" ("id" INTEGER PRIMARY KEY  NOT NULL , "pageid" INTEGER, "content" TEXT, "format" CHAR, "version" INTEGER, "created" INTEGER);
