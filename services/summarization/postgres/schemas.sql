/*
* Copyright (C) 2021 Diego Miguel Lozano <dml1001@alu.ubu.es>
*
* This program is free software: you can redistribute it and/or modify
* it under the terms of the GNU General Public License as published by
* the Free Software Foundation, either version 3 of the License, or
* (at your option) any later version.
*
* This program is distributed in the hope that it will be useful,
* but WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
* GNU General Public License for more details.
*
* You should have received a copy of the GNU General Public License
* along with this program.  If not, see <https://www.gnu.org/licenses/>.
*
* For license information on the libraries used, see LICENSE.
*/


/*
* DROP TABLES, TYPES & SCHEMAS
*/
DROP TABLE IF EXISTS summaries.raw_id_preprocessed_id CASCADE;
DROP TABLE IF EXISTS summaries.summary CASCADE;
DROP TABLE IF EXISTS summaries.model CASCADE;
DROP TABLE IF EXISTS summaries.model_family CASCADE;
DROP TABLE IF EXISTS summaries.vendor CASCADE;
DROP TABLE IF EXISTS summaries.language CASCADE;
drop table if exists summaries.source CASCADE;

drop table if exists files.file_id_content_id CASCADE;
drop table if exists files.content CASCADE;

DROP TYPE IF EXISTS summaries.NLP_TASK;
DROP TYPE IF EXISTS summaries.STATUS;

DROP TYPE IF EXISTS files.FILE_TYPE;

DROP SCHEMA IF EXISTS summaries;
DROP SCHEMA IF EXISTS files;

DROP ROLE IF EXISTS dispatcher_summaries;
DROP ROLE IF EXISTS dispatcher_files;


/*
* CREATE SCHEMAS
*/
CREATE SCHEMA summaries;
CREATE SCHEMA files;

/*
* CREATE TABLES for SCHEMA summaries
*/
CREATE TABLE summaries.source (
    source_id           CHAR(64) PRIMARY KEY,
    content             TEXT NOT NULL,
    content_length      INTEGER NOT NULL CHECK (content_length > 0)
);

CREATE TABLE summaries.language (
    language_id         SERIAL PRIMARY KEY,
    name                TEXT NOT NULL,
    language_tag        TEXT UNIQUE NOT NULL
);

CREATE TABLE summaries.vendor (
    vendor_id           SERIAL PRIMARY KEY,
    name                TEXT UNIQUE NOT NULL,
    see                 TEXT
);

CREATE TABLE summaries.model_family (
    family_id           SERIAL PRIMARY KEY,
    name                TEXT UNIQUE NOT NULL,
    authors             TEXT[],
    organizations       TEXT[],
    year                DATE,
    see                 TEXT
);

CREATE TYPE summaries.NLP_TASK AS ENUM ('summarization', 'question-answering',
                                        'text-classification', 'conversational',
                                        'translation');
CREATE TABLE summaries.model (
    model_id            SERIAL PRIMARY KEY,
    name                TEXT UNIQUE NOT NULL,
    family_name         TEXT NOT NULL
        CONSTRAINT FK_family_name
        REFERENCES summaries.model_family(name) ON UPDATE CASCADE,
    tasks               summaries.NLP_TASK[] NOT NULL,
    vendor_name         TEXT NOT NULL 
        CONSTRAINT FK_vendor_name
        REFERENCES summaries.vendor(name) ON UPDATE CASCADE,
    year                DATE,
    see                 TEXT
);

CREATE TYPE summaries.STATUS AS ENUM ('preprocessing', 'encoding', 'summarizing',
                                      'postprocessing', 'completed');
CREATE TABLE summaries.summary (
    summary_id          CHAR(64) PRIMARY KEY,
    source_id           CHAR(64) NOT NULL
        CONSTRAINT FK_source_id
        REFERENCES summaries.source ON DELETE CASCADE ON UPDATE CASCADE,
    summary             TEXT,
    summary_length      INTEGER,
    model_name          TEXT NOT NULL
        CONSTRAINT FK_model_name
        REFERENCES summaries.model(name) ON UPDATE CASCADE,
    params              JSON NOT NULL,
    status              summaries.STATUS NOT NULL,
    started_at          TIMESTAMPTZ NOT NULL,
    ended_at            TIMESTAMPTZ,
    language_tag        TEXT NOT NULL
        CONSTRAINT FK_language_tag
        REFERENCES summaries.language(language_tag) ON UPDATE CASCADE,
    request_count       INTEGER NOT NULL CHECK (request_count >= 0) DEFAULT 0
);

CREATE TABLE summaries.raw_id_preprocessed_id (
    raw_id              CHAR(64) UNIQUE NOT NULL,
    preprocessed_id     CHAR(64) NOT NULL
        CONSTRAINT FK_preprocessed_id
        REFERENCES summaries.summary ON DELETE CASCADE ON UPDATE CASCADE,
    cache               BOOLEAN NOT NULL DEFAULT TRUE,
    last_accessed       TIMESTAMPTZ NOT NULL,
    warnings            JSON,
    PRIMARY KEY(raw_id, preprocessed_id)
);

/*
* CREATE TABLES for SCHEMA files
*/
CREATE TYPE files.FILE_TYPE AS ENUM ('document', 'audio', 'image', 'video');

CREATE TABLE files.content (
    content_id          CHAR(64) PRIMARY KEY,
    content             TEXT NOT NULL
);

CREATE TABLE files.file_id_content_id (
    file_id             CHAR(64) UNIQUE NOT NULL,
    content_id          CHAR(64) NOT NULL
        CONSTRAINT FK_content_id
        REFERENCES files.content ON DELETE CASCADE ON UPDATE CASCADE,
    cache               BOOLEAN NOT NULL DEFAULT TRUE,
    file_type           files.FILE_TYPE NOT NULL,
    last_accessed       TIMESTAMPTZ NOT NULL,
    request_count       INTEGER NOT NULL CHECK (request_count >= 0) DEFAULT 0
);

/*
* Set up ROLES
*/
CREATE ROLE dispatcher_summaries;
CREATE ROLE dispatcher_files;
GRANT CONNECT ON DATABASE jizt TO dispatcher_summaries;
GRANT CONNECT ON DATABASE jizt TO dispatcher_files;
GRANT USAGE ON SCHEMA summaries TO dispatcher_summaries;
GRANT USAGE ON SCHEMA files TO dispatcher_files;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA summaries TO dispatcher_summaries;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA files TO dispatcher_files;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA summaries TO dispatcher_summaries;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA files TO dispatcher_files;

/* Users have to be created manually. Kubernetes secrets must be set up.
*  values.yaml has to refer to the created secrets.
*
*  CREATE USER my_user WITH PASSWORD 'my_password';
*  GRANT my_role TO my_user;
*/


/*
* INSERTS
*/
INSERT INTO summaries.language
VALUES (DEFAULT, 'English', 'en');

INSERT INTO summaries.vendor
VALUES (DEFAULT, 'Hugging Face', 'https://huggingface.co');

INSERT INTO summaries.model_family
VALUES (DEFAULT, 'T5', '{"Colin Raffel", "Noam Shazeer", "Adam Roberts",
                 "Katherine Lee", "Sharan Narang", "Michael Matena",
                 "Yanqi Zhou", "Wei Li", "Peter J. Liu"}',
                 '{"Google"}', '2019-10-23', 'https://arxiv.org/abs/1910.10683');

INSERT INTO summaries.model
VALUES (DEFAULT, 't5-large', 'T5', '{"summarization", "translation"}',
        'Hugging Face', '2019-12-12',
        'https://huggingface.co/transformers/model_doc/t5.html');
