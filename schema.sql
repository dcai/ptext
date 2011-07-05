CREATE TABLE "pages" ("id" INTEGER PRIMARY KEY  NOT NULL ,"title" TEXT NOT NULL ,"created" INTEGER,"modified" INTEGER,"parent_id" INTEGER NOT NULL  DEFAULT (0) );
CREATE TABLE "sessions" ("session_id" TEXT NOT NULL  UNIQUE , "atime" INTEGER NOT NULL  DEFAULT CURRENT_TIMESTAMP, "data" TEXT);
CREATE TABLE "tags" ("id" INTEGER PRIMARY KEY  NOT NULL , "tagname" TEXT NOT NULL  UNIQUE , "tagdescription" TEXT, "created" INTEGER);
CREATE TABLE "users" ("id" INTEGER PRIMARY KEY  NOT NULL , "username" TEXT NOT NULL  UNIQUE , "password" TEXT NOT NULL , "firstname" TEXT, "lastname" TEXT, "email" TEXT, "created" INTEGER DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE "versions" ("id" INTEGER PRIMARY KEY  NOT NULL , "pageid" INTEGER, "content" TEXT, "format" CHAR, "version" INTEGER, "created" INTEGER);
