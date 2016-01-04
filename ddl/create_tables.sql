// Tabelle Liefereinheit
CREATE TABLE LIEFEREINHEIT 
	(
	   	ID 			NUMBER(10,0)	NOT NULL PRIMARY KEY,
	   	NAME		NVARCHAR2(255)	NOT NULL, 
		BFSNR		NUMBER(10,0), 
		GPR_SOURCE	NVARCHAR2(512),
		TS_SOURCE	NVARCHAR2(512), 
		MD5			VARCHAR2(36 BYTE),
		GPRCODE		NVARCHAR2(8),
		WORKFLOW	NVARCHAR2(32)	NOT NULL
  	);

// Tabelle Ticket
CREATE TABLE TICKET 
  	(
	  	ID				NUMBER(38,0) 	NOT NULL PRIMARY KEY,
	  	NAME			NVARCHAR2(255),
		LIEFEREINHEIT 	NUMBER(10,0) 	REFERENCES LIEFEREINHEIT(ID), 
		STATUS			NUMBER(2,0) 	NOT NULL,
		ART				NUMBER(2,0) 	NOT NULL,
		TASK_ID_GEODB	NUMBER(38,0)
	);
CREATE SEQUENCE ticket_seq;

CREATE OR REPLACE TRIGGER ticket_insert_trigger
  BEFORE INSERT ON ticket
  FOR EACH ROW
BEGIN
  :new.id := ticket_seq.nextval;
END;

// Tabelle GPR
CREATE TABLE GPR
	(
		GPRCODE			NVARCHAR2(8)	NOT NULL,
		EBECODE 		NVARCHAR2(24)	NOT NULL,
		FILTER_FIELD	NVARCHAR2(32),
		FILTER_TYPE		NVARCHAR2(16)
	);